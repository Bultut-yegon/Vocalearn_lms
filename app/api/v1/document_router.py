from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
import os
import shutil
from pathlib import Path
from app.models.document_models import (
    DocumentUploadResponse,
    DocumentSearchRequest,
    DocumentBasedQuizRequest
)
from app.services.document_service import DocumentProcessingService
from app.services.quiz_service_enhanced import DocumentAwareQuizService
from app.core.logging_config import logger

router = APIRouter()
doc_service = DocumentProcessingService()
quiz_service = DocumentAwareQuizService()

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload course document (PDF)",
    description="Upload PDF document for quiz generation and grading"
)
async def upload_document(
    file: UploadFile = File(...),
    course: str = Form(...),
    topic: str = Form(...),
    week: Optional[int] = Form(None),
    instructor: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload a PDF document for processing.
    
    The document will be:
    1. Text extracted
    2. Chunked for efficient retrieval
    3. Embedded and stored in vector database
    4. Available for quiz generation
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Only PDF files are supported")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{course}_{topic}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Saved file: {file_path}")
        
        # Process document
        metadata = {
            "course": course,
            "topic": topic,
            "week": week,
            "instructor": instructor,
            "description": description,
            "upload_date": str(Path(file_path).stat().st_mtime)
        }
        
        result = await doc_service.process_pdf(str(file_path), metadata)
        
        logger.info(f"Successfully processed document: {result['document_id']}")
        
        return DocumentUploadResponse(**result)
        
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(500, f"Failed to process document: {str(e)}")

@router.post(
    "/search",
    summary="Search documents",
    description="Search for relevant content in uploaded documents"
)
async def search_documents(request: DocumentSearchRequest):
    """
    Search across all uploaded documents.
    Returns relevant chunks with metadata.
    """
    try:
        filters = {}
        if request.course:
            filters["course"] = request.course
        if request.topic:
            filters["topic"] = request.topic
        
        results = doc_service.retrieve_relevant_content(
            query=request.query,
            filters=filters if filters else None,
            top_k=request.top_k
        )
        
        return {
            "query": request.query,
            "results_found": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(500, f"Search failed: {str(e)}")

@router.post(
    "/generate-quiz",
    summary="Generate quiz from documents",
    description="Create quiz based on uploaded course materials"
)
async def generate_document_based_quiz(request: DocumentBasedQuizRequest):
    """
    Generate quiz from uploaded documents.
    
    Features:
    - Uses actual course materials
    - Contextual questions
    - Document references included
    - Supports timeframes (daily/weekly)
    """
    try:
        quiz = await quiz_service.generate_quiz_from_documents(
            course=request.course,
            topic=request.topic,
            timeframe=request.timeframe,
            difficulty=request.difficulty_level,
            num_mcq=request.num_mcq,
            num_true_false=request.num_true_false,
            num_short_answer=request.num_short_answer,
            document_ids=request.document_ids
        )
        
        return quiz
        
    except Exception as e:
        logger.error(f"Document-based quiz generation failed: {e}")
        raise HTTPException(500, f"Quiz generation failed: {str(e)}")

@router.get(
    "/list",
    summary="List uploaded documents",
    description="Get list of all processed documents"
)
async def list_documents(course: Optional[str] = None):
    """List all uploaded documents, optionally filtered by course."""
    try:
        if course:
            docs = doc_service.get_documents_by_timeframe(course, "monthly")
        else:
            # Get all documents
            docs = doc_service.get_documents_by_timeframe("", "monthly")
        
        return {
            "total_documents": len(docs),
            "documents": docs
        }
        
    except Exception as e:
        logger.error(f"List documents failed: {e}")
        raise HTTPException(500, f"Failed to list documents: {str(e)}")

@router.get(
    "/{document_id}",
    summary="Get document details",
    description="Get information about a specific document"
)
async def get_document(document_id: str):
    """Get details of a specific document."""
    try:
        summary = doc_service.get_document_summary(document_id)
        return summary
    except Exception as e:
        logger.error(f"Get document failed: {e}")
        raise HTTPException(404, f"Document not found: {str(e)}")

@router.delete(
    "/{document_id}",
    summary="Delete document",
    description="Remove document from system"
)
async def delete_document(document_id: str):
    """Delete a document and all its chunks."""
    try:
        # Delete from ChromaDB
        doc_service.collection.delete(
            where={"document_id": document_id}
        )
        
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Delete document failed: {e}")
        raise HTTPException(500, f"Failed to delete: {str(e)}")