from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class DocumentUpload(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 200

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    status: str
    created_at: datetime
    total_chunks: int = 0

class DocumentDetail(DocumentResponse):
    content_preview: str
    chunks: List[Dict[str, Any]]

class DocumentList(BaseModel):
    documents: List[DocumentResponse]
    total: int