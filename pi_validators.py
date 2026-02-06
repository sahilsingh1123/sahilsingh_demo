import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set
from pi_models import PIType, PIMatch, PIValidationResult, PIConstants
from pi_checkers import PICheckerFactory


class BasePIValidator(ABC):
    """Abstract base class for PI validators"""
    
    def __init__(self, pi_type: PIType):
        self.pi_type = pi_type
        self.checker = PICheckerFactory.create_checker(pi_type)
    
    @abstractmethod
    def validate(self, original_text: str, processed_text: str) -> PIValidationResult:
        """Validate that PI has been properly removed from processed text"""
        pass
    
    def _check_remaining_pi(self, text: str) -> List[PIMatch]:
        """Check for remaining PI in text"""
        return self.checker.check(text)
    
    def _calculate_validation_score(self, original_matches: List[PIMatch], remaining_matches: List[PIMatch]) -> float:
        """Calculate validation score based on removal effectiveness"""
        if not original_matches:
            return 1.0  # No PI to remove, perfect score
        
        removed_count = len(original_matches) - len(remaining_matches)
        removal_rate = removed_count / len(original_matches)
        
        # Consider severity of remaining PI
        severity_penalty = 0.0
        for match in remaining_matches:
            if match.severity.value == "critical":
                severity_penalty += 0.3
            elif match.severity.value == "high":
                severity_penalty += 0.2
            elif match.severity.value == "medium":
                severity_penalty += 0.1
        
        # Adjust score based on severity penalty
        final_score = max(0.0, removal_rate - severity_penalty)
        return min(1.0, final_score)
    
    def _generate_recommendations(self, remaining_matches: List[PIMatch]) -> List[str]:
        """Generate recommendations for improving PI removal"""
        recommendations = []
        
        if not remaining_matches:
            return recommendations
        
        # Group by PI type
        pi_type_counts = {}
        for match in remaining_matches:
            pi_type_counts[match.pi_type] = pi_type_counts.get(match.pi_type, 0) + 1
        
        # Generate specific recommendations
        for pi_type, count in pi_type_counts.items():
            if pi_type == PIType.EMAIL:
                recommendations.append(f"Consider using stricter email pattern matching to remove {count} remaining email(s)")
            elif pi_type == PIType.PHONE:
                recommendations.append(f"Update phone number patterns to catch {count} remaining phone number(s)")
            elif pi_type == PIType.DOB:
                recommendations.append(f"Enhance date pattern detection to remove {count} remaining date(s)")
            elif pi_type == PIType.SSN:
                recommendations.append(f"Critical: {count} SSN(s) still present - use complete removal method")
            elif pi_type == PIType.CREDIT_CARD:
                recommendations.append(f"Critical: {count} credit card number(s) still present - use complete removal method")
            elif pi_type == PIType.NAME:
                recommendations.append(f"Consider using name dictionary validation to remove {count} remaining name(s)")
        
        # General recommendations
        high_severity_remaining = [m for m in remaining_matches if m.severity.value in ["critical", "high"]]
        if high_severity_remaining:
            recommendations.append("Use complete removal method for high-severity PI data")
        
        return recommendations


class BasicPIValidator(BasePIValidator):
    """Basic validator that checks if PI patterns are still present"""
    
    def __init__(self, pi_type: PIType):
        super().__init__(pi_type)
    
    def validate(self, original_text: str, processed_text: str) -> PIValidationResult:
        """Basic validation - check if any PI patterns remain"""
        original_matches = self._check_remaining_pi(original_text)
        remaining_matches = self._check_remaining_pi(processed_text)
        
        # Filter matches for this PI type
        original_filtered = [m for m in original_matches if m.pi_type == self.pi_type]
        remaining_filtered = [m for m in remaining_matches if m.pi_type == self.pi_type]
        
        validation_score = self._calculate_validation_score(original_filtered, remaining_filtered)
        is_valid = len(remaining_filtered) == 0
        recommendations = self._generate_recommendations(remaining_filtered)
        
        return PIValidationResult(
            is_valid=is_valid,
            validation_score=validation_score,
            remaining_matches=remaining_filtered,
            recommendations=recommendations
        )


