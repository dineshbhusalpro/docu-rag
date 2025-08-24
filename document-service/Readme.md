# Document Service

Simple document processing service with vector storage capabilities.

## Features

- **Document Upload:** PDF, TXT, DOCX support
- **Advanced Text Processing:** 5 intelligent chunking strategies
- **Flexible Embeddings:** Local models or HuggingFace API
- **Vector Storage:** Qdrant integration for semantic search
- **MongoDB Storage:** Document metadata and chunk information
- **RESTful API:** Comprehensive endpoints with detailed analytics

## Quick Start

### Prerequisites

 Start MongoDB and Qdrant:
```bash
# Start MongoDB
docker run -d --name mongo -p 27017:27017 mongo:7.0

# Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:v1.7.4
```
# Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Create uploads directory:
```bash
mkdir uploads
```

3. Run the service:
```bash
uvicorn app.main:app --reload
```

# Using Docker

1. Build the service:
```bash
docker build -t document-service . --no-cache
```
2. Run the service:
```bash
docker run -d --name document-service -p 8000:8000 \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  -e QDRANT_HOST=host.docker.internal \
  -v $(pwd)/uploads:/app/uploads \
  document-service
```
# API docs
http://localhost:8000/docs

# API Endpoints
## Document Management

POST /api/v1/documents/upload - Upload document with chunking strategy.  
GET /api/v1/documents/ - List documents with pagination.   
GET /api/v1/documents/{id} - Get document details and chunks.   
DELETE /api/v1/documents/{id} - Delete document and cleanup.   
GET /api/v1/documents/{id}/status - Check processing status

## Analytics & Statistics

GET /api/v1/documents/{id}/stats - Detailed chunking statistics    
GET /api/v1/documents/{id}/chunks/{index} - Individual chunk analysis.   
GET /api/v1/documents/strategies/available - List chunking strategies.   

## Debug & Monitoring

GET /api/v1/documents/debug/system-info - System capabilities.       
POST /api/v1/documents/debug/simple-upload - Basic upload test


# Environment Variables
Create a .env file:
```env
MONGODB_URL=mongodb://localhost:27017
QDRANT_HOST=localhost
QDRANT_PORT=6333
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
```
# Testing
Upload a document:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-document.pdf"
```
# Clean Up
Stop and remove containers:
```bash
docker stop document-service mongo qdrant
docker rm document-service mongo qdrant
```


## Chunking Strategies

### 1. **Fixed-Size Chunking** (`fixed`)
- **Method:** Character-based splitting with configurable overlap
- **Best For:** General purpose, consistent chunk sizes
- **Parameters:** `chunk_size`, `chunk_overlap`
- **Features:** Smart sentence boundary detection

### 2. **Sentence-Based Chunking** (`sentence`)
- **Method:** Respects sentence boundaries using NLTK tokenization
- **Best For:** Maintaining sentence integrity and readability
- **Parameters:** `target_size`, `overlap`
- **Features:** Preserves sentence completeness, intelligent overlap

### 3. **Semantic Chunking** (`semantic`)
- **Method:** Groups sentences by semantic similarity using embeddings + clustering
- **Best For:** Maintaining topical coherence, excellent for Q&A systems
- **Parameters:** `max_chunks`
- **Features:** Semantic coherence scoring, topic-aware grouping

### 4. **Paragraph-Based Chunking** (`paragraph`)
- **Method:** Splits by paragraph boundaries while respecting size limits
- **Best For:** Formal documents, maintaining document structure
- **Parameters:** `target_size`, `overlap`
- **Features:** Document structure preservation, smart paragraph handling

### 5. **Hybrid Chunking** (`hybrid`)
- **Method:** Combines semantic clustering with size-based splitting
- **Best For:** Best of both worlds - semantic coherence + size control
- **Parameters:** `chunk_size`, `chunk_overlap`
- **Features:** Intelligent fallbacks, optimal chunk sizing

## Embedding Options
### **HuggingFace API Embeddings (Default)**
- **Model:** Same model via HuggingFace Inference API
- **Memory:** Zero additional RAM usage
- **Pros:** No memory overhead, always latest model, no local setup
- **Cons:** Requires internet, API key, rate limits apply

### **Local Embeddings **
- **Model:** sentence-transformers/all-MiniLM-L6-v2
- **Memory:** ~400MB RAM required
- **Pros:** No API dependencies, no rate limits, faster after initial load
- **Cons:** High memory usage, initial loading time


## Configuration Options

### HuggingFace API (Recommended for memory-constrained environments)

Get HuggingFace API Key.   
Visit: https://huggingface.co/settings/tokens.    
Create new token with "Read" permissions

Copy token to your .env file

```env
# Embedding Configuration
USE_HUGGINGFACE_API=true
HUGGINGFACE_API_KEY=hf_your_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
API_EMBEDDING_MODEL_URL=https://router.huggingface.co/hf-inference/models/{model}/pipeline/feature-extraction
```

# Troubleshooting
## Memory Issues

Use HuggingFace API instead of local embeddings
Reduce chunk_size parameter for smaller chunks
Use fixed or paragraph strategies instead of semantic

## API Issues

Verify HuggingFace API key is valid
Check internet connectivity
Monitor API rate limits

## Processing Failures

Check document format compatibility
Verify database connections (MongoDB, Qdrant)
Use debug endpoints to isolate issues

# Performance Tips

HuggingFace API: Best for memory-constrained environments
Local Models: Best for high-throughput, offline processing
Semantic Chunking: Use for documents where topic coherence matters.   
Fixed Chunking: Use for consistent, predictable chunk sizes
Hybrid Strategy: Best balance of semantic coherence and size control


# Documentation
Auto-generated at /docs endpoint