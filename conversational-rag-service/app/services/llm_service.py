from typing import List, Optional
import openai
import anthropic
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self._setup_clients()

    def _setup_clients(self):
        """Initialize LLM clients based on provider"""
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
        else:
            logger.warning(f"No valid API key found for provider: {self.provider}")

    async def generate_response(
        self,
        user_message: str,
        conversation_context: str = "",
        rag_context: str = ""
    ) -> str:
        """Generate response using the configured LLM"""
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(rag_context)
            
            # Build messages for the conversation
            messages = []
            
            # Add system message
            messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation context if available
            if conversation_context:
                messages.append({"role": "system", "content": f"Previous conversation:\n{conversation_context}"})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response based on provider
            if self.provider == "openai":
                return await self._generate_openai_response(messages)
            elif self.provider == "anthropic":
                return await self._generate_anthropic_response(messages)
            else:
                return "I'm sorry, but I'm not properly configured to respond right now."
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "I apologize, but I encountered an error while processing your request. Please try again."

    def _build_system_prompt(self, rag_context: str = "") -> str:
        """Build system prompt for the assistant"""
        base_prompt = """You are a helpful AI assistant with access to a knowledge base. 
You can help users with questions, provide information, and assist with various tasks.

Guidelines:
- Be helpful, accurate, and concise
- Use the provided context when relevant
- If you don't know something, say so honestly
- Maintain a professional but friendly tone
- For interview scheduling, be helpful and accommodating"""

        if rag_context:
            base_prompt += f"\n\nRelevant information from knowledge base:\n{rag_context}"

        return base_prompt

    async def _generate_openai_response(self, messages: List[dict]) -> str:
        """Generate response using OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _generate_anthropic_response(self, messages: List[dict]) -> str:
        """Generate response using Anthropic API"""
        try:
            # Convert messages format for Anthropic
            system_messages = [msg["content"] for msg in messages if msg["role"] == "system"]
            user_messages = [msg for msg in messages if msg["role"] != "system"]
            
            system_prompt = "\n\n".join(system_messages)
            
            response = await self.anthropic_client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=user_messages,
                max_tokens=800,
                temperature=0.7
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get text embedding for RAG (using OpenAI embeddings)"""
        try:
            if not settings.OPENAI_API_KEY:
                logger.warning("No OpenAI API key available for embeddings")
                return None
                
            response = await openai.Embedding.acreate(
                model="text-embedding-ada-002",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None