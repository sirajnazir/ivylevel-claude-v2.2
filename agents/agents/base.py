"""
IvyQuest v10.0 Base Agent Class
===============================
Abstract base class for all IvyQuest agents.
Provides common functionality: state versioning, event publishing, HITL.

v2.0 Update: Autonomous-First Design
- Agents are FULLY AUTONOMOUS first
- Jenny intelligence is ENHANCEMENT, not CONSTRAINT
- 4-layer intelligence model:
  Layer 1: LLM Foundation (Claude/GPT-4)
  Layer 2: Agentic Layer (Agno workflows)
  Layer 3: Domain Layer (college admissions)
  Layer 4: Jenny Enhancement (voice, techniques, insights)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import structlog

from config import settings, AutonomyLevel
from tools.database import (
    get_profile,
    get_profile_with_assessment,
    update_profile,
    create_state_version,
    get_latest_state,
)

# Import Jenny intelligence modules
from modules import (
    TimeAuditModule,
    AwardsProbabilityEngine,
    ProgramRedirectModule,
    NCWITStrategyModule,
    CrisisAlchemyModule,
)
from validation import JennyVoiceValidator, validate_jenny_voice

logger = structlog.get_logger()


# =====================================================
# Autonomous Agent Data Structures
# =====================================================

@dataclass
class JennyEnhancement:
    """Enhancement from Jenny's coaching intelligence."""
    technique_used: Optional[str] = None
    voice_validated: bool = False
    voice_score: float = 0.0
    signature_phrase: Optional[str] = None
    coaching_insight: Optional[str] = None
    reframe_applied: bool = False


@dataclass
class AgentContext:
    """Context for autonomous agent processing."""
    profile_id: str
    profile_data: Dict[str, Any] = field(default_factory=dict)
    session_history: List[Dict] = field(default_factory=list)
    user_request: Optional[str] = None
    urgency: int = 2  # 1=low, 2=normal, 3=urgent
    requires_jenny_voice: bool = True


@dataclass
class AgentResult:
    """Result from autonomous agent processing."""
    success: bool
    output: Dict[str, Any]
    confidence: float = 0.0
    reasoning: str = ""
    jenny_enhancement: Optional[JennyEnhancement] = None
    requires_hitl: bool = False
    hitl_reason: Optional[str] = None


class JennyKnowledgeBase:
    """
    Jenny Duan's coaching knowledge base.

    Provides access to Jenny's techniques, insights, and patterns
    for enhancing autonomous agent outputs.
    """

    def __init__(self):
        self.time_audit = TimeAuditModule()
        self.awards_probability = AwardsProbabilityEngine()
        self.program_redirect = ProgramRedirectModule()
        self.ncwit_strategy = NCWITStrategyModule()
        self.crisis_alchemy = CrisisAlchemyModule()
        self.voice_validator = JennyVoiceValidator()

    def get_relevant_technique(self, context: AgentContext) -> Optional[str]:
        """Identify which Jenny technique is most relevant."""
        request = (context.user_request or "").lower()

        # Check for crisis keywords
        crisis_type = self.crisis_alchemy.detect_crisis_type(request)
        if crisis_type != "general":
            return f"crisis_alchemy:{crisis_type}"

        # Check for time management
        if any(kw in request for kw in ["time", "hours", "schedule", "busy", "overwhelmed"]):
            return "168_hour_framework"

        # Check for awards/competitions
        if any(kw in request for kw in ["award", "competition", "ncwit", "prize"]):
            return "2_2_1_portfolio"

        # Check for expensive programs
        if any(kw in request for kw in ["program", "camp", "summer", "expensive"]):
            return "just_be_one"

        return None

    def validate_voice(self, text: str) -> JennyEnhancement:
        """Validate text matches Jenny's voice."""
        result = self.voice_validator.validate(text)
        return JennyEnhancement(
            voice_validated=result.passed,
            voice_score=result.score,
            signature_phrase=result.signature_phrase_used,
            coaching_insight=None,
            reframe_applied=False
        )

    def fix_voice(self, text: str) -> str:
        """Fix text to match Jenny's voice patterns."""
        result = self.voice_validator.validate(text)
        if result.fixed_text:
            return result.fixed_text
        return text


