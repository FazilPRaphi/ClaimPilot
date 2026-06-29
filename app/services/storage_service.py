"""
Storage service for ClaimPilot.

Responsible for interacting with Supabase Storage.

Responsibilities:
- Upload files
- Delete files
- Generate storage paths
- Validate storage operations

This service does NOT create database records.
That responsibility belongs to DocumentService.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import BinaryIO

from fastapi import UploadFile
from supabase import Client

from app.exceptions import ValidationError


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
        Generate the storage path for a document.

        Example:
        claim-files/user_uuid/claim_uuid/receipt.pdf
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

        Returns:
            The storage path.
        """

        storage_path = self.generate_storage_path(
            user_id=user_id,
            claim_id=claim_id,
            filename=filename,
        )

        self.storage.from_(self.BUCKET_NAME).upload(
            path=storage_path,
            file=file_bytes,
            file_options={
                "content-type": content_type,
                "upsert": False,
            },
        )

        return storage_path

    def delete_file(
        self,
        storage_path: str,
    ) -> None:
        """
        Delete a file from Supabase Storage.
        """

        self.storage.from_(self.BUCKET_NAME).remove(
            [storage_path]
        )

    def get_public_url(
        self,
        storage_path: str,
    ) -> str:
        """
        Returns the storage URL.

        The bucket is private, so this is mainly useful
        if signed URLs are added later.
        """

        return self.storage.from_(self.BUCKET_NAME).get_public_url(
            storage_path
        )

    @staticmethod
    def validate_file_size(
        file_size: int,
        max_size: int = 10 * 1024 * 1024,
    ) -> None:
        """
        Validate maximum file size.

        Default: 10 MB
        """

        if file_size > max_size:
            raise ValidationError(
                "File exceeds maximum allowed size of 10 MB."
            )

    @staticmethod
    def validate_content_type(
        content_type: str,
    ) -> None:
        """
        Validate supported MIME types.
        """

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