class StrictPIValidator(BasePIValidator):
    """Strict validator with additional checks"""
    
    def __init__(self, pi_type: PIType):
        super().__init__(pi_type)
    
    def validate(self, original_text: str, processed_text: str) -> PIValidationResult:
        """Strict validation with additional checks"""
        original_matches = self._check_remaining_pi(original_text)
        remaining_matches = self._check_remaining_pi(processed_text)
        
        # Filter matches for this PI type
        original_filtered = [m for m in original_matches if m.pi_type == self.pi_type]
        remaining_filtered = [m for m in remaining_matches if m.pi_type == self.pi_type]
        
        # Additional strict checks
        strict_violations = self._strict_checks(processed_text)
        all_remaining = remaining_filtered + strict_violations
        
        validation_score = self._calculate_validation_score(original_filtered, all_remaining)
        is_valid = len(all_remaining) == 0
        recommendations = self._generate_recommendations(all_remaining)
        
        return PIValidationResult(
            is_valid=is_valid,
            validation_score=validation_score,
            remaining_matches=all_remaining,
            recommendations=recommendations
        )
    
    def _strict_checks(self, text: str) -> List[PIMatch]:
        """Additional strict validation checks"""
        violations = []
        
        if self.pi_type == PIType.EMAIL:
            violations.extend(self._strict_email_checks(text))
        elif self.pi_type == PIType.PHONE:
            violations.extend(self._strict_phone_checks(text))
        elif self.pi_type == PIType.SSN:
            violations.extend(self._strict_ssn_checks(text))
        elif self.pi_type == PIType.CREDIT_CARD:
            violations.extend(self._strict_credit_card_checks(text))
        
        return violations
    
    def _strict_email_checks(self, text: str) -> List[PIMatch]:
        """Strict email validation checks"""
        violations = []
        
        # Check for partial email patterns
        partial_patterns = [
            r'\b[A-Za-z0-9._%+-]+@\*\*\*',  # john.doe@***
            r'\b\*\*\*\*\*\*\*\@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # ********@domain.com
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\*\*\*',  # john.doe@domain.***
        ]
        
        for pattern in partial_patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            for match in regex.finditer(text):
                violations.append(PIMatch(
                    pi_type=PIType.EMAIL,
                    matched_text=match.group(),
                    start_position=match.start(),
                    end_position=match.end(),
                    pattern_used=pattern,
                    severity=PISeverity.MEDIUM,
                    confidence=0.7
                ))
        
        return violations
    
    def _strict_phone_checks(self, text: str) -> List[PIMatch]:
        """Strict phone validation checks"""
        violations = []
        
        # Check for partial phone patterns
        partial_patterns = [
            r'\b\*\*\*\-\*\*\*\-(\d{4})\b',  # ***-***-1234
            r'\b\(\*\*\*\)\s*\*\*\*\-(\d{4})\b',  # (***) ***-1234
            r'\b\*\*\*\s*\*\*\*\s*(\d{4})\b',  # *** *** 1234
        ]
        
        for pattern in partial_patterns:
            regex = re.compile(pattern)
            for match in regex.finditer(text):
                violations.append(PIMatch(
                    pi_type=PIType.PHONE,
                    matched_text=match.group(),
                    start_position=match.start(),
                    end_position=match.end(),
                    pattern_used=pattern,
                    severity=PISeverity.MEDIUM,
                    confidence=0.6
                ))
        
        return violations
    
    def _strict_ssn_checks(self, text: str) -> List[PIMatch]:
        """Strict SSN validation checks"""
        violations = []
        
        # Check for partial SSN patterns
        partial_patterns = [
            r'\b\*\*\*\-\*\*\-(\d{4})\b',  # ***-**-1234
            r'\b(\d{3})\-\*\*\-\*\*\*\*\b',  # 123-**-****
        ]
        
        for pattern in partial_patterns:
            regex = re.compile(pattern)
            for match in regex.finditer(text):
                violations.append(PIMatch(
                    pi_type=PIType.SSN,
                    matched_text=match.group(),
                    start_position=match.start(),
                    end_position=match.end(),
                    pattern_used=pattern,
                    severity=PISeverity.HIGH,
                    confidence=0.8
                ))
        
        return violations
    
    def _strict_credit_card_checks(self, text: str) -> List[PIMatch]:
        """Strict credit card validation checks"""
        violations = []
        
        # Check for partial credit card patterns
        partial_patterns = [
            r'\b\*\*\*\*\s*\*\*\*\*\s*\*\*\*\s*(\d{4})\b',  # **** **** **** 1234
            r'\b\*\*\*\*\-\*\*\*\*\-\*\*\*\*\-(\d{4})\b',  # ****-****-****-1234
        ]
        
        for pattern in partial_patterns:
            regex = re.compile(pattern)
            for match in regex.finditer(text):
                violations.append(PIMatch(
                    pi_type=PIType.CREDIT_CARD,
                    matched_text=match.group(),
                    start_position=match.start(),
                    end_position=match.end(),
                    pattern_used=pattern,
                    severity=PISeverity.HIGH,
                    confidence=0.8
                ))
        
        return violations


