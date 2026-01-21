"""
Execution Agent v5.3 - Chat-Enabled Coaching Buddy
===================================================

The student's 2+ year coaching buddy for execution management.
Builds on the existing ExecutionAgent with chat/streaming capabilities.

Responsibilities:
1. Weekly planning (P0/P1/P2 prioritization)
2. Stall detection and nudging
3. EDS (Execution Debt Score) calculation
4. Crisis escalation (via existing crises table)
5. Conversational support with memory

Uses existing tables:
- projects, project_steps (execution tracking)
- crises (Crisis Alchemy)
- weekly_plans (P0/P1/P2)
- agent_memories (long-term memory)
- conversations (chat history - v5.3)
- notifications (nudge delivery)
"""

from typing import AsyncGenerator, Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import structlog

from config import settings

# v8: Middleware Integration (40 patterns)
from .mixins import MiddlewareIntegrationMixin

import logging
mw_logger = logging.getLogger(__name__)

logger = structlog.get_logger()


class ExecutionChatAgent(MiddlewareIntegrationMixin):
    """
    Execution Agent with ReAct reasoning and proactive capabilities.
    Provides chat interface with streaming responses.

    v8: Integrated with MiddlewareStackV8 (40 patterns) for:
    - J1: Reasoning Traces (conversation tracking)
    - J3: Audit Trail (chat compliance)
    - E4: Quality Scoring
    - H3: Retry Logic
    """

    AGENT_NAME = "Execution"
    AGENT_TYPE = "execution"

    # Thresholds (from legacy patterns)
    STALL_THRESHOLD_NUDGE = 5      # Days before nudge
    STALL_THRESHOLD_ESCALATE = 14  # Days before crisis escalation
    EDS_WARNING = 25               # EDS warning threshold
    EDS_CRITICAL = 50              # EDS critical threshold

    def __init__(self):
        self.logger = logger.bind(agent=self.AGENT_NAME)
        self._supabase = None
        self._llm = None

        # v8: Initialize middleware integration (40 patterns)
        # Note: clients are lazy-loaded, so we init without them
        try:
            self.init_middleware(
                supabase_client=None,  # Will be set on first access
                llm_client=None,
            )
        except Exception as e:
            mw_logger.warning(f"Middleware init failed (non-fatal): {e}")

    @property
    def supabase(self):
        """Lazy-load supabase client."""
        if self._supabase is None:
            from tools.database import get_supabase_client
            self._supabase = get_supabase_client()
        return self._supabase

    @property
    def llm(self):
        """Lazy-load LLM client."""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=settings.agent_primary_model,
                temperature=0.7,
                api_key=settings.openai_api_key,
                streaming=True,
            )
        return self._llm

    # =========================================================================
    # MAIN CHAT INTERFACE
    # =========================================================================

    async def chat(
        self,
        profile_id: str,
        message: str,
        context_type: Optional[str] = None,
        context_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Main chat interface - streams responses.

        Args:
            profile_id: Student's profile ID
            message: User's message
            context_type: Optional context ('project', 'crisis', 'weekly_plan')
            context_id: Optional ID of the context entity
            thread_id: Optional conversation thread ID

        Yields:
            Chunks of response with metadata
        """
        self.logger.info(
            "chat_started",
            profile_id=profile_id,
            context_type=context_type,
        )

        try:
            # 1. Build context
            context = await self._build_context(profile_id, context_type, context_id)

            # 2. Build system prompt
            system_prompt = self._build_system_prompt(context)

            # 3. Get recent conversation history
            conversation_history = await self._get_recent_conversations(profile_id, limit=10)

            # 4. Build messages for LLM
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            messages = [SystemMessage(content=system_prompt)]

            # Add conversation history
            for conv in conversation_history:
                if conv.get('role') == 'user':
                    messages.append(HumanMessage(content=conv.get('content', '')))
                elif conv.get('role') == 'assistant':
                    messages.append(AIMessage(content=conv.get('content', '')))

            # Add current message
            messages.append(HumanMessage(content=message))

            # 5. Stream response from LLM
            full_response = ""

            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    full_response += chunk.content
                    yield {"type": "content", "content": chunk.content}

            # 6. Extract and store insights (non-blocking)
            try:
                await self._extract_and_store_insights(profile_id, message, full_response, context)
            except Exception as e:
                self.logger.warning("insight_extraction_failed", error=str(e))

            # 7. Yield completion
            yield {
                "type": "done",
                "full_response": full_response,
            }

            self.logger.info(
                "chat_completed",
                profile_id=profile_id,
                response_length=len(full_response),
            )

        except Exception as e:
            self.logger.error("chat_error", error=str(e), profile_id=profile_id)
            yield {"type": "error", "error": str(e)}

    async def chat_sync(
        self,
        profile_id: str,
        message: str,
        context_type: Optional[str] = None,
        context_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Non-streaming chat for simple requests.

        v8: Wrapped with MiddlewareStackV8 (40 patterns):
        - J1: Reasoning traces for observability
        - J3: Audit trail for chat compliance
        - E4: Quality scoring
        """
        # v8: Generate session context
        session_id = session_id or f"execution_chat_{profile_id}"
        trace_id = self.start_reasoning_trace(profile_id, session_id, "execution_chat")

        try:
            async with self.with_middleware_context(profile_id, session_id, "execution_chat") as ctx:
                self.add_thought(trace_id, f"Chat request from profile {profile_id}: {message[:100]}...")

                self.add_action(trace_id, "chat", {
                    "context_type": context_type,
                    "has_context_id": bool(context_id),
                    "message_length": len(message),
                })

                full_response = ""

                async for chunk in self.chat(profile_id, message, context_type, context_id):
                    if chunk.get("type") == "content":
                        full_response += chunk.get("content", "")
                    elif chunk.get("type") == "error":
                        await self.end_reasoning_trace(trace_id, success=False, error=chunk.get("error"))
                        return {"success": False, "error": chunk.get("error")}

                result = {"success": True, "response": full_response}

                # v8: Score quality (E4)
                if full_response:
                    quality = await self.score_quality(full_response[:1000], "chat_response")
                    if quality:
                        result["_quality_score"] = quality.overall_score

                # v8: Finalize with middleware
                result = self.middleware_finalize(result, output_type="execution_chat")

                # v8: Audit trail (J3 - chat compliance)
                await self.audit_action(
                    action="execution_chat",
                    resource_type="chat",
                    resource_id=profile_id,
                    details={
                        "context_type": context_type,
                        "response_length": len(full_response),
                    },
                    success=True,
                )

                await self.end_reasoning_trace(trace_id, success=True)
                return result

        except Exception as e:
            await self.end_reasoning_trace(trace_id, success=False, error=str(e))
            raise

    async def _build_context(
        self,
        profile_id: str,
        context_type: Optional[str],
        context_id: Optional[str],
    ) -> Dict[str, Any]:
        """Build comprehensive context for the agent."""
        context = {
            "profile": await self._get_profile(profile_id),
            "weekly_plan": await self._get_current_weekly_plan(profile_id),
            "active_projects": await self._get_active_projects_summary(profile_id),
            "eds": await self.tool_calculate_eds(profile_id),
            "stalled_projects": await self.tool_detect_stalls(profile_id, threshold_days=5),
            "pending_nudges": await self.tool_get_pending_nudges(profile_id),
            "game_plan": await self._get_game_plan(profile_id),  # v5.4: Include full game plan
        }

        # Add specific context if provided
        if context_type == "project" and context_id:
            context["focused_project"] = await self.tool_get_project_details(context_id)
        elif context_type == "crisis" and context_id:
            context["focused_crisis"] = await self._get_crisis(context_id)
        elif context_type == "weekly_plan" and context_id:
            context["focused_weekly_plan"] = await self._get_weekly_plan(context_id)

        return context

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build the system prompt with Jenny's coaching patterns."""
        profile = context.get("profile", {})
        weekly_plan = context.get("weekly_plan", {})
        eds = context.get("eds", {})
        stalled = context.get("stalled_projects", [])
        pending_nudges = context.get("pending_nudges", [])
        game_plan = context.get("game_plan", {})  # v5.4: Game plan data

        # Get profile data from nested structure if needed
        profile_data = profile.get("profile_data", {}) or {}
        first_name = profile_data.get("first_name") or profile.get("first_name", "Student")
        last_name = profile_data.get("last_name") or profile.get("last_name", "")
        grade = profile_data.get("grade") or profile.get("grade", "Unknown")
        archetype = profile.get("archetype", "Unknown")

        # Format P0 tasks
        p0_tasks = weekly_plan.get("p0_tasks", []) if weekly_plan else []
        p0_display = json.dumps(p0_tasks[:3], indent=2) if p0_tasks else "No weekly plan yet"

        # Format stalled projects
        stalled_display = json.dumps(
            [{"title": p.get("title", "Untitled"), "days": p.get("days_since_activity", 0)}
             for p in stalled[:3]], indent=2
        ) if stalled else "None - great job!"

        # Format pending nudges for proactive topics
        nudge_display = ""
        if pending_nudges:
            nudge_items = []
            for n in pending_nudges[:3]:
                nudge_items.append(f"- [{n.get('nudge_type')}] {n.get('message_draft', '')[:100]}...")
            nudge_display = "\n".join(nudge_items)
        else:
            nudge_display = "None pending"

        # v5.4: Format game plan components (summer programs, awards, ECs)
        summer_programs = game_plan.get("summer_programs", [])
        awards = game_plan.get("awards", [])
        ecs = game_plan.get("ecs", [])
        spike = game_plan.get("spike", "")
        narrative_theme = game_plan.get("narrative_theme", "")

        # Format summer programs for display
        summer_display = ""
        if summer_programs:
            program_items = []
            for p in summer_programs[:5]:
                name = p.get("name") or p.get("program_name", "Unknown Program")
                deadline = p.get("deadline", "TBD")
                fit = p.get("fit_score") or p.get("match_score", "")
                fit_str = f" (Fit: {fit}%)" if fit else ""
                program_items.append(f"- {name} - Deadline: {deadline}{fit_str}")
            summer_display = "\n".join(program_items)
        else:
            summer_display = "None in game plan"

        # Format awards for display
        awards_display = ""
        if awards:
            award_items = []
            for a in awards[:5]:
                name = a.get("name") or a.get("award_name", "Unknown Award")
                deadline = a.get("deadline", "TBD")
                award_items.append(f"- {name} - Deadline: {deadline}")
            awards_display = "\n".join(award_items)
        else:
            awards_display = "None in game plan"

        # Format ECs for display
        ecs_display = ""
        if ecs:
            ec_items = []
            for e in ecs[:5]:
                name = e.get("name") or e.get("activity_name", "Unknown EC")
                role = e.get("role") or e.get("position", "")
                role_str = f" ({role})" if role else ""
                ec_items.append(f"- {name}{role_str}")
            ecs_display = "\n".join(ec_items)
        else:
            ecs_display = "None in game plan"

        return f"""You are the Execution Coach (EC) - {first_name}'s personal coaching buddy for the next 2+ years. You help students GET THINGS DONE, not just advise.

## YOUR IDENTITY
- You're always available, 24/7, whenever they need help
- You're proactive - you reach out first when you notice issues
- You learn their execution style and adapt
- You coordinate with specialist agents (Game Plan, Essay, Research)

## COACHING PATTERNS (from elite college prep coaching)

### Crisis → Opportunity
When student hits a setback (rejection, failure, missed deadline):
1. VALIDATE first (2 seconds): "I hear you. That's frustrating."
2. ACT immediately (10 seconds): Give ONE concrete micro-action
3. REFRAME (30 seconds): Find the opportunity angle
4. CREATE (2 minutes): Design a pivot or new approach

### Talk First, Write Second
For essays and applications, help them talk through ideas before writing:
- "Tell me about that experience..."
- "What made that moment meaningful?"
- Extract themes from conversation, then help structure

### Blocker Removal Doctrine
Your PRIMARY job is removing what's in their way:
- "What's blocking you right now?"
- "What would make this easier?"
- Offer specific help: "I can help you outline that" / "Let's break this into 3 steps"

### Bookmark Technique
When overwhelmed, help them:
1. Pick the ONE thing that matters most right now
2. Set aside everything else (bookmark for later)
3. Focus energy on that one thing
4. Return to bookmarks after completion

## SESSION ANATOMY
Follow this flow for substantive conversations:
1. **Check-in** (30s): "How are you doing? What's on your mind?"
2. **Progress Scan** (1-2 min): What got done since last time?
3. **Blocker Detection**: "What's in your way?"
4. **Deep Work**: Help with the actual task
5. **Tactical Planning**: What happens next? By when?
6. **Confidence Close**: End on an encouraging note

## CURRENT CONTEXT
Student: {first_name} {last_name}
Grade: {grade}
Archetype: {archetype}
Spike/Focus: {spike or 'Not defined'}
Narrative Theme: {narrative_theme or 'Not defined'}

## GAME PLAN - SUMMER PROGRAMS (These are the ACTUAL programs to apply to)
{summer_display}

## GAME PLAN - AWARDS TO PURSUE
{awards_display}

## GAME PLAN - EXTRACURRICULARS
{ecs_display}

## WEEKLY FOCUS (P0 Items)
{p0_display}

## EXECUTION STATUS
EDS Score: {eds.get('eds_score', 0)} ({eds.get('status', 'unknown')})
Active Projects: {eds.get('active_projects', 0)}
Overdue Projects: {eds.get('overdue_projects', 0)}

## STALLED PROJECTS ({len(stalled)} items needing attention)
{stalled_display}

## PROACTIVE TOPICS TO RAISE
{nudge_display}

## BEHAVIOR RULES
1. ALWAYS use the ACTUAL program/award/EC names from the Game Plan sections above - NEVER say "Program A" or generic placeholders
2. If there are pending nudges → Weave them into conversation naturally
3. If student seems stressed → Use Blocker Removal Doctrine
4. If discussing rejection/failure → Use Crisis → Opportunity
5. If they're overwhelmed → Use Bookmark Technique
6. If they're working on essays → Use Talk First, Write Second
7. If severely blocked (14+ days) → Escalate to crisis mode
8. When discussing summer programs, reference the specific deadlines and fit scores from the game plan

## TONE
- Warm but not sycophantic ("Good" not "Amazing!")
- Direct and specific (no vague advice)
- Brief for simple questions, thorough when needed
- Use their name occasionally
- Celebrate real wins proportional to difficulty

## WHAT NOT TO DO
- Don't just advise - help them DO
- Don't overwhelm with options - give them THE answer
- Don't ignore blockers - always ask what's in the way
- Don't be passive - if you notice an issue, raise it

Remember: Your job is to help {first_name} execute, not just plan. Every conversation should end with a clear next action."""

    # =========================================================================
    # TOOL IMPLEMENTATIONS (13 tools)
    # =========================================================================

    # --- Weekly Planning Tools ---

    async def tool_get_weekly_focus(self, profile_id: str) -> Dict[str, Any]:
        """Get top 3 P0 items from weekly_plans table."""
        try:
            result = self.supabase.table("weekly_plans") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .order("week_start", desc=True) \
                .limit(1) \
                .execute()

            if not result.data:
                return {"focus_items": [], "message": "No weekly plan found"}

            plan = result.data[0]
            p0_tasks = plan.get("p0_tasks", [])

            return {
                "week_start": plan.get("week_start"),
                "week_end": plan.get("week_end"),
                "focus_items": p0_tasks[:3] if p0_tasks else [],
                "total_p0": len(p0_tasks) if p0_tasks else 0,
                "total_p1": len(plan.get("p1_tasks", []) or []),
                "total_p2": len(plan.get("p2_tasks", []) or []),
            }
        except Exception as e:
            self.logger.error("get_weekly_focus_error", error=str(e))
            return {"focus_items": [], "error": str(e)}

    async def tool_generate_weekly_plan(
        self,
        profile_id: str,
        week_start: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a new weekly plan with P0/P1/P2 priorities."""
        try:
            # Get active projects
            projects = await self.tool_get_active_projects(profile_id)

            # Calculate week dates
            if not week_start:
                today = datetime.now()
                week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")

            week_end = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")

            # Use LLM to prioritize
            prioritization_prompt = f"""Given these projects, create a weekly plan with P0 (must do), P1 (should do), P2 (nice to do).

Projects:
{json.dumps(projects[:10], indent=2, default=str)}

Rules:
1. P0: Maximum 3 items - highest impact, most urgent
2. P1: 3-5 items - important but not critical this week
3. P2: Remaining items - can be deferred

Return ONLY valid JSON (no markdown):
{{
  "p0_tasks": [{{"project_id": "...", "title": "...", "reason": "..."}}],
  "p1_tasks": [...],
  "p2_tasks": [...]
}}"""

            from langchain_core.messages import HumanMessage, SystemMessage
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a strategic planner. Return only valid JSON."),
                HumanMessage(content=prioritization_prompt)
            ])

            plan_data = self._parse_json_response(response.content, {
                "p0_tasks": [],
                "p1_tasks": [],
                "p2_tasks": []
            })

            # Store in weekly_plans table
            self.supabase.table("weekly_plans").upsert({
                "profile_id": profile_id,
                "week_start": week_start,
                "week_end": week_end,
                "p0_tasks": plan_data.get("p0_tasks", []),
                "p1_tasks": plan_data.get("p1_tasks", []),
                "p2_tasks": plan_data.get("p2_tasks", []),
                "generated_at": datetime.now().isoformat(),
                "generated_by": "execution_agent",
            }, on_conflict="profile_id,week_start").execute()

            return {
                "success": True,
                "week_start": week_start,
                "week_end": week_end,
                "plan": plan_data,
            }
        except Exception as e:
            self.logger.error("generate_weekly_plan_error", error=str(e))
            return {"success": False, "error": str(e)}

    # --- Execution Tracking Tools ---

    async def tool_get_active_projects(self, profile_id: str) -> List[Dict[str, Any]]:
        """Get all active projects for a student."""
        try:
            result = self.supabase.table("projects") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .execute()

            # Filter active projects in Python (more defensive)
            all_projects = result.data or []
            active = [
                p for p in all_projects
                if p.get("status") not in ["completed", "abandoned", "cancelled"]
            ]
            return active
        except Exception as e:
            self.logger.error("get_active_projects_error", error=str(e))
            return []

    async def tool_get_project_details(self, project_id: str) -> Dict[str, Any]:
        """Get detailed info about a specific project."""
        try:
            result = self.supabase.table("projects") \
                .select("*") \
                .eq("id", project_id) \
                .maybe_single() \
                .execute()

            if not result.data:
                return {"error": "Project not found"}

            project = result.data

            # Calculate days since activity
            days_inactive = self._calculate_days_since(project.get("last_activity_at"))

            return {
                **project,
                "days_since_activity": days_inactive,
            }
        except Exception as e:
            self.logger.error("get_project_details_error", error=str(e))
            return {"error": str(e)}

    async def tool_update_project_status(
        self,
        project_id: str,
        status: Optional[str] = None,
        step_id: Optional[str] = None,
        step_complete: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update project or step status."""
        try:
            if step_id and step_complete is not None:
                # Update step status
                step_status = "completed" if step_complete else "pending"
                self.supabase.table("project_steps") \
                    .update({
                        "status": step_status,
                        "completed_at": datetime.now().isoformat() if step_complete else None,
                    }) \
                    .eq("id", step_id) \
                    .execute()

                # Note: project stats auto-update via database trigger

                return {"success": True, "updated": "step", "step_id": step_id}

            if status:
                # Update project status
                update_data = {
                    "status": status,
                }
                if status == "completed":
                    update_data["actual_end_date"] = datetime.now().strftime("%Y-%m-%d")

                self.supabase.table("projects") \
                    .update(update_data) \
                    .eq("id", project_id) \
                    .execute()

                return {"success": True, "updated": "project", "project_id": project_id, "status": status}

            return {"error": "No updates specified"}
        except Exception as e:
            self.logger.error("update_project_status_error", error=str(e))
            return {"success": False, "error": str(e)}

    # --- Stall Detection Tools ---

    async def tool_detect_stalls(
        self,
        profile_id: str,
        threshold_days: int = 5,
    ) -> List[Dict[str, Any]]:
        """Detect stalled projects."""
        try:
            # Get projects - use select * for flexibility with schema
            result = self.supabase.table("projects") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .execute()

            stalled = []
            now = datetime.now()

            for project in result.data or []:
                # Skip completed/abandoned projects
                status = project.get("status", "")
                if status in ["completed", "abandoned", "cancelled"]:
                    continue

                # Try multiple possible column names for last activity
                last_activity = (
                    project.get("last_activity_at") or
                    project.get("updated_at") or
                    project.get("created_at")
                )
                if not last_activity:
                    continue

                # Parse datetime
                try:
                    if isinstance(last_activity, str):
                        last_activity_dt = datetime.fromisoformat(
                            last_activity.replace("Z", "+00:00").replace("+00:00", "")
                        )
                    else:
                        last_activity_dt = last_activity
                except:
                    continue

                days_since_activity = (now - last_activity_dt).days

                if days_since_activity >= threshold_days:
                    severity = "mild"
                    if days_since_activity >= self.STALL_THRESHOLD_ESCALATE:
                        severity = "severe"
                    elif days_since_activity >= 10:
                        severity = "moderate"

                    stalled.append({
                        "id": project.get("id"),
                        "title": project.get("name") or project.get("title", "Untitled"),
                        "status": status,
                        "days_since_activity": days_since_activity,
                        "type": project.get("type"),
                        "target_end_date": project.get("target_end_date") or project.get("deadline"),
                        "severity": severity,
                        "suggested_action": self._get_stall_suggestion(days_since_activity),
                    })

            return sorted(stalled, key=lambda x: x.get("days_since_activity", 0), reverse=True)
        except Exception as e:
            self.logger.error("detect_stalls_error", error=str(e))
            return []

    def _get_stall_suggestion(self, days: int) -> str:
        """Get suggested action for a stalled project."""
        if days >= 14:
            return "escalate_crisis"  # Needs Crisis Alchemy
        elif days >= 10:
            return "scope_cut"  # Reduce scope
        elif days >= 7:
            return "ally_recruit"  # Get help
        else:
            return "nudge"  # Gentle reminder

    async def tool_calculate_eds(self, profile_id: str) -> Dict[str, Any]:
        """Calculate Execution Debt Score."""
        try:
            eds = 0
            overdue_count = 0
            stalled_count = 0
            active_count = 0

            # Get active projects - try minimal query first
            try:
                projects_result = self.supabase.table("projects") \
                    .select("*") \
                    .eq("profile_id", profile_id) \
                    .execute()

                all_projects = projects_result.data or []

                # Filter to active projects
                active_projects = [
                    p for p in all_projects
                    if p.get("status") not in ["completed", "abandoned", "cancelled"]
                ]
                active_count = len(active_projects)
                now = datetime.now()

                for project in active_projects:
                    # Check if overdue (try multiple possible column names)
                    target_date = (
                        project.get("target_end_date") or
                        project.get("deadline") or
                        project.get("due_date")
                    )
                    if target_date:
                        try:
                            target_dt = datetime.strptime(str(target_date)[:10], "%Y-%m-%d")
                            if target_dt < now:
                                overdue_count += 1
                                eds += 5
                        except:
                            pass

                    # Check if stalled (try multiple possible column names)
                    last_activity = (
                        project.get("last_activity_at") or
                        project.get("updated_at") or
                        project.get("created_at")
                    )
                    if last_activity:
                        try:
                            last_activity_dt = datetime.fromisoformat(
                                str(last_activity).replace("Z", "+00:00").replace("+00:00", "")
                            )
                            days_inactive = (now - last_activity_dt).days
                            if days_inactive >= self.STALL_THRESHOLD_NUDGE:
                                stalled_count += 1
                                eds += 3
                        except:
                            pass

            except Exception as inner_e:
                self.logger.warning("eds_projects_query_error", error=str(inner_e))

            return {
                "eds_score": eds,
                "status": "healthy" if eds < self.EDS_WARNING else "warning" if eds < self.EDS_CRITICAL else "critical",
                "active_projects": active_count,
                "overdue_projects": overdue_count,
                "stalled_projects": stalled_count,
            }
        except Exception as e:
            self.logger.error("calculate_eds_error", error=str(e))
            return {
                "eds_score": 0,
                "status": "healthy",  # Default to healthy if we can't calculate
                "active_projects": 0,
                "overdue_projects": 0,
                "stalled_projects": 0,
            }

    # --- Nudging & Escalation Tools ---

    async def tool_create_nudge(
        self,
        profile_id: str,
        message: str,
        nudge_type: str = "general",
        project_id: Optional[str] = None,
        priority: str = "medium",
    ) -> Dict[str, Any]:
        """Create a proactive nudge notification."""
        try:
            # Store in notifications table
            result = self.supabase.table("notifications").insert({
                "profile_id": profile_id,
                "type": "execution_nudge",
                "title": "Execution Agent",
                "message": message,
                "metadata": {
                    "nudge_type": nudge_type,
                    "project_id": project_id,
                    "priority": priority,
                },
                "read": False,
                "created_at": datetime.now().isoformat(),
            }).execute()

            # Also store in conversations as proactive message
            self.supabase.table("conversations").insert({
                "profile_id": profile_id,
                "agent_type": self.AGENT_TYPE,
                "role": "assistant",
                "content": message,
                "context_type": "project" if project_id else None,
                "context_id": project_id,
                "is_proactive": True,
                "nudge_trigger": nudge_type,
                "created_at": datetime.now().isoformat(),
            }).execute()

            return {
                "success": True,
                "notification_id": result.data[0]["id"] if result.data else None,
                "message": message,
            }
        except Exception as e:
            self.logger.error("create_nudge_error", error=str(e))
            return {"success": False, "error": str(e)}

    async def tool_escalate_to_crisis(
        self,
        project_id: str,
        reason: str,
        severity: str = "medium",
    ) -> Dict[str, Any]:
        """Escalate a blocked project to Crisis Alchemy."""
        try:
            # Get project details
            project = await self.tool_get_project_details(project_id)
            if project.get("error"):
                return {"success": False, "error": project.get("error")}

            profile_id = project.get("profile_id")
            project_name = project.get("name", "Unknown Project")

            # Create crisis record
            result = self.supabase.table("crises").insert({
                "profile_id": profile_id,
                "project_id": project_id,
                "type": "execution_blocker",
                "title": f"Blocked: {project_name}",
                "description": reason,
                "urgency": severity,
                "status": "detected",
                "detected_by": "execution_agent",
                "created_at": datetime.now().isoformat(),
            }).execute()

            # Update project status to blocked
            self.supabase.table("projects") \
                .update({"status": "blocked"}) \
                .eq("id", project_id) \
                .execute()

            return {
                "success": True,
                "crisis_id": result.data[0]["id"] if result.data else None,
                "message": f"Created Crisis Alchemy ticket for '{project_name}'",
            }
        except Exception as e:
            self.logger.error("escalate_to_crisis_error", error=str(e))
            return {"success": False, "error": str(e)}

    # --- Memory Tools ---

    async def tool_search_memory(
        self,
        profile_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search long-term memory for relevant context."""
        try:
            # Search agent_memories table
            result = self.supabase.table("agent_memories") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .ilike("content", f"%{query}%") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()

            return result.data or []
        except Exception as e:
            self.logger.error("search_memory_error", error=str(e))
            return []

    async def tool_store_insight(
        self,
        profile_id: str,
        insight: str,
        insight_type: str = "observation",
        confidence: float = 0.8,
    ) -> Dict[str, Any]:
        """Store an insight in long-term memory."""
        try:
            result = self.supabase.table("agent_memories").insert({
                "profile_id": profile_id,
                "agent_id": self.AGENT_TYPE,
                "observation_type": insight_type,
                "content": insight,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
            }).execute()

            return {"success": True, "memory_id": result.data[0]["id"] if result.data else None}
        except Exception as e:
            self.logger.error("store_insight_error", error=str(e))
            return {"success": False, "error": str(e)}

    async def tool_get_conversation_history(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        return await self._get_recent_conversations(profile_id, limit)

    # --- Project Update Tools (v9.1) ---

    async def tool_update_project(
        self,
        project_id: str,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        progress_update: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update project status after conversation.
        Called when student provides update or completes something.

        Args:
            project_id: UUID of the project
            status: New status ('active', 'completed', 'stalled', 'dropped')
            notes: Optional notes to add
            progress_update: Description of progress made (stored in notes)

        Returns:
            Result dict with success status and updated project data
        """
        try:
            update_data = {
                "last_update": datetime.now().isoformat(),
                "last_activity_at": datetime.now().isoformat(),
            }

            if status:
                update_data["status"] = status
                if status == "completed":
                    update_data["completed_at"] = datetime.now().isoformat()

            if notes or progress_update:
                # Append to existing notes
                existing = self.supabase.table("projects").select("notes").eq(
                    "id", project_id
                ).execute()

                existing_notes = ""
                if existing.data and existing.data[0].get("notes"):
                    existing_notes = existing.data[0]["notes"]

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                new_note = progress_update or notes
                combined_notes = f"{existing_notes}\n[{timestamp}] {new_note}".strip()
                update_data["notes"] = combined_notes

            result = self.supabase.table("projects").update(update_data).eq(
                "id", project_id
            ).execute()

            if result.data:
                self.logger.info(
                    "project_updated",
                    project_id=project_id,
                    status=status,
                    has_notes=bool(notes or progress_update),
                )
                return {
                    "success": True,
                    "project": result.data[0],
                    "message": f"Project updated successfully",
                }
            else:
                return {"success": False, "error": "Project not found"}

        except Exception as e:
            self.logger.error("update_project_error", error=str(e), project_id=project_id)
            return {"success": False, "error": str(e)}

    async def tool_get_pending_nudges(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        Get pending nudges for a profile.
        Used at start of conversation to know what proactive topics to raise.

        Args:
            profile_id: Student's profile UUID

        Returns:
            List of pending nudges, ordered by priority and creation time
        """
        try:
            result = self.supabase.table("nudge_queue").select(
                "id, nudge_type, project_id, priority, message_draft, created_at"
            ).eq("profile_id", profile_id).eq("status", "pending").order(
                "priority", desc=True
            ).order("created_at").execute()

            nudges = result.data or []
            self.logger.info(
                "pending_nudges_retrieved",
                profile_id=profile_id,
                count=len(nudges),
            )
            return nudges

        except Exception as e:
            self.logger.error("get_pending_nudges_error", error=str(e), profile_id=profile_id)
            return []

    async def tool_mark_nudge_delivered(self, nudge_id: str) -> Dict[str, Any]:
        """
        Mark a nudge as delivered after it's been raised in conversation.

        Args:
            nudge_id: UUID of the nudge to mark as delivered

        Returns:
            Result dict with success status
        """
        try:
            self.supabase.table("nudge_queue").update({
                "status": "delivered",
                "delivered_at": datetime.now().isoformat(),
            }).eq("id", nudge_id).execute()

            return {"success": True, "nudge_id": nudge_id}

        except Exception as e:
            self.logger.error("mark_nudge_delivered_error", error=str(e), nudge_id=nudge_id)
            return {"success": False, "error": str(e)}

    async def tool_mark_nudge_dismissed(self, nudge_id: str) -> Dict[str, Any]:
        """
        Mark a nudge as dismissed (user acknowledged but didn't act).

        Args:
            nudge_id: UUID of the nudge to dismiss

        Returns:
            Result dict with success status
        """
        try:
            self.supabase.table("nudge_queue").update({
                "status": "dismissed",
                "dismissed_at": datetime.now().isoformat(),
            }).eq("id", nudge_id).execute()

            return {"success": True, "nudge_id": nudge_id}

        except Exception as e:
            self.logger.error("mark_nudge_dismissed_error", error=str(e), nudge_id=nudge_id)
            return {"success": False, "error": str(e)}

    async def tool_get_upcoming_deadlines(
        self,
        profile_id: str,
        days_ahead: int = 14,
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming project deadlines for a student.

        Args:
            profile_id: Student's profile UUID
            days_ahead: Number of days to look ahead (default 14)

        Returns:
            List of projects with upcoming deadlines, ordered by urgency
        """
        try:
            # Get active projects with deadlines
            result = self.supabase.table("projects").select(
                "id, name, category, deadline, status, metadata"
            ).eq("profile_id", profile_id).eq("status", "active").not_.is_(
                "deadline", "null"
            ).execute()

            now = datetime.now()
            threshold = now + timedelta(days=days_ahead)

            upcoming = []
            for project in result.data or []:
                deadline_str = project.get("deadline")
                if not deadline_str:
                    continue

                try:
                    if isinstance(deadline_str, str):
                        deadline = datetime.fromisoformat(
                            deadline_str.replace("Z", "+00:00").replace("+00:00", "")
                        )
                    else:
                        deadline = deadline_str

                    deadline = deadline.replace(tzinfo=None)

                    if now < deadline <= threshold:
                        days_until = (deadline - now).days

                        # Determine urgency
                        if days_until <= 1:
                            urgency = "critical"
                        elif days_until <= 3:
                            urgency = "urgent"
                        elif days_until <= 7:
                            urgency = "soon"
                        else:
                            urgency = "normal"

                        upcoming.append({
                            "project_id": project["id"],
                            "name": project["name"],
                            "category": project.get("category"),
                            "deadline": deadline.isoformat(),
                            "days_until": days_until,
                            "urgency": urgency,
                        })

                except Exception:
                    continue

            # Sort by days until deadline
            return sorted(upcoming, key=lambda x: x["days_until"])

        except Exception as e:
            self.logger.error("get_upcoming_deadlines_error", error=str(e), profile_id=profile_id)
            return []

    async def get_proactive_welcome(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get proactive welcome message for new students.

        Called when Execution tab loads to check if there's a welcome
        message waiting (from EC onboarding after game plan generation).

        Returns:
            Welcome message data or None if no welcome pending
        """
        try:
            # Check for welcome_onboarding nudge
            result = self.supabase.table("nudge_queue").select(
                "id, nudge_type, message_draft, created_at"
            ).eq("profile_id", profile_id).eq(
                "nudge_type", "welcome_onboarding"
            ).eq("status", "pending").limit(1).execute()

            if result.data:
                nudge = result.data[0]
                self.logger.info(
                    "welcome_message_found",
                    profile_id=profile_id,
                    nudge_id=nudge["id"],
                )
                return {
                    "has_welcome": True,
                    "nudge_id": nudge["id"],
                    "message": nudge.get("message_draft", ""),
                    "created_at": nudge.get("created_at"),
                }

            return None

        except Exception as e:
            self.logger.error("get_proactive_welcome_error", error=str(e), profile_id=profile_id)
            return None

    async def deliver_welcome_and_mark(self, profile_id: str, nudge_id: str) -> Dict[str, Any]:
        """
        Deliver the welcome message and mark nudge as delivered.

        This is called after the frontend displays the welcome message.

        Args:
            profile_id: Student's profile UUID
            nudge_id: Welcome nudge UUID

        Returns:
            Result with success status
        """
        try:
            # Get the nudge message
            nudge_result = self.supabase.table("nudge_queue").select(
                "message_draft"
            ).eq("id", nudge_id).single().execute()

            if not nudge_result.data:
                return {"success": False, "error": "Nudge not found"}

            message = nudge_result.data.get("message_draft", "")

            # Store in conversations as the first message
            self.supabase.table("conversations").insert({
                "profile_id": profile_id,
                "agent_type": self.AGENT_TYPE,
                "role": "assistant",
                "content": message,
                "is_proactive": True,
                "context_type": "onboarding",
                "created_at": datetime.now().isoformat(),
            }).execute()

            # Mark nudge as delivered
            await self.tool_mark_nudge_delivered(nudge_id)

            self.logger.info(
                "welcome_delivered",
                profile_id=profile_id,
                nudge_id=nudge_id,
            )

            return {
                "success": True,
                "message": message,
            }

        except Exception as e:
            self.logger.error("deliver_welcome_error", error=str(e), profile_id=profile_id)
            return {"success": False, "error": str(e)}

    async def get_first_session_context(self, profile_id: str) -> Dict[str, Any]:
        """
        Get first session context for new students.

        Returns session agenda and priority focus for the first conversation.

        Args:
            profile_id: Student's profile UUID

        Returns:
            First session agenda and priorities
        """
        try:
            # Get profile for personalization
            profile = await self._get_profile(profile_id)
            profile_data = profile.get("profile_data", {}) or {}
            first_name = profile_data.get("first_name") or profile.get("first_name", "Student")
            archetype = profile.get("archetype", "Unknown")

            # Get projects and find nearest deadline
            projects = await self.tool_get_active_projects(profile_id)
            now = datetime.now()

            nearest_deadline = None
            nearest_project = None

            for project in projects:
                deadline_str = project.get("target_end_date")
                if deadline_str:
                    try:
                        deadline = datetime.fromisoformat(
                            deadline_str.replace("Z", "+00:00").replace("+00:00", "")
                        )
                        days_until = (deadline.replace(tzinfo=None) - now).days
                        if days_until > 0 and (nearest_deadline is None or days_until < nearest_deadline):
                            nearest_deadline = days_until
                            nearest_project = project
                    except:
                        pass

            # Build first session agenda
            agenda = {
                "title": f"Welcome, {first_name}!",
                "sections": [
                    {
                        "name": "Game Plan Overview",
                        "description": "Walk through your personalized game plan",
                        "duration_minutes": 5,
                    },
                    {
                        "name": "168-Hour Framework",
                        "description": "Map out how you'll allocate your time each week",
                        "duration_minutes": 10,
                    },
                    {
                        "name": "Priority Projects",
                        "description": "Identify your P0 priority for the next 2 weeks",
                        "duration_minutes": 10,
                    },
                    {
                        "name": "Working Style & Support",
                        "description": "Understand how you work best",
                        "duration_minutes": 5,
                    },
                ],
                "total_projects": len(projects),
                "immediate_priority": None,
            }

            # Determine immediate priority
            if nearest_deadline and nearest_deadline <= 14:
                agenda["immediate_priority"] = {
                    "project": nearest_project.get("title", "Upcoming Deadline"),
                    "days_until": nearest_deadline,
                    "reason": f"Due in {nearest_deadline} days",
                }
            elif archetype == "SCHOLAR":
                agenda["immediate_priority"] = {
                    "focus": "Academic Foundation",
                    "reason": "Scholars thrive when academics are solid",
                }
            elif archetype == "BUILDER":
                agenda["immediate_priority"] = {
                    "focus": "EC Impact Projects",
                    "reason": "Builders need tangible projects to drive",
                }
            else:
                agenda["immediate_priority"] = {
                    "focus": "168-Hour Framework",
                    "reason": "Start with time management foundation",
                }

            return agenda

        except Exception as e:
            self.logger.error("get_first_session_context_error", error=str(e), profile_id=profile_id)
            return {
                "title": "Welcome to Your Coaching Journey",
                "sections": [],
                "error": str(e),
            }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    async def _get_profile(self, profile_id: str) -> Dict[str, Any]:
        """Get student profile."""
        try:
            from tools.database import get_profile_with_assessment
            return await get_profile_with_assessment(profile_id) or {}
        except Exception as e:
            self.logger.warning("get_profile_error", error=str(e))
            return {}

    async def _get_current_weekly_plan(self, profile_id: str) -> Dict[str, Any]:
        """Get current week's plan."""
        try:
            result = self.supabase.table("weekly_plans") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .order("week_start", desc=True) \
                .limit(1) \
                .execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            self.logger.warning("get_weekly_plan_error", error=str(e))
            return {}

    async def _get_game_plan(self, profile_id: str) -> Dict[str, Any]:
        """
        Get the student's game plan with summer programs, awards, and ECs.
        v5.4: Critical for Execution Agent to know WHAT to help execute.
        """
        try:
            result = self.supabase.table("game_plans") \
                .select("id, plan_data, created_at") \
                .eq("profile_id", profile_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()

            if not result.data:
                return {}

            plan_data = result.data[0].get("plan_data", {})

            # Extract key components for context
            return {
                "summer_programs": plan_data.get("summer_programs", []),
                "awards": plan_data.get("awards", []),
                "ecs": plan_data.get("ecs", []),
                "academic_goals": plan_data.get("academic_goals", []),
                "timeline": plan_data.get("timeline", {}),
                "spike": plan_data.get("spike", ""),
                "narrative_theme": plan_data.get("narrative_theme", ""),
            }
        except Exception as e:
            self.logger.warning("get_game_plan_error", error=str(e))
            return {}

    async def _get_active_projects_summary(self, profile_id: str) -> List[Dict[str, Any]]:
        """Get summary of active projects."""
        projects = await self.tool_get_active_projects(profile_id)
        return [{
            "id": p.get("id"),
            "title": p.get("name", "Untitled"),
            "status": p.get("status"),
            "type": p.get("type"),
            "days_since_activity": self._calculate_days_since(p.get("last_activity_at")),
            "target_end_date": p.get("target_end_date"),
        } for p in projects[:10]]  # Limit for context window

    def _calculate_days_since(self, timestamp: Optional[str]) -> int:
        """Calculate days since a timestamp."""
        if not timestamp:
            return 0
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00").replace("+00:00", ""))
            return (datetime.now() - dt).days
        except:
            return 0

    async def _get_recent_conversations(self, profile_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history from conversations table."""
        try:
            result = self.supabase.table("conversations") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .eq("agent_type", self.AGENT_TYPE) \
                .is_("deleted_at", "null") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()

            # Return in chronological order
            return list(reversed(result.data or []))
        except Exception as e:
            self.logger.warning("get_conversations_error", error=str(e))
            return []

    async def _get_crisis(self, crisis_id: str) -> Dict[str, Any]:
        """Get crisis details."""
        try:
            result = self.supabase.table("crises") \
                .select("*") \
                .eq("id", crisis_id) \
                .single() \
                .execute()
            return result.data or {}
        except Exception as e:
            self.logger.warning("get_crisis_error", error=str(e))
            return {}

    async def _get_weekly_plan(self, plan_id: str) -> Dict[str, Any]:
        """Get weekly plan by ID."""
        try:
            result = self.supabase.table("weekly_plans") \
                .select("*") \
                .eq("id", plan_id) \
                .single() \
                .execute()
            return result.data or {}
        except Exception as e:
            self.logger.warning("get_weekly_plan_by_id_error", error=str(e))
            return {}

    async def _extract_and_store_insights(
        self,
        profile_id: str,
        user_message: str,
        assistant_response: str,
        context: Dict[str, Any],
    ) -> None:
        """Extract insights from conversation and store in memory."""
        # Simple keyword-based extraction (could be enhanced with LLM)
        keywords = {
            "blocker": ["stuck", "blocked", "can't", "won't", "impossible"],
            "milestone": ["finished", "completed", "done", "achieved", "won"],
            "preference": ["prefer", "like", "enjoy", "love", "hate"],
            "pattern": ["always", "usually", "never", "tend to"],
        }

        message_lower = user_message.lower()

        for insight_type, words in keywords.items():
            if any(word in message_lower for word in words):
                insight = f"User mentioned: {user_message[:100]}..."
                await self.tool_store_insight(
                    profile_id=profile_id,
                    insight=insight,
                    insight_type=insight_type,
                    confidence=0.6,
                )
                break

    def _parse_json_response(self, content: str, fallback: dict) -> dict:
        """Parse JSON from LLM response with fallback."""
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())
        except json.JSONDecodeError:
            self.logger.warning("json_parse_failed", content=content[:100])
            return fallback


# Singleton instance
execution_chat_agent = ExecutionChatAgent()
