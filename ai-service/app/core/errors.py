from fastapi import HTTPException, status

class AIServiceException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class DocumentParsingError(AIServiceException):
    def __init__(self, detail: str = "Failed to parse document"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class EmbeddingGenerationError(AIServiceException):
    def __init__(self, detail: str = "Failed to generate embeddings"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

class VectorStoreError(AIServiceException):
    def __init__(self, detail: str = "Vector database operation failed"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)

