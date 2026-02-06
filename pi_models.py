from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re


class PIType(Enum):
    """Enumeration of different types of Personal Information"""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    DOB = "date_of_birth"
    SSN = "social_security_number"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"


class PISeverity(Enum):
    """Severity levels for PI data exposure"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PIPattern:
    """Pattern definition for detecting PI data"""
    pi_type: PIType
    pattern: str
    description: str
    severity: PISeverity
    examples: List[str]


@dataclass
class PIMatch:
    """Represents a detected PI match in text"""
    pi_type: PIType
    matched_text: str
    start_position: int
    end_position: int
    pattern_used: str
    severity: PISeverity
    confidence: float  # 0.0 to 1.0


@dataclass
class PIRemovalResult:
    """Result of PI removal operation"""
    original_text: str
    processed_text: str
    removed_matches: List[PIMatch]
    removal_method: str
    success: bool
    remaining_pi_count: int


@dataclass
class PIValidationResult:
    """Result of PI validation operation"""
    is_valid: bool
    validation_score: float  # 0.0 to 1.0
    remaining_matches: List[PIMatch]
    recommendations: List[str]


class PIConstants:
    """Constants for PI detection and removal"""
    
    # PI Patterns
    PATTERNS = {
        PIType.EMAIL: [
            PIPattern(
                pi_type=PIType.EMAIL,
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                description="Email address pattern",
                severity=PISeverity.MEDIUM,
                examples=["john.doe@example.com", "user+tag@domain.org"]
            )
        ],
        
        PIType.PHONE: [
            PIPattern(
                pi_type=PIType.PHONE,
                pattern=r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                description="US phone number pattern",
                severity=PISeverity.MEDIUM,
                examples=["(555) 123-4567", "555.123.4567", "+1-555-123-4567"]
            ),
            PIPattern(
                pi_type=PIType.PHONE,
                pattern=r'\b(?:\+?91[-.\s]?)?([0-9]{5})[-.\s]?([0-9]{5})\b',
                description="Indian phone number pattern",
                severity=PISeverity.MEDIUM,
                examples=["98765-43210", "+91-98765-43210"]
            )
        ],
        
        PIType.DOB: [
            PIPattern(
                pi_type=PIType.DOB,
                pattern=r'\b(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/([0-9]{4})\b',
                description="Date of birth in MM/DD/YYYY format",
                severity=PISeverity.HIGH,
                examples=["12/25/1990", "01/01/2000"]
            ),
            PIPattern(
                pi_type=PIType.DOB,
                pattern=r'\b(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-([0-9]{4})\b',
                description="Date of birth in DD-MM-YYYY format",
                severity=PISeverity.HIGH,
                examples=["25-12-1990", "01-01-2000"]
            ),
            PIPattern(
                pi_type=PIType.DOB,
                pattern=r'\b([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])\b',
                description="Date of birth in YYYY-MM-DD format",
                severity=PISeverity.HIGH,
                examples=["1990-12-25", "2000-01-01"]
            )
        ],
        
        PIType.SSN: [
            PIPattern(
                pi_type=PIType.SSN,
                pattern=r'\b([0-9]{3})-([0-9]{2})-([0-9]{4})\b',
                description="Social Security Number pattern",
                severity=PISeverity.CRITICAL,
                examples=["123-45-6789"]
            )
        ],
        
        PIType.CREDIT_CARD: [
            PIPattern(
                pi_type=PIType.CREDIT_CARD,
                pattern=r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
                description="Credit card number pattern",
                severity=PISeverity.CRITICAL,
                examples=["4111111111111111", "5555555555554444"]
            )
        ],
        
        PIType.NAME: [
            PIPattern(
                pi_type=PIType.NAME,
                pattern=r'\b(?:Mr|Mrs|Ms|Dr)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                description="Full name with title pattern",
                severity=PISeverity.HIGH,
                examples=["Mr. John Doe", "Dr. Jane Smith"]
            ),
            PIPattern(
                pi_type=PIType.NAME,
                pattern=r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                description="Full name pattern (first + last)",
                severity=PISeverity.HIGH,
                examples=["John Doe", "Jane Smith"]
            )
        ]
    }
    
    # Masking patterns
    MASKING_PATTERNS = {
        PIType.EMAIL: lambda match: f"[EMAIL_REDACTED_{len(match)}]",
        PIType.PHONE: lambda match: f"[PHONE_REDACTED]",
        PIType.DOB: lambda match: "[DOB_REDACTED]",
        PIType.SSN: lambda match: "[SSN_REDACTED]",
        PIType.CREDIT_CARD: lambda match: "[CC_REDACTED]",
        PIType.NAME: lambda match: "[NAME_REDACTED]"
    }
    
    # Confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        PIType.EMAIL: 0.9,
        PIType.PHONE: 0.8,
        PIType.DOB: 0.7,
        PIType.SSN: 0.95,
        PIType.CREDIT_CARD: 0.9,
        PIType.NAME: 0.6
    }
