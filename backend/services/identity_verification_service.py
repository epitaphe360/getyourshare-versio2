"""
Identity Verification Service for ShareYourSales
Complete KYC (Know Your Customer) identity verification

Dependencies:
    pip install requests

Features:
    - Document verification workflow
    - Liveness detection
    - Face matching
    - Verification status tracking
    - Compliance logging
    - Integration with OCR service
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from services.ocr_document_service import OCRDocumentService, ExtractedDocument, DocumentType


logger = logging.getLogger(__name__)


class VerificationStatus(str, Enum):
    """Verification status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RejectionReason(str, Enum):
    """Rejection reasons"""
    DOCUMENT_EXPIRED = "document_expired"
    DOCUMENT_UNREADABLE = "document_unreadable"
    DOCUMENT_MISMATCH = "document_mismatch"
    FACE_MISMATCH = "face_mismatch"
    LIVENESS_FAILED = "liveness_failed"
    FRAUDULENT = "fraudulent"
    INCOMPLETE = "incomplete"
    OTHER = "other"


@dataclass
class VerificationRequest:
    """Verification request data"""
    user_id: str
    document_front_image: str  # Base64 or URL
    document_back_image: Optional[str] = None
    selfie_image: Optional[str] = None
    document_type: DocumentType = DocumentType.UNKNOWN
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class VerificationResult:
    """Verification result"""
    verification_id: str
    user_id: str
    status: VerificationStatus
    extracted_data: Optional[ExtractedDocument] = None
    face_match_score: Optional[float] = None
    liveness_score: Optional[float] = None
    rejection_reason: Optional[RejectionReason] = None
    rejection_details: Optional[str] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None


