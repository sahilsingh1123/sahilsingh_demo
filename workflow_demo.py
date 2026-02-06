#!/usr/bin/env python3
"""
End-to-End Workflow Demo for PI RuleEngine System

This script demonstrates the complete workflow of:
1. Generating logs with PI data
2. Processing logs through RuleEngine
3. Validating PI removal
4. Generating reports
"""

import time
import json
from typing import List, Dict, Any
from rule_engine import RuleEngine, RuleEngineBuilder, RuleEngineConfig
from log_generator import LogGenerator, LogScenarioGenerator, LogType, LogLevel
from pi_models import PIType


class WorkflowDemo:
    """Demonstrates the complete PI processing workflow"""
    
    def __init__(self):
        self.log_generator = LogGenerator()
        self.scenario_generator = LogScenarioGenerator()
    
    def run_basic_workflow(self) -> Dict[str, Any]:
        """Run basic workflow with default configuration"""
        print("=" * 60)
        print("BASIC WORKFLOW DEMO")
        print("=" * 60)
        
        # Step 1: Create RuleEngine with basic configuration
        print("\n1. Creating RuleEngine with basic configuration...")
        engine = (RuleEngineBuilder()
                 .with_pi_types([PIType.EMAIL, PIType.PHONE, PIType.DOB, PIType.NAME])
                 .with_removal_method("masking")
                 .with_validation_type("basic")
                 .with_log_level("INFO")
                 .build())
        
        # Step 2: Generate sample logs with PI data
        print("\n2. Generating sample logs with PI data...")
        logs = self.log_generator.generate_log_batch(5, [LogType.USER_REGISTRATION, LogType.USER_LOGIN])
        formatted_logs = self.log_generator.format_log_batch(logs)
        
        for i, log in enumerate(formatted_logs, 1):
            print(f"   Log {i}: {log}")
        
        # Step 3: Process logs through RuleEngine
        print("\n3. Processing logs through RuleEngine...")
        results = []
        
        for i, log in enumerate(formatted_logs, 1):
            print(f"\n   Processing Log {i}:")
            print(f"   Original: {log}")
            
            result = engine.process_text(log)
            results.append(result)
            
            print(f"   Processed: {result.processed_text}")
            print(f"   PI Detected: {len(result.all_matches)} instances")
            print(f"   Success: {result.success}")
            
            if result.all_matches:
                for match in result.all_matches:
                    print(f"     - {match.pi_type.value}: '{match.matched_text}' (confidence: {match.confidence:.2f})")
        
        # Step 4: Generate summary report
        print("\n4. Generating summary report...")
        report = self._generate_summary_report(results, engine)
        print(json.dumps(report, indent=2))
        
        return {
            "engine": engine,
            "results": results,
            "report": report
        }
    
    def run_compliance_workflow(self) -> Dict[str, Any]:
        """Run compliance-focused workflow (GDPR)"""
        print("\n" + "=" * 60)
        print("GDPR COMPLIANCE WORKFLOW DEMO")
        print("=" * 60)
        
        # Step 1: Create RuleEngine with GDPR compliance configuration
        print("\n1. Creating RuleEngine with GDPR compliance configuration...")
        engine = (RuleEngineBuilder()
                 .with_pi_types([PIType.EMAIL, PIType.PHONE, PIType.DOB, PIType.NAME, PIType.SSN])
                 .with_removal_method("complete")  # Complete removal for GDPR
                 .with_compliance_standard("GDPR")
                 .with_confidence_threshold(0.9)  # Higher threshold for compliance
                 .with_log_level("WARNING")
                 .build())
        
        # Step 2: Generate GDPR compliance test scenario
        print("\n2. Generating GDPR compliance test scenario...")
        gdpr_logs = self.scenario_generator.generate_compliance_test_scenario()
        
        for i, log in enumerate(gdpr_logs, 1):
            print(f"   Log {i}: {log}")
        
        # Step 3: Process logs with compliance validation
        print("\n3. Processing logs with GDPR compliance validation...")
        results = []
        
        for i, log in enumerate(gdpr_logs, 1):
            print(f"\n   Processing Log {i}:")
            print(f"   Original: {log}")
            
            result = engine.process_text(log)
            results.append(result)
            
            print(f"   Processed: {result.processed_text}")
            print(f"   GDPR Compliant: {all(vr.is_valid for vr in result.validation_results.values())}")
            
            # Show validation results
            for pi_type, validation in result.validation_results.items():
                print(f"     {pi_type.value} Validation: Score={validation.validation_score:.2f}, Valid={validation.is_valid}")
                if validation.recommendations:
                    for rec in validation.recommendations:
                        print(f"       Recommendation: {rec}")
        
        # Step 4: Generate compliance report
        print("\n4. Generating GDPR compliance report...")
        report = self._generate_compliance_report(results, engine, "GDPR")
        print(json.dumps(report, indent=2))
        
        return {
            "engine": engine,
            "results": results,
            "report": report
        }
    
    def run_performance_workflow(self) -> Dict[str, Any]:
        """Run performance testing workflow"""
        print("\n" + "=" * 60)
        print("PERFORMANCE TESTING WORKFLOW DEMO")
        print("=" * 60)
        
        # Step 1: Create optimized RuleEngine
        print("\n1. Creating optimized RuleEngine for performance...")
        engine = (RuleEngineBuilder()
                 .with_pi_types([PIType.EMAIL, PIType.PHONE, PIType.DOB, PIType.NAME])
                 .with_removal_method("masking")
                 .with_validation_type("basic")  # Basic validation for performance
                 .with_log_level("ERROR")  # Minimal logging
                 .with_audit_trail(False)  # Disable audit trail for performance
                 .build())
        
        # Step 2: Generate large batch of logs
        print("\n2. Generating large batch of logs for performance testing...")
        log_count = 100
        performance_logs = self.scenario_generator.generate_performance_test_scenario(log_count)
        print(f"   Generated {len(performance_logs)} logs")
        
        # Step 3: Process logs and measure performance
        print("\n3. Processing logs and measuring performance...")
        start_time = time.time()
        
        results = []
        total_pi_detected = 0
        total_processing_time = 0
        
        for i, log in enumerate(performance_logs, 1):
            if i % 20 == 0:  # Progress update every 20 logs
                print(f"   Processed {i}/{len(performance_logs)} logs...")
            
            result = engine.process_text(log)
            results.append(result)
            total_pi_detected += len(result.all_matches)
            total_processing_time += result.processing_time_ms
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Step 4: Generate performance report
        print("\n4. Generating performance report...")
        report = self._generate_performance_report(results, total_time, log_count)
        print(json.dumps(report, indent=2))
        
        return {
            "engine": engine,
            "results": results,
            "report": report
        }
    
    def run_edge_case_workflow(self) -> Dict[str, Any]:
        """Run edge case testing workflow"""
        print("\n" + "=" * 60)
        print("EDGE CASE TESTING WORKFLOW DEMO")
        print("=" * 60)
        
        # Step 1: Create RuleEngine with strict validation
        print("\n1. Creating RuleEngine with strict validation...")
        engine = (RuleEngineBuilder()
                 .with_pi_types(list(PIType))  # All PI types
                 .with_removal_method("partial")  # Partial masking to test edge cases
                 .with_validation_type("strict")  # Strict validation
                 .with_confidence_threshold(0.7)  # Lower threshold to catch edge cases
                 .with_log_level("DEBUG")
                 .build())
        
        # Step 2: Generate edge case scenarios
        print("\n2. Generating edge case scenarios...")
        edge_case_logs = self.scenario_generator.generate_edge_case_scenario()
        false_positive_logs = self.scenario_generator.generate_false_positive_scenario()
        
        all_edge_logs = edge_case_logs + false_positive_logs
        
        for i, log in enumerate(all_edge_logs, 1):
            print(f"   Edge Case {i}: {log}")
        
        # Step 3: Process edge cases
        print("\n3. Processing edge cases...")
        results = []
        
        for i, log in enumerate(all_edge_logs, 1):
            print(f"\n   Processing Edge Case {i}:")
            print(f"   Original: {log}")
            
            result = engine.process_text(log)
            results.append(result)
            
            print(f"   Processed: {result.processed_text}")
            print(f"   PI Detected: {len(result.all_matches)} instances")
            
            # Show strict validation results
            for pi_type, validation in result.validation_results.items():
                if not validation.is_valid:
                    print(f"     {pi_type.value} Strict Validation FAILED:")
                    print(f"       Score: {validation.validation_score:.2f}")
                    print(f"       Remaining PI: {len(validation.remaining_matches)}")
                    for rec in validation.recommendations:
                        print(f"       Recommendation: {rec}")
        
        # Step 4: Generate edge case analysis
        print("\n4. Generating edge case analysis...")
        analysis = self._generate_edge_case_analysis(results, engine)
        print(json.dumps(analysis, indent=2))
        
        return {
            "engine": engine,
            "results": results,
            "analysis": analysis
        }
    
    def run_medical_compliance_workflow(self) -> Dict[str, Any]:
        """Run HIPAA compliance workflow for medical data"""
        print("\n" + "=" * 60)
        print("HIPAA COMPLIANCE WORKFLOW DEMO")
        print("=" * 60)
        
        # Step 1: Create RuleEngine with HIPAA compliance
        print("\n1. Creating RuleEngine with HIPAA compliance configuration...")
        engine = (RuleEngineBuilder()
                 .with_pi_types([PIType.NAME, PIType.DOB, PIType.PHONE, PIType.EMAIL, PIType.SSN])
                 .with_removal_method("complete")  # Complete removal for HIPAA
                 .with_compliance_standard("HIPAA")
                 .with_confidence_threshold(0.95)  # Very high threshold for medical data
                 .with_log_level("WARNING")
                 .build())
        
        # Step 2: Generate medical record logs
        print("\n2. Generating medical record logs...")
        medical_logs = self.log_generator.generate_log_batch(5, [LogType.MEDICAL_RECORD])
        formatted_medical_logs = self.log_generator.format_log_batch(medical_logs)
        
        for i, log in enumerate(formatted_medical_logs, 1):
            print(f"   Medical Log {i}: {log}")
        
        # Step 3: Process with HIPAA validation
        print("\n3. Processing medical logs with HIPAA compliance validation...")
        results = []
        
        for i, log in enumerate(formatted_medical_logs, 1):
            print(f"\n   Processing Medical Log {i}:")
            print(f"   Original: {log}")
            
            result = engine.process_text(log)
            results.append(result)
            
            print(f"   Processed: {result.processed_text}")
            print(f"   HIPAA Compliant: {all(vr.is_valid for vr in result.validation_results.values())}")
            
            # Show HIPAA-specific validation
            for pi_type, validation in result.validation_results.items():
                print(f"     {pi_type.value} HIPAA Validation: Score={validation.validation_score:.2f}, Valid={validation.is_valid}")
                if not validation.is_valid:
                    for rec in validation.recommendations:
                        print(f"       HIPAA Recommendation: {rec}")
        
        # Step 4: Generate HIPAA compliance report
        print("\n4. Generating HIPAA compliance report...")
        report = self._generate_compliance_report(results, engine, "HIPAA")
        print(json.dumps(report, indent=2))
        
        return {
            "engine": engine,
            "results": results,
            "report": report
        }
    
    def _generate_summary_report(self, results: List, engine: RuleEngine) -> Dict[str, Any]:
        """Generate summary report for basic workflow"""
        total_logs = len(results)
        total_pi_detected = sum(len(r.all_matches) for r in results)
        total_processing_time = sum(r.processing_time_ms for r in results)
        successful_processing = sum(1 for r in results if r.success)
        
        # Count PI types
        pi_type_counts = {}
        for result in results:
            for match in result.all_matches:
                pi_type_counts[match.pi_type.value] = pi_type_counts.get(match.pi_type.value, 0) + 1
        
        # Get engine statistics
        stats = engine.get_statistics()
        
        return {
            "workflow_type": "basic",
            "summary": {
                "total_logs_processed": total_logs,
                "successful_processing": successful_processing,
                "success_rate": successful_processing / total_logs if total_logs > 0 else 0,
                "total_pi_detected": total_pi_detected,
                "pi_detected_by_type": pi_type_counts,
                "total_processing_time_ms": total_processing_time,
                "average_processing_time_ms": total_processing_time / total_logs if total_logs > 0 else 0
            },
            "engine_statistics": stats
        }
    
    def _generate_compliance_report(self, results: List, engine: RuleEngine, standard: str) -> Dict[str, Any]:
        """Generate compliance report"""
        total_logs = len(results)
        compliant_logs = sum(1 for r in results if all(vr.is_valid for vr in r.validation_results.values()))
        
        # Count validation failures by type
        validation_failures = {}
        for result in results:
            for pi_type, validation in result.validation_results.items():
                if not validation.is_valid:
                    validation_failures[pi_type.value] = validation_failures.get(pi_type.value, 0) + 1
        
        # Count remaining PI by type and severity
        remaining_pi = {}
        for result in results:
            for validation in result.validation_results.values():
                for match in validation.remaining_matches:
                    key = f"{match.pi_type.value}_{match.severity.value}"
                    remaining_pi[key] = remaining_pi.get(key, 0) + 1
        
        return {
            "workflow_type": "compliance",
            "compliance_standard": standard,
            "summary": {
                "total_logs_processed": total_logs,
                "compliant_logs": compliant_logs,
                "compliance_rate": compliant_logs / total_logs if total_logs > 0 else 0,
                "validation_failures_by_type": validation_failures,
                "remaining_pi_by_type_severity": remaining_pi
            },
            "recommendations": self._get_compliance_recommendations(validation_failures, standard)
        }
    
    def _generate_performance_report(self, results: List, total_time: float, log_count: int) -> Dict[str, Any]:
        """Generate performance report"""
        total_pi_detected = sum(len(r.all_matches) for r in results)
        total_processing_time = sum(r.processing_time_ms for r in results)
        successful_processing = sum(1 for r in results if r.success)
        
        return {
            "workflow_type": "performance",
            "performance_metrics": {
                "total_logs_processed": log_count,
                "total_execution_time_ms": total_time,
                "average_log_processing_time_ms": total_time / log_count,
                "logs_per_second": log_count / (total_time / 1000),
                "total_engine_processing_time_ms": total_processing_time,
                "average_engine_processing_time_ms": total_processing_time / log_count,
                "successful_processing": successful_processing,
                "success_rate": successful_processing / log_count,
                "total_pi_detected": total_pi_detected,
                "pi_detection_rate": total_pi_detected / log_count
            },
            "optimization_suggestions": self._get_performance_suggestions(total_time, log_count)
        }
    
    def _generate_edge_case_analysis(self, results: List, engine: RuleEngine) -> Dict[str, Any]:
        """Generate edge case analysis"""
        total_logs = len(results)
        total_pi_detected = sum(len(r.all_matches) for r in results)
        
        # Analyze detection patterns
        detection_patterns = {}
        for result in results:
            for match in result.all_matches:
                confidence_range = f"{int(match.confidence * 10) * 10}%-{int(match.confidence * 10) * 10 + 10}%"
                detection_patterns[match.pi_type.value] = detection_patterns.get(match.pi_type.value, {})
                detection_patterns[match.pi_type.value][confidence_range] = detection_patterns[match.pi_type.value].get(confidence_range, 0) + 1
        
        # Analyze validation failures
        validation_issues = {}
        for result in results:
            for pi_type, validation in result.validation_results.items():
                if not validation.is_valid:
                    validation_issues[pi_type.value] = validation_issues.get(pi_type.value, {
                        "failures": 0,
                        "remaining_pi": 0,
                        "common_issues": []
                    })
                    validation_issues[pi_type.value]["failures"] += 1
                    validation_issues[pi_type.value]["remaining_pi"] += len(validation.remaining_matches)
                    validation_issues[pi_type.value]["common_issues"].extend(validation.recommendations[:2])
        
        return {
            "workflow_type": "edge_case_analysis",
            "analysis": {
                "total_edge_cases_tested": total_logs,
                "total_pi_detected": total_pi_detected,
                "detection_patterns_by_confidence": detection_patterns,
                "validation_issues_by_type": validation_issues
            },
            "recommendations": self._get_edge_case_recommendations(validation_issues)
        }
    
    def _get_compliance_recommendations(self, failures: Dict[str, int], standard: str) -> List[str]:
        """Get compliance-specific recommendations"""
        recommendations = []
        
        if failures:
            recommendations.append(f"Consider using complete removal method for {standard} compliance")
            recommendations.append("Increase confidence threshold to reduce false positives")
            
            if standard == "GDPR":
                recommendations.append("Ensure all direct personal identifiers are completely removed")
            elif standard == "HIPAA":
                recommendations.append("Verify that all Protected Health Information (PHI) is removed")
            elif standard == "PCI_DSS":
                recommendations.append("Implement tokenization for payment card data")
        else:
            recommendations.append(f"All logs are {standard} compliant")
        
        return recommendations
    
    def _get_performance_suggestions(self, total_time: float, log_count: int) -> List[str]:
        """Get performance optimization suggestions"""
        suggestions = []
        avg_time_per_log = total_time / log_count
        
        if avg_time_per_log > 10:  # More than 10ms per log
            suggestions.append("Consider disabling audit trail for better performance")
            suggestions.append("Use basic validation instead of strict validation")
            suggestions.append("Reduce the number of enabled PI types if possible")
        
        if avg_time_per_log > 50:  # More than 50ms per log
            suggestions.append("Consider implementing batch processing for large volumes")
            suggestions.append("Use masking instead of complete removal for better performance")
        
        return suggestions
    
    def _get_edge_case_recommendations(self, issues: Dict[str, Dict]) -> List[str]:
        """Get edge case-specific recommendations"""
        recommendations = []
        
        for pi_type, issue_data in issues.items():
            if issue_data["failures"] > 0:
                recommendations.append(f"Improve {pi_type} detection patterns for edge cases")
                recommendations.append(f"Consider adding custom rules for {pi_type} variations")
        
        if not issues:
            recommendations.append("All edge cases handled successfully")
        
        return recommendations