class CompliancePIValidator(BasePIValidator):
    """Compliance-focused validator for regulatory requirements"""
    
    def __init__(self, pi_type: PIType, compliance_standard: str = "GDPR"):
        super().__init__(pi_type)
        self.compliance_standard = compliance_standard
    
    def validate(self, original_text: str, processed_text: str) -> PIValidationResult:
        """Compliance-focused validation"""
        original_matches = self._check_remaining_pi(original_text)
        remaining_matches = self._check_remaining_pi(processed_text)
        
        # Filter matches for this PI type
        original_filtered = [m for m in original_matches if m.pi_type == self.pi_type]
        remaining_filtered = [m for m in remaining_matches if m.pi_type == self.pi_type]
        
        # Compliance-specific checks
        compliance_violations = self._compliance_checks(processed_text)
        all_remaining = remaining_filtered + compliance_violations
        
        validation_score = self._calculate_compliance_score(original_filtered, all_remaining)
        is_valid = len(all_remaining) == 0 and self._passes_compliance_rules(processed_text)
        recommendations = self._generate_compliance_recommendations(all_remaining)
        
        return PIValidationResult(
            is_valid=is_valid,
            validation_score=validation_score,
            remaining_matches=all_remaining,
            recommendations=recommendations
        )
    
    def _compliance_checks(self, text: str) -> List[PIMatch]:
        """Compliance-specific validation checks"""
        violations = []
        
        if self.compliance_standard == "GDPR":
            violations.extend(self._gdpr_checks(text))
        elif self.compliance_standard == "HIPAA":
            violations.extend(self._hipaa_checks(text))
        elif self.compliance_standard == "PCI_DSS":
            violations.extend(self._pci_dss_checks(text))
        
        return violations
    
    def _gdpr_checks(self, text: str) -> List[PIMatch]:
        """GDPR-specific checks"""
        violations = []
        
        # Check for direct identifiers that should be completely removed
        if self.pi_type in [PIType.EMAIL, PIType.SSN, PIType.CREDIT_CARD]:
            # Any remaining instance is a violation
            remaining = self._check_remaining_pi(text)
            for match in remaining:
                if match.pi_type == self.pi_type:
                    violations.append(PIMatch(
                        pi_type=match.pi_type,
                        matched_text=match.matched_text,
                        start_position=match.start_position,
                        end_position=match.end_position,
                        pattern_used="GDPR_COMPLIANCE_CHECK",
                        severity=PISeverity.CRITICAL,
                        confidence=1.0
                    ))
        
        return violations
    
    def _hipaa_checks(self, text: str) -> List[PIMatch]:
        """HIPAA-specific checks for healthcare data"""
        violations = []
        
        # HIPAA requires complete removal of PHI
        if self.pi_type in [PIType.NAME, PIType.DOB, PIType.PHONE, PIType.EMAIL]:
            remaining = self._check_remaining_pi(text)
            for match in remaining:
                if match.pi_type == self.pi_type:
                    violations.append(PIMatch(
                        pi_type=match.pi_type,
                        matched_text=match.matched_text,
                        start_position=match.start_position,
                        end_position=match.end_position,
                        pattern_used="HIPAA_COMPLIANCE_CHECK",
                        severity=PISeverity.CRITICAL,
                        confidence=1.0
                    ))
        
        return violations
    
    def _pci_dss_checks(self, text: str) -> List[PIMatch]:
        """PCI DSS-specific checks for payment card data"""
        violations = []
        
        # PCI DSS requires complete removal of card data
        if self.pi_type == PIType.CREDIT_CARD:
            remaining = self._check_remaining_pi(text)
            for match in remaining:
                violations.append(PIMatch(
                    pi_type=match.pi_type,
                    matched_text=match.matched_text,
                    start_position=match.start_position,
                    end_position=match.end_position,
                    pattern_used="PCI_DSS_COMPLIANCE_CHECK",
                    severity=PISeverity.CRITICAL,
                    confidence=1.0
                ))
        
        return violations
    
    def _calculate_compliance_score(self, original_matches: List[PIMatch], remaining_matches: List[PIMatch]) -> float:
        """Calculate compliance-specific validation score"""
        if not original_matches:
            return 1.0
        
        # Compliance requires 100% removal for critical data
        critical_remaining = [m for m in remaining_matches if m.severity == PISeverity.CRITICAL]
        if critical_remaining:
            return 0.0  # Any critical remaining PI = compliance failure
        
        return self._calculate_validation_score(original_matches, remaining_matches)
    
    def _passes_compliance_rules(self, text: str) -> bool:
        """Check if text passes compliance-specific rules"""
        if self.compliance_standard == "GDPR":
            return self._passes_gdpr_rules(text)
        elif self.compliance_standard == "HIPAA":
            return self._passes_hipaa_rules(text)
        elif self.compliance_standard == "PCI_DSS":
            return self._passes_pci_dss_rules(text)
        return True
    
    def _passes_gdpr_rules(self, text: str) -> bool:
        """GDPR-specific rule checks"""
        # GDPR requires no direct identifiers remain
        critical_pi_types = [PIType.EMAIL, PIType.SSN, PIType.CREDIT_CARD]
        for pi_type in critical_pi_types:
            checker = PICheckerFactory.create_checker(pi_type)
            matches = checker.check(text)
            if matches:
                return False
        return True
    
    def _passes_hipaa_rules(self, text: str) -> bool:
        """HIPAA-specific rule checks"""
        # HIPAA requires no PHI remain
        phi_types = [PIType.NAME, PIType.DOB, PIType.PHONE, PIType.EMAIL]
        for pi_type in phi_types:
            checker = PICheckerFactory.create_checker(pi_type)
            matches = checker.check(text)
            if matches:
                return False
        return True
    
    def _passes_pci_dss_rules(self, text: str) -> bool:
        """PCI DSS-specific rule checks"""
        # PCI DSS requires no card data remain
        checker = PICheckerFactory.create_checker(PIType.CREDIT_CARD)
        matches = checker.check(text)
        return len(matches) == 0
    
    def _generate_compliance_recommendations(self, remaining_matches: List[PIMatch]) -> List[str]:
        """Generate compliance-specific recommendations"""
        recommendations = self._generate_recommendations(remaining_matches)
        
        # Add compliance-specific recommendations
        if self.compliance_standard == "GDPR":
            recommendations.append("GDPR requires complete removal of all direct personal identifiers")
            recommendations.append("Consider using complete removal method instead of masking for GDPR compliance")
        elif self.compliance_standard == "HIPAA":
            recommendations.append("HIPAA requires complete removal of all Protected Health Information (PHI)")
            recommendations.append("Use complete removal method for all healthcare-related data")
        elif self.compliance_standard == "PCI_DSS":
            recommendations.append("PCI DSS requires complete removal of all payment card data")
            recommendations.append("Never store or log full credit card numbers - use tokenization instead")
        
        return recommendations


