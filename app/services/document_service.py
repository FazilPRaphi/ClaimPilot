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

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile
from postgrest.exceptions import APIError
from supabase import Client

from app.exceptions import DatabaseError, NotFoundError
from app.schemas.document import DocumentResponse
from app.services.storage_service import StorageService
from app.services.ocr_service import OCRService


class DocumentService:
    """
    Business logic for document management.
    """

    def __init__(self, db: Client):
        self.db = db
        self.storage = StorageService(db)
        self.ocr = OCRService()
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

    @staticmethod
    def _normalize_document_id(document_id: str | UUID) -> str:
        """
        Normalize a document id into a canonical UUID string when possible.
        """
        if isinstance(document_id, UUID):
            return str(document_id)

        normalized = str(document_id).strip().strip('"').strip("'")

        try:
            return str(UUID(normalized))
        except ValueError:
            return normalized

    async def extract_document_text(
        self,
        document_id: str | UUID,
    ) -> DocumentResponse:
        """
        Download a document from storage,
        extract text using OCR,
        store the extracted text,
        and return the updated document.
        """

        # ----------------------------------
        # Step 1
        # Retrieve document metadata
        # ----------------------------------

        normalized_document_id = self._normalize_document_id(document_id)

        response = (
            self.db
            .table("claim_documents")
            .select("*")
            .eq("id", normalized_document_id)
            .single()
            .execute()
        )

        document = response.data

        # ----------------------------------
        # Step 2
        # Generate signed URL
        # ----------------------------------

        signed_url = self.storage.create_signed_url(
            document["storage_path"]
        )

        # ----------------------------------
        # Step 3
        # Run OCR
        # ----------------------------------

        ocr_result = self.ocr.extract_text(
            signed_url=signed_url,
            filename=document["file_name"],
        )

        # ----------------------------------
        # Step 4
        # Save OCR Results
        # ----------------------------------

        updated = (
            self.db
            .table("claim_documents")
            .update(
                {
                    "extracted_text": ocr_result.text,
                    "ocr_confidence": ocr_result.confidence,
                    "upload_status": "processed",
                }
            )
            .eq("id", normalized_document_id)
            .execute()
        )

        return DocumentResponse.model_validate(
            updated.data[0]
        )
        
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
        document_id: str | UUID,
    ):
        """
        Retrieve a document.
        """

        normalized_document_id = self._normalize_document_id(document_id)

        return (
            self.db
            .table("claim_documents")
            .select("*")
            .eq("id", normalized_document_id)
            .single()
            .execute()
        )

    def generate_download_url(
        self,
        document_id: str | UUID,
    ) -> str:
        """
        Generate a signed download URL for a document.
        """

        document = self._get_active_document(document_id)
        storage_path = document["storage_path"]

        return self.storage.create_signed_url(storage_path)

    def delete_document(
        self,
        document_id: str | UUID,
    ) -> None:
        """
        Delete a document from storage and soft delete its record.
        """

        document = self._get_active_document(document_id)
        storage_path = document["storage_path"]

        try:
            self.storage.delete_file(storage_path)

            response = (
                self.db
                .table("claim_documents")
                .update(
                    {
                        "deleted_at": datetime.now(UTC).isoformat()
                    }
                )
                .eq("id", document_id)
                .is_("deleted_at", None)
                .execute()
            )

            if not response.data:
                raise NotFoundError("Document not found.")

        except NotFoundError:
            raise
        except Exception as exc:
            raise DatabaseError(
                "Unable to delete document."
            ) from exc

    def _get_active_document(
        self,
        document_id: str | UUID,
    ) -> dict:
        """
        Fetch a document that has not been soft deleted.
        """

        try:
            normalized_document_id = self._normalize_document_id(document_id)
            response = (
                self.db
                .table("claim_documents")
                .select("id, storage_path")
                .eq("id", normalized_document_id)
                .is_("deleted_at", None)
                .limit(1)
                .execute()
            )

            document = response.data[0] if response.data else None

            if not document:
                raise NotFoundError("Document not found.")

            return document

        except NotFoundError:
            raise
        except APIError as exc:
            raise DatabaseError(
                "Unable to retrieve document."
            ) from exc
        except Exception as exc:
            raise DatabaseError(
                "Unable to retrieve document."
            ) from exc
