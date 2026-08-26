"""
SevaSetu AI — Document OCR & Field Extraction Engine
Author: Rahul Jha | Made in India 🇮🇳

Capabilities:
- PDF / Image OCR using Tesseract (English + Hindi + Marathi)
- Intelligent field extraction (name, DOB, Aadhaar, address, etc.)
- Document type detection (Aadhaar, PAN, Voter ID, etc.)
- Checklist generation for missing fields
- Document verification scoring
"""

import re
import io
import logging
import asyncio
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import fitz  # PyMuPDF
import cv2
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ExtractedFields:
    """Structured output from OCR extraction."""
    document_type: str
    confidence: float
    fields: dict
    raw_text: str
    is_valid: bool
    missing_fields: list
    verification_score: float


class DocumentOCREngine:
    """
    Handles all document processing:
    upload → preprocess → OCR → extract → verify → checklist
    """

    # Aadhaar: 12-digit number in groups
    AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
    # PAN: 5 letters, 4 digits, 1 letter
    PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
    # Voter ID: 3 letters + 7 digits
    VOTER_ID_PATTERN = re.compile(r"\b[A-Z]{3}[0-9]{7}\b")
    # Date in various formats
    DATE_PATTERN = re.compile(
        r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b"
    )
    # Indian mobile number
    MOBILE_PATTERN = re.compile(r"\b[6-9]\d{9}\b")
    # PIN code
    PIN_PATTERN = re.compile(r"\b[1-9][0-9]{5}\b")

    # Document-type keyword mapping
    DOC_TYPE_KEYWORDS = {
        "aadhaar": ["aadhaar", "aadhar", "uid", "unique identification", "uidai"],
        "pan": ["permanent account number", "income tax", "pan card"],
        "voter_id": ["election commission", "epic", "electoral", "voter", "photo voter"],
        "passport": ["republic of india", "passport", "passaport"],
        "birth_certificate": ["birth certificate", "birth registration", "born"],
        "income_certificate": ["income certificate", "annual income", "income proof"],
        "caste_certificate": ["caste certificate", "sc", "st", "obc", "backward class"],
        "domicile": ["domicile certificate", "residence certificate"],
        "driving_license": ["driving licence", "dlno", "transport"],
        "ration_card": ["ration card", "national food", "nfsa"],
    }

    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance image quality for better OCR accuracy.
        Steps: grayscale → denoise → contrast → sharpen → threshold
        """
        # Convert PIL to OpenCV
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # Sharpen
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)

        # Adaptive threshold for better text binarization
        thresh = cv2.adaptiveThreshold(
            sharpened, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Convert back to PIL
        return Image.fromarray(thresh)

    async def extract_from_image(
        self, image_path: str, lang: str = "eng+hin+mar"
    ) -> ExtractedFields:
        """Run OCR on a single image file."""
        try:
            logger.info(f"🔍 Running OCR on image: {image_path}")
            image = Image.open(image_path)
            processed = self._preprocess_image(image)

            # Run Tesseract OCR
            raw_text = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pytesseract.image_to_string(
                    processed,
                    lang=lang,
                    config="--psm 6 --oem 3",  # Uniform block, LSTM engine
                ),
            )

            return self._extract_fields(raw_text)

        except Exception as e:
            logger.error(f"❌ OCR failed for {image_path}: {e}")
            return ExtractedFields(
                document_type="unknown", confidence=0.0, fields={},
                raw_text="", is_valid=False, missing_fields=[], verification_score=0.0
            )

    async def extract_from_pdf(self, pdf_path: str) -> ExtractedFields:
        """Extract text from PDF — first try native text, then OCR each page."""
        try:
            logger.info(f"📄 Processing PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            full_text = ""

            for page_num, page in enumerate(doc):
                # Try native text extraction first (fast)
                text = page.get_text("text")
                if len(text.strip()) > 50:
                    full_text += text + "\n"
                else:
                    # Fallback to image-based OCR
                    logger.info(f"  → Page {page_num+1}: using image OCR")
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    processed = self._preprocess_image(img)
                    text = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: pytesseract.image_to_string(processed, lang="eng+hin+mar"),
                    )
                    full_text += text + "\n"

            doc.close()
            return self._extract_fields(full_text)

        except Exception as e:
            logger.error(f"❌ PDF OCR failed: {e}")
            return ExtractedFields(
                document_type="unknown", confidence=0.0, fields={},
                raw_text="", is_valid=False, missing_fields=[], verification_score=0.0
            )

    def _detect_document_type(self, text: str) -> tuple[str, float]:
        """Detect document type from OCR text using keyword matching."""
        text_lower = text.lower()
        scores = {}

        for doc_type, keywords in self.DOC_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[doc_type] = score / len(keywords)

        if not scores:
            return "unknown", 0.0

        best_type = max(scores, key=scores.get)
        return best_type, min(scores[best_type] * 2, 1.0)

    def _extract_fields(self, raw_text: str) -> ExtractedFields:
        """Extract structured fields from raw OCR text."""
        text = raw_text.strip()
        fields = {}
        missing_fields = []

        # Detect document type
        doc_type, type_confidence = self._detect_document_type(text)

        # ── Common extractions ───────────────────────────────────────────────

        # Aadhaar number
        aadhaar_matches = self.AADHAAR_PATTERN.findall(text)
        if aadhaar_matches:
            num = aadhaar_matches[0].replace(" ", "")
            # Mask for privacy: XXXX XXXX 1234
            fields["aadhaar_number"] = f"XXXX XXXX {num[-4:]}"
        else:
            missing_fields.append("Aadhaar Number")

        # PAN number
        pan_matches = self.PAN_PATTERN.findall(text.upper())
        if pan_matches:
            fields["pan_number"] = pan_matches[0]

        # Voter ID
        voter_matches = self.VOTER_ID_PATTERN.findall(text.upper())
        if voter_matches:
            fields["voter_id"] = voter_matches[0]

        # Dates (DOB, issue date, expiry)
        dates = self.DATE_PATTERN.findall(text)
        if dates:
            fields["date"] = dates[0]
            if len(dates) > 1:
                fields["date_of_birth"] = dates[0]
                fields["issue_date"] = dates[1] if len(dates) > 1 else None
                fields["expiry_date"] = dates[2] if len(dates) > 2 else None

        # Mobile number
        mobile_matches = self.MOBILE_PATTERN.findall(text)
        if mobile_matches:
            fields["mobile"] = mobile_matches[0]

        # PIN code
        pin_matches = self.PIN_PATTERN.findall(text)
        if pin_matches:
            fields["pin_code"] = pin_matches[0]

        # Name extraction (line after "Name:" or standalone capitalized line)
        name_match = re.search(r"(?:Name|नाम|नाव)\s*[:\-]\s*([A-Z][A-Za-z\s]{2,40})", text)
        if name_match:
            fields["name"] = name_match.group(1).strip()

        # Gender
        gender_match = re.search(r"\b(Male|Female|M|F|MALE|FEMALE|पुरुष|महिला)\b", text)
        if gender_match:
            g = gender_match.group(1).upper()
            fields["gender"] = "Male" if g in ["M", "MALE", "पुरुष"] else "Female"

        # Address extraction (multi-line after "Address:")
        addr_match = re.search(
            r"(?:Address|पता|Address:)\s*[:\-]?\s*(.{20,200}?)(?:\n\n|\Z)",
            text, re.DOTALL
        )
        if addr_match:
            fields["address"] = addr_match.group(1).strip().replace("\n", ", ")

        # ── Document-specific validation ─────────────────────────────────────
        required = self._get_required_fields(doc_type)
        missing_fields += [f for f in required if f not in fields]

        # Calculate verification score
        if required:
            present = sum(1 for f in required if f in fields)
            verification_score = present / len(required)
        else:
            verification_score = 0.7 if fields else 0.0

        is_valid = verification_score >= 0.6

        return ExtractedFields(
            document_type=doc_type,
            confidence=type_confidence,
            fields=fields,
            raw_text=text[:2000],  # Truncate for storage
            is_valid=is_valid,
            missing_fields=list(set(missing_fields)),
            verification_score=round(verification_score, 3),
        )

    def _get_required_fields(self, doc_type: str) -> list:
        """Return required fields for each document type."""
        required_map = {
            "aadhaar": ["name", "date_of_birth", "aadhaar_number", "gender", "address"],
            "pan": ["name", "pan_number", "date_of_birth"],
            "voter_id": ["name", "voter_id", "date_of_birth", "address"],
            "passport": ["name", "date_of_birth", "issue_date", "expiry_date"],
            "birth_certificate": ["name", "date"],
            "income_certificate": ["name", "address"],
            "caste_certificate": ["name", "address"],
            "domicile": ["name", "address"],
            "driving_license": ["name", "date_of_birth", "date"],
        }
        return required_map.get(doc_type, ["name"])

    def generate_checklist(
        self, service_type: str, uploaded_doc_fields: Optional[dict] = None
    ) -> dict:
        """Generate document checklist for a specific government service."""
        checklists = {
            "voter_id_new": {
                "title": "Voter ID Registration (Form 6)",
                "documents": [
                    {"name": "Aadhaar Card", "status": "required", "purpose": "Identity + Address Proof"},
                    {"name": "Recent Passport Photo", "status": "required", "purpose": "Photo ID"},
                    {"name": "Age Proof", "status": "required", "purpose": "DOB verification (Birth Certificate / 10th Marksheet)"},
                    {"name": "Address Proof", "status": "optional", "purpose": "If Aadhaar address differs"},
                ],
                "online_portal": "voters.eci.gov.in",
                "helpline": "1950",
                "form": "Form 6",
            },
            "voter_id_correction": {
                "title": "Voter ID Correction (Form 8)",
                "documents": [
                    {"name": "Current Voter ID", "status": "required", "purpose": "Existing EPIC card"},
                    {"name": "Proof of Correct Information", "status": "required", "purpose": "Aadhaar / PAN / School Certificate"},
                    {"name": "Passport Photo", "status": "required", "purpose": "Updated photo"},
                ],
                "online_portal": "voters.eci.gov.in",
                "helpline": "1950",
                "form": "Form 8",
            },
            "pan_card": {
                "title": "PAN Card Application (Form 49A)",
                "documents": [
                    {"name": "Aadhaar Card", "status": "required", "purpose": "POI + POA"},
                    {"name": "Date of Birth Proof", "status": "required", "purpose": "Birth Certificate / 10th Marksheet"},
                    {"name": "2 Passport Photos", "status": "required", "purpose": "Identity"},
                    {"name": "Signature Scan", "status": "required", "purpose": "For PAN card"},
                ],
                "online_portal": "tin.tin.nsdl.com",
                "helpline": "020-27218080",
                "form": "Form 49A",
                "fee": "₹107",
            },
            "passport": {
                "title": "Passport Application (Fresh)",
                "documents": [
                    {"name": "Aadhaar Card", "status": "required", "purpose": "Mandatory"},
                    {"name": "Birth Certificate", "status": "required", "purpose": "DOB Proof"},
                    {"name": "10th Certificate", "status": "required", "purpose": "Educational qualification"},
                    {"name": "Address Proof", "status": "required", "purpose": "Utility bill / Bank statement"},
                    {"name": "2 Passport Photos", "status": "required", "purpose": "White background"},
                    {"name": "Fee Receipt", "status": "required", "purpose": "Payment confirmation"},
                ],
                "online_portal": "passportindia.gov.in",
                "helpline": "1800-258-1800",
                "form": "Form-1",
                "fee": "₹1,500 (36 pages) / ₹2,000 (60 pages)",
            },
            "income_certificate": {
                "title": "Income Certificate",
                "documents": [
                    {"name": "Aadhaar Card", "status": "required", "purpose": "Identity proof"},
                    {"name": "Ration Card", "status": "required", "purpose": "Family details"},
                    {"name": "Salary Slips (3 months)", "status": "required", "purpose": "Income evidence"},
                    {"name": "Bank Statement", "status": "required", "purpose": "Last 6 months"},
                    {"name": "Self-Declaration Affidavit", "status": "required", "purpose": "On stamp paper"},
                    {"name": "Application Form", "status": "required", "purpose": "From Tehsildar office"},
                ],
                "online_portal": "aaplesarkar.mahaonline.gov.in",
                "helpline": "1800-120-8040",
                "fee": "₹20-50",
            },
            "birth_certificate": {
                "title": "Birth Certificate",
                "documents": [
                    {"name": "Hospital Discharge Summary", "status": "required", "purpose": "Proof of birth"},
                    {"name": "Parent's Aadhaar Cards", "status": "required", "purpose": "Identity of parents"},
                    {"name": "Ration Card", "status": "required", "purpose": "Family proof"},
                    {"name": "Application Form", "status": "required", "purpose": "From Municipal Office"},
                    {"name": "Affidavit (delayed registration)", "status": "conditional", "purpose": "If > 21 days"},
                ],
                "online_portal": "aaplesarkar.mahaonline.gov.in",
                "helpline": "1800-233-4444",
                "fee": "₹0 (within 21 days) / ₹50+ (delayed)",
            },
        }
        result = checklists.get(service_type, {"title": "Unknown Service", "documents": []})

        # Mark items as completed if documents were uploaded
        if uploaded_doc_fields:
            for doc in result.get("documents", []):
                # Simple heuristic: if Aadhaar uploaded and Aadhaar required, mark done
                if "Aadhaar" in doc["name"] and uploaded_doc_fields.get("aadhaar_number"):
                    doc["status"] = "completed"

        return result


# Singleton
ocr_engine = DocumentOCREngine()
