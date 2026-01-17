"""
Redis Client Initialization v5.3
================================

Provides async and sync Redis clients for:
- Session state (short-term memory)
- Agent handoffs
- Rate limiting
- Pub/Sub for real-time events

Configuration via environment variables:
- REDIS_ENABLED: Enable Redis (default: false)
- REDIS_HOST: Redis host (default: localhost)
- REDIS_PORT: Redis port (default: 6379)
- REDIS_DB: Redis database (default: 0)
- REDIS_PASSWORD: Redis password (optional)
- REDIS_SSL: Use SSL (default: false)
- REDIS_SESSION_TTL: Session TTL in seconds (default: 3600)
- REDIS_HANDOFF_TTL: Handoff TTL in seconds (default: 86400)
"""

import logging
from typing import Optional, Any
from functools import lru_cache

import redis
from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import ConnectionError, RedisError

from agents.config import get_settings

logger = logging.getLogger(__name__)

# ============================================================================
# Redis Client Factory
# ============================================================================


class RedisClient:
    """
    Redis client wrapper with connection management.

    Supports both sync and async operations.
    Gracefully handles connection failures with fallback behavior.
    """

    def __init__(self):
        self._sync_client: Optional[redis.Redis] = None
        self._async_client: Optional[AsyncRedis] = None
        self._is_connected = False
        self._connection_error: Optional[str] = None

    @property
    def enabled(self) -> bool:
        """Check if Redis is enabled in settings."""
        settings = get_settings()
        return settings.redis_enabled

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._is_connected

    @property
    def connection_error(self) -> Optional[str]:
        """Get last connection error if any."""
        return self._connection_error

    def _get_connection_params(self) -> dict:
        """Get Redis connection parameters from settings."""
        settings = get_settings()
        return {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db,
            "password": settings.redis_password,
            "ssl": settings.redis_ssl,
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
        }

    def connect_sync(self) -> Optional[redis.Redis]:
        """
        Create synchronous Redis connection.

        Returns None if Redis is disabled or connection fails.
        """
        if not self.enabled:
            logger.info("[Redis] Disabled by configuration")
            return None

        if self._sync_client is not None:
            return self._sync_client

        try:
            params = self._get_connection_params()
            self._sync_client = redis.Redis(**params)

            # Test connection
            self._sync_client.ping()
            self._is_connected = True
            self._connection_error = None
            logger.info(f"[Redis] Connected to {params['host']}:{params['port']}")
            return self._sync_client

        except ConnectionError as e:
            self._connection_error = str(e)
            self._is_connected = False
            logger.warning(f"[Redis] Connection failed: {e}. Running without Redis.")
            return None

        except Exception as e:
            self._connection_error = str(e)
            self._is_connected = False
            logger.error(f"[Redis] Unexpected error: {e}")
            return None

    async def connect_async(self) -> Optional[AsyncRedis]:
        """
        Create async Redis connection.

        Returns None if Redis is disabled or connection fails.
        """
        if not self.enabled:
            logger.info("[Redis] Disabled by configuration")
            return None

        if self._async_client is not None:
            return self._async_client

        try:
            params = self._get_connection_params()
            self._async_client = AsyncRedis(**params)

            # Test connection
            await self._async_client.ping()
            self._is_connected = True
            self._connection_error = None
            logger.info(f"[Redis] Async connected to {params['host']}:{params['port']}")
            return self._async_client

        except ConnectionError as e:
            self._connection_error = str(e)
            self._is_connected = False
            logger.warning(f"[Redis] Async connection failed: {e}. Running without Redis.")
            return None

        except Exception as e:
            self._connection_error = str(e)
            self._is_connected = False
            logger.error(f"[Redis] Async unexpected error: {e}")
            return None

    async def close(self):
        """Close all Redis connections."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

        if self._async_client:
            await self._async_client.close()
            self._async_client = None

        self._is_connected = False
        logger.info("[Redis] Connections closed")

    # =========================================================================
    # Session Operations (Short-term Memory)
    # =========================================================================

    async def set_session(self, profile_id: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store session data for a profile.

        Args:
            profile_id: Profile identifier
            key: Session key
            value: Value to store (will be JSON encoded)
            ttl: TTL in seconds (uses default if not provided)

        Returns:
            True if stored, False if Redis unavailable
        """
        client = await self.connect_async()
        if not client:
            return False

        try:
            settings = get_settings()
            ttl = ttl or settings.redis_session_ttl
            session_key = f"session:{profile_id}:{key}"

            import json
            await client.setex(session_key, ttl, json.dumps(value))
            return True

        except RedisError as e:
            logger.error(f"[Redis] Set session error: {e}")
            return False

    async def get_session(self, profile_id: str, key: str) -> Optional[Any]:
        """
        Retrieve session data for a profile.

        Returns:
            Stored value or None if not found/unavailable
        """
        client = await self.connect_async()
        if not client:
            return None

        try:
            session_key = f"session:{profile_id}:{key}"
            value = await client.get(session_key)

            if value:
                import json
                return json.loads(value)
            return None

        except RedisError as e:
            logger.error(f"[Redis] Get session error: {e}")
            return None

    async def delete_session(self, profile_id: str, key: str) -> bool:
        """Delete session data."""
        client = await self.connect_async()
        if not client:
            return False

        try:
            session_key = f"session:{profile_id}:{key}"
            await client.delete(session_key)
            return True

        except RedisError as e:
            logger.error(f"[Redis] Delete session error: {e}")
            return False

    # =========================================================================
    # Agent Handoff Operations
    # =========================================================================

    async def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        profile_id: str,
        context: dict,
        task: str,
        reason: str,
    ) -> Optional[str]:
        """
        Create an agent handoff record.

        Args:
            from_agent: Source agent name
            to_agent: Target agent name
            profile_id: Profile being handed off
            context: Context data for the receiving agent
            task: Task description
            reason: Reason for handoff

        Returns:
            Handoff ID or None if failed
        """
        client = await self.connect_async()
        if not client:
            return None

        try:
            import json
            import uuid
            from datetime import datetime

            settings = get_settings()
            handoff_id = str(uuid.uuid4())
            handoff_key = f"handoff:{profile_id}:{to_agent}:{from_agent}"

            handoff_data = {
                "id": handoff_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "profile_id": profile_id,
                "context": context,
                "task": task,
                "reason": reason,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            }

            await client.setex(
                handoff_key,
                settings.redis_handoff_ttl,
                json.dumps(handoff_data)
            )

            logger.info(f"[Redis] Handoff created: {from_agent} -> {to_agent} for {profile_id}")
            return handoff_id

        except RedisError as e:
            logger.error(f"[Redis] Create handoff error: {e}")
            return None

    async def get_handoff(
        self,
        profile_id: str,
        to_agent: str,
        from_agent: Optional[str] = None
    ) -> Optional[dict]:
        """
        Get pending handoff for an agent.

        Returns:
            Handoff data or None if not found
        """
        client = await self.connect_async()
        if not client:
            return None

        try:
            import json

            if from_agent:
                handoff_key = f"handoff:{profile_id}:{to_agent}:{from_agent}"
                value = await client.get(handoff_key)
                if value:
                    return json.loads(value)
            else:
                # Search for any handoff to this agent
                pattern = f"handoff:{profile_id}:{to_agent}:*"
                keys = await client.keys(pattern)
                if keys:
                    value = await client.get(keys[0])
                    if value:
                        return json.loads(value)

            return None

        except RedisError as e:
            logger.error(f"[Redis] Get handoff error: {e}")
            return None

    async def acknowledge_handoff(
        self,
        profile_id: str,
        from_agent: str,
        to_agent: str
    ) -> bool:
        """
        Acknowledge (delete) a handoff after processing.
        """
        client = await self.connect_async()
        if not client:
            return False

        try:
            handoff_key = f"handoff:{profile_id}:{to_agent}:{from_agent}"
            await client.delete(handoff_key)
            logger.info(f"[Redis] Handoff acknowledged: {from_agent} -> {to_agent}")
            return True

        except RedisError as e:
            logger.error(f"[Redis] Acknowledge handoff error: {e}")
            return False

    # =========================================================================
    # Pub/Sub Operations
    # =========================================================================

    async def publish(self, channel: str, message: dict) -> bool:
        """
        Publish message to a channel.

        Args:
            channel: Channel name
            message: Message to publish (will be JSON encoded)

        Returns:
            True if published, False if failed
        """
        client = await self.connect_async()
        if not client:
            return False

        try:
            import json
            await client.publish(channel, json.dumps(message))
            return True

        except RedisError as e:
            logger.error(f"[Redis] Publish error: {e}")
            return False


# ============================================================================
# Singleton Instance
# ============================================================================

@lru_cache()
def get_redis_client() -> RedisClient:
    """Get singleton Redis client instance."""
    return RedisClient()


# Convenience accessor
redis_client = get_redis_client()


# ============================================================================
# Async Context Manager for FastAPI Lifespan
# ============================================================================

async def init_redis():
    """Initialize Redis connection. Call during app startup."""
    client = get_redis_client()
    await client.connect_async()

    if client.is_connected:
        logger.info("[Redis] Initialized successfully")
    else:
        logger.warning("[Redis] Running without Redis (disabled or connection failed)")


async def close_redis():
    """Close Redis connection. Call during app shutdown."""
    client = get_redis_client()
    await client.close()
