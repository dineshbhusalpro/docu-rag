from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator

def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class DocumentModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    filename: str
    file_path: str
    file_size: int
    content: str
    chunks: List[Dict[str, Any]] = []
    status: str = "processing"  # processing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }