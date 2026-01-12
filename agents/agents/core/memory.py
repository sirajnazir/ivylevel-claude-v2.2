# agents/agents/core/memory.py
"""
IvyQuest v13.2 - Memory Manager

This module implements the 3-tier memory system:
1. Working Memory: In-memory buffers for active reasoning
2. Short-term Memory: Redis for session state, handoffs (24hr TTL)
3. Long-term Memory: Supabase for persistent storage

v13.2 adds:
- WorkingMemoryBuffer (not dict)
- Agent handoff protocol
- Profile snapshot manager
- Interaction memory manager
- Coaching knowledge search
- Outcome tracking
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

from .working_memory import WorkingMemoryBuffer
from .handoff import HandoffManager, AgentHandoff
from .profile_snapshot import ProfileSnapshotManager, ProfileSnapshot
from .interaction_memory import InteractionMemoryManager, InteractionSummary

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    v13.2 3-tier memory manager with:
    - WorkingMemoryBuffer (not dict)
    - Agent handoff protocol
    - Profile snapshot manager
    - Interaction memory manager
    - Coaching knowledge search
    - Outcome tracking
    
    Usage:
        memory = MemoryManager(
            redis_client=redis,
            supabase_client=supabase,
            embedding_model=embeddings,
        )
        
        # Working memory
        buffer = memory.get_working_buffer(profile_id, agent_name)
        
        # Handoffs
        await memory.create_handoff(from_agent, to_agent, profile_id, ...)
        
        # Snapshots
        await memory.snapshots.create_snapshot(profile_id, profile_data, ...)
        
        # Interactions
        await memory.interactions.store_interaction(summary)
    """

    def __init__(
        self,
        redis_client=None,
        supabase_client=None,
        embedding_model=None,
    ):
        """
        Initialize MemoryManager.
        
        Args:
            redis_client: Async Redis client for short-term memory
            supabase_client: Async Supabase client for long-term memory
            embedding_model: Embedding model for semantic search
        """
        self.redis = redis_client
        self.supabase = supabase_client
        self.embeddings = embedding_model

        # v13.2: Proper working memory buffers (NOT dict)
        self._working_buffers: Dict[str, WorkingMemoryBuffer] = {}

        # v13.2: Handoff manager
        self.handoffs = HandoffManager(redis_client) if redis_client else None

        # v13.2: Profile snapshot manager
        self.snapshots = ProfileSnapshotManager(supabase_client) if supabase_client else None

        # v13.2: Interaction memory manager
        self.interactions = InteractionMemoryManager(
            supabase_client, embedding_model
        ) if supabase_client else None

        self.short_term_ttl = timedelta(hours=24)

    # ============ WORKING MEMORY (v13.2) ============

    def get_working_buffer(
        self,
        profile_id: str,
        agent_name: str,
    ) -> WorkingMemoryBuffer:
        """
        Get or create working memory buffer for an agent.
        
        Args:
            profile_id: Profile ID
            agent_name: Name of agent requesting buffer
            
        Returns:
            WorkingMemoryBuffer instance
        """
        key = f"{profile_id}:{agent_name}"
        if key not in self._working_buffers:
            self._working_buffers[key] = WorkingMemoryBuffer(agent_name, profile_id)
            logger.debug(f"Created working buffer for {agent_name} on profile {profile_id}")
        return self._working_buffers[key]

    def clear_working_buffer(
        self,
        profile_id: str,
        agent_name: str,
    ) -> None:
        """
        Clear working memory after agent completes.
        
        Args:
            profile_id: Profile ID
            agent_name: Name of agent
        """
        key = f"{profile_id}:{agent_name}"
        if key in self._working_buffers:
            self._working_buffers[key].clear()
            del self._working_buffers[key]
            logger.debug(f"Cleared working buffer for {agent_name} on profile {profile_id}")

    def get_active_buffers(self) -> List[Dict[str, Any]]:
        """Get list of active working buffers."""
        return [buffer.to_dict() for buffer in self._working_buffers.values()]

    # ============ HANDOFFS (v13.2) ============

    async def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        profile_id: str,
        context: Dict[str, Any],
        task: str,
        reason: str,
        **kwargs,
    ) -> Optional[AgentHandoff]:
        """
        Create agent handoff.
        
        Args:
            from_agent: Agent creating handoff
            to_agent: Agent receiving handoff
            profile_id: Profile ID
            context: Context to pass
            task: What receiving agent should do
            reason: Why handoff is happening
            **kwargs: Additional AgentHandoff fields
            
        Returns:
            Created AgentHandoff or None if disabled
        """
        if not self.handoffs:
            logger.warning("No Redis client - handoffs disabled")
            return None

        return await self.handoffs.create_handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            profile_id=profile_id,
            context=context,
            task=task,
            reason=reason,
            **kwargs,
        )

    async def get_handoff(
        self,
        profile_id: str,
        to_agent: str,
        from_agent: Optional[str] = None,
    ) -> Optional[AgentHandoff]:
        """
        Get latest handoff to an agent.
        
        Args:
            profile_id: Profile ID
            to_agent: Agent receiving handoff
            from_agent: Optional specific source agent
            
        Returns:
            AgentHandoff or None
        """
        if not self.handoffs:
            return None
        return await self.handoffs.get_handoff(profile_id, to_agent, from_agent)

    async def acknowledge_handoff(
        self,
        profile_id: str,
        from_agent: str,
        to_agent: str,
    ) -> bool:
        """Acknowledge (delete) a handoff after processing."""
        if not self.handoffs:
            return False
        return await self.handoffs.acknowledge_handoff(profile_id, from_agent, to_agent)

    # ============ COACHING KNOWLEDGE (v13.1+) ============

    async def search_coaching_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        archetype: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over Jenny's coaching knowledge base.
        
        Categories: 'crisis_response', 'narrative', 'execution', 
                   'awards', 'opportunity', 'time_management', 
                   'essay_strategy', 'general'
        
        Args:
            query: Search query
            category: Optional category filter
            archetype: Optional archetype filter
            limit: Maximum results
            
        Returns:
            List of matching coaching knowledge entries
        """
        if not self.supabase or not self.embeddings:
            return []

        try:
            query_embedding = await self.embeddings.encode(query)

            result = await self.supabase.rpc(
                "match_coaching_knowledge",
                {
                    "query_embedding": query_embedding.tolist(),
                    "match_threshold": 0.7,
                    "match_count": limit,
                    "filter_category": category,
                    "filter_archetype": archetype,
                }
            ).execute()

            return result.data or []
        except Exception as e:
            logger.error(f"Coaching knowledge search failed: {e}")
            return []

    # ============ OUTCOME TRACKING (v13.1+) ============

    async def record_outcome(
        self,
        profile_id: str,
        outcome_type: str,
        outcome_subtype: str,
        entity_name: str,
        success: bool,
        predicted_probability: Optional[float] = None,
        contributing_factors: Optional[Dict[str, Any]] = None,
        lessons_learned: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Record an outcome for learning.
        
        Args:
            profile_id: Profile ID
            outcome_type: 'award', 'program', 'project', 'essay', 'application'
            outcome_subtype: 'won', 'lost', 'completed', 'abandoned', etc.
            entity_name: Name of the entity
            success: Whether outcome was successful
            predicted_probability: Agent's prediction (for calibration)
            contributing_factors: What led to outcome
            lessons_learned: Extracted learnings
            
        Returns:
            Created outcome record or None
        """
        if not self.supabase:
            return None

        try:
            result = await self.supabase.table("outcome_history").insert({
                "profile_id": profile_id,
                "outcome_type": outcome_type,
                "outcome_subtype": outcome_subtype,
                "entity_name": entity_name,
                "success": success,
                "predicted_probability": predicted_probability,
                "contributing_factors": contributing_factors or {},
                "lessons_learned": lessons_learned,
                "completed_at": datetime.utcnow().isoformat(),
            }).execute()

            if result.data:
                logger.info(
                    f"Recorded {outcome_type} outcome for profile {profile_id}: "
                    f"{entity_name} ({outcome_subtype})"
                )
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to record outcome: {e}")
            return None

    async def get_outcome_patterns(
        self,
        profile_id: str,
        outcome_type: Optional[str] = None,
        success_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get outcome history for pattern analysis.
        
        Args:
            profile_id: Profile ID
            outcome_type: Optional type filter
            success_only: Only return successful outcomes
            
        Returns:
            List of outcome records
        """
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("outcome_history")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .order("completed_at", desc=True)\
                .limit(50)

            if outcome_type:
                query = query.eq("outcome_type", outcome_type)

            if success_only:
                query = query.eq("success", True)

            result = await query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get outcome patterns: {e}")
            return []

    # ============ OBSERVATIONS (Agent Memories) ============

    async def store_observation(
        self,
        agent_id: str,
        profile_id: str,
        observation: Dict[str, Any],
        importance: float = 0.5,
        tags: List[str] = None,
    ) -> Optional[str]:
        """
        Store an agent observation to long-term memory.
        
        Args:
            agent_id: Agent making observation
            profile_id: Profile ID
            observation: Observation data
            importance: Importance score 0-1
            tags: Optional tags for filtering
            
        Returns:
            ID of stored observation or None
        """
        if not self.supabase:
            return None

        try:
            data = {
                "agent_id": agent_id,
                "profile_id": profile_id,
                "observation": observation,
                "importance": importance,
                "tags": tags or [],
                "created_at": datetime.utcnow().isoformat(),
            }

            # Generate embedding for semantic search
            if self.embeddings:
                obs_text = json.dumps(observation, default=str)
                embedding = await self.embeddings.encode(obs_text)
                data["embedding"] = embedding.tolist()

            result = await self.supabase.table("agent_memories").insert(data).execute()

            if result.data:
                return result.data[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Failed to store observation: {e}")
            return None

    async def search_observations(
        self,
        profile_id: str,
        query: str,
        agent_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search observations semantically.
        
        Args:
            profile_id: Profile ID
            query: Search query
            agent_id: Optional agent filter
            limit: Maximum results
            
        Returns:
            List of matching observations
        """
        if not self.supabase or not self.embeddings:
            return []

        try:
            query_embedding = await self.embeddings.encode(query)

            params = {
                "query_embedding": query_embedding.tolist(),
                "match_threshold": 0.7,
                "match_count": limit,
                "filter_profile_id": profile_id,
            }
            if agent_id:
                params["filter_agent_id"] = agent_id

            result = await self.supabase.rpc("match_memories", params).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to search observations: {e}")
            return []

    async def get_recent_observations(
        self,
        profile_id: str,
        agent_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get most recent observations for a profile."""
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("agent_memories")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .order("created_at", desc=True)\
                .limit(limit)

            if agent_id:
                query = query.eq("agent_id", agent_id)

            result = await query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get recent observations: {e}")
            return []

    # ============ SHORT-TERM MEMORY (Redis) ============

    async def set_session_state(
        self,
        session_id: str,
        key: str,
        value: Any,
        ttl_seconds: int = None,
    ) -> bool:
        """
        Store session state in Redis.
        
        Args:
            session_id: Session ID
            key: State key
            value: Value to store (will be JSON serialized)
            ttl_seconds: Optional TTL override
            
        Returns:
            Success status
        """
        if not self.redis:
            return False

        try:
            redis_key = f"session:{session_id}:{key}"
            ttl = ttl_seconds or int(self.short_term_ttl.total_seconds())
            await self.redis.setex(redis_key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"Failed to set session state: {e}")
            return False

    async def get_session_state(
        self,
        session_id: str,
        key: str,
    ) -> Optional[Any]:
        """
        Retrieve session state from Redis.
        
        Args:
            session_id: Session ID
            key: State key
            
        Returns:
            Stored value or None
        """
        if not self.redis:
            return None

        try:
            redis_key = f"session:{session_id}:{key}"
            data = await self.redis.get(redis_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get session state: {e}")
            return None

    async def delete_session_state(
        self,
        session_id: str,
        key: str = None,
    ) -> bool:
        """
        Delete session state.
        
        Args:
            session_id: Session ID
            key: Optional specific key (None = delete all session state)
            
        Returns:
            Success status
        """
        if not self.redis:
            return False

        try:
            if key:
                redis_key = f"session:{session_id}:{key}"
                await self.redis.delete(redis_key)
            else:
                # Delete all session keys
                pattern = f"session:{session_id}:*"
                cursor = 0
                while True:
                    cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self.redis.delete(*keys)
                    if cursor == 0:
                        break
            return True
        except Exception as e:
            logger.error(f"Failed to delete session state: {e}")
            return False

    # ============ LEARNED PATTERNS ============

    async def store_learned_pattern(
        self,
        pattern_type: str,
        pattern_name: str,
        trigger_conditions: Dict[str, Any],
        successful_responses: Dict[str, Any],
        failed_approaches: Dict[str, Any] = None,
        applicable_archetypes: List[str] = None,
    ) -> Optional[str]:
        """
        Store a learned pattern for future use.
        
        Args:
            pattern_type: Type of pattern
            pattern_name: Name of pattern
            trigger_conditions: When pattern applies
            successful_responses: What works
            failed_approaches: What to avoid
            applicable_archetypes: Which archetypes this applies to
            
        Returns:
            Pattern ID or None
        """
        if not self.supabase:
            return None

        try:
            data = {
                "pattern_type": pattern_type,
                "pattern_name": pattern_name,
                "trigger_conditions": trigger_conditions,
                "successful_responses": successful_responses,
                "failed_approaches": failed_approaches or {},
                "applicable_archetypes": applicable_archetypes or [],
            }

            # Generate embedding
            if self.embeddings:
                pattern_text = f"{pattern_name} {json.dumps(trigger_conditions)}"
                embedding = await self.embeddings.encode(pattern_text)
                data["embedding"] = embedding.tolist()

            result = await self.supabase.table("learned_patterns").insert(data).execute()

            if result.data:
                logger.info(f"Stored learned pattern: {pattern_name}")
                return result.data[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Failed to store learned pattern: {e}")
            return None

    async def find_applicable_patterns(
        self,
        situation_description: str,
        pattern_type: Optional[str] = None,
        archetype: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find patterns applicable to a situation.
        
        Args:
            situation_description: Description of current situation
            pattern_type: Optional type filter
            archetype: Optional archetype filter
            limit: Maximum results
            
        Returns:
            List of applicable patterns
        """
        if not self.supabase or not self.embeddings:
            return []

        try:
            query_embedding = await self.embeddings.encode(situation_description)

            # Use RPC for semantic search if available
            # Otherwise fall back to simple query
            query = self.supabase.table("learned_patterns")\
                .select("*")\
                .order("success_rate", desc=True)\
                .limit(limit)

            if pattern_type:
                query = query.eq("pattern_type", pattern_type)

            if archetype:
                query = query.contains("applicable_archetypes", [archetype])

            result = await query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to find applicable patterns: {e}")
            return []

    # ============ HEALTH CHECK ============

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of memory subsystems.
        
        Returns:
            Dict with status of each subsystem
        """
        health = {
            "working_memory": True,
            "short_term_memory": False,
            "long_term_memory": False,
            "embeddings": self.embeddings is not None,
        }

        # Check Redis
        if self.redis:
            try:
                await self.redis.ping()
                health["short_term_memory"] = True
            except Exception:
                pass

        # Check Supabase
        if self.supabase:
            try:
                await self.supabase.table("profiles").select("id").limit(1).execute()
                health["long_term_memory"] = True
            except Exception:
                pass

        health["healthy"] = all([
            health["working_memory"],
            health["short_term_memory"] or not self.redis,  # OK if not configured
            health["long_term_memory"] or not self.supabase,  # OK if not configured
        ])

        return health
