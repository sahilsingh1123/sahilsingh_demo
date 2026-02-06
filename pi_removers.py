import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pi_models import PIType, PIMatch, PIRemovalResult, PIConstants


class BasePIRemover(ABC):
    """Abstract base class for PI removers"""
    
    def __init__(self, pi_type: PIType):
        self.pi_type = pi_type
        self.masking_pattern = PIConstants.MASKING_PATTERNS.get(pi_type)
    
    @abstractmethod
    def remove(self, text: str, matches: List[PIMatch]) -> PIRemovalResult:
        """Remove PI data from text based on matches"""
        pass
    
    def _sort_matches_by_position(self, matches: List[PIMatch]) -> List[PIMatch]:
        """Sort matches by start position in descending order to avoid index issues"""
        return sorted(matches, key=lambda x: x.start_position, reverse=True)
    
    def _apply_masking(self, match_text: str) -> str:
        """Apply masking pattern to matched text"""
        if self.masking_pattern:
            return self.masking_pattern(match_text)
        return f"[{self.pi_type.value.upper()}_REDACTED]"


class CompleteRemover(BasePIRemover):
    """Remover that completely removes PI data"""
    
    def __init__(self, pi_type: PIType):
        super().__init__(pi_type)
    
    def remove(self, text: str, matches: List[PIMatch]) -> PIRemovalResult:
        """Completely remove PI data from text"""
        if not matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="complete_removal",
                success=True,
                remaining_pi_count=0
            )
        
        # Filter matches for this PI type
        relevant_matches = [m for m in matches if m.pi_type == self.pi_type]
        if not relevant_matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="complete_removal",
                success=True,
                remaining_pi_count=0
            )
        
        # Sort matches by position to avoid index issues
        sorted_matches = self._sort_matches_by_position(relevant_matches)
        processed_text = text
        
        # Remove matches from text
        for match in sorted_matches:
            processed_text = (
                processed_text[:match.start_position] + 
                processed_text[match.end_position:]
            )
        
        return PIRemovalResult(
            original_text=text,
            processed_text=processed_text,
            removed_matches=relevant_matches,
            removal_method="complete_removal",
            success=True,
            remaining_pi_count=0
        )


class MaskingRemover(BasePIRemover):
    """Remover that masks PI data with placeholder text"""
    
    def __init__(self, pi_type: PIType):
        super().__init__(pi_type)
    
    def remove(self, text: str, matches: List[PIMatch]) -> PIRemovalResult:
        """Mask PI data in text with placeholders"""
        if not matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="masking",
                success=True,
                remaining_pi_count=0
            )
        
        # Filter matches for this PI type
        relevant_matches = [m for m in matches if m.pi_type == self.pi_type]
        if not relevant_matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="masking",
                success=True,
                remaining_pi_count=0
            )
        
        # Sort matches by position to avoid index issues
        sorted_matches = self._sort_matches_by_position(relevant_matches)
        processed_text = text
        
        # Replace matches with masked versions
        for match in sorted_matches:
            masked_text = self._apply_masking(match.matched_text)
            processed_text = (
                processed_text[:match.start_position] + 
                masked_text + 
                processed_text[match.end_position:]
            )
        
        return PIRemovalResult(
            original_text=text,
            processed_text=processed_text,
            removed_matches=relevant_matches,
            removal_method="masking",
            success=True,
            remaining_pi_count=0
        )


