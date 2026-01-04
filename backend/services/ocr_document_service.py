"""
OCR Document Extraction Service for ShareYourSales
Extract text and data from identity documents using OCR

Dependencies:
    pip install google-cloud-vision pytesseract pillow

Environment Variables:
    GOOGLE_CLOUD_VISION_API_KEY: Google Cloud Vision API key
    GOOGLE_APPLICATION_CREDENTIALS: Path to Google service account JSON

Features:
    - Extract text from images (passports, IDs, driver's licenses)
    - Parse structured document data
    - Multiple OCR providers (Google Vision, Tesseract)
    - Document type detection
    - Data validation
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import base64

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logging.warning("google-cloud-vision not installed. Run: pip install google-cloud-vision")

try:
    import pytesseract
    from PIL import Image
    import io
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not installed. Run: pip install pytesseract pillow")


logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    """Supported document types"""
    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    DRIVER_LICENSE = "driver_license"
    RESIDENCE_PERMIT = "residence_permit"
    UNKNOWN = "unknown"


@dataclass
class ExtractedDocument:
    """Extracted document data"""
    document_type: DocumentType
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    document_number: Optional[str] = None
    expiry_date: Optional[str] = None
    issue_date: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    raw_text: Optional[str] = None
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class OCRDocumentService:
    """
    OCR document extraction service

    Supports:
    - Google Cloud Vision API
    - Tesseract OCR (fallback)
    - Document parsing and validation

    Example:
        service = OCRDocumentService()

        # Extract from image file
        result = service.extract_from_file("/path/to/id.jpg")

        # Extract from base64
        result = service.extract_from_base64(base64_string)

        print(f"Name: {result.full_name}")
        print(f"ID Number: {result.document_number}")
    """

    def __init__(
        self,
        provider: str = "google",  # "google" or "tesseract"
        credentials_path: Optional[str] = None
    ):
        """
        Initialize OCR service

        Args:
            provider: OCR provider to use
            credentials_path: Path to Google Cloud credentials
        """
        self.provider = provider

        if provider == "google":
            if not GOOGLE_VISION_AVAILABLE:
                raise ImportError("google-cloud-vision required. Run: pip install google-cloud-vision")

            # Set credentials if provided
            if credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            elif not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set")

            try:
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("Google Cloud Vision initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Vision: {e}")
                self.vision_client = None

        elif provider == "tesseract":
            if not TESSERACT_AVAILABLE:
                raise ImportError("pytesseract required. Run: pip install pytesseract pillow")

            logger.info("Tesseract OCR initialized")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    # ===== OCR Extraction =====

    def extract_from_file(self, file_path: str) -> ExtractedDocument:
        """
        Extract text from image file

        Args:
            file_path: Path to image file

        Returns:
            Extracted document data
        """
        with open(file_path, "rb") as f:
            content = f.read()

        return self.extract_from_bytes(content)

    def extract_from_base64(self, base64_string: str) -> ExtractedDocument:
        """
        Extract text from base64-encoded image

        Args:
            base64_string: Base64-encoded image

        Returns:
            Extracted document data
        """
        content = base64.b64decode(base64_string)
        return self.extract_from_bytes(content)

    def extract_from_bytes(self, image_bytes: bytes) -> ExtractedDocument:
        """
        Extract text from image bytes

        Args:
            image_bytes: Image bytes

        Returns:
            Extracted document data
        """
        if self.provider == "google":
            return self._extract_google_vision(image_bytes)
        elif self.provider == "tesseract":
            return self._extract_tesseract(image_bytes)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _extract_google_vision(self, image_bytes: bytes) -> ExtractedDocument:
        """Extract using Google Cloud Vision"""
        if not self.vision_client:
            raise ValueError("Google Vision client not initialized")

        # Create image object
        image = vision.Image(content=image_bytes)

        # Perform text detection
        response = self.vision_client.text_detection(image=image)

        if response.error.message:
            raise Exception(f"Google Vision error: {response.error.message}")

        texts = response.text_annotations

        if not texts:
            return ExtractedDocument(
                document_type=DocumentType.UNKNOWN,
                raw_text="",
                confidence=0.0
            )

        # First annotation contains full text
        full_text = texts[0].description
        confidence = texts[0].confidence if hasattr(texts[0], 'confidence') else 0.9

        # Parse document
        return self._parse_document_text(full_text, confidence)

    def _extract_tesseract(self, image_bytes: bytes) -> ExtractedDocument:
        """Extract using Tesseract OCR"""
        # Load image
        image = Image.open(io.BytesIO(image_bytes))

        # Perform OCR
        text = pytesseract.image_to_string(image)

        # Parse document
        return self._parse_document_text(text, 0.8)  # Tesseract has lower confidence

    # ===== Document Parsing =====

    def _parse_document_text(
        self,
        text: str,
        confidence: float
    ) -> ExtractedDocument:
        """
        Parse extracted text into structured data

        Args:
            text: Raw OCR text
            confidence: OCR confidence score

        Returns:
            Parsed document
        """
        # Detect document type
        document_type = self._detect_document_type(text)

        # Extract fields
        extracted = ExtractedDocument(
            document_type=document_type,
            raw_text=text,
            confidence=confidence
        )

        # Extract name
        names = self._extract_names(text)
        if names:
            extracted.full_name = names.get("full_name")
            extracted.first_name = names.get("first_name")
            extracted.last_name = names.get("last_name")

        # Extract dates
        dates = self._extract_dates(text)
        extracted.date_of_birth = dates.get("date_of_birth")
        extracted.expiry_date = dates.get("expiry_date")
        extracted.issue_date = dates.get("issue_date")

        # Extract document number
        extracted.document_number = self._extract_document_number(text, document_type)

        # Extract nationality
        extracted.nationality = self._extract_nationality(text)

        # Extract gender
        extracted.gender = self._extract_gender(text)

        # Extract address (for some documents)
        if document_type in [DocumentType.DRIVER_LICENSE, DocumentType.NATIONAL_ID]:
            extracted.address = self._extract_address(text)

        return extracted

    def _detect_document_type(self, text: str) -> DocumentType:
        """Detect document type from text"""
        text_upper = text.upper()

        if any(keyword in text_upper for keyword in ["PASSPORT", "PASSEPORT", "PASAPORTE"]):
            return DocumentType.PASSPORT

        if any(keyword in text_upper for keyword in ["NATIONAL ID", "IDENTITY CARD", "CARTE D'IDENTITÉ", "CIN"]):
            return DocumentType.NATIONAL_ID

        if any(keyword in text_upper for keyword in ["DRIVER", "DRIVING", "PERMIS DE CONDUIRE", "LICENSE"]):
            return DocumentType.DRIVER_LICENSE

        if any(keyword in text_upper for keyword in ["RESIDENCE", "SÉJOUR", "RESIDENCIA"]):
            return DocumentType.RESIDENCE_PERMIT

        return DocumentType.UNKNOWN

    def _extract_names(self, text: str) -> Dict[str, str]:
        """Extract names from text"""
        names = {}

        # Common patterns for names
        # Pattern 1: "Name: JOHN DOE"
        name_match = re.search(r"(?:NAME|NOM|NOMBRE)[:\s]+([A-Z\s]{2,50})", text, re.IGNORECASE)
        if name_match:
            full_name = name_match.group(1).strip()
            names["full_name"] = full_name

            # Split into first and last
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                names["first_name"] = name_parts[0]
                names["last_name"] = " ".join(name_parts[1:])

        # Pattern 2: "Given Names: JOHN"
        first_match = re.search(r"(?:GIVEN NAMES?|PRENOM|FIRST NAME)[:\s]+([A-Z\s]{2,30})", text, re.IGNORECASE)
        if first_match:
            names["first_name"] = first_match.group(1).strip()

        # Pattern 3: "Surname: DOE"
        last_match = re.search(r"(?:SURNAME|NOM DE FAMILLE|LAST NAME)[:\s]+([A-Z\s]{2,30})", text, re.IGNORECASE)
        if last_match:
            names["last_name"] = last_match.group(1).strip()

        # Construct full name if we have parts
        if not names.get("full_name") and names.get("first_name") and names.get("last_name"):
            names["full_name"] = f"{names['first_name']} {names['last_name']}"

        return names

    def _extract_dates(self, text: str) -> Dict[str, str]:
        """Extract dates from text"""
        dates = {}

        # Pattern for dates: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
        date_pattern = r"(\d{1,2}[\s/.-]\d{1,2}[\s/.-]\d{4})"

        # Date of birth
        dob_match = re.search(r"(?:DATE OF BIRTH|DOB|NÉ LE|NAISSANCE)[:\s]*" + date_pattern, text, re.IGNORECASE)
        if dob_match:
            dates["date_of_birth"] = dob_match.group(1).strip()

        # Expiry date
        expiry_match = re.search(r"(?:EXPIRY|EXPIRES?|EXPIRATION|EXPIRE LE)[:\s]*" + date_pattern, text, re.IGNORECASE)
        if expiry_match:
            dates["expiry_date"] = expiry_match.group(1).strip()

        # Issue date
        issue_match = re.search(r"(?:ISSUE DATE|ISSUED|DÉLIVRÉ LE)[:\s]*" + date_pattern, text, re.IGNORECASE)
        if issue_match:
            dates["issue_date"] = issue_match.group(1).strip()

        return dates

    def _extract_document_number(self, text: str, doc_type: DocumentType) -> Optional[str]:
        """Extract document number"""
        # Different patterns for different document types
        if doc_type == DocumentType.PASSPORT:
            # Passport numbers are usually alphanumeric, 6-9 characters
            match = re.search(r"(?:PASSPORT NO\.?|P<)[:\s]*([A-Z0-9]{6,9})", text, re.IGNORECASE)
        elif doc_type == DocumentType.NATIONAL_ID:
            # National ID patterns vary by country
            match = re.search(r"(?:ID NO\.?|CARD NO\.?|N°)[:\s]*([A-Z0-9]{5,15})", text, re.IGNORECASE)
        elif doc_type == DocumentType.DRIVER_LICENSE:
            # Driver's license number
            match = re.search(r"(?:LICENSE NO\.?|DL NO\.?)[:\s]*([A-Z0-9]{5,15})", text, re.IGNORECASE)
        else:
            # Generic document number
            match = re.search(r"(?:DOCUMENT NO\.?|NO\.?)[:\s]*([A-Z0-9]{5,15})", text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return None

    def _extract_nationality(self, text: str) -> Optional[str]:
        """Extract nationality"""
        match = re.search(r"(?:NATIONALITY|NATIONALITÉ)[:\s]*([A-Z]{2,30})", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def _extract_gender(self, text: str) -> Optional[str]:
        """Extract gender"""
        # Look for M/F or Male/Female
        match = re.search(r"(?:SEX|GENDER|SEXE)[:\s]*(M|F|MALE|FEMALE)", text, re.IGNORECASE)
        if match:
            gender = match.group(1).upper()
            if gender in ["M", "MALE"]:
                return "M"
            elif gender in ["F", "FEMALE"]:
                return "F"

        return None

    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address"""
        # Address extraction is complex and varies by country
        # Look for common address keywords
        match = re.search(r"(?:ADDRESS|ADRESSE)[:\s]*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    # ===== Validation =====

    def validate_document(self, document: ExtractedDocument) -> Dict[str, Any]:
        """
        Validate extracted document data

        Args:
            document: Extracted document

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        # Check required fields
        if not document.full_name and not (document.first_name and document.last_name):
            errors.append("Name is required")

        if not document.document_number:
            errors.append("Document number is required")

        if not document.date_of_birth:
            warnings.append("Date of birth not found")

        if not document.expiry_date:
            warnings.append("Expiry date not found")

        # Validate expiry date
        if document.expiry_date:
            try:
                expiry = datetime.strptime(document.expiry_date.replace("/", "-").replace(".", "-"), "%d-%m-%Y")
                if expiry < datetime.now():
                    errors.append("Document has expired")
            except:
                warnings.append("Could not parse expiry date")

        # Check confidence
        if document.confidence < 0.7:
            warnings.append("Low OCR confidence - manual review recommended")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "confidence": document.confidence
        }


# ===== Usage Example =====
if __name__ == "__main__":
    service = OCRDocumentService(provider="google")

    # Extract from file
    result = service.extract_from_file("/path/to/passport.jpg")

    print(f"Document Type: {result.document_type}")
    print(f"Name: {result.full_name}")
    print(f"Document Number: {result.document_number}")
    print(f"Date of Birth: {result.date_of_birth}")
    print(f"Expiry Date: {result.expiry_date}")
    print(f"Confidence: {result.confidence}")

    # Validate
    validation = service.validate_document(result)
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
    print(f"Warnings: {validation['warnings']}")
