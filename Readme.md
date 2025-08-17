# Docu-RAG

## Introduction
Docu-RAG is a backend system that provides document ingestion and conversational RAG capabilities with interview booking functionality. The system processes PDF and text documents, generates embeddings, and enables multi-turn conversations with integrated chat memory and email notifications.

## Technical Stack
- **Framework:** FastAPI
- **Vector Database:** Qdrant
- **Metadata Storage:** MongoDB
- **Chat Memory:** Redis
- **Embeddings:** Local (sentence-transformers) or HuggingFace API
- **Authentication:** Token-based with API Gateway rate limiting
- **Email Service:** Gmail SMTP

## System Design
**Document Ingestion API:** Handles file upload (.pdf/.txt), text extraction, dual chunking strategies (fixed-size and semantic), embedding generation, and vector storage with metadata persistence.

**Conversational RAG API:** Implements custom RAG without RetrievalQAChain, manages multi-turn conversations with Redis memory, supports interview booking functionality, and sends email confirmations.