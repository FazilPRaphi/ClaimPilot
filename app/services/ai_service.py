"""
AI service for ClaimPilot.

Responsibilities
----------------
- Send OCR text to Groq
- Parse AI response
- Validate structured output
"""

from __future__ import annotations

import json

from groq import Groq

from app.ai.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
)
from app.core.settings import settings
from app.exceptions import ValidationError
from app.schemas.ai import (
    AIAnalysisResponse,
    StructuredClaimData,
)


class AIService:
    """
    Service responsible for AI-powered claim analysis.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValidationError(
                "GROQ_API_KEY is not configured."
            )

        self.model = settings.GROQ_MODEL

        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )

    def analyze(
        self,
        ocr_text: str,
    ) -> AIAnalysisResponse:
        """
        Analyze OCR text using Groq.
        """

        if not ocr_text.strip():
            raise ValidationError(
                "OCR text is empty."
            )

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            response_format={
                "type": "json_object",
            },
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": build_analysis_prompt(
                        ocr_text
                    ),
                },
            ],
        )

        content = (
            completion
            .choices[0]
            .message
            .content
        )

        try:

            data = json.loads(content)

        except json.JSONDecodeError as exc:

            raise ValidationError(
                "Groq returned invalid JSON."
            ) from exc

        structured = StructuredClaimData(
            claim_type=data.get("claim_type"),
            claimant_name=data.get(
                "claimant_name"
            ),
            hospital_name=data.get(
                "hospital_name"
            ),
            invoice_number=data.get(
                "invoice_number"
            ),
            policy_number=data.get(
                "policy_number"
            ),
            date=data.get("date"),
            amount=data.get("amount"),
            currency=data.get("currency"),
        )

        return AIAnalysisResponse(
            summary=data.get(
                "summary",
                "",
            ),
            structured_data=structured,
            important_entities=data.get(
                "important_entities",
                [],
            ),
            missing_information=data.get(
                "missing_information",
                [],
            ),
            readiness_score=data.get(
                "readiness_score",
                0,
            ),
        )