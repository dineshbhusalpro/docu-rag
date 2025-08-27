from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.services.vector_service import VectorService
from app.services.memory_service import MemoryService
from app.services.llm_service import LLMService
from app.models.conversation_model import ChatMessage
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.vector_service = VectorService()
        self.memory_service = MemoryService()
        self.llm_service = LLMService()

    async def process_chat_message(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        use_rag: bool = True,
        max_context_chunks: int = 5
    ) -> Dict[str, Any]:
        """Process a chat message with RAG capabilities"""
        start_time = datetime.utcnow()
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        try:
            # Store user message
            user_msg = ChatMessage(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                timestamp=datetime.utcnow()
            )
            await self.memory_service.store_message(user_msg)
            
            # Get conversation context
            conversation_context = await self.memory_service.get_recent_context(
                conversation_id, 
                max_messages=10,
                max_tokens=1500
            )
            
            retrieved_chunks = []
            total_chunks_found = 0
            
            if use_rag:
                # Get query embedding for semantic search
                query_embedding = await self.llm_service.get_embedding(user_message)
                
                if query_embedding:
                    # Search for relevant chunks
                    retrieved_chunks = self.vector_service.search_similar_chunks(
                        query_embedding=query_embedding,
                        document_ids=document_ids,
                        limit=max_context_chunks,
                        score_threshold=settings.SIMILARITY_THRESHOLD
                    )
                    total_chunks_found = len(retrieved_chunks)
            
            # Build context for LLM
            rag_context = ""
            if retrieved_chunks:
                rag_context = "\n\n".join([
                    f"Document {chunk['document_id']} (Score: {chunk['score']:.3f}):\n{chunk['content']}"
                    for chunk in retrieved_chunks
                ])
            
            # Generate response using LLM
            assistant_response = await self.llm_service.generate_response(
                user_message=user_message,
                conversation_context=conversation_context,
                rag_context=rag_context
            )
            
            # Store assistant response
            assistant_msg = ChatMessage(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_response,
                timestamp=datetime.utcnow(),
                retrieved_chunks=retrieved_chunks
            )
            await self.memory_service.store_message(assistant_msg)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = {
                "message_id": assistant_msg.message_id,
                "conversation_id": conversation_id,
                "response": assistant_response,
                "retrieved_chunks": retrieved_chunks,
                "total_chunks_found": total_chunks_found,
                "processing_time_ms": int(processing_time),
                "timestamp": assistant_msg.timestamp
            }
            
            logger.info(f"Processed chat message in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            raise Exception(f"Failed to process chat message: {str(e)}")

    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Generate a summary of the conversation"""
        try:
            messages = await self.memory_service.get_conversation_history(conversation_id)
            
            if not messages:
                return {"error": "No conversation history found"}
            
            # Basic statistics
            total_messages = len(messages)
            user_messages = [msg for msg in messages if msg["role"] == "user"]
            assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
            
            # Calculate duration
            first_msg = messages[0] if messages else None
            last_msg = messages[-1] if messages else None
            
            duration_minutes = 0
            if first_msg and last_msg:
                start_time = first_msg["timestamp"]
                end_time = last_msg["timestamp"]
                duration_minutes = (end_time - start_time).total_seconds() / 60
            
            # Extract referenced documents
            referenced_docs = set()
            for message in assistant_messages:
                chunks = message.get("retrieved_chunks", [])
                for chunk in chunks:
                    if chunk.get("document_id"):
                        referenced_docs.add(chunk["document_id"])
            
            return {
                "conversation_id": conversation_id,
                "total_messages": total_messages,
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "duration_minutes": round(duration_minutes, 2),
                "documents_referenced": list(referenced_docs),
                "first_message_time": first_msg["timestamp"] if first_msg else None,
                "last_message_time": last_msg["timestamp"] if last_msg else None
            }
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return {"error": str(e)}