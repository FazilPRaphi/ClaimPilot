"""
Unit tests for ClaimService.
"""

import unittest
from types import SimpleNamespace
from typing import Any

from app.exceptions import NotFoundError, ValidationError
from app.services.claim_service import ClaimService


class FakeQuery:
    """Small chainable fake for Supabase table queries."""

    def __init__(self, responses: list[Any]) -> None:
        """Initialize with queued response payloads."""
        self.responses = responses
        self.insert_payload = None
        self.update_payload = None
        self.filters = []

    def select(self, value: str) -> "FakeQuery":
        """Record selected columns."""
        self.selected = value
        return self

    def insert(self, payload: dict) -> "FakeQuery":
        """Record insert payload."""
        self.insert_payload = payload
        return self

    def update(self, payload: dict) -> "FakeQuery":
        """Record update payload."""
        self.update_payload = payload
        return self

    def eq(self, field_name: str, value: str) -> "FakeQuery":
        """Record equality filter."""
        self.filters.append(("eq", field_name, value))
        return self

    def is_(self, field_name: str, value: str) -> "FakeQuery":
        """Record null filter."""
        self.filters.append(("is", field_name, value))
        return self

    def order(self, field_name: str, desc: bool = False) -> "FakeQuery":
        """Record ordering."""
        self.ordering = (field_name, desc)
        return self

    def limit(self, value: int) -> "FakeQuery":
        """Record limit."""
        self.limit_value = value
        return self

    def execute(self) -> SimpleNamespace:
        """Return the next queued response payload."""
        data = self.responses.pop(0)
        return SimpleNamespace(data=data)


class FakeClient:
    """Small fake Supabase client exposing table()."""

    def __init__(self, responses: list[Any]) -> None:
        """Initialize with queued table responses."""
        self.query = FakeQuery(responses)
        self.table_name = None

    def table(self, table_name: str) -> FakeQuery:
        """Return a chainable query fake."""
        self.table_name = table_name
        return self.query


class ClaimServiceTestCase(unittest.TestCase):
    """Tests for claim CRUD business behavior."""

    def test_create_claim_sets_required_defaults(self) -> None:
        """Create payload includes authenticated user and draft defaults."""
        claim = {
            "id": "claim-1",
            "claim_number": "CP-1",
            "user_id": "user-1",
            "title": "Phone repair",
            "description": "Screen cracked",
            "claim_type": "warranty",
            "status": "draft",
            "current_stage": "upload",
            "deleted_at": None,
        }
        client = FakeClient([[claim]])

        result = ClaimService(client).create_claim(
            "user-1",
            {
                "title": " Phone repair ",
                "description": " Screen cracked ",
                "claim_type": " warranty ",
            },
        )

        self.assertEqual(result, claim)
        self.assertEqual(client.table_name, "claims")
        self.assertEqual(client.query.insert_payload["user_id"], "user-1")
        self.assertEqual(client.query.insert_payload["status"], "draft")
        self.assertEqual(client.query.insert_payload["current_stage"], "upload")
        self.assertIsNone(client.query.insert_payload["deleted_at"])

    def test_create_claim_rejects_blank_title(self) -> None:
        """Blank required fields raise a business validation error."""
        client = FakeClient([])

        with self.assertRaises(ValidationError):
            ClaimService(client).create_claim(
                "user-1",
                {
                    "title": " ",
                    "description": "Damage",
                    "claim_type": "auto",
                },
            )

    def test_list_claims_filters_soft_deleted_rows(self) -> None:
        """List operation filters deleted_at to null."""
        claim = {"id": "claim-1", "deleted_at": None}
        client = FakeClient([[claim]])

        result = ClaimService(client).list_claims("user-1")

        self.assertEqual(result, [claim])
        self.assertIn(("is", "deleted_at", "null"), client.query.filters)

    def test_get_claim_raises_not_found_for_empty_response(self) -> None:
        """Empty active-claim response maps to NotFoundError."""
        client = FakeClient([[]])

        with self.assertRaises(NotFoundError):
            ClaimService(client).get_claim("missing-claim")

    def test_update_claim_updates_only_user_editable_fields(self) -> None:
        """Update payload is sanitized and excludes unset fields."""
        existing_claim = {"id": "claim-1", "title": "Old"}
        updated_claim = {"id": "claim-1", "title": "New"}
        client = FakeClient([[existing_claim], [updated_claim]])

        result = ClaimService(client).update_claim(
            "claim-1",
            {"title": " New ", "status": "completed"},
        )

        self.assertEqual(result, updated_claim)
        self.assertEqual(client.query.update_payload, {"title": "New"})
        self.assertIn(("is", "deleted_at", "null"), client.query.filters)

    def test_delete_claim_sets_deleted_at(self) -> None:
        """Delete operation performs a soft delete."""
        existing_claim = {"id": "claim-1", "deleted_at": None}
        deleted_claim = {"id": "claim-1", "deleted_at": "timestamp"}
        client = FakeClient([[existing_claim], [deleted_claim]])

        result = ClaimService(client).delete_claim("claim-1")

        self.assertEqual(result, deleted_claim)
        self.assertIn("deleted_at", client.query.update_payload)


if __name__ == "__main__":
    unittest.main()
