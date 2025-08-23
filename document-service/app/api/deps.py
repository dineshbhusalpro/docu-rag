from app.services.document_service import DocumentService

def get_document_service() -> DocumentService:
    return DocumentService()