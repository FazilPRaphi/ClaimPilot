"""
Unit tests for DocumentService.
"""

import unittest
from datetime import datetime
from io import BytesIO
from types import SimpleNamespace
from typing import Any
from fastapi import UploadFile

from app.exceptions import ValidationError
from app.services.document_service import DocumentService


class FakeStorageBucket:
    """Mock bucket to collect upload info."""

    def __init__(self) -> None:
        self.uploaded_files = []

    def upload(self, path: str, file: bytes, file_options: dict) -> dict:
        self.uploaded_files.append({
            "path": path,
            "file": file,
            "options": file_options
        })
        return {"path": path}


class FakeStorage:
    """Mock storage system exposing from_()."""

    def __init__(self) -> None:
        self.bucket = FakeStorageBucket()
        self.bucket_name = None

    def from_(self, bucket_name: str) -> FakeStorageBucket:
        self.bucket_name = bucket_name
        return self.bucket


class FakeQuery:
    """Chainable mock query for Supabase."""

    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.insert_payload = None
        self.filters = []
        self.update_payload = None

    def insert(self, payload: dict) -> "FakeQuery":
        self.insert_payload = payload
        return self

    def update(self, payload: dict) -> "FakeQuery":
        self.update_payload = payload
        return self

    def select(self, *args, **kwargs) -> "FakeQuery":
        return self

    def eq(self, field_name: str, value: Any) -> "FakeQuery":
        self.filters.append(("eq", field_name, value))
        return self

    def is_(self, field_name: str, value: Any) -> "FakeQuery":
        self.filters.append(("is", field_name, value))
        return self

    def order(self, *args, **kwargs) -> "FakeQuery":
        return self

    def execute(self) -> SimpleNamespace:
        data = self.responses.pop(0) if self.responses else []
        return SimpleNamespace(data=data)


class FakeClient:
    """Mock Supabase client."""

    def __init__(self, responses: list[Any]) -> None:
        self.query = FakeQuery(responses)
        self.storage = FakeStorage()
        self.table_name = None

    def table(self, table_name: str) -> FakeQuery:
        self.table_name = table_name
        return self.query


class DocumentServiceTestCase(unittest.IsolatedAsyncioTestCase):
    """Tests for document management business behavior."""

    async def test_upload_document_success(self) -> None:
        """Uploading a valid document successfully stores it and records metadata."""
        db_doc = {
            "id": "doc-uuid-123",
            "claim_id": "claim-uuid-456",
            "file_name": "unique-name.png",
            "storage_path": "user-789/claim-uuid-456/unique-name.png",
            "document_type": "receipt",
            "upload_status": "uploaded",
            "extracted_text": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "deleted_at": None,
        }
        client = FakeClient([[db_doc]])
        service = DocumentService(client)

        # Create a fake file
        file_content = b"fake png data"
        upload_file = UploadFile(
            file=BytesIO(file_content),
            filename="receipt.png",
            headers={"content-type": "image/png"}
        )

        result = await service.upload_document(
            user_id="user-789",
            claim_id="claim-uuid-456",
            file=upload_file,
            document_type="receipt"
        )

        # Assertions
        self.assertEqual(result.id, "doc-uuid-123")
        self.assertEqual(result.document_type, "receipt")
        self.assertEqual(result.upload_status, "uploaded")
        
        # Verify storage was called
        uploaded = client.storage.bucket.uploaded_files
        self.assertEqual(len(uploaded), 1)
        self.assertEqual(uploaded[0]["file"], file_content)
        self.assertEqual(uploaded[0]["options"]["content-type"], "image/png")

        # Verify DB insert payload matches DB schema
        insert_payload = client.query.insert_payload
        self.assertEqual(insert_payload["claim_id"], "claim-uuid-456")
        self.assertEqual(insert_payload["document_type"], "receipt")
        self.assertNotIn("mime_type", insert_payload)
        self.assertNotIn("file_size", insert_payload)

    async def test_upload_document_invalid_type(self) -> None:
        """Uploading an unsupported document type raises ValidationError."""
        client = FakeClient([])
        service = DocumentService(client)

        upload_file = UploadFile(
            file=BytesIO(b"fake txt"),
            filename="test.txt",
            headers={"content-type": "text/plain"}
        )

        with self.assertRaises(ValidationError):
            await service.upload_document(
                user_id="user-789",
                claim_id="claim-uuid-456",
                file=upload_file,
                document_type="receipt"
            )

    async def test_upload_document_too_large(self) -> None:
        """Uploading a document exceeding 10MB raises ValidationError."""
        client = FakeClient([])
        service = DocumentService(client)

        # 11 MB file
        large_content = b"x" * (11 * 1024 * 1024)
        upload_file = UploadFile(
            file=BytesIO(large_content),
            filename="large.png",
            headers={"content-type": "image/png"}
        )

        with self.assertRaises(ValidationError):
            await service.upload_document(
                user_id="user-789",
                claim_id="claim-uuid-456",
                file=upload_file,
                document_type="receipt"
            )

    def test_list_documents(self) -> None:
        """List active documents for a claim, filtering deleted ones."""
        client = FakeClient([[]])
        service = DocumentService(client)

        service.list_documents("claim-1")

        self.assertEqual(client.table_name, "claim_documents")
        self.assertIn(("eq", "claim_id", "claim-1"), client.query.filters)
        self.assertIn(("is", "deleted_at", None), client.query.filters)

    def test_delete_document(self) -> None:
        """Delete performs a soft delete by setting deleted_at timestamp."""
        client = FakeClient([[]])
        service = DocumentService(client)

        service.delete_document("doc-1")

        self.assertEqual(client.table_name, "claim_documents")
        self.assertEqual(client.query.filters[0], ("eq", "id", "doc-1"))
        self.assertIn("deleted_at", client.query.update_payload)

    def test_normalize_document_id_strips_quotes(self) -> None:
        """UUIDs wrapped in quotes are normalized before database filters."""
        service = DocumentService(FakeClient([[]]))

        normalized = service._normalize_document_id(
            '"6163f707-0c3b-4c73-b62a-2a37013c6a0a"'
        )

        self.assertEqual(
            normalized,
            "6163f707-0c3b-4c73-b62a-2a37013c6a0a",
        )


if __name__ == "__main__":
    unittest.main()