def main():
    """Main function to run all workflow demos"""
    demo = WorkflowDemo()
    
    print("PI RULEENGINE WORKFLOW DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases the complete PI processing workflow:")
    print("1. Basic workflow with default configuration")
    print("2. GDPR compliance workflow")
    print("3. Performance testing workflow")
    print("4. Edge case testing workflow")
    print("5. HIPAA compliance workflow")
    
    try:
        # Run all workflows
        basic_results = demo.run_basic_workflow()
        gdpr_results = demo.run_compliance_workflow()
        performance_results = demo.run_performance_workflow()
        edge_case_results = demo.run_edge_case_workflow()
        hipaa_results = demo.run_medical_compliance_workflow()
        
        print("\n" + "=" * 60)
        print("ALL WORKFLOW DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        # Final summary
        print("\nFINAL SUMMARY:")
        print(f"- Basic workflow: {len(basic_results['results'])} logs processed")
        print(f"- GDPR workflow: {len(gdpr_results['results'])} logs processed")
        print(f"- Performance workflow: {len(performance_results['results'])} logs processed")
        print(f"- Edge case workflow: {len(edge_case_results['results'])} logs processed")
        print(f"- HIPAA workflow: {len(hipaa_results['results'])} logs processed")
        
    except Exception as e:
        print(f"\nERROR: Workflow demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
