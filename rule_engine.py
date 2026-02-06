import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pi_models import PIType, PIMatch, PIRemovalResult, PIValidationResult, PISeverity
from pi_checkers import BasePIChecker, PICheckerFactory
from pi_removers import BasePIRemover, PIRemoverFactory
from pi_validators import BasePIValidator, PIValidatorFactory


@dataclass
class RuleEngineConfig:
    """Configuration for RuleEngine"""
    enabled_pi_types: List[PIType]
    removal_method: str = "masking"
    validation_type: str = "basic"
    compliance_standard: Optional[str] = None
    confidence_threshold: float = 0.8
    log_level: str = "INFO"
    enable_audit_trail: bool = True


@dataclass
class ProcessingResult:
    """Result of processing text through RuleEngine"""
    original_text: str
    processed_text: str
    all_matches: List[PIMatch]
    removal_results: Dict[PIType, PIRemovalResult]
    validation_results: Dict[PIType, PIValidationResult]
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class AuditEntry:
    """Audit trail entry for PI processing"""
    timestamp: str
    pi_type: PIType
    action: str  # 'detected', 'removed', 'validated'
    details: Dict[str, Any]


class RuleEngine:
    """Main RuleEngine class for PI detection, removal, and validation"""
    
    def __init__(self, config: RuleEngineConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.checkers = self._initialize_checkers()
        self.removers = self._initialize_removers()
        self.validators = self._initialize_validators()
        self.audit_trail: List[AuditEntry] = []
        
        self.logger.info(f"RuleEngine initialized with {len(self.config.enabled_pi_types)} PI types")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for RuleEngine"""
        logger = logging.getLogger("RuleEngine")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_checkers(self) -> Dict[PIType, BasePIChecker]:
        """Initialize PI checkers for enabled types"""
        checkers = {}
        for pi_type in self.config.enabled_pi_types:
            try:
                checker = PICheckerFactory.create_checker(pi_type)
                checkers[pi_type] = checker
                self.logger.debug(f"Initialized checker for {pi_type.value}")
            except Exception as e:
                self.logger.error(f"Failed to initialize checker for {pi_type.value}: {e}")
        
        return checkers
    
    def _initialize_removers(self) -> Dict[PIType, BasePIRemover]:
        """Initialize PI removers for enabled types"""
        removers = {}
        for pi_type in self.config.enabled_pi_types:
            try:
                remover = PIRemoverFactory.create_remover(pi_type, self.config.removal_method)
                removers[pi_type] = remover
                self.logger.debug(f"Initialized remover for {pi_type.value} with method {self.config.removal_method}")
            except Exception as e:
                self.logger.error(f"Failed to initialize remover for {pi_type.value}: {e}")
        
        return removers
    
    def _initialize_validators(self) -> Dict[PIType, BasePIValidator]:
        """Initialize PI validators for enabled types"""
        validators = {}
        for pi_type in self.config.enabled_pi_types:
            try:
                validator_kwargs = {}
                if self.config.validation_type == "compliance" and self.config.compliance_standard:
                    validator_kwargs["compliance_standard"] = self.config.compliance_standard
                
                validator = PIValidatorFactory.create_validator(
                    pi_type, 
                    self.config.validation_type, 
                    **validator_kwargs
                )
                validators[pi_type] = validator
                self.logger.debug(f"Initialized validator for {pi_type.value} with type {self.config.validation_type}")
            except Exception as e:
                self.logger.error(f"Failed to initialize validator for {pi_type.value}: {e}")
        
        return validators
    
    def process_text(self, text: str) -> ProcessingResult:
        """Process text through the complete PI detection, removal, and validation pipeline"""
        import time
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting processing of text ({len(text)} characters)")
            
            # Step 1: Detect PI in text
            all_matches = self._detect_pi(text)
            self._add_audit_entry("detection", None, {"total_matches": len(all_matches)})
            
            if not all_matches:
                self.logger.info("No PI detected in text")
                return ProcessingResult(
                    original_text=text,
                    processed_text=text,
                    all_matches=[],
                    removal_results={},
                    validation_results={},
                    processing_time_ms=(time.time() - start_time) * 1000,
                    success=True
                )
            
            # Step 2: Remove detected PI
            removal_results = self._remove_pi(text, all_matches)
            processed_text = self._get_processed_text(text, removal_results)
            self._add_audit_entry("removal", None, {"removals_performed": len(removal_results)})
            
            # Step 3: Validate removal effectiveness
            validation_results = self._validate_removal(text, processed_text)
            self._add_audit_entry("validation", None, {"validations_performed": len(validation_results)})
            
            processing_time = (time.time() - start_time) * 1000
            self.logger.info(f"Processing completed in {processing_time:.2f}ms")
            
            return ProcessingResult(
                original_text=text,
                processed_text=processed_text,
                all_matches=all_matches,
                removal_results=removal_results,
                validation_results=validation_results,
                processing_time_ms=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Processing failed: {str(e)}"
            self.logger.error(error_msg)
            
            return ProcessingResult(
                original_text=text,
                processed_text=text,
                all_matches=[],
                removal_results={},
                validation_results={},
                processing_time_ms=processing_time,
                success=False,
                error_message=error_msg
            )
    
    def _detect_pi(self, text: str) -> List[PIMatch]:
        """Detect all PI in text using enabled checkers"""
        all_matches = []
        
        for pi_type, checker in self.checkers.items():
            try:
                matches = checker.check(text)
                # Filter by confidence threshold
                filtered_matches = [m for m in matches if m.confidence >= self.config.confidence_threshold]
                all_matches.extend(filtered_matches)
                
                if filtered_matches:
                    self.logger.debug(f"Detected {len(filtered_matches)} {pi_type.value} instances")
                    self._add_audit_entry("detected", pi_type, {"count": len(filtered_matches)})
                
            except Exception as e:
                self.logger.error(f"Error detecting {pi_type.value}: {e}")
        
        # Sort matches by position
        all_matches.sort(key=lambda x: x.start_position)
        return all_matches
    
    def _remove_pi(self, text: str, matches: List[PIMatch]) -> Dict[PIType, PIRemovalResult]:
        """Remove detected PI using appropriate removers"""
        removal_results = {}
        current_text = text
        
        # Group matches by PI type
        matches_by_type = {}
        for match in matches:
            if match.pi_type not in matches_by_type:
                matches_by_type[match.pi_type] = []
            matches_by_type[match.pi_type].append(match)
        
        # Process each PI type
        for pi_type, type_matches in matches_by_type.items():
            if pi_type not in self.removers:
                self.logger.warning(f"No remover available for {pi_type.value}")
                continue
            
            try:
                remover = self.removers[pi_type]
                result = remover.remove(current_text, type_matches)
                removal_results[pi_type] = result
                
                if result.success:
                    current_text = result.processed_text
                    self.logger.debug(f"Removed {len(result.removed_matches)} {pi_type.value} instances")
                    self._add_audit_entry("removed", pi_type, {"count": len(result.removed_matches)})
                else:
                    self.logger.error(f"Failed to remove {pi_type.value}")
                
            except Exception as e:
                self.logger.error(f"Error removing {pi_type.value}: {e}")
        
        return removal_results
    
    def _validate_removal(self, original_text: str, processed_text: str) -> Dict[PIType, PIValidationResult]:
        """Validate PI removal effectiveness"""
        validation_results = {}
        
        for pi_type, validator in self.validators.items():
            try:
                result = validator.validate(original_text, processed_text)
                validation_results[pi_type] = result
                
                self.logger.debug(f"Validation for {pi_type.value}: score={result.validation_score:.2f}, valid={result.is_valid}")
                self._add_audit_entry("validated", pi_type, {
                    "score": result.validation_score,
                    "is_valid": result.is_valid,
                    "remaining_count": len(result.remaining_matches)
                })
                
            except Exception as e:
                self.logger.error(f"Error validating {pi_type.value}: {e}")
        
        return validation_results
    
    def _get_processed_text(self, original_text: str, removal_results: Dict[PIType, PIRemovalResult]) -> str:
        """Get the final processed text after all removals"""
        if not removal_results:
            return original_text
        
        # Use the last processed text from the removal results
        # (removals are applied sequentially)
        processed_text = original_text
        for result in removal_results.values():
            if result.success:
                processed_text = result.processed_text
        
        return processed_text
    
    def _add_audit_entry(self, action: str, pi_type: Optional[PIType], details: Dict[str, Any]):
        """Add entry to audit trail"""
        if not self.config.enable_audit_trail:
            return
        
        from datetime import datetime
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            pi_type=pi_type or PIType.EMAIL,  # Default for non-PI-specific actions
            action=action,
            details=details
        )
        self.audit_trail.append(entry)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        if not self.audit_trail:
            return {"message": "No processing history available"}
        
        stats = {
            "total_processed": len([e for e in self.audit_trail if e.action == "detection"]),
            "pi_detected_by_type": {},
            "pi_removed_by_type": {},
            "validation_scores": {},
            "average_processing_time": 0.0,
            "success_rate": 0.0
        }
        
        # Count PI detections by type
        for entry in self.audit_trail:
            if entry.action == "detected":
                pi_type = entry.pi_type.value
                count = entry.details.get("count", 0)
                stats["pi_detected_by_type"][pi_type] = stats["pi_detected_by_type"].get(pi_type, 0) + count
            elif entry.action == "removed":
                pi_type = entry.pi_type.value
                count = entry.details.get("count", 0)
                stats["pi_removed_by_type"][pi_type] = stats["pi_removed_by_type"].get(pi_type, 0) + count
            elif entry.action == "validated":
                pi_type = entry.pi_type.value
                score = entry.details.get("score", 0.0)
                if pi_type not in stats["validation_scores"]:
                    stats["validation_scores"][pi_type] = []
                stats["validation_scores"][pi_type].append(score)
        
        # Calculate average validation scores
        for pi_type, scores in stats["validation_scores"].items():
            if scores:
                stats["validation_scores"][pi_type] = sum(scores) / len(scores)
        
        return stats
    
    def get_audit_trail(self) -> List[AuditEntry]:
        """Get the audit trail"""
        return self.audit_trail.copy()
    
    def clear_audit_trail(self):
        """Clear the audit trail"""
        self.audit_trail.clear()
        self.logger.info("Audit trail cleared")
    
    def update_config(self, new_config: RuleEngineConfig):
        """Update RuleEngine configuration"""
        self.config = new_config
        self.logger = self._setup_logger()
        self.checkers = self._initialize_checkers()
        self.removers = self._initialize_removers()
        self.validators = self._initialize_validators()
        self.logger.info("RuleEngine configuration updated")
    
    def get_supported_pi_types(self) -> List[PIType]:
        """Get list of supported PI types"""
        return list(PIType)
    
    def get_available_removal_methods(self) -> List[str]:
        """Get list of available removal methods"""
        return PIRemoverFactory.get_available_methods()
    
    def get_available_validation_types(self) -> List[str]:
        """Get list of available validation types"""
        return PIValidatorFactory.get_available_validation_types()
    
    def get_available_compliance_standards(self) -> List[str]:
        """Get list of available compliance standards"""
        return PIValidatorFactory.get_available_compliance_standards()


class RuleEngineBuilder:
    """Builder class for creating RuleEngine instances with custom configuration"""
    
    def __init__(self):
        self.enabled_pi_types = [PIType.EMAIL, PIType.PHONE, PIType.DOB, PIType.NAME]
        self.removal_method = "masking"
        self.validation_type = "basic"
        self.compliance_standard = None
        self.confidence_threshold = 0.8
        self.log_level = "INFO"
        self.enable_audit_trail = True
    
    def with_pi_types(self, pi_types: List[PIType]) -> 'RuleEngineBuilder':
        """Set enabled PI types"""
        self.enabled_pi_types = pi_types
        return self
    
    def with_removal_method(self, method: str) -> 'RuleEngineBuilder':
        """Set removal method"""
        self.removal_method = method
        return self
    
    def with_validation_type(self, validation_type: str) -> 'RuleEngineBuilder':
        """Set validation type"""
        self.validation_type = validation_type
        return self
    
    def with_compliance_standard(self, standard: str) -> 'RuleEngineBuilder':
        """Set compliance standard"""
        self.compliance_standard = standard
        self.validation_type = "compliance"  # Force compliance validation
        return self
    
    def with_confidence_threshold(self, threshold: float) -> 'RuleEngineBuilder':
        """Set confidence threshold"""
        self.confidence_threshold = threshold
        return self
    
    def with_log_level(self, level: str) -> 'RuleEngineBuilder':
        """Set log level"""
        self.log_level = level
        return self
    
    def with_audit_trail(self, enable: bool) -> 'RuleEngineBuilder':
        """Enable/disable audit trail"""
        self.enable_audit_trail = enable
        return self
    
    def build(self) -> RuleEngine:
        """Build RuleEngine instance"""
        config = RuleEngineConfig(
            enabled_pi_types=self.enabled_pi_types,
            removal_method=self.removal_method,
            validation_type=self.validation_type,
            compliance_standard=self.compliance_standard,
            confidence_threshold=self.confidence_threshold,
            log_level=self.log_level,
            enable_audit_trail=self.enable_audit_trail
        )
        return RuleEngine(config)
