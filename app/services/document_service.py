"""
Document service for ClaimPilot.

Responsible for:

- Uploading documents
- Saving document metadata
- Listing claim documents
- Retrieving a document
- Soft deleting document records

This service orchestrates storage and database operations.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from supabase import Client

from app.schemas.document import DocumentResponse
from app.services.storage_service import StorageService


class DocumentService:
    """
    Business logic for document management.
    """

    def __init__(self, db: Client):
        self.db = db
        self.storage = StorageService(db)

    async def upload_document(
        self,
        user_id: str,
        claim_id: str,
        file: UploadFile,
        document_type: str = "other",
    ) -> DocumentResponse:
        """
        Upload a document and save its metadata.
        """

        # ----------------------------
        # Validate File Type
        # ----------------------------

        StorageService.validate_content_type(
            file.content_type
        )

        # ----------------------------
        # Read File
        # ----------------------------

        file_bytes = await file.read()

        StorageService.validate_file_size(
            len(file_bytes)
        )

        # ----------------------------
        # Generate Unique Filename
        # ----------------------------

        extension = Path(file.filename).suffix

        unique_name = (
            f"{uuid4().hex}"
            f"{extension}"
        )

        # ----------------------------
        # Upload
        # ----------------------------

        storage_path = await self.storage.upload_file(
            user_id=user_id,
            claim_id=claim_id,
            filename=unique_name,
            file_bytes=file_bytes,
            content_type=file.content_type,
        )

        # ----------------------------
        # Save Metadata
        # ----------------------------

        response = (
            self.db
            .table("claim_documents")
            .insert(
                {
                    "claim_id": claim_id,
                    "file_name": unique_name,
                    "storage_path": storage_path,
                    "document_type": document_type,
                }
            )
            .execute()
        )

        document = response.data[0]

        return DocumentResponse.model_validate(document)

    def list_documents(
        self,
        claim_id: str,
    ):
        """
        List all documents for a claim.
        """

        return (
            self.db
            .table("claim_documents")
            .select("*")
            .eq("claim_id", claim_id)
            .is_("deleted_at", None)
            .order("created_at")
            .execute()
        )

    def get_document(
        self,
        document_id: str,
    ):
        """
        Retrieve a document.
        """

        return (
            self.db
            .table("claim_documents")
            .select("*")
            .eq("id", document_id)
            .single()
            .execute()
        )

    def delete_document(
        self,
        document_id: str,
    ):
        """
        Soft delete a document.
        """

        return (
            self.db
            .table("claim_documents")
            .update(
                {
                    "deleted_at": datetime.utcnow().isoformat()
                }
            )
            .eq("id", document_id)
            .execute()
        )