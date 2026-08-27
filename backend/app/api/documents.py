"""
SevaSetu AI — Document Upload & OCR API Router
Author: Rahul Jha | Made in India 🇮🇳

Endpoints:
  POST /api/v1/documents/upload          - Upload document for OCR
  GET  /api/v1/documents/                - List user's documents
  GET  /api/v1/documents/{id}            - Get document details + OCR fields
  GET  /api/v1/documents/checklist/{svc} - Get service document checklist
  DELETE /api/v1/documents/{id}          - Delete document
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.models.user import User, Document, DocumentField, DocumentStatus
from ai.ocr.ocr_engine import ocr_engine

logger = logging.getLogger(__name__)
router = APIRouter()

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "tiff", "tif"}
MAX_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


# ── UPLOAD ────────────────────────────────────────────────────────────────────

@router.post("/upload", summary="Upload document for OCR processing")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF or image document"),
    service_type: Optional[str] = Form(None, description="voter_id | pan_card | passport | income_certificate | birth_certificate"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a document (PDF/image) for OCR processing.

    Process:
    1. Validate file type and size
    2. Save with UUID filename
    3. Create DB record (status=PENDING)
    4. Trigger async OCR in background
    5. Return document ID for polling
    """
    # Validate extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file
    contents = await file.read()

    # Validate size
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
        )

    # Generate unique stored filename
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_name)

    # Save to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    # Create DB record
    doc = Document(
        user_id=current_user.id,
        original_name=file.filename,
        stored_name=stored_name,
        file_path=file_path,
        file_type=ext,
        file_size_kb=len(contents) // 1024,
        service_type=service_type,
        ocr_status=DocumentStatus.PENDING,
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Trigger async OCR processing
    background_tasks.add_task(_process_document_ocr, doc.id, file_path, ext)

    logger.info(f"📤 Document uploaded: {file.filename} by user {current_user.id} → {stored_name}")

    return {
        "success": True,
        "message": "Document uploaded successfully. OCR processing started.",
        "document_id": doc.id,
        "original_name": file.filename,
        "file_size_kb": doc.file_size_kb,
        "status": "pending",
        "estimated_processing_seconds": 10,
    }


# ── BACKGROUND OCR TASK ───────────────────────────────────────────────────────

async def _process_document_ocr(document_id: int, file_path: str, ext: str):
    """
    Background task: Run OCR on uploaded document and update DB.
    Called by FastAPI BackgroundTasks after upload response is sent.
    """
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Fetch document record
            result = await db.execute(select(Document).where(Document.id == document_id))
            doc = result.scalar_one_or_none()
            if not doc:
                return

            # Update status to processing
            doc.ocr_status = DocumentStatus.PROCESSING
            await db.commit()

            logger.info(f"🔍 OCR started for document {document_id}")

            # Run OCR based on file type
            if ext == "pdf":
                extracted = await ocr_engine.extract_from_pdf(file_path)
            else:
                extracted = await ocr_engine.extract_from_image(file_path)

            # Update document with OCR results
            doc.doc_type = extracted.document_type
            doc.extracted_text = extracted.raw_text[:5000]   # Truncate for storage
            doc.extracted_fields = extracted.fields
            doc.verification_score = extracted.verification_score
            doc.is_valid = extracted.is_valid
            doc.missing_fields = extracted.missing_fields
            doc.ocr_status = DocumentStatus.COMPLETED
            doc.processed_at = datetime.now(timezone.utc)

            # Save individual field records
            for field_name, field_value in extracted.fields.items():
                field_record = DocumentField(
                    document_id=document_id,
                    field_name=field_name,
                    field_value=str(field_value) if field_value else None,
                    confidence=extracted.confidence,
                )
                db.add(field_record)

            await db.commit()
            logger.info(
                f"✅ OCR completed for doc {document_id}: "
                f"type={extracted.document_type}, score={extracted.verification_score}"
            )

        except Exception as e:
            logger.error(f"❌ OCR background task failed for doc {document_id}: {e}", exc_info=True)
            try:
                doc.ocr_status = DocumentStatus.FAILED
                await db.commit()
            except Exception:
                pass


# ── LIST DOCUMENTS ────────────────────────────────────────────────────────────

@router.get("/", summary="List user's uploaded documents")
async def list_documents(
    page: int = 1,
    limit: int = 10,
    service_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get paginated list of documents uploaded by current user."""
    offset = (page - 1) * limit
    query = (
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(desc(Document.uploaded_at))
    )
    if service_type:
        query = query.where(Document.service_type == service_type)

    result = await db.execute(query.offset(offset).limit(limit))
    docs = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": d.id,
                "original_name": d.original_name,
                "file_type": d.file_type,
                "file_size_kb": d.file_size_kb,
                "service_type": d.service_type,
                "doc_type": d.doc_type,
                "ocr_status": d.ocr_status.value if d.ocr_status else None,
                "is_valid": d.is_valid,
                "verification_score": d.verification_score,
                "missing_fields": d.missing_fields,
                "uploaded_at": str(d.uploaded_at),
            }
            for d in docs
        ],
    }


# ── GET DOCUMENT DETAIL ───────────────────────────────────────────────────────

@router.get("/{doc_id}", summary="Get document details with OCR results")
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get full details of a specific document including extracted fields."""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get individual field records
    fields_result = await db.execute(
        select(DocumentField).where(DocumentField.document_id == doc_id)
    )
    fields = fields_result.scalars().all()

    return {
        "success": True,
        "data": {
            "id": doc.id,
            "original_name": doc.original_name,
            "file_type": doc.file_type,
            "file_size_kb": doc.file_size_kb,
            "service_type": doc.service_type,
            "doc_type": doc.doc_type,
            "ocr_status": doc.ocr_status.value if doc.ocr_status else None,
            "extracted_fields": doc.extracted_fields or {},
            "verification_score": doc.verification_score,
            "is_valid": doc.is_valid,
            "missing_fields": doc.missing_fields or [],
            "uploaded_at": str(doc.uploaded_at),
            "processed_at": str(doc.processed_at) if doc.processed_at else None,
            "fields": [
                {
                    "name": f.field_name,
                    "value": f.field_value,
                    "is_verified": f.is_verified,
                    "confidence": f.confidence,
                }
                for f in fields
            ],
        },
    }


# ── CHECKLIST ─────────────────────────────────────────────────────────────────

@router.get("/checklist/{service_type}", summary="Get document checklist for a service")
async def get_checklist(
    service_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Returns the required documents checklist for a service.
    If user has uploaded documents, marks applicable items as completed.
    """
    # Get user's latest uploaded docs for this service
    result = await db.execute(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.service_type == service_type,
            Document.ocr_status == DocumentStatus.COMPLETED,
        )
    )
    uploaded_docs = result.scalars().all()

    # Collect all extracted fields from user's uploads
    combined_fields = {}
    for doc in uploaded_docs:
        if doc.extracted_fields:
            combined_fields.update(doc.extracted_fields)

    # Generate checklist (cross-reference with uploaded fields)
    checklist = ocr_engine.generate_checklist(service_type, combined_fields)

    return {
        "success": True,
        "service_type": service_type,
        "checklist": checklist,
        "uploaded_documents": len(uploaded_docs),
    }


# ── DELETE DOCUMENT ───────────────────────────────────────────────────────────

@router.delete("/{doc_id}", summary="Delete a document")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a document and its file from disk."""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete physical file
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception as e:
        logger.warning(f"⚠️ Could not delete file {doc.file_path}: {e}")

    await db.delete(doc)
    await db.commit()

    logger.info(f"🗑️ Document {doc_id} deleted by user {current_user.id}")
    return {"success": True, "message": "Document deleted successfully"}
