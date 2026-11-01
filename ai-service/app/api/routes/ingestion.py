import time
from fastapi import APIRouter, Depends, status
from app.schemas.documents import IngestDocumentRequest, IngestDocumentResponse
from app.security.permissions import verify_internal_key
from app.security.input_validation import validate_safe_storage_path
from app.services.document_parser import document_parser
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service
from app.repositories.vector_repository import vector_repository
from app.core.logging import logger

router = APIRouter(prefix="/internal/v1", tags=["Ingestion"])

async def process_document_ingestion(request: IngestDocumentRequest) -> IngestDocumentResponse:
    start_time = time.time()
    logger.info(f"Ingesting document: {request.document_id} for user: {request.user_id}")

    # 1. Validate storage path
    safe_path = validate_safe_storage_path(request.storage_path)

    # 2. Parse PDF pages
    pages, is_scanned = document_parser.parse_pdf(safe_path)

    # 3. Chunk text preserving page references
    chunks = chunking_service.chunk_pages(
        pages=pages,
        document_id=request.document_id,
        user_id=request.user_id,
        document_name=request.document_name
    )

    # 4. Generate batch embeddings if chunks exist
    if chunks:
        texts = [c.content for c in chunks]
        embeddings = await embedding_service.compute_embeddings(texts)

        # 5. Idempotent persistence in vector repository
        await vector_repository.save_chunks_with_embeddings(chunks=chunks, embeddings=embeddings)
    else:
        logger.warn(f"Document {request.document_id} yielded 0 chunks")

    duration_ms = int((time.time() - start_time) * 1000)

    return IngestDocumentResponse(
        document_id=request.document_id,
        status="ready",
        total_pages=len(pages),
        total_chunks=len(chunks),
        processing_duration_ms=duration_ms,
        embedding_model=embedding_service.model_name,
        embedding_dimension=embedding_service.dimension,
        is_scanned=is_scanned
    )

@router.post("/ingest", response_model=IngestDocumentResponse, status_code=status.HTTP_200_OK)
async def ingest_document(
    request: IngestDocumentRequest,
    authorized: bool = Depends(verify_internal_key)
):
    return await process_document_ingestion(request)

@router.post("/rag/index", response_model=IngestDocumentResponse, status_code=status.HTTP_200_OK)
async def rag_index_alias(
    request: IngestDocumentRequest,
    authorized: bool = Depends(verify_internal_key)
):
    """Backward compatibility alias for Phase 1 Express callers."""
    return await process_document_ingestion(request)

