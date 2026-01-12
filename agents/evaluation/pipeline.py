"""
IvyQuest v10.0 - Evaluation Pipeline
====================================

Orchestrate full evaluation runs combining objective metrics
and LLM-as-judge scoring.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from collections import Counter
import uuid
import structlog

from .golden_loader import GoldenDatasetLoader, GoldenExample
from .objective_metrics import ObjectiveMetricsCalculator, ObjectiveScore
from .llm_judge import LLMJudge, JudgeResult

logger = structlog.get_logger()


@dataclass
class EvaluationResult:
    """Result of evaluating a single golden example."""
    run_id: str
    golden_id: str
    agent_version: str
    timestamp: str

    # Scores
    objective_scores: Dict[str, float]
    llm_judge_scores: Dict[str, float]
    overall_score: float

    # Pass/Fail
    passed: bool
    pass_threshold: float

    # Diagnostics
    weaknesses: List[str]
    suggestions: List[str]

    # Performance
    duration_ms: int

    # Raw data
    agent_output: Dict[str, Any]
    expected_output: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'run_id': self.run_id,
            'golden_id': self.golden_id,
            'agent_version': self.agent_version,
            'timestamp': self.timestamp,
            'objective_scores': self.objective_scores,
            'llm_judge_scores': self.llm_judge_scores,
            'overall_score': self.overall_score,
            'passed': self.passed,
            'pass_threshold': self.pass_threshold,
            'weaknesses': self.weaknesses,
            'suggestions': self.suggestions,
            'duration_ms': self.duration_ms,
        }


class EvaluationPipeline:
    """Orchestrate full evaluation runs."""

    PASS_THRESHOLD = 0.7  # 70% to pass

    # Weights for combining objective and subjective scores
    OBJECTIVE_WEIGHT = 0.4
    SUBJECTIVE_WEIGHT = 0.6

    def __init__(
        self,
        db_client,
        agent_version: str = "v10.0",
        llm_model: str = "gpt-4o"
    ):
        """
        Initialize the evaluation pipeline.

        Args:
            db_client: Supabase client instance
            agent_version: Version string for tracking
            llm_model: Model to use for LLM-as-judge
        """
        self.db = db_client
        self.agent_version = agent_version
        self.golden_loader = GoldenDatasetLoader(db_client)
        self.objective_calc = ObjectiveMetricsCalculator()
        self.llm_judge = LLMJudge(model=llm_model)
        self.logger = logger.bind(component='eval_pipeline')

    async def run_full_evaluation(
        self,
        agent_name: str,
        agent_callable: Callable[[Dict], Awaitable[Dict]],
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        max_examples: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run full evaluation suite for an agent.

        Args:
            agent_name: Name of the agent being evaluated
            agent_callable: Async function that takes profile and returns output
            tags: Optional tags to filter golden examples
            difficulty: Optional difficulty tier to filter
            max_examples: Optional max number of examples to evaluate

        Returns:
            Dict with evaluation results and aggregate stats
        """
        run_id = str(uuid.uuid4())[:8]
        start_time = datetime.utcnow()

        self.logger.info(
            "evaluation_starting",
            run_id=run_id,
            agent_name=agent_name,
            tags=tags,
            difficulty=difficulty
        )

        # Load golden examples
        if tags:
            examples = await self.golden_loader.load_by_tags(tags)
        elif difficulty:
            examples = await self.golden_loader.load_by_difficulty(difficulty)
        else:
            examples = await self.golden_loader.load_all()

        if not examples:
            return {
                "error": "No golden examples found",
                "run_id": run_id,
                "filters": {"tags": tags, "difficulty": difficulty}
            }

        # Limit examples if specified
        if max_examples and len(examples) > max_examples:
            examples = examples[:max_examples]

        results: List[EvaluationResult] = []
        for example in examples:
            try:
                result = await self.evaluate_single(
                    run_id=run_id,
                    agent_name=agent_name,
                    agent_callable=agent_callable,
                    golden=example
                )
                results.append(result)

                # Store result in database
                await self._store_result(result)

            except Exception as e:
                self.logger.error(
                    "example_evaluation_error",
                    golden_id=example.id,
                    error=str(e)
                )

        # Calculate aggregate stats
        aggregate = self._aggregate_results(results)

        # Calculate total duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        self.logger.info(
            "evaluation_completed",
            run_id=run_id,
            examples_evaluated=len(results),
            pass_rate=aggregate.get('pass_rate', 0),
            avg_score=aggregate.get('avg_score', 0),
            duration_ms=duration_ms
        )

        return {
            "run_id": run_id,
            "agent_name": agent_name,
            "agent_version": self.agent_version,
            "timestamp": start_time.isoformat(),
            "duration_ms": duration_ms,
            "examples_evaluated": len(results),
            "passed": aggregate.get('passed_count', 0),
            "failed": aggregate.get('failed_count', 0),
            "pass_rate": aggregate.get('pass_rate', 0),
            "avg_score": aggregate.get('avg_score', 0),
            "common_weaknesses": aggregate.get('common_weaknesses', []),
            "score_distribution": aggregate.get('score_distribution', {}),
            "results": [r.to_dict() for r in results]
        }

    async def evaluate_single(
        self,
        run_id: str,
        agent_name: str,
        agent_callable: Callable[[Dict], Awaitable[Dict]],
        golden: GoldenExample
    ) -> EvaluationResult:
        """
        Evaluate a single golden example.

        Args:
            run_id: The evaluation run ID
            agent_name: Name of the agent
            agent_callable: Async function to call the agent
            golden: The golden example to evaluate against

        Returns:
            EvaluationResult
        """
        start_time = datetime.utcnow()

        # Get agent output
        try:
            agent_output = await agent_callable(golden.input_profile)
        except Exception as e:
            self.logger.error(
                "agent_call_error",
                golden_id=golden.id,
                error=str(e)
            )
            agent_output = {"error": str(e)}

        # Calculate objective metrics
        obj_scores = await self._calculate_objective_scores(
            agent_name, agent_output, golden
        )

        # Get LLM judge scores
        judge_result = await self._get_judge_scores(
            agent_name, agent_output, golden
        )

        # Calculate composite score
        obj_avg = (
            sum(s.score for s in obj_scores.values()) / len(obj_scores)
            if obj_scores else 0
        )
        subj_avg = judge_result.normalized_score  # Already 0-1

        overall = (
            (obj_avg * self.OBJECTIVE_WEIGHT) +
            (subj_avg * self.SUBJECTIVE_WEIGHT)
        )

        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return EvaluationResult(
            run_id=run_id,
            golden_id=golden.id,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow().isoformat(),
            objective_scores={k: v.score for k, v in obj_scores.items()},
            llm_judge_scores={s.dimension: s.score for s in judge_result.scores},
            overall_score=overall,
            passed=overall >= self.PASS_THRESHOLD,
            pass_threshold=self.PASS_THRESHOLD,
            weaknesses=[judge_result.top_weakness] if judge_result.top_weakness else [],
            suggestions=[judge_result.improvement_suggestion] if judge_result.improvement_suggestion else [],
            duration_ms=duration_ms,
            agent_output=agent_output,
            expected_output=golden.expected_outputs
        )

    async def _calculate_objective_scores(
        self,
        agent_name: str,
        agent_output: Dict[str, Any],
        golden: GoldenExample
    ) -> Dict[str, ObjectiveScore]:
        """Calculate objective metrics based on agent type."""
        golden_dict = {
            'expected_outputs': golden.expected_outputs,
            'input_profile': golden.input_profile
        }

        if agent_name == "narrative":
            return self.objective_calc.calculate_narrative_metrics(
                agent_output, golden_dict
            )
        elif agent_name == "awards":
            return self.objective_calc.calculate_awards_metrics(
                agent_output, golden_dict
            )
        elif agent_name == "crisis":
            return self.objective_calc.calculate_crisis_metrics(
                agent_output, golden_dict
            )
        else:
            # Default to narrative metrics
            return self.objective_calc.calculate_narrative_metrics(
                agent_output, golden_dict
            )

    async def _get_judge_scores(
        self,
        agent_name: str,
        agent_output: Dict[str, Any],
        golden: GoldenExample
    ) -> JudgeResult:
        """Get LLM-as-judge scores based on agent type."""
        try:
            if agent_name == "narrative":
                return await self.llm_judge.evaluate_narrative(
                    golden.input_profile,
                    agent_output,
                    golden.expected_outputs,
                    golden.jenny_annotations
                )
            elif agent_name == "awards":
                return await self.llm_judge.evaluate_awards(
                    golden.input_profile,
                    agent_output,
                    golden.expected_outputs
                )
            elif agent_name == "crisis":
                return await self.llm_judge.evaluate_crisis(
                    golden.input_profile,  # Used as crisis context
                    agent_output,
                    golden.expected_outputs
                )
            else:
                # Default to narrative
                return await self.llm_judge.evaluate_narrative(
                    golden.input_profile,
                    agent_output,
                    golden.expected_outputs,
                    golden.jenny_annotations
                )
        except Exception as e:
            self.logger.error("judge_error", error=str(e))
            return JudgeResult(
                scores=[],
                overall_score=3.0,
                top_weakness=f"Judge error: {str(e)}",
                improvement_suggestion="",
                raw_response=""
            )

    async def _store_result(self, result: EvaluationResult) -> None:
        """Store evaluation result in database."""
        try:
            self.db.table('evaluation_runs').insert({
                'run_id': result.run_id,
                'golden_id': result.golden_id,
                'agent_version': result.agent_version,
                'actual_outputs': result.agent_output,
                'objective_scores': result.objective_scores,
                'llm_judge_scores': result.llm_judge_scores,
                'overall_score': result.overall_score,
                'passed': result.passed,
                'duration_ms': result.duration_ms,
            }).execute()
        except Exception as e:
            self.logger.error(
                "store_result_error",
                run_id=result.run_id,
                golden_id=result.golden_id,
                error=str(e)
            )

    def _aggregate_results(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Aggregate results across multiple examples."""
        if not results:
            return {
                'passed_count': 0,
                'failed_count': 0,
                'pass_rate': 0.0,
                'avg_score': 0.0,
                'common_weaknesses': [],
                'score_distribution': {}
            }

        passed_count = sum(1 for r in results if r.passed)
        scores = [r.overall_score for r in results]

        # Collect all weaknesses
        all_weaknesses = []
        for r in results:
            all_weaknesses.extend(r.weaknesses)

        # Count weakness frequency
        weakness_counts = Counter(all_weaknesses)

        # Score distribution
        distribution = {
            'excellent': sum(1 for s in scores if s >= 0.9),
            'good': sum(1 for s in scores if 0.7 <= s < 0.9),
            'acceptable': sum(1 for s in scores if 0.5 <= s < 0.7),
            'poor': sum(1 for s in scores if s < 0.5),
        }

        return {
            'passed_count': passed_count,
            'failed_count': len(results) - passed_count,
            'pass_rate': passed_count / len(results),
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'common_weaknesses': [w for w, _ in weakness_counts.most_common(5)],
            'score_distribution': distribution
        }

    async def get_historical_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get evaluation score trends over time.

        Args:
            days: Number of days to look back

        Returns:
            Dict with trend data
        """
        from datetime import timedelta

        since = datetime.utcnow() - timedelta(days=days)

        try:
            result = self.db.table('evaluation_runs').select(
                'created_at, agent_version, overall_score, passed'
            ).gte('created_at', since.isoformat()).order('created_at').execute()

            # Group by date
            from collections import defaultdict
            daily: Dict[str, List[float]] = defaultdict(list)

            for row in (result.data or []):
                date = row['created_at'][:10]
                daily[date].append(row['overall_score'])

            trends = [
                {
                    "date": date,
                    "avg_score": sum(scores) / len(scores),
                    "count": len(scores),
                    "pass_rate": sum(1 for s in scores if s >= self.PASS_THRESHOLD) / len(scores)
                }
                for date, scores in sorted(daily.items())
            ]

            return {
                "days": days,
                "total_evaluations": sum(len(s) for s in daily.values()),
                "trends": trends
            }

        except Exception as e:
            self.logger.error("get_trends_error", error=str(e))
            return {"error": str(e)}

    async def compare_versions(
        self,
        version_a: str,
        version_b: str
    ) -> Dict[str, Any]:
        """
        Compare evaluation results between two agent versions.

        Args:
            version_a: First version to compare
            version_b: Second version to compare

        Returns:
            Dict with comparison data
        """
        try:
            result_a = self.db.table('evaluation_runs').select(
                'overall_score, passed'
            ).eq('agent_version', version_a).execute()

            result_b = self.db.table('evaluation_runs').select(
                'overall_score, passed'
            ).eq('agent_version', version_b).execute()

            def calc_stats(data):
                if not data:
                    return {'count': 0, 'avg_score': 0, 'pass_rate': 0}
                scores = [r['overall_score'] for r in data]
                passed = sum(1 for r in data if r['passed'])
                return {
                    'count': len(data),
                    'avg_score': sum(scores) / len(scores),
                    'pass_rate': passed / len(data)
                }

            stats_a = calc_stats(result_a.data)
            stats_b = calc_stats(result_b.data)

            return {
                "version_a": {
                    "version": version_a,
                    **stats_a
                },
                "version_b": {
                    "version": version_b,
                    **stats_b
                },
                "improvement": {
                    "avg_score_delta": stats_b['avg_score'] - stats_a['avg_score'],
                    "pass_rate_delta": stats_b['pass_rate'] - stats_a['pass_rate'],
                }
            }

        except Exception as e:
            self.logger.error("compare_versions_error", error=str(e))
            return {"error": str(e)}
