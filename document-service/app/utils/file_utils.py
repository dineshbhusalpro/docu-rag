import os
import aiofiles
from fastapi import UploadFile, HTTPException
from pathlib import Path
from app.config import settings

class FileUtils:
    def __init__(self):
        # Create upload directory
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        # Check file size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Check file extension
        allowed_extensions = ['.pdf', '.txt', '.docx']
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not supported")

    async def save_file(self, file: UploadFile) -> str:
        """Save uploaded file"""
        import uuid
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path