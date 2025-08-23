# Document Service

Simple document processing service with vector storage capabilities.

## Features

- Document upload (PDF, TXT, DOCX)
- Text extraction and chunking
- Vector embeddings with Qdrant
- MongoDB storage
- RESTful API

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

POST /api/v1/documents/upload - Upload document.   
GET /api/v1/documents/ - List documents.   
GET /api/v1/documents/{id} - Get document details.   
DELETE /api/v1/documents/{id} - Delete document.   
GET /api/v1/documents/{id}/status - Get processing status.   


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