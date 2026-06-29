"""
Business logic for insurance claim CRUD operations.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from postgrest.exceptions import APIError
from supabase import Client

from app.core.logger import get_logger
from app.exceptions import DatabaseError, NotFoundError, ValidationError
from app.services.base_service import BaseService


class ClaimService(BaseService):
    """
    Service for authenticated user's claim operations.

    The injected database client must be user-scoped so Supabase RLS remains
    responsible for ownership enforcement.
    """

    TABLE_NAME = "claims"
    DEFAULT_STATUS = "draft"
    DEFAULT_STAGE = "upload"

    def __init__(self, db_client: Client):
        """Initialize service with a user-scoped database client."""
        super().__init__(db_client)
        self.logger = get_logger(__name__)

    def create_claim(self, user_id: str, claim_data: dict) -> dict:
        """
        Create a draft claim for the authenticated user.

        Raises:
            ValidationError: If claim_data is invalid.
            DatabaseError: If Supabase rejects the insert.
        """
        self._validate_required_claim_data(claim_data)

        payload = {
            "claim_number": self._generate_claim_number(),
            "user_id": user_id,
            "title": claim_data["title"].strip(),
            "description": claim_data["description"].strip(),
            "claim_type": claim_data["claim_type"].strip(),
            "status": self.DEFAULT_STATUS,
            "current_stage": self.DEFAULT_STAGE,
            "deleted_at": None,
        }

        try:
            response = self.db_client.table(self.TABLE_NAME).insert(payload).execute()
            claim = self._first_row(response.data)
            if not claim:
                raise DatabaseError("Claim could not be created.")

            self.logger.info("Claim Created: user_id=%s claim_id=%s", user_id, claim.get("id"))
            return claim
        except ValidationError:
            raise
        except Exception as exc:
            self.logger.error("Claim creation failed: user_id=%s error=%s", user_id, exc)
            raise DatabaseError("Unable to create claim.") from exc

    def list_claims(self, user_id: str) -> list[dict]:
        """
        List non-deleted claims visible to the authenticated user.

        RLS enforces ownership; user_id is logged for operational context.
        """
        try:
            response = (
                self.db_client.table(self.TABLE_NAME)
                .select("*")
                .is_("deleted_at", "null")
                .order("created_at", desc=True)
                .execute()
            )

            claims = response.data or []
            self.logger.info("Claims Listed: user_id=%s count=%s", user_id, len(claims))
            return claims
        except Exception as exc:
            self.logger.error("Claims list failed: user_id=%s error=%s", user_id, exc)
            raise DatabaseError("Unable to list claims.") from exc

    def get_claim(self, claim_id: str) -> dict:
        """
        Retrieve one non-deleted claim by ID.

        Raises:
            NotFoundError: If the claim is missing, deleted, or blocked by RLS.
            DatabaseError: If the database query fails unexpectedly.
        """
        return self._get_active_claim(claim_id)

    def update_claim(self, claim_id: str, claim_data: dict) -> dict:
        """
        Update user-editable fields on a non-deleted claim.

        Raises:
            ValidationError: If no valid fields are provided.
            NotFoundError: If the claim is missing, deleted, or blocked by RLS.
            DatabaseError: If the database update fails.
        """
        updates = self._build_update_payload(claim_data)
        if not updates:
            raise ValidationError("At least one claim field must be provided.")

        self._get_active_claim(claim_id)

        try:
            response = (
                self.db_client.table(self.TABLE_NAME)
                .update(updates)
                .eq("id", claim_id)
                .is_("deleted_at", "null")
                .execute()
            )
            claim = self._first_row(response.data)
            if not claim:
                raise NotFoundError("Claim not found.")

            self.logger.info("Claim Updated: claim_id=%s", claim_id)
            return claim
        except (NotFoundError, ValidationError):
            raise
        except Exception as exc:
            self.logger.error("Claim update failed: claim_id=%s error=%s", claim_id, exc)
            raise DatabaseError("Unable to update claim.") from exc

    def delete_claim(self, claim_id: str) -> dict:
        """
        Soft delete a claim by setting deleted_at.

        Raises:
            NotFoundError: If the claim is missing, deleted, or blocked by RLS.
            DatabaseError: If the database update fails.
        """
        self._get_active_claim(claim_id)

        try:
            response = (
                self.db_client.table(self.TABLE_NAME)
                .update({"deleted_at": self._current_timestamp()})
                .eq("id", claim_id)
                .is_("deleted_at", "null")
                .execute()
            )
            claim = self._first_row(response.data)
            if not claim:
                raise NotFoundError("Claim not found.")

            self.logger.info("Claim Deleted: claim_id=%s", claim_id)
            return claim
        except NotFoundError:
            raise
        except Exception as exc:
            self.logger.error("Claim delete failed: claim_id=%s error=%s", claim_id, exc)
            raise DatabaseError("Unable to delete claim.") from exc

    def _get_active_claim(self, claim_id: str) -> dict:
        """Fetch a claim that has not been soft deleted."""
        try:
            response = (
                self.db_client.table(self.TABLE_NAME)
                .select("*")
                .eq("id", claim_id)
                .is_("deleted_at", "null")
                .limit(1)
                .execute()
            )
            claim = self._first_row(response.data)
            if not claim:
                raise NotFoundError("Claim not found.")
            return claim
        except NotFoundError:
            raise
        except APIError as exc:
            self.logger.error("Claim fetch failed: claim_id=%s error=%s", claim_id, exc)
            raise DatabaseError("Unable to retrieve claim.") from exc
        except Exception as exc:
            self.logger.error("Claim fetch failed: claim_id=%s error=%s", claim_id, exc)
            raise DatabaseError("Unable to retrieve claim.") from exc

    def _build_update_payload(self, claim_data: dict) -> dict:
        """Build a sanitized update payload from user-editable fields."""
        updates = {}
        for field_name in ("title", "description", "claim_type"):
            value = claim_data.get(field_name)
            if value is not None:
                self._validate_text_field(field_name, value)
                updates[field_name] = value.strip()
        return updates

    def _validate_required_claim_data(self, claim_data: dict) -> None:
        """Validate required claim creation fields."""
        for field_name in ("title", "description", "claim_type"):
            self._validate_text_field(field_name, claim_data.get(field_name))

    def _validate_text_field(self, field_name: str, value: str | None) -> None:
        """Validate a required text field."""
        if value is None or not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} is required.")

    def _generate_claim_number(self) -> str:
        """Generate a unique claim number without relying on schema changes."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid4().hex[:8].upper()
        return f"CP-{timestamp}-{suffix}"

    def _current_timestamp(self) -> str:
        """Return an ISO-8601 UTC timestamp for soft deletes."""
        return datetime.now(UTC).isoformat()

    def _first_row(self, data: Any) -> dict | None:
        """Return the first row from a Supabase response payload."""
        if isinstance(data, list):
            return data[0] if data else None
        if isinstance(data, dict):
            return data
        return None
