"""
OCR service for ClaimPilot.

Responsibilities
----------------
- Download documents from Supabase Storage
- Preprocess images
- Extract text from images
- Extract text from PDFs
- Calculate OCR confidence
"""

from __future__ import annotations

import io
import os
from platform import platform
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image
from pdf2image import convert_from_path

from app.exceptions import ValidationError
from app.schemas.ocr import OCRResult


class OCRService:
    """
    Handles OCR operations.
    """

    TESSERACT_CONFIG = "--oem 3 --psm 6"

def __init__(self):
    """
        Configure the Tesseract executable based on the OS.
    """

    if platform.system() == "Windows":
            pytesseract.pytesseract.tesseract_cmd = (
            r"D:\Program Files\Tesseract-OCR\tesseract.exe"
        )
    else:
            pytesseract.pytesseract.tesseract_cmd = os.getenv(
            "TESSERACT_CMD",
            "/usr/bin/tesseract",
        )

    def extract_text(
        self,
        signed_url: str,
        filename: str,
    ) -> OCRResult:
        """
        Download a document from storage and perform OCR.

        Returns
        -------
        OCRResult
            OCR output including extracted text,
            confidence, page count and processing time.
        """

        start_time = time.perf_counter()

        response = requests.get(
            signed_url,
            timeout=60,
        )

        response.raise_for_status()

        extension = Path(filename).suffix.lower()

        if extension in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }:
            result = self._extract_from_image(
                response.content
            )

        elif extension == ".pdf":
            result = self._extract_from_pdf(
                response.content
            )

        else:
            raise ValidationError(
                f"Unsupported file type: {extension}"
            )

        result.processing_time_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        return result

    def _preprocess_image(
        self,
        image: Image.Image,
    ) -> Image.Image:
        """
        Preprocess an image to improve OCR accuracy.
        """

        image = image.convert("RGB")

        img = np.array(image)

        img = cv2.cvtColor(
            img,
            cv2.COLOR_RGB2GRAY,
        )

        img = cv2.fastNlMeansDenoising(img)

        img = cv2.adaptiveThreshold(
            img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11,
        )

        height, width = img.shape

        if width < 1200:
            scale = 1200 / width

            img = cv2.resize(
                img,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC,
            )

        return Image.fromarray(img)

    def _run_tesseract(
        self,
        image: Image.Image,
    ) -> tuple[str, float]:
        """
        Run OCR and compute average confidence.
        """

        data = pytesseract.image_to_data(
            image,
            config=self.TESSERACT_CONFIG,
            output_type=pytesseract.Output.DICT,
        )

        words = []
        confidences = []

        for text, conf in zip(
            data["text"],
            data["conf"],
        ):

            text = text.strip()

            if not text:
                continue

            try:
                confidence = float(conf)
            except (ValueError, TypeError):
                continue

            if confidence >= 0:
                words.append(text)
                confidences.append(confidence)

        extracted_text = " ".join(words)

        average_confidence = (
            round(
                sum(confidences) / len(confidences),
                2,
            )
            if confidences
            else 0.0
        )

        return (
            extracted_text,
            average_confidence,
        )

    def _extract_from_image(
        self,
        image_bytes: bytes,
    ) -> OCRResult:
        """
        Perform OCR on a single image.
        """

        try:
            image = Image.open(
                io.BytesIO(image_bytes)
            )

        except Exception as exc:
            raise ValidationError(
                "Unable to open image."
            ) from exc

        image = self._preprocess_image(image)

        text, confidence = self._run_tesseract(
            image
        )

        return OCRResult(
            text=text,
            confidence=confidence,
            page_count=1,
            processing_time_ms=0,
        )

    def _extract_from_pdf(
        self,
        pdf_bytes: bytes,
    ) -> OCRResult:
        """
        Perform OCR on every page of a PDF.
        """

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=True,
        ) as pdf_file:

            pdf_file.write(pdf_bytes)
            pdf_file.flush()

            pages = convert_from_path(
                pdf_file.name,
                dpi=300,
            )

        texts = []
        confidences = []

        for page in pages:

            page = self._preprocess_image(page)

            text, confidence = self._run_tesseract(
                page
            )

            texts.append(text)
            confidences.append(confidence)

        average_confidence = (
            round(
                sum(confidences) / len(confidences),
                2,
            )
            if confidences
            else 0.0
        )

        return OCRResult(
            text="\n\n".join(texts),
            confidence=average_confidence,
            page_count=len(pages),
            processing_time_ms=0,
        )