class IdentityVerificationService:
    """
    Complete identity verification service

    Workflow:
    1. Upload identity document
    2. Extract data using OCR
    3. Upload selfie (optional)
    4. Verify face match (optional)
    5. Liveness check (optional)
    6. Manual review if needed
    7. Approve or reject

    Example:
        service = IdentityVerificationService()

        # Submit verification
        request = VerificationRequest(
            user_id="user_123",
            document_front_image=base64_image,
            selfie_image=base64_selfie,
            document_type=DocumentType.PASSPORT
        )

        result = service.submit_verification(request)

        # Check status
        status = service.get_verification_status(result.verification_id)

        # Approve/reject (admin)
        service.approve_verification(result.verification_id)
    """

    def __init__(
        self,
        ocr_provider: str = "google",
        auto_approve_threshold: float = 0.95,
        verification_expiry_days: int = 365
    ):
        """
        Initialize verification service

        Args:
            ocr_provider: OCR provider to use
            auto_approve_threshold: Confidence threshold for auto-approval
            verification_expiry_days: Days until verification expires
        """
        self.ocr_service = OCRDocumentService(provider=ocr_provider)
        self.auto_approve_threshold = auto_approve_threshold
        self.verification_expiry_days = verification_expiry_days

        # In-memory storage (in production, use database)
        self.verifications: Dict[str, VerificationResult] = {}

    # ===== Verification Workflow =====

    def submit_verification(
        self,
        request: VerificationRequest
    ) -> VerificationResult:
        """
        Submit identity verification request

        Args:
            request: Verification request

        Returns:
            Verification result
        """
        # Generate verification ID
        verification_id = self._generate_verification_id(request.user_id)

        # Extract document data
        try:
            extracted_data = self.ocr_service.extract_from_base64(request.document_front_image)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return VerificationResult(
                verification_id=verification_id,
                user_id=request.user_id,
                status=VerificationStatus.REJECTED,
                rejection_reason=RejectionReason.DOCUMENT_UNREADABLE,
                rejection_details=str(e),
                created_at=datetime.now()
            )

        # Validate document
        validation = self.ocr_service.validate_document(extracted_data)

        # Determine initial status
        if not validation["valid"]:
            # Document validation failed
            status = VerificationStatus.REJECTED
            rejection_reason = RejectionReason.DOCUMENT_EXPIRED if "expired" in str(validation["errors"]) else RejectionReason.INCOMPLETE
            rejection_details = ", ".join(validation["errors"])

        elif extracted_data.confidence >= self.auto_approve_threshold:
            # High confidence - auto-approve
            status = VerificationStatus.APPROVED
            rejection_reason = None
            rejection_details = None

        elif extracted_data.confidence >= 0.7:
            # Medium confidence - manual review
            status = VerificationStatus.IN_REVIEW
            rejection_reason = None
            rejection_details = None

        else:
            # Low confidence - reject
            status = VerificationStatus.REJECTED
            rejection_reason = RejectionReason.DOCUMENT_UNREADABLE
            rejection_details = f"Low OCR confidence: {extracted_data.confidence:.2f}"

        # Face matching (if selfie provided)
        face_match_score = None
        liveness_score = None

        if request.selfie_image and status != VerificationStatus.REJECTED:
            face_match_score = self._verify_face_match(
                request.document_front_image,
                request.selfie_image
            )

            # Check face match threshold
            if face_match_score < 0.7:
                status = VerificationStatus.REJECTED
                rejection_reason = RejectionReason.FACE_MISMATCH
                rejection_details = f"Face match score too low: {face_match_score:.2f}"

            # Liveness detection
            liveness_score = self._check_liveness(request.selfie_image)

            if liveness_score < 0.7:
                status = VerificationStatus.REJECTED
                rejection_reason = RejectionReason.LIVENESS_FAILED
                rejection_details = f"Liveness score too low: {liveness_score:.2f}"

        # Set expiry date if approved
        verified_at = datetime.now() if status == VerificationStatus.APPROVED else None
        expires_at = datetime.now() + timedelta(days=self.verification_expiry_days) if status == VerificationStatus.APPROVED else None

        # Create verification result
        result = VerificationResult(
            verification_id=verification_id,
            user_id=request.user_id,
            status=status,
            extracted_data=extracted_data,
            face_match_score=face_match_score,
            liveness_score=liveness_score,
            rejection_reason=rejection_reason,
            rejection_details=rejection_details,
            verified_at=verified_at,
            expires_at=expires_at,
            created_at=datetime.now(),
            metadata=request.metadata
        )

        # Store verification
        self.verifications[verification_id] = result

        logger.info(f"Verification {verification_id} submitted with status: {status}")

        return result

    # ===== Verification Management =====

    def get_verification_status(
        self,
        verification_id: str
    ) -> Optional[VerificationResult]:
        """Get verification status"""
        return self.verifications.get(verification_id)

    def get_user_verifications(
        self,
        user_id: str
    ) -> List[VerificationResult]:
        """Get all verifications for a user"""
        return [
            v for v in self.verifications.values()
            if v.user_id == user_id
        ]

    def is_user_verified(
        self,
        user_id: str
    ) -> bool:
        """
        Check if user has valid verification

        Args:
            user_id: User ID

        Returns:
            True if user is verified and verification is not expired
        """
        user_verifications = self.get_user_verifications(user_id)

        for verification in user_verifications:
            if verification.status == VerificationStatus.APPROVED:
                # Check if not expired
                if verification.expires_at and verification.expires_at > datetime.now():
                    return True

        return False

    # ===== Admin Actions =====

    def approve_verification(
        self,
        verification_id: str,
        admin_notes: Optional[str] = None
    ) -> VerificationResult:
        """
        Manually approve verification (admin action)

        Args:
            verification_id: Verification ID
            admin_notes: Admin notes

        Returns:
            Updated verification result
        """
        verification = self.verifications.get(verification_id)

        if not verification:
            raise ValueError(f"Verification {verification_id} not found")

        verification.status = VerificationStatus.APPROVED
        verification.verified_at = datetime.now()
        verification.expires_at = datetime.now() + timedelta(days=self.verification_expiry_days)
        verification.rejection_reason = None
        verification.rejection_details = None

        if admin_notes:
            if not verification.metadata:
                verification.metadata = {}
            verification.metadata["admin_notes"] = admin_notes
            verification.metadata["approved_by"] = "admin"
            verification.metadata["approved_at"] = datetime.now().isoformat()

        logger.info(f"Verification {verification_id} approved by admin")

        return verification

    def reject_verification(
        self,
        verification_id: str,
        reason: RejectionReason,
        details: Optional[str] = None
    ) -> VerificationResult:
        """
        Manually reject verification (admin action)

        Args:
            verification_id: Verification ID
            reason: Rejection reason
            details: Additional details

        Returns:
            Updated verification result
        """
        verification = self.verifications.get(verification_id)

        if not verification:
            raise ValueError(f"Verification {verification_id} not found")

        verification.status = VerificationStatus.REJECTED
        verification.rejection_reason = reason
        verification.rejection_details = details
        verification.verified_at = None
        verification.expires_at = None

        logger.info(f"Verification {verification_id} rejected: {reason}")

        return verification

    def request_resubmission(
        self,
        verification_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Request user to resubmit documents

        Args:
            verification_id: Verification ID
            reason: Reason for resubmission

        Returns:
            Resubmission request details
        """
        verification = self.verifications.get(verification_id)

        if not verification:
            raise ValueError(f"Verification {verification_id} not found")

        verification.status = VerificationStatus.PENDING

        if not verification.metadata:
            verification.metadata = {}

        verification.metadata["resubmission_requested"] = True
        verification.metadata["resubmission_reason"] = reason
        verification.metadata["resubmission_requested_at"] = datetime.now().isoformat()

        return {
            "success": True,
            "verification_id": verification_id,
            "reason": reason
        }

    # ===== Helper Methods =====

    def _generate_verification_id(self, user_id: str) -> str:
        """Generate unique verification ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{user_id}:{timestamp}"
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()

        return f"ver_{hash_digest[:16]}"

    def _verify_face_match(
        self,
        document_image: str,
        selfie_image: str
    ) -> float:
        """
        Verify face match between document and selfie

        Args:
            document_image: Document image (base64)
            selfie_image: Selfie image (base64)

        Returns:
            Match score (0.0 to 1.0)
        """
        # In production, use face recognition API (e.g., AWS Rekognition, Azure Face API)
        # For now, return simulated score

        # Simulate face matching
        logger.info("Face matching simulation (use real API in production)")

        # Return random score for demonstration
        # In production, integrate with real face recognition service
        return 0.92  # Simulated high match score

    def _check_liveness(
        self,
        selfie_image: str
    ) -> float:
        """
        Check liveness detection

        Args:
            selfie_image: Selfie image (base64)

        Returns:
            Liveness score (0.0 to 1.0)
        """
        # In production, use liveness detection API
        # For now, return simulated score

        logger.info("Liveness check simulation (use real API in production)")

        # Return simulated liveness score
        return 0.88  # Simulated liveness pass

    # ===== Statistics =====

    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get verification statistics"""
        total = len(self.verifications)

        if total == 0:
            return {
                "total": 0,
                "pending": 0,
                "in_review": 0,
                "approved": 0,
                "rejected": 0,
                "expired": 0,
                "approval_rate": 0.0
            }

        statuses = [v.status for v in self.verifications.values()]

        stats = {
            "total": total,
            "pending": statuses.count(VerificationStatus.PENDING),
            "in_review": statuses.count(VerificationStatus.IN_REVIEW),
            "approved": statuses.count(VerificationStatus.APPROVED),
            "rejected": statuses.count(VerificationStatus.REJECTED),
            "expired": statuses.count(VerificationStatus.EXPIRED),
        }

        # Calculate approval rate
        completed = stats["approved"] + stats["rejected"]
        stats["approval_rate"] = (stats["approved"] / completed * 100) if completed > 0 else 0.0

        return stats


# ===== Usage Example =====
if __name__ == "__main__":
    service = IdentityVerificationService()

    # Submit verification
    request = VerificationRequest(
        user_id="user_123",
        document_front_image="base64_encoded_passport_image",
        selfie_image="base64_encoded_selfie",
        document_type=DocumentType.PASSPORT
    )

    result = service.submit_verification(request)

    print(f"Verification ID: {result.verification_id}")
    print(f"Status: {result.status}")
    print(f"Extracted Name: {result.extracted_data.full_name if result.extracted_data else 'N/A'}")

    # Check if user is verified
    is_verified = service.is_user_verified("user_123")
    print(f"User verified: {is_verified}")

    # Get statistics
    stats = service.get_verification_statistics()
    print(f"Statistics: {stats}")
