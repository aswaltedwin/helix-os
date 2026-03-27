import redis
import json
from typing import Optional, Dict, Any
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

class AgentMemory:
    """Short-term memory layer for agents using Redis"""
    
    @staticmethod
    def store_context(agent_id: str, context: Dict[str, Any], ttl: int = 86400):
        """Store agent context in Redis (24h default TTL)"""
        key = f"agent:{agent_id}:context"
        redis_client.setex(
            key,
            ttl,
            json.dumps(context)
        )
    
    @staticmethod
    def get_context(agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent context from Redis"""
        key = f"agent:{agent_id}:context"
        data = redis_client.get(key)
        return json.loads(data) if data else {}
    
    @staticmethod
    def store_conversation(agent_id: str, messages: list, ttl: int = 3600):
        """Store conversation history (1h default TTL)"""
        key = f"agent:{agent_id}:conversation"
        redis_client.setex(
            key,
            ttl,
            json.dumps(messages)
        )
    
    @staticmethod
    def get_conversation(agent_id: str) -> list:
        """Retrieve conversation history"""
        key = f"agent:{agent_id}:conversation"
        data = redis_client.get(key)
        return json.loads(data) if data else []