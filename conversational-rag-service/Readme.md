# Conversational RAG API Service

Advanced conversational AI service with RAG capabilities and interview booking functionality.

## Features

- **Multi-turn Conversations** with Redis-based memory
- **RAG Integration** with Qdrant vector search
- **Multiple LLM Providers** (OpenAI, Anthropic, HuggingFace)
- **Interview Booking System** with email notifications
- **Chat Memory Management** with conversation persistence
- **Email Service** with Gmail SMTP integration

## Quick Start

### Prerequisites

Start Redis and Qdrant:
```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:7.2-alpine

# Start Qdrant  
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:v1.7.4
```
# Configuration
## Create .env file:
```env
# LLM Provider (openai, anthropic, huggingface)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=documents

# Chat Memory
REDIS_URL=redis://localhost:6379
REDIS_SESSION_TTL=3600

# Email Service (Gmail SMTP)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# RAG Settings
SIMILARITY_THRESHOLD=0.7
MAX_RETRIEVED_CHUNKS=5
MAX_CONTEXT_LENGTH=4000
```

# Installation & Running

## Install dependencies:

```bash 
pip install -r requirements.txt
```
## Run the service:

```bash 
uvicorn app.main:app --reload --port 8001
```

## Access API docs: 
http://localhost:8001/docs

# Using Docker
```bash
# Build the service
docker build -t conversational-rag-service . --no-cache
```

## Run the service
```bash
docker run -d --name conversational-rag-service -p 8001:8001 \
  -e OPENAI_API_KEY=your-key \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  -e QDRANT_HOST=host.docker.internal \
  conversational-rag-service
```

# API Endpoints
## Chat Endpoints

POST /api/v1/chat/chat - Send message with RAG.  
GET /api/v1/chat/conversations - List active conversations.   
GET /api/v1/chat/conversations/{id} - Get conversation history.   
DELETE /api/v1/chat/conversations/{id} - Clear conversation.   
GET /api/v1/chat/conversations/{id}/summary - Get conversation summary.   

## Interview Endpoints

POST /api/v1/interviews/book - Book new interview.   
GET /api/v1/interviews/ - List interviews.   
GET /api/v1/interviews/{id} - Get interview details.   
PUT /api/v1/interviews/{id} - Update interview.   
DELETE /api/v1/interviews/{id} - Cancel interview.   
GET /api/v1/interviews/upcoming/list - Get upcoming interviews.   
POST /api/v1/interviews/reminders/send - Send reminders.   

# Usage Examples
## Chat with RAG
```bash
curl -X POST "http://localhost:8001/api/v1/chat/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": true,
    "max_context_chunks": 5
  }'
```
## Book Interview
```bash
curl -X POST "http://localhost:8001/api/v1/interviews/book" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_email": "candidate@example.com",
    "candidate_name": "John Doe",
    "preferred_date": "2024-01-15T10:00:00Z",
    "interview_type": "technical",
    "position": "Software Engineer",
    "duration_minutes": 60
  }'
```
## Multi-turn Conversation
```bash
# First message
curl -X POST "http://localhost:8001/api/v1/chat/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I want to learn about AI"}'

# Follow-up message (use conversation_id from response)
curl -X POST "http://localhost:8001/api/v1/chat/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you tell me more about neural networks?",
    "conversation_id": "your-conversation-id-here"
  }'
```
# Architecture
## Chat Memory

Redis-based storage for conversation history.  
Configurable TTL for session management.   
Context building for multi-turn conversations.   

## RAG Pipeline

Query Processing - Extract user intent.   
Vector Search - Find relevant document chunks.   
Context Assembly - Combine search results with conversation history.   
Response Generation - Generate contextual response using LLM.   

## Interview System

Email Integration with confirmation, reminders, and cancellations.   
Flexible scheduling with timezone support.   
Status tracking throughout interview lifecycle.   

## Environment Variables
| Variable               | Required | Default                  | Description                                  |
|------------------------|----------|--------------------------|----------------------------------------------|
| LLM_PROVIDER           | Yes      | openai                   | LLM provider (openai/anthropic/huggingface) |
| OPENAI_API_KEY         | If using OpenAI | -                 | OpenAI API key                               |
| ANTHROPIC_API_KEY      | If using Anthropic | -             | Anthropic API key                            |
| REDIS_URL              | Yes      | redis://localhost:6379   | Redis connection URL                         |
| QDRANT_HOST            | Yes      | localhost                | Qdrant host                                  |
| QDRANT_PORT            | No       | 6333                     | Qdrant port                                  |
| SMTP_USERNAME          | For emails | -                      | Gmail username                               |
| SMTP_PASSWORD          | For emails | -                      | Gmail app password                            |
| SIMILARITY_THRESHOLD   | No       | 0.7                      | RAG similarity threshold                      |
| MAX_RETRIEVED_CHUNKS   | No       | 5                        | Maximum chunks to retrieve                   |

# Troubleshooting
## Connection Issues

Ensure Redis and Qdrant are running and accessible
Check firewall settings for ports 6379 (Redis) and 6333 (Qdrant).   
Verify API keys are correctly set in environment

## Email Issues

Use Gmail App Passwords instead of regular password.   
Enable 2-factor authentication on Gmail account.   
Check SMTP credentials and server settings.   

## RAG Issues

Verify Qdrant collection exists and has documents.   
Check vector embedding dimensions match.   
Adjust similarity threshold if no results found.   

## Performance Tips

Redis Memory: Configure appropriate memory limits.   
Context Length: Tune max context length based on your LLM limits.   
Chunk Size: Optimize chunk size for your use case.   
Connection Pooling: Use connection pooling for production.   

# Clean Up
````bash
docker stop conversational-rag-service redis qdrant
docker rm conversational-rag-service redis qdrant
````


# ✅ **Key Features Implemented:**

### **🤖 Advanced RAG Capabilities:**
- Multi-turn conversations with Redis memory
- Vector search integration with Qdrant  
- Multiple LLM providers (OpenAI, Anthropic, HuggingFace)
- Intelligent context building and retrieval

### **📅 Interview Booking System:**
- Complete interview lifecycle management
- Email notifications (confirmation, reminders, cancellations)
- Gmail SMTP integration
- Flexible scheduling with timezone support

### **💬 Chat Memory Management:**
- Redis-based conversation persistence
- Configurable session TTL
- Conversation history and summaries
- Context optimization for LLM limits

### **🏗️ Clean Architecture:**
- Proper separation of concerns (models, schemas, services, routes)
- Async throughout for high performance
- Comprehensive error handling and logging
- Docker containerization ready

### **📧 Email Service:**
- Professional email templates
- HTML and text versions
- Interview confirmations and reminders
- Status update notifications

This microservice is completely independent and can run alongside the document service. It provides the conversational AI layer that can interact with the documents processed by the document service through the shared Qdrant vector database!