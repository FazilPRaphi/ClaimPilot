"""
Storage service for ClaimPilot.

Responsible for interacting with Supabase Storage.

Responsibilities:
- Upload files
- Delete files
- Generate storage paths
- Generate signed download URLs
- Validate storage operations

This service does NOT create database records.
That responsibility belongs to DocumentService.
"""

from __future__ import annotations

import os

from supabase import Client

from app.database.client import create_admin_client
from app.exceptions import DatabaseError, ValidationError


class StorageService:
    """
    Handles all storage-related operations.

    This service only interacts with Supabase Storage.
    It never touches the database.
    """

    BUCKET_NAME = "claim-files"

    def __init__(self, storage_client: Client):
        self.storage = storage_client.storage

    @staticmethod
    def generate_storage_path(
        user_id: str,
        claim_id: str,
        filename: str,
    ) -> str:
        """
        Generate a safe storage path.

        Example:

            user_uuid/
                claim_uuid/
                    receipt.pdf
        """

        safe_name = os.path.basename(filename)

        return (
            f"{user_id}/"
            f"{claim_id}/"
            f"{safe_name}"
        )

    async def upload_file(
        self,
        user_id: str,
        claim_id: str,
        filename: str,
        file_bytes: bytes,
        content_type: str,
    ) -> str:
        """
        Upload a file to Supabase Storage.

        Returns
        -------
        str
            Storage path.
        """

        storage_path = self.generate_storage_path(
            user_id=user_id,
            claim_id=claim_id,
            filename=filename,
        )

        try:
            # NOTE:
            # Keep using the admin client until Storage RLS
            # is fully configured for authenticated uploads.
            admin = create_admin_client()

            admin.storage.from_(self.BUCKET_NAME).upload(
                path=storage_path,
                file=file_bytes,
                file_options={
                    "content-type": content_type,
                    "upsert": False,
                },
            )

            return storage_path

        except Exception as exc:
            raise DatabaseError(
                "Failed to upload document to storage."
            ) from exc

    def delete_file(
        self,
        storage_path: str,
    ) -> None:
        """
        Delete a file from Supabase Storage.
        """

        try:
            self.storage.from_(self.BUCKET_NAME).remove(
                [storage_path]
            )

        except Exception as exc:
            raise DatabaseError(
                "Failed to delete document from storage."
            ) from exc

    def create_signed_url(
        self,
        storage_path: str,
        expires_in: int = 300,
    ) -> str:
        """
        Generate a temporary signed download URL.

        Parameters
        ----------
        storage_path:
            Path stored in claim_documents.storage_path.

        expires_in:
            Expiry time in seconds.

        Returns
        -------
        str
            Signed download URL.
        """

        try:
            response = (
                self.storage
                .from_(self.BUCKET_NAME)
                .create_signed_url(
                    storage_path,
                    expires_in,
                )
            )

            if isinstance(response, str):
                return response

            if isinstance(response, dict):
                url = (
                    response.get("signedURL")
                    or response.get("signed_url")
                    or response.get("url")
                )

                if url:
                    return url

            if hasattr(response, "signedURL"):
                return response.signedURL

            if hasattr(response, "signed_url"):
                return response.signed_url

            raise DatabaseError(
                "Supabase returned an invalid signed URL response."
            )

        except Exception as exc:
            raise DatabaseError(
                "Failed to generate signed download URL."
            ) from exc

    def get_public_url(
        self,
        storage_path: str,
    ) -> str:
        """
        Return the public URL.

        Useful only if the bucket becomes public.
        """

        try:
            return (
                self.storage
                .from_(self.BUCKET_NAME)
                .get_public_url(storage_path)
            )

        except Exception as exc:
            raise DatabaseError(
                "Failed to generate public URL."
            ) from exc

    @staticmethod
    def validate_file_size(
        file_size: int,
        max_size: int = 10 * 1024 * 1024,
    ) -> None:
        """
        Validate maximum file size.

        Default: 10 MB.
        """

        if file_size <= 0:
            raise ValidationError(
                "Uploaded file is empty."
            )

        if file_size > max_size:
            raise ValidationError(
                "File exceeds maximum allowed size of 10 MB."
            )

    @staticmethod
    def validate_content_type(
        content_type: str | None,
    ) -> None:
        """
        Validate supported MIME types.
        """

        if not content_type:
            raise ValidationError(
                "Missing content type."
            )

        allowed_types = {
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if content_type not in allowed_types:
            raise ValidationError(
                f"Unsupported file type: {content_type}"
            )