class PartialMaskingRemover(BasePIRemover):
    """Remover that partially masks PI data (shows some characters)"""
    
    def __init__(self, pi_type: PIType):
        super().__init__(pi_type)
    
    def remove(self, text: str, matches: List[PIMatch]) -> PIRemovalResult:
        """Partially mask PI data, showing some characters"""
        if not matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="partial_masking",
                success=True,
                remaining_pi_count=0
            )
        
        # Filter matches for this PI type
        relevant_matches = [m for m in matches if m.pi_type == self.pi_type]
        if not relevant_matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="partial_masking",
                success=True,
                remaining_pi_count=0
            )
        
        # Sort matches by position to avoid index issues
        sorted_matches = self._sort_matches_by_position(relevant_matches)
        processed_text = text
        
        # Replace matches with partially masked versions
        for match in sorted_matches:
            masked_text = self._apply_partial_masking(match.matched_text)
            processed_text = (
                processed_text[:match.start_position] + 
                masked_text + 
                processed_text[match.end_position:]
            )
        
        return PIRemovalResult(
            original_text=text,
            processed_text=processed_text,
            removed_matches=relevant_matches,
            removal_method="partial_masking",
            success=True,
            remaining_pi_count=0
        )
    
    def _apply_partial_masking(self, match_text: str) -> str:
        """Apply partial masking based on PI type"""
        if self.pi_type == PIType.EMAIL:
            return self._partial_mask_email(match_text)
        elif self.pi_type == PIType.PHONE:
            return self._partial_mask_phone(match_text)
        elif self.pi_type == PIType.SSN:
            return self._partial_mask_ssn(match_text)
        elif self.pi_type == PIType.CREDIT_CARD:
            return self._partial_mask_credit_card(match_text)
        elif self.pi_type == PIType.DOB:
            return self._partial_mask_dob(match_text)
        elif self.pi_type == PIType.NAME:
            return self._partial_mask_name(match_text)
        else:
            return f"[{self.pi_type.value.upper()}_PARTIAL_MASK]"
    
    def _partial_mask_email(self, email: str) -> str:
        """Partially mask email - show first 2 chars of local and domain"""
        if '@' not in email:
            return "[EMAIL_PARTIAL_MASK]"
        
        local, domain = email.split('@', 1)
        if len(local) > 2:
            masked_local = local[:2] + '*' * (len(local) - 2)
        else:
            masked_local = '*' * len(local)
        
        if '.' in domain:
            domain_parts = domain.split('.')
            if len(domain_parts) > 1:
                main_domain = domain_parts[0]
                if len(main_domain) > 2:
                    masked_main = main_domain[:2] + '*' * (len(main_domain) - 2)
                else:
                    masked_main = '*' * len(main_domain)
                domain = masked_main + '.' + domain_parts[1]
        
        return f"{masked_local}@{domain}"
    
    def _partial_mask_phone(self, phone: str) -> str:
        """Partially mask phone - show last 4 digits"""
        clean_phone = re.sub(r'[^\d]', '', phone)
        if len(clean_phone) >= 4:
            visible = clean_phone[-4:]
            masked = '*' * (len(clean_phone) - 4)
            # Preserve original formatting
            result = phone
            for i, digit in enumerate(clean_phone):
                if i < len(clean_phone) - 4:
                    result = result.replace(digit, '*', 1)
            return result
        return "[PHONE_PARTIAL_MASK]"
    
    def _partial_mask_ssn(self, ssn: str) -> str:
        """Partially mask SSN - show last 4 digits"""
        if '-' in ssn:
            parts = ssn.split('-')
            if len(parts) == 3:
                return f"***-**-{parts[2]}"
        return "***-**-" + ssn[-4:] if len(ssn.replace('-', '')) == 9 else "[SSN_PARTIAL_MASK]"
    
    def _partial_mask_credit_card(self, card: str) -> str:
        """Partially mask credit card - show last 4 digits"""
        clean_card = re.sub(r'[^\d]', '', card)
        if len(clean_card) >= 4:
            visible = clean_card[-4:]
            masked = '*' * (len(clean_card) - 4)
            # Preserve original formatting
            result = card
            for i, digit in enumerate(clean_card):
                if i < len(clean_card) - 4:
                    result = result.replace(digit, '*', 1)
            return result
        return "[CC_PARTIAL_MASK]"
    
    def _partial_mask_dob(self, dob: str) -> str:
        """Partially mask date of birth - show only year"""
        if '/' in dob:
            parts = dob.split('/')
            if len(parts) == 3:
                return f"**/**/{parts[2]}"
        elif '-' in dob:
            parts = dob.split('-')
            if len(parts) == 3:
                if len(parts[0]) == 4:  # YYYY-MM-DD
                    return f"{parts[0]}-**-**"
                else:  # DD-MM-YYYY
                    return f"**-**-{parts[2]}"
        return "[DOB_PARTIAL_MASK]"
    
    def _partial_mask_name(self, name: str) -> str:
        """Partially mask name - show first initial"""
        words = name.split()
        if len(words) >= 2:
            first_initial = words[0][0] + '*'
            last_initial = words[-1][0] + '*'
            if len(words) == 2:
                return f"{first_initial} {last_initial}"
            else:
                middle = ' '.join(['*' * len(word) for word in words[1:-1]])
                return f"{first_initial} {middle} {last_initial}"
        elif len(words) == 1:
            return words[0][0] + '*' * (len(words[0]) - 1)
        return "[NAME_PARTIAL_MASK]"


class HashRemover(BasePIRemover):
    """Remover that replaces PI data with hash values"""
    
    def __init__(self, pi_type: PIType):
        super().__init__(pi_type)
    
    def remove(self, text: str, matches: List[PIMatch]) -> PIRemovalResult:
        """Replace PI data with hash values"""
        if not matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="hashing",
                success=True,
                remaining_pi_count=0
            )
        
        # Filter matches for this PI type
        relevant_matches = [m for m in matches if m.pi_type == self.pi_type]
        if not relevant_matches:
            return PIRemovalResult(
                original_text=text,
                processed_text=text,
                removed_matches=[],
                removal_method="hashing",
                success=True,
                remaining_pi_count=0
            )
        
        # Sort matches by position to avoid index issues
        sorted_matches = self._sort_matches_by_position(relevant_matches)
        processed_text = text
        
        # Replace matches with hash values
        for match in sorted_matches:
            hash_value = self._generate_hash(match.matched_text)
            processed_text = (
                processed_text[:match.start_position] + 
                hash_value + 
                processed_text[match.end_position:]
            )
        
        return PIRemovalResult(
            original_text=text,
            processed_text=processed_text,
            removed_matches=relevant_matches,
            removal_method="hashing",
            success=True,
            remaining_pi_count=0
        )
    
    def _generate_hash(self, text: str) -> str:
        """Generate hash for the text"""
        import hashlib
        hash_object = hashlib.sha256(text.encode())
        hash_hex = hash_object.hexdigest()
        # Return first 8 characters of hash with prefix
        return f"[{self.pi_type.value.upper()}_HASH_{hash_hex[:8]}]"


class PIRemoverFactory:
    """Factory class for creating PI removers"""
    
    _removers = {
        "complete": CompleteRemover,
        "masking": MaskingRemover,
        "partial": PartialMaskingRemover,
        "hash": HashRemover
    }
    
    @classmethod
    def create_remover(cls, pi_type: PIType, removal_method: str = "masking") -> BasePIRemover:
        """Create a remover for the specified PI type and method"""
        if removal_method not in cls._removers:
            raise ValueError(f"Unknown removal method: {removal_method}")
        
        return cls._removers[removal_method](pi_type)
    
    @classmethod
    def create_all_removers(cls, pi_type: PIType) -> Dict[str, BasePIRemover]:
        """Create all available removers for a PI type"""
        return {method: cls.create_remover(pi_type, method) for method in cls._removers}
    
    @classmethod
    def get_available_methods(cls) -> List[str]:
        """Get list of available removal methods"""
        return list(cls._removers.keys())
