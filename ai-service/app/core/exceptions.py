from fastapi import HTTPException, status

class AIServiceException(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str = "AI_SERVICE_ERROR"):
        super().__init__(status_code=status_code, detail={"code": code, "message": detail})
        self.code = code
        self.message = detail

class AuthenticationError(AIServiceException):
    def __init__(self, detail: str = "Invalid internal service credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code="UNAUTHORIZED")

class PermissionDeniedError(AIServiceException):
    def __init__(self, detail: str = "Access to requested document or resource is denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="FORBIDDEN")

class DocumentNotFoundError(AIServiceException):
    def __init__(self, detail: str = "Document not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, code="NOT_FOUND")

class DocumentParsingError(AIServiceException):
    def __init__(self, detail: str = "Failed to parse document text or page structure"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail, code="PARSING_ERROR")

class CorruptDocumentError(AIServiceException):
    def __init__(self, detail: str = "Document is corrupted, truncated, or invalid"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code="CORRUPT_DOCUMENT")

class EmbeddingError(AIServiceException):
    def __init__(self, detail: str = "Failed to compute vector embeddings"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail, code="EMBEDDING_ERROR")

class RetrievalError(AIServiceException):
    def __init__(self, detail: str = "Vector similarity search failed"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail, code="RETRIEVAL_ERROR")

class LLMGenerationError(AIServiceException):
    def __init__(self, detail: str = "LLM inference call failed"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail, code="LLM_GENERATION_ERROR")

class ToolExecutionError(AIServiceException):
    def __init__(self, detail: str = "Agent tool execution failed"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code="TOOL_EXECUTION_ERROR")

