import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pi_models import PIType, PIMatch, PIPattern, PISeverity, PIConstants


class BasePIChecker(ABC):
    """Abstract base class for PI checkers"""
    
    def __init__(self, pi_type: PIType):
        self.pi_type = pi_type
        self.patterns = PIConstants.PATTERNS.get(pi_type, [])
        self.confidence_threshold = PIConstants.CONFIDENCE_THRESHOLDS.get(pi_type, 0.8)
    
    @abstractmethod
    def check(self, text: str) -> List[PIMatch]:
        """Check for PI data in text and return matches"""
        pass
    
    @abstractmethod
    def calculate_confidence(self, match_text: str, pattern: PIPattern) -> float:
        """Calculate confidence score for a match"""
        pass
    
    def _create_match(self, match_text: str, start: int, end: int, pattern: PIPattern) -> PIMatch:
        """Create a PIMatch object"""
        confidence = self.calculate_confidence(match_text, pattern)
        return PIMatch(
            pi_type=self.pi_type,
            matched_text=match_text,
            start_position=start,
            end_position=end,
            pattern_used=pattern.pattern,
            severity=pattern.severity,
            confidence=confidence
        )


class EmailChecker(BasePIChecker):
    """Checker for email addresses"""
    
    def __init__(self):
        super().__init__(PIType.EMAIL)
    
    def check(self, text: str) -> List[PIMatch]:
        """Check for email addresses in text"""
        matches = []
        
        for pattern in self.patterns:
            regex = re.compile(pattern.pattern, re.IGNORECASE)
            for match in regex.finditer(text):
                match_text = match.group()
                pi_match = self._create_match(
                    match_text, 
                    match.start(), 
                    match.end(), 
                    pattern
                )
                if pi_match.confidence >= self.confidence_threshold:
                    matches.append(pi_match)
        
        return matches
    
    def calculate_confidence(self, match_text: str, pattern: PIPattern) -> float:
        """Calculate confidence for email matches"""
        confidence = 0.0
        
        # Basic email format check
        if '@' in match_text and '.' in match_text.split('@')[-1]:
            confidence += 0.4
        
        # Domain check
        domain = match_text.split('@')[-1]
        if '.' in domain and len(domain.split('.')[-1]) >= 2:
            confidence += 0.3
        
        # Local part check
        local = match_text.split('@')[0]
        if len(local) > 1 and not local.startswith('.'):
            confidence += 0.2
        
        # No suspicious characters
        if not any(char in match_text for char in ['<', '>', '"', "'", '\\']):
            confidence += 0.1
        
        return min(confidence, 1.0)


class PhoneChecker(BasePIChecker):
    """Checker for phone numbers"""
    
    def __init__(self):
        super().__init__(PIType.PHONE)
    
    def check(self, text: str) -> List[PIMatch]:
        """Check for phone numbers in text"""
        matches = []
        
        for pattern in self.patterns:
            regex = re.compile(pattern.pattern)
            for match in regex.finditer(text):
                match_text = match.group()
                pi_match = self._create_match(
                    match_text, 
                    match.start(), 
                    match.end(), 
                    pattern
                )
                if pi_match.confidence >= self.confidence_threshold:
                    matches.append(pi_match)
        
        return matches
    
    def calculate_confidence(self, match_text: str, pattern: PIPattern) -> float:
        """Calculate confidence for phone number matches"""
        confidence = 0.0
        
        # Remove common separators
        clean_number = re.sub(r'[+()\s.-]', '', match_text)
        
        # Length check for typical phone numbers
        if 10 <= len(clean_number) <= 15:
            confidence += 0.4
        
        # Check for valid phone number patterns
        if re.match(r'^\d+$', clean_number):
            confidence += 0.3
        
        # Check for area code patterns
        if len(clean_number) >= 10:
            if clean_number[:3] not in ['000', '111', '999']:
                confidence += 0.2
        
        # Check for country code
        if match_text.startswith('+'):
            confidence += 0.1
        
        return min(confidence, 1.0)