class PIValidatorFactory:
    """Factory class for creating PI validators"""
    
    _validators = {
        "basic": BasicPIValidator,
        "strict": StrictPIValidator,
        "compliance": CompliancePIValidator
    }
    
    @classmethod
    def create_validator(cls, pi_type: PIType, validation_type: str = "basic", **kwargs) -> BasePIValidator:
        """Create a validator for the specified PI type and validation type"""
        if validation_type not in cls._validators:
            raise ValueError(f"Unknown validation type: {validation_type}")
        
        if validation_type == "compliance":
            compliance_standard = kwargs.get("compliance_standard", "GDPR")
            return cls._validators[validation_type](pi_type, compliance_standard)
        else:
            return cls._validators[validation_type](pi_type)
    
    @classmethod
    def create_all_validators(cls, pi_type: PIType) -> Dict[str, BasePIValidator]:
        """Create all available validators for a PI type"""
        return {
            "basic": cls.create_validator(pi_type, "basic"),
            "strict": cls.create_validator(pi_type, "strict"),
            "compliance": cls.create_validator(pi_type, "compliance")
        }
    
    @classmethod
    def get_available_validation_types(cls) -> List[str]:
        """Get list of available validation types"""
        return list(cls._validators.keys())
    
    @classmethod
    def get_available_compliance_standards(cls) -> List[str]:
        """Get list of available compliance standards"""
        return ["GDPR", "HIPAA", "PCI_DSS"]