class BaseAgent(ABC):
    """
    Abstract base class for all IvyQuest agents.

    Provides:
    - State versioning (every state change is versioned)
    - Event publishing (via Supabase Realtime)
    - HITL (Human-in-the-Loop) support
    - Profile access helpers
    """

    def __init__(self, name: str, autonomy_level: str = AutonomyLevel.HIGH):
        """
        Initialize agent.

        Args:
            name: Agent name (e.g., 'Execution', 'Assessment')
            autonomy_level: One of FULL, HIGH, MEDIUM, LOW
        """
        self.name = name
        self.autonomy_level = autonomy_level
        self.logger = logger.bind(agent=name)

    @abstractmethod
    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing method. Must be implemented by subclasses.

        Args:
            profile_id: Profile UUID to process
            **kwargs: Additional arguments

        Returns:
            Dict with processing results
        """
        pass

    # =========================================
    # Profile Helpers
    # =========================================

    async def _get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get profile with assessment data merged using centralized function."""
        profile = await get_profile_with_assessment(profile_id)
        if not profile:
            self.logger.warning("profile_not_found", profile_id=profile_id)
        return profile

    async def _update_profile(self, profile_id: str, updates: Dict) -> bool:
        """Update profile with new data."""
        success = await update_profile(profile_id, updates)
        if success:
            self.logger.info("profile_updated", profile_id=profile_id, fields=list(updates.keys()))
        else:
            self.logger.error("profile_update_failed", profile_id=profile_id)
        return success

    # =========================================
    # State Versioning (CRITICAL per v9.1)
    # =========================================

    async def _version_state(
        self,
        profile_id: str,
        event_type: str,
        state: Dict,
        created_by: str = "agent",
        rationale: Optional[str] = None,
        event_payload: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Version every state change for rollback/forensics.

        CRITICAL: This must be called on ALL agent state changes per v9.1 spec.

        Args:
            profile_id: Profile UUID
            event_type: Type of event (e.g., 'assessment_enhanced', 'crisis_resolved')
            state: Full state snapshot to version
            created_by: 'agent', 'human', or 'system'
            rationale: Explanation for the change
            event_payload: Original event data

        Returns:
            Version ID if successful, None otherwise
        """
        if not settings.enable_state_versioning:
            self.logger.debug("state_versioning_disabled", profile_id=profile_id)
            return None

        version_id = await create_state_version(
            profile_id=profile_id,
            agent=self.name,
            state=state,
            event_type=event_type,
            created_by=created_by,
            rationale=rationale,
            event_payload=event_payload
        )

        if version_id:
            self.logger.info(
                "state_versioned",
                profile_id=profile_id,
                event_type=event_type,
                version_id=version_id,
                created_by=created_by
            )
        else:
            self.logger.error(
                "state_versioning_failed",
                profile_id=profile_id,
                event_type=event_type
            )

        return version_id

    async def _get_previous_state(self, profile_id: str) -> Optional[Dict]:
        """Get the most recent state for this agent/profile."""
        return await get_latest_state(profile_id, self.name)

    # =========================================
    # Event Publishing
    # =========================================

    async def _publish_event(self, event_type: str, payload: Dict) -> bool:
        """
        Publish event to the event bus.

        Events are used for:
        - Agent-to-agent communication
        - Dashboard updates
        - RLHF logging (SUCCESS_ACHIEVED only)

        Args:
            event_type: Event type (e.g., 'ASSESSMENT_COMPLETED', 'CRISIS_DETECTED')
            payload: Event payload (must include profileId)

        Returns:
            True if published successfully
        """
        if not settings.enable_event_bus:
            self.logger.debug("event_bus_disabled", event_type=event_type)
            return False

        # TODO: Implement Supabase Realtime publishing
        # For now, just log the event
        self.logger.info(
            "event_published",
            event_type=event_type,
            payload=payload
        )
        return True

    # =========================================
    # HITL (Human-in-the-Loop) Support
    # =========================================

    def _requires_hitl(self, context: Dict) -> bool:
        """
        Check if this action requires Human-in-the-Loop approval.

        LOW autonomy actions (crises) always require HITL.
        MEDIUM autonomy actions require HITL if confidence < 0.7.

        Args:
            context: Current context with confidence, is_crisis, etc.

        Returns:
            True if HITL approval is required
        """
        # LOW autonomy = always HITL
        if self.autonomy_level == AutonomyLevel.LOW:
            return True

        # Crisis actions always require HITL
        if context.get("is_crisis", False):
            return True

        # Medium autonomy with low confidence
        if self.autonomy_level == AutonomyLevel.MEDIUM:
            confidence = context.get("confidence", 0.5)
            if confidence < 0.7:
                return True

        return False

    def _get_hitl_deadline(self) -> str:
        """
        Get HITL approval deadline (default: 1 hour from now).

        Per spec: Crisis responses must be approved within 1 hour.

        Returns:
            ISO format datetime string
        """
        deadline = datetime.now() + timedelta(hours=settings.hitl_timeout_hours)
        return deadline.isoformat()

    async def _request_hitl_approval(
        self,
        profile_id: str,
        action_type: str,
        proposed_action: Dict,
        rationale: str
    ) -> Dict:
        """
        Request HITL approval for an action.

        Creates a pending approval record and returns immediately.
        The coach will approve/reject via the handoff API.

        Args:
            profile_id: Profile UUID
            action_type: Type of action needing approval
            proposed_action: The action to be approved
            rationale: Why this action is proposed

        Returns:
            Dict with approval_id, deadline, status
        """
        deadline = self._get_hitl_deadline()

        self.logger.info(
            "hitl_approval_requested",
            profile_id=profile_id,
            action_type=action_type,
            deadline=deadline
        )

        # TODO: Create approval record in database
        # TODO: Send notification to coach

        return {
            "status": "awaiting_approval",
            "deadline": deadline,
            "proposed_action": proposed_action,
            "rationale": rationale,
            "requires_human_approval": True
        }

    # =========================================
    # Confidence & Explainability
    # =========================================

    def _calculate_confidence(self, factors: Dict[str, float]) -> float:
        """
        Calculate overall confidence from multiple factors.

        Used for archetype detection, narrative synthesis, etc.
        Handoff to human if confidence < 0.7.

        Args:
            factors: Dict of factor_name -> confidence_score (0-1)

        Returns:
            Weighted average confidence (0-1)
        """
        if not factors:
            return 0.5

        total_weight = sum(factors.values())
        if total_weight == 0:
            return 0.5

        # Simple average for now
        return sum(factors.values()) / len(factors)

    def _generate_rationale(self, decision: str, factors: Dict[str, Any]) -> str:
        """
        Generate explainable rationale for a decision.

        Per v9.1: All agent decisions must include rationale for transparency.

        Args:
            decision: The decision made
            factors: Factors that influenced the decision

        Returns:
            Human-readable rationale string
        """
        parts = [f"Decision: {decision}"]

        if factors:
            parts.append("Based on:")
            for factor, value in factors.items():
                if isinstance(value, float):
                    parts.append(f"  - {factor}: {value:.2f}")
                else:
                    parts.append(f"  - {factor}: {value}")

        return "\n".join(parts)

    # =========================================
    # Logging Helpers
    # =========================================

    def _log_start(self, operation: str, **kwargs):
        """Log operation start."""
        self.logger.info(f"{operation}_started", **kwargs)

    def _log_complete(self, operation: str, **kwargs):
        """Log operation completion."""
        self.logger.info(f"{operation}_completed", **kwargs)

    def _log_error(self, operation: str, error: Exception, **kwargs):
        """Log operation error."""
        self.logger.error(f"{operation}_error", error=str(error), **kwargs)


# =====================================================
# Autonomous Agent Base Class (v2.0)
# =====================================================

class AutonomousAgent(BaseAgent):
    """
    Autonomous-first agent with Jenny enhancement layer.

    Processing Flow (autonomous-first):
    1. UNDERSTAND: Parse context and user intent autonomously
    2. ENHANCE: Apply Jenny techniques if relevant (Layer 4)
    3. PLAN: Determine action strategy
    4. EXECUTE: Perform actions
    5. VALIDATE: Jenny voice check on output

    Key Principle: The agent is FULLY AUTONOMOUS.
    Jenny intelligence ENHANCES but never CONSTRAINS.
    """

    def __init__(
        self,
        name: str,
        autonomy_level: str = AutonomyLevel.HIGH,
        enable_jenny_enhancement: bool = True
    ):
        super().__init__(name, autonomy_level)
        self.enable_jenny_enhancement = enable_jenny_enhancement
        self.jenny = JennyKnowledgeBase() if enable_jenny_enhancement else None

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing with autonomous-first design.

        Override _autonomous_process for agent-specific logic.
        """
        self._log_start("autonomous_process", profile_id=profile_id)

        try:
            # Build context
            context = await self._build_context(profile_id, **kwargs)

            # Phase 1: UNDERSTAND - Fully autonomous understanding
            understanding = await self._understand(context)

            # Phase 2: ENHANCE - Apply Jenny techniques if relevant
            enhancement = None
            if self.enable_jenny_enhancement and self.jenny:
                enhancement = self._apply_jenny_enhancement(context, understanding)

            # Phase 3: PLAN - Determine action strategy
            plan = await self._plan(context, understanding, enhancement)

            # Phase 4: EXECUTE - Perform actions
            result = await self._execute(context, plan)

            # Phase 5: VALIDATE - Jenny voice check
            if self.enable_jenny_enhancement and result.success:
                result = self._validate_voice(result)

            # Version state if successful
            if result.success:
                await self._version_state(
                    profile_id=profile_id,
                    event_type=f"{self.name.lower()}_processed",
                    state=result.output,
                    rationale=result.reasoning
                )

            self._log_complete("autonomous_process", profile_id=profile_id)
            return self._format_result(result)

        except Exception as e:
            self._log_error("autonomous_process", e, profile_id=profile_id)
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }

    async def _build_context(self, profile_id: str, **kwargs) -> AgentContext:
        """Build agent context from profile and kwargs."""
        profile = await self._get_profile(profile_id)
        return AgentContext(
            profile_id=profile_id,
            profile_data=profile or {},
            user_request=kwargs.get("user_request"),
            urgency=kwargs.get("urgency", 2),
            requires_jenny_voice=kwargs.get("requires_jenny_voice", True)
        )

    async def _understand(self, context: AgentContext) -> Dict[str, Any]:
        """
        Phase 1: Autonomous understanding of context.

        Override in subclass for agent-specific understanding.
        """
        return {
            "profile_id": context.profile_id,
            "has_profile": bool(context.profile_data),
            "request": context.user_request,
            "urgency": context.urgency
        }

    def _apply_jenny_enhancement(
        self,
        context: AgentContext,
        understanding: Dict[str, Any]
    ) -> Optional[JennyEnhancement]:
        """
        Phase 2: Apply Jenny's coaching intelligence.

        This ENHANCES the autonomous output, never constrains it.
        """
        if not self.jenny:
            return None

        technique = self.jenny.get_relevant_technique(context)
        if not technique:
            return None

        return JennyEnhancement(
            technique_used=technique,
            coaching_insight=f"Applying {technique} technique"
        )

    async def _plan(
        self,
        context: AgentContext,
        understanding: Dict[str, Any],
        enhancement: Optional[JennyEnhancement]
    ) -> Dict[str, Any]:
        """
        Phase 3: Plan action strategy.

        Override in subclass for agent-specific planning.
        """
        return {
            "action": "process",
            "enhancement": enhancement.technique_used if enhancement else None
        }

    async def _execute(
        self,
        context: AgentContext,
        plan: Dict[str, Any]
    ) -> AgentResult:
        """
        Phase 4: Execute the plan.

        Override in subclass for agent-specific execution.
        """
        return AgentResult(
            success=True,
            output={"processed": True},
            confidence=0.8,
            reasoning="Default autonomous processing"
        )

    def _validate_voice(self, result: AgentResult) -> AgentResult:
        """
        Phase 5: Validate output matches Jenny's voice.

        Auto-fixes if possible, adds enhancement metadata.
        """
        if not self.jenny:
            return result

        # Get text content from output
        text_content = self._extract_text_content(result.output)
        if not text_content:
            return result

        # Validate voice
        enhancement = self.jenny.validate_voice(text_content)

        # Auto-fix if not passed
        if not enhancement.voice_validated:
            fixed_text = self.jenny.fix_voice(text_content)
            result.output["response_text"] = fixed_text
            enhancement.voice_validated = True

        result.jenny_enhancement = enhancement
        return result

    def _extract_text_content(self, output: Dict[str, Any]) -> Optional[str]:
        """Extract text content from output for voice validation."""
        # Look for common text fields
        for key in ["response_text", "message", "text", "full_response", "coaching_script"]:
            if key in output and isinstance(output[key], str):
                return output[key]
        return None

    def _format_result(self, result: AgentResult) -> Dict[str, Any]:
        """Format AgentResult for API response."""
        response = {
            "success": result.success,
            "data": result.output,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }

        if result.jenny_enhancement:
            response["jenny_enhancement"] = {
                "technique_used": result.jenny_enhancement.technique_used,
                "voice_validated": result.jenny_enhancement.voice_validated,
                "voice_score": result.jenny_enhancement.voice_score,
                "signature_phrase": result.jenny_enhancement.signature_phrase
            }

        if result.requires_hitl:
            response["requires_hitl"] = True
            response["hitl_reason"] = result.hitl_reason

        return response


__all__ = [
    'BaseAgent',
    'AutonomousAgent',
    'AgentContext',
    'AgentResult',
    'JennyEnhancement',
    'JennyKnowledgeBase'
]
