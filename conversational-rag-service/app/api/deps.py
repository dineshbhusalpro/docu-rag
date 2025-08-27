from typing import Generator
from app.services.rag_service import RAGService
from app.services.interview_service import InterviewService
from app.services.memory_service import MemoryService
from app.services.vector_service import VectorService
from app.services.email_service import EmailService

def get_rag_service() -> RAGService:
    """Dependency for RAG service"""
    return RAGService()

def get_interview_service() -> InterviewService:
    """Dependency for interview service"""
    return InterviewService()

def get_memory_service() -> MemoryService:
    """Dependency for memory service"""
    return MemoryService()

def get_vector_service() -> VectorService:
    """Dependency for vector service"""
    return VectorService()

def get_email_service() -> EmailService:
    """Dependency for email service"""
    return EmailService()