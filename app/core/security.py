"""
Security utilities for ClaimPilot.

Currently unused directly as Supabase handles most of the security,
but serves as a placeholder for future custom security logic (e.g. rate limiting, custom hashing).
"""

import secrets

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(length)