class DOBChecker(BasePIChecker):
    """Checker for dates of birth"""
    
    def __init__(self):
        super().__init__(PIType.DOB)
    
    def check(self, text: str) -> List[PIMatch]:
        """Check for dates of birth in text"""
        matches = []
        
        for pattern in self.patterns:
            regex = re.compile(pattern.pattern)
            for match in regex.finditer(text):
                match_text = match.group()
                pi_match = self._create_match(
                    match_text, 
                    match.start(), 
                    match.end(), 
                    pattern
                )
                if pi_match.confidence >= self.confidence_threshold:
                    matches.append(pi_match)
        
        return matches
    
    def calculate_confidence(self, match_text: str, pattern: PIPattern) -> float:
        """Calculate confidence for date of birth matches"""
        confidence = 0.0
        
        # Try to parse the date
        date_formats = ['%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in date_formats:
            try:
                import datetime
                parsed_date = datetime.datetime.strptime(match_text, fmt)
                
                # Reasonable year range (1900-2025)
                if 1900 <= parsed_date.year <= 2025:
                    confidence += 0.5
                
                # Reasonable month and day
                if 1 <= parsed_date.month <= 12 and 1 <= parsed_date.day <= 31:
                    confidence += 0.3
                
                # Not a future date
                if parsed_date.date() <= datetime.datetime.now().date():
                    confidence += 0.2
                
                break
            except ValueError:
                continue
        
        return min(confidence, 1.0)


class SSNChecker(BasePIChecker):
    """Checker for Social Security Numbers"""
    
    def __init__(self):
        super().__init__(PIType.SSN)
    
    def check(self, text: str) -> List[PIMatch]:
        """Check for SSN in text"""
        matches = []
        
        for pattern in self.patterns:
            regex = re.compile(pattern.pattern)
            for match in regex.finditer(text):
                match_text = match.group()
                pi_match = self._create_match(
                    match_text, 
                    match.start(), 
                    match.end(), 
                    pattern
                )
                if pi_match.confidence >= self.confidence_threshold:
                    matches.append(pi_match)
        
        return matches
    
    def calculate_confidence(self, match_text: str, pattern: PIPattern) -> float:
        """Calculate confidence for SSN matches"""
        confidence = 0.0
        
        # Remove dashes for validation
        clean_ssn = match_text.replace('-', '')
        
        # Check if all digits
        if re.match(r'^\d{9}$', clean_ssn):
            confidence += 0.4
        
        # Check for invalid patterns
        if not (clean_ssn.startswith('000') or clean_ssn.startswith('666') or 
                clean_ssn in ['123456789', '987654321']):
            confidence += 0.3
        
        # Check area number rules (first 3 digits)
        area = clean_ssn[:3]
        if not (area == '000' or area == '666' or int(area) > 900):
            confidence += 0.2
        
        # Check serial number rules (last 4 digits)
        serial = clean_ssn[5:]
        if serial != '0000':
            confidence += 0.1
        
        return min(confidence, 1.0)


class CreditCardChecker(BasePIChecker):
    """Checker for credit card numbers"""
    
    def __init__(self):
        super().__init__(PIType.CREDIT_CARD)
    
    def check(self, text: str) -> List[PIMatch]:
        """Check for credit card numbers in text"""
        matches = []
        
        for pattern in self.patterns:
            regex = re.compile(pattern.pattern)
            for match in regex.finditer(text):
                match_text = match.group()
                pi_match = self._create_match(
                    match_text, 
                    match.start(), 
                    match.end(), 
                    pattern
                )
                if pi_match.confidence >= self.confidence_threshold:
                    matches.append(pi_match)
        
        return matches
    
    def calculate_confidence(self, match_text: str, pattern: PIPattern) -> float:
        """Calculate confidence for credit card matches"""
        confidence = 0.0
        
        # Remove spaces and dashes
        clean_card = re.sub(r'[\s-]', '', match_text)
        
        # Check if all digits
        if re.match(r'^\d+$', clean_card):
            confidence += 0.3
        
        # Check length (13-19 digits)
        if 13 <= len(clean_card) <= 19:
            confidence += 0.2
        
        # Luhn algorithm check
        if self._luhn_check(clean_card):
            confidence += 0.4
        
        # Check card type patterns
        if self._get_card_type(clean_card):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _luhn_check(self, card_number: str) -> bool:
        """Check if credit card number passes Luhn algorithm"""
        total = 0
        reverse_digits = card_number[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n = (n // 10) + (n % 10)
            total += n
        
        return total % 10 == 0
    
    def _get_card_type(self, card_number: str) -> str:
        """Get credit card type from number"""
        if card_number.startswith('4'):
            return 'Visa'
        elif card_number.startswith('5'):
            return 'MasterCard'
        elif card_number.startswith('3'):
            return 'American Express'
        elif card_number.startswith('6'):
            return 'Discover'
        return 'Unknown'


class NameChecker(BasePIChecker):
    """Checker for personal names"""
    
    def __init__(self):
        super().__init__(PIType.NAME)
    
    def check(self, text: str) -> List[PIMatch]:
        """Check for personal names in text"""
        matches = []
        
        for pattern in self.patterns:
            regex = re.compile(pattern.pattern)
            for match in regex.finditer(text):
                match_text = match.group()
                pi_match = self._create_match(
                    match_text, 
                    match.start(), 
                    match.end(), 
                    pattern
                )
                if pi_match.confidence >= self.confidence_threshold:
                    matches.append(pi_match)
        
        return matches
    
    def calculate_confidence(self, match_text: str, pattern: PIPattern) -> float:
        """Calculate confidence for name matches"""
        confidence = 0.0
        
        # Check for title
        if any(title in match_text for title in ['Mr.', 'Mrs.', 'Ms.', 'Dr.']):
            confidence += 0.3
        
        # Check capitalization pattern
        words = match_text.split()
        if all(word.istitle() for word in words if word not in ['Mr.', 'Mrs.', 'Ms.', 'Dr.']):
            confidence += 0.2
        
        # Check word count (2-3 words typical for names)
        if 2 <= len(words) <= 3:
            confidence += 0.2
        
        # Check length (reasonable name length)
        if 5 <= len(match_text) <= 30:
            confidence += 0.2
        
        # Check for common name patterns (avoid false positives)
        if not any(common in match_text.lower() for common in 
                  ['error', 'exception', 'null', 'undefined', 'test', 'demo']):
            confidence += 0.1
        
        return min(confidence, 1.0)


class PICheckerFactory:
    """Factory class for creating PI checkers"""
    
    _checkers = {
        PIType.EMAIL: EmailChecker,
        PIType.PHONE: PhoneChecker,
        PIType.DOB: DOBChecker,
        PIType.SSN: SSNChecker,
        PIType.CREDIT_CARD: CreditCardChecker,
        PIType.NAME: NameChecker
    }
    
    @classmethod
    def create_checker(cls, pi_type: PIType) -> BasePIChecker:
        """Create a checker for the specified PI type"""
        if pi_type not in cls._checkers:
            raise ValueError(f"No checker available for PI type: {pi_type}")
        
        return cls._checkers[pi_type]()
    
    @classmethod
    def create_all_checkers(cls) -> Dict[PIType, BasePIChecker]:
        """Create all available checkers"""
        return {pi_type: cls.create_checker(pi_type) for pi_type in cls._checkers}
