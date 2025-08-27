from typing import List, Dict, Any, Optional, Tuple
import re
import json
from datetime import datetime
from app.config import settings

class LLMUtils:
    """Utility functions for LLM operations"""
    
    @staticmethod
    def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
        """Estimate token count for a given text"""
        # Simple approximation: 1 token ≈ 4 characters for most models
        # This is a rough estimate - for production, use tiktoken or similar
        if model.startswith("gpt"):
            return len(text) // 4
        elif model.startswith("claude"):
            return len(text) // 4  # Similar tokenization
        else:
            return len(text.split())  # Word count for other models

    @staticmethod
    def truncate_context(
        text: str, 
        max_tokens: int, 
        model: str = "gpt-3.5-turbo"
    ) -> str:
        """Truncate text to fit within token limit"""
        current_tokens = LLMUtils.count_tokens(text, model)
        
        if current_tokens <= max_tokens:
            return text
        
        # Estimate characters to keep
        chars_per_token = len(text) / current_tokens
        target_chars = int(max_tokens * chars_per_token * 0.9)  # 10% buffer
        
        # Try to cut at sentence boundaries
        sentences = text.split('. ')
        truncated = ""
        
        for sentence in sentences:
            test_text = truncated + sentence + ". "
            if LLMUtils.count_tokens(test_text, model) > max_tokens:
                break
            truncated = test_text
        
        return truncated.strip()

    @staticmethod
    def build_rag_prompt(
        user_message: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_context: str = ""
    ) -> str:
        """Build a prompt with RAG context"""
        
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            content = chunk.get("content", "")
            score = chunk.get("score", 0.0)
            doc_id = chunk.get("document_id", "unknown")
            
            context_parts.append(
                f"[Context {i} - Document {doc_id} - Relevance: {score:.3f}]\n{content}"
            )
        
        rag_context = "\n\n".join(context_parts)
        
        # Build the full prompt
        prompt_parts = []
        
        if rag_context:
            prompt_parts.append("Relevant information from knowledge base:")
            prompt_parts.append(rag_context)
            prompt_parts.append("")
        
        if conversation_context:
            prompt_parts.append("Previous conversation:")
            prompt_parts.append(conversation_context)
            prompt_parts.append("")
        
        prompt_parts.append(f"User question: {user_message}")
        
        return "\n".join(prompt_parts)

    @staticmethod
    def extract_metadata_from_response(response: str) -> Dict[str, Any]:
        """Extract metadata from LLM response"""
        metadata = {
            "word_count": len(response.split()),
            "character_count": len(response),
            "sentence_count": len([s for s in response.split('.') if s.strip()]),
            "has_code": bool(re.search(r'```|`[^`]+`', response)),
            "has_urls": bool(re.search(r'https?://\S+', response)),
            "has_lists": bool(re.search(r'^\s*[-*+]\s+', response, re.MULTILINE)),
            "confidence_indicators": []
        }
        
        # Check for confidence indicators
        confidence_phrases = [
            "I think", "probably", "might", "could be", "perhaps",
            "I'm not sure", "uncertain", "likely", "possibly"
        ]
        
        for phrase in confidence_phrases:
            if phrase.lower() in response.lower():
                metadata["confidence_indicators"].append(phrase)
        
        return metadata

    @staticmethod
    def validate_llm_response(response: str, min_length: int = 10) -> Tuple[bool, str]:
        """Validate LLM response quality"""
        if not response or not response.strip():
            return False, "Empty response"
        
        if len(response.strip()) < min_length:
            return False, f"Response too short (min {min_length} characters)"
        
        # Check for common error patterns
        error_patterns = [
            r"I apologize.*error",
            r"something went wrong",
            r"unable to process",
            r"system error",
            r"internal error"
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return False, "Response indicates an error"
        
        return True, "Valid response"

    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """Sanitize user input for LLM safety"""
        # Remove potential prompt injection attempts
        dangerous_patterns = [
            r"ignore previous instructions",
            r"forget everything above",
            r"act as.*assistant",
            r"roleplay as",
            r"pretend you are"
        ]
        
        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)
        
        # Limit length
        if len(sanitized) > 4000:
            sanitized = sanitized[:4000] + "... [TRUNCATED]"
        
        return sanitized

    @staticmethod
    def format_conversation_history(
        messages: List[Dict[str, Any]], 
        max_messages: int = 10
    ) -> str:
        """Format conversation history for context"""
        if not messages:
            return ""
        
        # Take the most recent messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        formatted_lines = []
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            # Format timestamp if available
            time_str = ""
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        dt = timestamp
                    time_str = f" [{dt.strftime('%H:%M')}]"
                except:
                    pass
            
            formatted_lines.append(f"{role.title()}{time_str}: {content}")
        
        return "\n".join(formatted_lines)

    @staticmethod
    def get_model_limits(model: str) -> Dict[str, int]:
        """Get context and output limits for different models"""
        model_limits = {
            "gpt-3.5-turbo": {"context": 4096, "output": 1024},
            "gpt-3.5-turbo-16k": {"context": 16384, "output": 4096},
            "gpt-4": {"context": 8192, "output": 2048},
            "gpt-4-32k": {"context": 32768, "output": 8192},
            "claude-3-haiku-20240307": {"context": 200000, "output": 4096},
            "claude-3-sonnet-20240229": {"context": 200000, "output": 4096},
            "claude-3-opus-20240229": {"context": 200000, "output": 4096},
            "default": {"context": 4000, "output": 1000}
        }
        
        return model_limits.get(model, model_limits["default"])