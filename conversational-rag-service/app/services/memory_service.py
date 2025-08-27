from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from app.database import get_redis
from app.config import settings
from app.models.conversation_model import ChatMessage
import logging

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self):
        self.redis_prefix = settings.REDIS_CHAT_PREFIX
        self.session_ttl = settings.REDIS_SESSION_TTL

    async def store_message(self, message: ChatMessage) -> bool:
        """Store a chat message in Redis"""
        try:
            redis_client = get_redis()
            key = f"{self.redis_prefix}{message.conversation_id}"
            
            # Serialize message
            message_data = {
                "message_id": message.message_id,
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "retrieved_chunks": message.retrieved_chunks,
                "metadata": message.metadata
            }
            
            # Add to conversation history (list)
            await redis_client.lpush(key, json.dumps(message_data))
            
            # Set TTL for the conversation
            await redis_client.expire(key, self.session_ttl)
            
            logger.info(f"Stored message {message.message_id} in conversation {message.conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return False

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get conversation history from Redis"""
        try:
            redis_client = get_redis()
            key = f"{self.redis_prefix}{conversation_id}"
            
            # Get messages (LRANGE gets in reverse order - newest first)
            messages_json = await redis_client.lrange(key, offset, offset + limit - 1)
            
            messages = []
            for msg_json in messages_json:
                try:
                    message_data = json.loads(msg_json)
                    message_data["timestamp"] = datetime.fromisoformat(message_data["timestamp"])
                    messages.append(message_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse message JSON: {e}")
                    continue
            
            # Reverse to get chronological order
            messages.reverse()
            
            logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def get_recent_context(
        self,
        conversation_id: str,
        max_messages: int = 10,
        max_tokens: int = 2000
    ) -> str:
        """Get recent conversation context for RAG"""
        try:
            messages = await self.get_conversation_history(conversation_id, limit=max_messages)
            
            # Build context string
            context_parts = []
            current_tokens = 0
            
            for message in reversed(messages):  # Start from most recent
                role = message["role"]
                content = message["content"]
                
                # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                message_tokens = len(f"{role}: {content}") // 4
                
                if current_tokens + message_tokens > max_tokens:
                    break
                
                context_parts.append(f"{role}: {content}")
                current_tokens += message_tokens
            
            # Reverse to get chronological order
            context_parts.reverse()
            context = "\n".join(context_parts)
            
            logger.info(f"Built context with {len(context_parts)} messages ({current_tokens} tokens)")
            return context
            
        except Exception as e:
            logger.error(f"Error building recent context: {e}")
            return ""

    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history"""
        try:
            redis_client = get_redis()
            key = f"{self.redis_prefix}{conversation_id}"
            
            result = await redis_client.delete(key)
            logger.info(f"Cleared conversation {conversation_id}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False

    async def get_active_conversations(self, limit: int = 50) -> List[str]:
        """Get list of active conversation IDs"""
        try:
            redis_client = get_redis()
            pattern = f"{self.redis_prefix}*"
            
            keys = await redis_client.keys(pattern)
            conversation_ids = [key.replace(self.redis_prefix, "") for key in keys]
            
            return conversation_ids[:limit]
            
        except Exception as e:
            logger.error(f"Error getting active conversations: {e}")
            return []