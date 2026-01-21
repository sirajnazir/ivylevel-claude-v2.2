"""
Letta Client Wrapper
====================

Wrapper around the Letta client with feature flags, error handling,
and integration with IvyLevel infrastructure.

This client handles:
- Connection to Letta Cloud API
- Agent creation and management
- Message routing through Orchestrator
- Memory block synchronization
- Graceful fallback when disabled
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
from dataclasses import dataclass

from .config import (
    LETTA_CONFIG,
    AgentType,
    AgentStatus,
    is_letta_enabled,
    is_agent_enabled,
    LETTA_TABLES,
)

logger = structlog.get_logger()


@dataclass
class LettaResponse:
    """Response from Letta agent interaction."""
    success: bool
    message: str
    agent_type: AgentType
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "metadata": self.metadata or {},
            "error": self.error,
        }


class LettaClientWrapper:
    """
    Wrapper for Letta client with IvyLevel integration.

    Features:
    - Feature flag gating (LETTA_ENABLED must be true)
    - Automatic agent creation per student
    - Message routing through Orchestrator
    - Memory sync with Supabase
    - Graceful degradation when Letta unavailable

    Usage:
        client = LettaClientWrapper(supabase_client)

        if client.is_available():
            response = await client.chat(profile_id, "Help me plan my activities")
        else:
            # Fall back to existing agents
            ...
    """

    def __init__(self, supabase_client=None):
        """
        Initialize the Letta client wrapper.

        Args:
            supabase_client: Supabase client for database operations
        """
        self.supabase = supabase_client
        self._letta_client = None
        self._initialized = False
        self._agent_cache: Dict[str, Dict[AgentType, str]] = {}  # profile_id -> agent_ids

        logger.info(
            "letta_client_wrapper_created",
            enabled=LETTA_CONFIG.enabled,
            has_api_key=bool(LETTA_CONFIG.api_key),
        )

    def is_available(self) -> bool:
        """Check if Letta client is available and enabled."""
        return is_letta_enabled()

    async def initialize(self) -> bool:
        """
        Initialize the Letta client connection.

        Returns:
            True if initialization successful, False otherwise
        """
        if not self.is_available():
            logger.info("letta_client_disabled", reason="Feature flag disabled or no API key")
            return False

        if self._initialized:
            return True

        try:
            # Import letta client only when needed
            # Note: The package is 'letta_client', not 'letta'
            from letta_client import Letta

            self._letta_client = Letta(
                api_key=LETTA_CONFIG.api_key,
                base_url=LETTA_CONFIG.base_url,
            )

            # Verify connection
            # Note: Actual verification depends on Letta SDK
            self._initialized = True

            logger.info(
                "letta_client_initialized",
                base_url=LETTA_CONFIG.base_url,
            )
            return True

        except ImportError:
            logger.error("letta_client_import_error", error="letta package not installed")
            return False
        except Exception as e:
            logger.error("letta_client_init_error", error=str(e))
            return False

    async def get_or_create_agents(self, profile_id: str) -> Dict[AgentType, str]:
        """
        Get or create Letta agents for a student.

        Args:
            profile_id: Student profile ID

        Returns:
            Dictionary mapping AgentType to Letta agent IDs
        """
        if not self._initialized:
            await self.initialize()

        if not self._initialized:
            return {}

        # Check cache first
        if profile_id in self._agent_cache:
            cached = self._agent_cache[profile_id]
            # Verify orchestrator exists (minimum required)
            if AgentType.ORCHESTRATOR in cached:
                return cached

        # Check database for existing agents
        existing = await self._load_agents_from_db(profile_id)

        # Required agent types (all except dormant assessment)
        required_agents = {
            AgentType.ORCHESTRATOR,
            AgentType.GAMEPLAN,
            AgentType.EXECUTION,
            AgentType.AWARDS,
            AgentType.ESSAY,
        }

        # Check if all required agents exist
        existing_types = set(existing.keys()) if existing else set()
        missing_types = required_agents - existing_types

        if not missing_types:
            # All required agents exist
            self._agent_cache[profile_id] = existing
            return existing

        # Create missing agents
        logger.info(
            "letta_creating_missing_agents",
            profile_id=profile_id,
            missing=list(t.value for t in missing_types),
        )

        new_agents = await self._create_agent_set(profile_id)

        # Merge existing and new agents
        agents = {**existing, **new_agents}

        # Save to database (only new ones)
        await self._save_agents_to_db(profile_id, new_agents)

        # Cache
        self._agent_cache[profile_id] = agents

        return agents

    async def _load_agents_from_db(self, profile_id: str) -> Dict[AgentType, str]:
        """Load existing agent IDs from database."""
        if not self.supabase:
            return {}

        try:
            result = self.supabase.table(LETTA_TABLES["agent_registry"]) \
                .select("agent_type, letta_agent_id") \
                .eq("profile_id", profile_id) \
                .eq("is_active", True) \
                .execute()

            agents = {}
            for row in result.data or []:
                try:
                    agent_type = AgentType(row["agent_type"])
                    agents[agent_type] = row["letta_agent_id"]
                except ValueError:
                    continue

            return agents

        except Exception as e:
            logger.error("letta_load_agents_error", profile_id=profile_id, error=str(e))
            return {}

    async def _save_agents_to_db(self, profile_id: str, agents: Dict[AgentType, str]) -> None:
        """Save agent IDs to database."""
        if not self.supabase:
            return

        try:
            records = [
                {
                    "profile_id": profile_id,
                    "letta_agent_id": agent_id,
                    "agent_type": agent_type.value,
                    "is_active": True,
                }
                for agent_type, agent_id in agents.items()
            ]

            self.supabase.table(LETTA_TABLES["agent_registry"]) \
                .upsert(records, on_conflict="profile_id,agent_type") \
                .execute()

            logger.info(
                "letta_agents_saved",
                profile_id=profile_id,
                agent_count=len(agents),
            )

        except Exception as e:
            logger.error("letta_save_agents_error", profile_id=profile_id, error=str(e))

    async def _create_agent_set(self, profile_id: str) -> Dict[AgentType, str]:
        """
        Create a full set of Letta agents for a student.

        This creates:
        - 1 Orchestrator (supervisor)
        - 4 Specialists (GamePlan, Execution, Awards, Essay)
        - 1 Dormant Assessment (placeholder)
        """
        if not self._letta_client:
            return {}

        agents = {}

        # Import agent configs
        from .agents import (
            ORCHESTRATOR_CONFIG,
            GAMEPLAN_AGENT_CONFIG,
            EXECUTION_AGENT_CONFIG,
            AWARDS_AGENT_CONFIG,
            ESSAY_AGENT_CONFIG,
            ASSESSMENT_AGENT_CONFIG,
        )

        # Import memory blocks
        from .memory import MEMORY_BLOCKS

        agent_configs = [
            (AgentType.ORCHESTRATOR, ORCHESTRATOR_CONFIG),
            (AgentType.GAMEPLAN, GAMEPLAN_AGENT_CONFIG),
            (AgentType.EXECUTION, EXECUTION_AGENT_CONFIG),
            (AgentType.AWARDS, AWARDS_AGENT_CONFIG),
            (AgentType.ESSAY, ESSAY_AGENT_CONFIG),
            (AgentType.ASSESSMENT, ASSESSMENT_AGENT_CONFIG),
        ]

        for agent_type, config in agent_configs:
            try:
                # Skip creating dormant agents in Letta (just track locally)
                if config.get("status") == "DORMANT":
                    agents[agent_type] = f"dormant_{agent_type.value}_{profile_id}"
                    continue

                # Create agent in Letta
                agent = await self._create_single_agent(
                    profile_id=profile_id,
                    agent_type=agent_type,
                    config=config,
                    memory_blocks=MEMORY_BLOCKS,
                )

                if agent:
                    agents[agent_type] = agent

            except Exception as e:
                logger.error(
                    "letta_create_agent_error",
                    profile_id=profile_id,
                    agent_type=agent_type.value,
                    error=str(e),
                )

        return agents

    async def _create_single_agent(
        self,
        profile_id: str,
        agent_type: AgentType,
        config: Dict[str, Any],
        memory_blocks: Dict[str, Any],
    ) -> Optional[str]:
        """Create a single Letta agent."""
        if not self._letta_client:
            return None

        try:
            # Build agent creation parameters
            name = f"{config['name']}_{profile_id[:8]}"

            # Filter tools to only include Letta built-in tools
            # Custom IvyLevel tools will be registered separately
            LETTA_BUILTIN_TOOLS = {
                "send_message",
                "core_memory_get",
                "core_memory_replace",
                "core_memory_append",
                "conversation_search",
                "archival_memory_insert",
                "archival_memory_search",
            }

            requested_tools = config.get("tools", [])
            available_tools = [t for t in requested_tools if t in LETTA_BUILTIN_TOOLS]

            if len(available_tools) != len(requested_tools):
                skipped = set(requested_tools) - set(available_tools)
                logger.info(
                    "letta_tools_filtered",
                    agent_type=agent_type.value,
                    available=available_tools,
                    skipped=list(skipped),
                )

            # Create agent via Letta SDK
            # Note: Actual SDK usage depends on letta-client version
            agent = self._letta_client.agents.create(
                name=name,
                system=config.get("system_prompt", ""),
                # Don't pass tools parameter - use defaults
                tags=config.get("tags", []) + [f"profile:{profile_id}"],
                metadata={
                    "profile_id": profile_id,
                    "agent_type": agent_type.value,
                    "ivylevel_version": "1.0.0",
                },
            )

            logger.info(
                "letta_agent_created",
                profile_id=profile_id,
                agent_type=agent_type.value,
                agent_id=agent.id,
            )

            return agent.id

        except Exception as e:
            logger.error(
                "letta_create_single_agent_error",
                agent_type=agent_type.value,
                error=str(e),
            )
            return None

    async def chat(
        self,
        profile_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> LettaResponse:
        """
        Send a chat message to the Letta Orchestrator.

        The Orchestrator will route to the appropriate specialist agent.

        Args:
            profile_id: Student profile ID
            message: User message
            context: Optional context (e.g., current page, recent actions)

        Returns:
            LettaResponse with the agent's reply
        """
        if not self.is_available():
            return LettaResponse(
                success=False,
                message="",
                agent_type=AgentType.ORCHESTRATOR,
                error="Letta is not enabled. Set LETTA_ENABLED=true and provide LETTA_API_KEY.",
            )

        try:
            # Ensure initialized
            if not self._initialized:
                await self.initialize()

            # Get or create agents
            agents = await self.get_or_create_agents(profile_id)

            if AgentType.ORCHESTRATOR not in agents:
                return LettaResponse(
                    success=False,
                    message="",
                    agent_type=AgentType.ORCHESTRATOR,
                    error="Failed to create Orchestrator agent",
                )

            orchestrator_id = agents[AgentType.ORCHESTRATOR]

            # Sync memory before chat
            await self._sync_memory(profile_id, orchestrator_id)

            # Send message to Orchestrator
            response = self._letta_client.agents.messages.create(
                agent_id=orchestrator_id,
                messages=[{"role": "user", "content": message}],
            )

            # Extract response - Letta SDK returns AssistantMessage objects
            # with 'content' attribute and 'message_type' = 'assistant_message'
            assistant_message = ""
            for msg in response.messages:
                msg_type = getattr(msg, "message_type", None)
                if msg_type == "assistant_message" and hasattr(msg, "content"):
                    assistant_message = msg.content
                    break

            logger.info(
                "letta_chat_success",
                profile_id=profile_id,
                message_length=len(message),
                response_length=len(assistant_message),
            )

            return LettaResponse(
                success=True,
                message=assistant_message,
                agent_type=AgentType.ORCHESTRATOR,
                agent_id=orchestrator_id,
                metadata={
                    "profile_id": profile_id,
                    "context": context,
                },
            )

        except Exception as e:
            logger.error(
                "letta_chat_error",
                profile_id=profile_id,
                error=str(e),
            )
            return LettaResponse(
                success=False,
                message="",
                agent_type=AgentType.ORCHESTRATOR,
                error=str(e),
            )

    async def _sync_memory(self, profile_id: str, agent_id: str) -> None:
        """
        Sync memory blocks from Supabase to Letta agent.

        This updates the agent's memory with current student data.
        """
        if not self._letta_client or not self.supabase:
            return

        try:
            from .memory import MemorySyncService

            sync_service = MemorySyncService(self.supabase)
            blocks = await sync_service.build_memory_blocks(profile_id)

            # Update each memory block in Letta
            for block_name, block_content in blocks.items():
                try:
                    self._letta_client.agents.memory.update(
                        agent_id=agent_id,
                        block_name=block_name,
                        value=block_content,
                    )
                except Exception as e:
                    logger.warning(
                        "letta_memory_block_update_failed",
                        agent_id=agent_id,
                        block_name=block_name,
                        error=str(e),
                    )

            logger.debug(
                "letta_memory_synced",
                profile_id=profile_id,
                agent_id=agent_id,
                block_count=len(blocks),
            )

        except Exception as e:
            logger.error(
                "letta_memory_sync_error",
                profile_id=profile_id,
                agent_id=agent_id,
                error=str(e),
            )

    async def get_status(self, profile_id: str) -> Dict[str, Any]:
        """
        Get Letta integration status for a student.

        Args:
            profile_id: Student profile ID

        Returns:
            Status dictionary with agent info
        """
        return {
            "letta_enabled": self.is_available(),
            "initialized": self._initialized,
            "config": LETTA_CONFIG.to_dict(),
            "agents": {
                k.value: {"agent_id": v, "enabled": is_agent_enabled(k)}
                for k, v in self._agent_cache.get(profile_id, {}).items()
            },
        }

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self._agent_cache.clear()
        self._initialized = False
        self._letta_client = None
        logger.info("letta_client_cleanup")
