"""
Constants for the Conversational RAG service
"""

# Chat and conversation constants
DEFAULT_CONVERSATION_TTL = 3600  # 1 hour in seconds
MAX_CONVERSATION_HISTORY = 100   # Maximum messages to keep in memory
MAX_MESSAGE_LENGTH = 4000        # Maximum characters per message
MIN_MESSAGE_LENGTH = 1           # Minimum characters per message

# RAG constants
DEFAULT_SIMILARITY_THRESHOLD = 0.7
MAX_RETRIEVED_CHUNKS = 10
MIN_RETRIEVED_CHUNKS = 1
DEFAULT_MAX_CONTEXT_CHUNKS = 5
RAG_CONTEXT_SEPARATOR = "\n---\n"

# LLM constants
MAX_CONTEXT_TOKENS = {
    "gpt-3.5-turbo": 4096,
    "gpt-4": 8192,
    "claude-3-haiku": 200000,
    "claude-3-sonnet": 200000,
    "claude-3-opus": 200000,
    "default": 4000
}

MAX_OUTPUT_TOKENS = {
    "gpt-3.5-turbo": 1024,
    "gpt-4": 2048,
    "claude-3-haiku": 4096,
    "claude-3-sonnet": 4096,
    "claude-3-opus": 4096,
    "default": 1000
}

# Interview constants
INTERVIEW_TYPES = [
    "technical",
    "behavioral",
    "system_design",
    "coding",
    "general"
]

INTERVIEW_STATUSES = [
    "scheduled",
    "confirmed", 
    "in_progress",
    "completed",
    "cancelled",
    "no_show"
]

DEFAULT_INTERVIEW_DURATION = 60  # minutes
MIN_INTERVIEW_DURATION = 15      # minutes
MAX_INTERVIEW_DURATION = 180     # minutes
INTERVIEW_REMINDER_HOURS = 24    # hours before interview

# Email constants
EMAIL_TEMPLATES = {
    "interview_confirmation": {
        "subject": "Interview Scheduled - {position}",
        "priority": "high"
    },
    "interview_reminder": {
        "subject": "Interview Reminder - Tomorrow at {time}",
        "priority": "high"
    },
    "interview_cancellation": {
        "subject": "Interview Cancelled - {date} {time}",
        "priority": "normal"
    },
    "interview_update": {
        "subject": "Interview Update - {date} {time}",
        "priority": "normal"
    }
}

# Redis key patterns
REDIS_KEYS = {
    "conversation": "chat:conversation:{conversation_id}",
    "session": "chat:session:{session_id}", 
    "user_conversations": "chat:user:{user_id}:conversations",
    "analytics": "chat:analytics:{conversation_id}",
    "rate_limit": "chat:rate_limit:{identifier}"
}

# API response messages
RESPONSE_MESSAGES = {
    "conversation_created": "Conversation created successfully",
    "conversation_not_found": "Conversation not found",
    "conversation_cleared": "Conversation history cleared successfully",
    "message_sent": "Message sent successfully",
    "invalid_input": "Invalid input provided",
    "rate_limit_exceeded": "Rate limit exceeded. Please try again later",
    "interview_scheduled": "Interview scheduled successfully",
    "interview_cancelled": "Interview cancelled successfully", 
    "interview_updated": "Interview updated successfully",
    "email_sent": "Email notification sent successfully",
    "email_failed": "Failed to send email notification"
}

# Error codes
ERROR_CODES = {
    "INVALID_MESSAGE": "INVALID_MESSAGE",
    "CONVERSATION_NOT_FOUND": "CONVERSATION_NOT_FOUND",
    "RAG_SEARCH_FAILED": "RAG_SEARCH_FAILED",
    "LLM_ERROR": "LLM_ERROR",
    "MEMORY_ERROR": "MEMORY_ERROR",
    "INTERVIEW_BOOKING_FAILED": "INTERVIEW_BOOKING_FAILED",
    "EMAIL_SERVICE_ERROR": "EMAIL_SERVICE_ERROR",
    "RATE_LIMIT_EXCEEDED": "RATE_LIMIT_EXCEEDED",
    "AUTHENTICATION_FAILED": "AUTHENTICATION_FAILED",
    "VECTOR_SEARCH_ERROR": "VECTOR_SEARCH_ERROR"
}

# System prompts
SYSTEM_PROMPTS = {
    "default": """You are a helpful AI assistant with access to a knowledge base. 
You can help users with questions, provide information, and assist with various tasks.

Guidelines:
- Be helpful, accurate, and concise
- Use the provided context when relevant
- If you don't know something, say so honestly
- Maintain a professional but friendly tone
- For interview scheduling, be helpful and accommodating""",

    "interview_assistant": """You are an AI assistant specialized in helping with interview scheduling and career guidance.

Your capabilities include:
- Helping candidates schedule interviews
- Providing interview preparation advice
- Answering questions about the interview process
- Assisting with rescheduling when needed

Guidelines:
- Be professional and supportive
- Ask clarifying questions when needed
- Provide clear next steps
- Be accommodating with scheduling requests""",

    "technical_support": """You are a technical support AI assistant with access to documentation and knowledge base.

Your role:
- Help users troubleshoot technical issues
- Provide step-by-step guidance
- Reference relevant documentation
- Escalate complex issues when appropriate

Guidelines:
- Be precise and technical when needed
- Break down complex solutions into steps
- Ask for additional details when necessary
- Provide alternative solutions when possible"""
}

# Logging configuration
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20, 
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# Rate limiting
RATE_LIMITS = {
    "messages_per_minute": 60,
    "messages_per_hour": 1000,
    "conversations_per_day": 100,
    "api_calls_per_minute": 100
}

# Vector search constants
VECTOR_SEARCH = {
    "default_collection": "documents",
    "embedding_dimension": 384,  # for sentence-transformers/all-MiniLM-L6-v2
    "distance_metric": "cosine",
    "search_timeout": 30,  # seconds
    "max_search_results": 50
}

# Performance settings
PERFORMANCE = {
    "response_timeout": 30,      # seconds
    "llm_timeout": 25,           # seconds  
    "vector_search_timeout": 10, # seconds
    "redis_timeout": 5,          # seconds
    "email_timeout": 15,         # seconds
    "max_concurrent_requests": 100
}