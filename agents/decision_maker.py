"""
Decision Making Agent - Based on Real Medicare Audit Results for Final Decisions
Comprehensively considers coverage status, risk assessment, cost compliance and other factors
"""

from typing import Dict, Any
from datetime import datetime

class DecisionMaker:
    """
    Decision Making Agent
    Based on PolicyChecker's Medicare audit results to make final claims decisions
    """
    
    def __init__(self):
        # Decision weight configuration
        self.decision_weights = {
            "coverage_status": 0.40,    # Coverage status weight
            "risk_level": 0.25,         # Risk level weight
            "cost_compliance": 0.20,    # Cost compliance weight
            "special_requirements": 0.15 # Special requirements weight
        }
        
        # Decision thresholds
        self.decision_thresholds = {
            "auto_approve": 0.80,       # Auto-approval threshold
            "manual_review": 0.50,      # Manual review threshold
            "auto_deny": 0.20          # Auto-denial threshold
        }
    
    def make_decision(self, extracted_info: Dict[str, Any], policy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make final decision based on Medicare audit results
        
        Args:
            extracted_info: Extracted claims information
            policy_result: PolicyChecker's audit results
            
        Returns:
            Final decision result
        """
        # Get basic information
        patient = extracted_info.get('patient', 'Unknown')
        cost = extracted_info.get('cost', 0)
        
        # Calculate decision score
        decision_score = self._calculate_decision_score(policy_result)
        
        # Determine decision
        decision_type = self._determine_decision_type(decision_score, policy_result)
        
        # Generate decision reason
        reason = self._generate_decision_reason(policy_result, decision_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(policy_result, decision_score)
        
        # Generate recommended actions
        recommendations = self._generate_recommendations(policy_result, decision_type)
        
        return {
            "patient": patient,
            "decision": decision_type,
            "decision_score": round(decision_score, 3),
            "confidence": round(confidence, 3),
            "reason": reason,
            "recommendations": recommendations,
            "financial_impact": {
                "total_claim_amount": cost,
                "approved_amount": cost if decision_type == "APPROVED" else 0,
                "patient_responsibility": policy_result.get('cost_compliance', {}).get('patient_responsibility', 0),
                "insurance_payment": policy_result.get('cost_compliance', {}).get('insurance_payment', 0) if decision_type == "APPROVED" else 0
            },
            "medicare_details": {
                "coverage_status": policy_result.get('coverage_status', {}).get('status', 'UNKNOWN'),
                "applicable_ncds": policy_result.get('applicable_ncds', []),
                "benefit_category": policy_result.get('benefit_category', 'Unknown'),
                "risk_level": policy_result.get('risk_level', {}).get('level', 'MEDIUM')
            },
            "processing_metadata": {
                "decision_timestamp": datetime.now().isoformat(),
                "requires_manual_review": policy_result.get('risk_level', {}).get('requires_manual_review', False),
                "escalation_required": decision_type == "REQUIRES_REVIEW"
            }
        }
    
    def _calculate_decision_score(self, policy_result: Dict[str, Any]) -> float:
        """Calculate comprehensive decision score"""
        score = 0.0
        
        # 1. Coverage status score
        coverage_status = policy_result.get('coverage_status', {}).get('status', 'UNKNOWN')
        coverage_score = self._get_coverage_score(coverage_status)
        score += coverage_score * self.decision_weights["coverage_status"]
        
        # 2. Risk level score
        risk_level = policy_result.get('risk_level', {}).get('level', 'MEDIUM')
        risk_score = self._get_risk_score(risk_level)
        score += risk_score * self.decision_weights["risk_level"]
        
        # 3. Cost compliance score
        cost_compliance = policy_result.get('cost_compliance', {})
        cost_score = self._get_cost_score(cost_compliance)
        score += cost_score * self.decision_weights["cost_compliance"]
        
        # 4. Special requirements score
        special_requirements = policy_result.get('special_requirements', {})
        requirements_score = self._get_requirements_score(special_requirements)
        score += requirements_score * self.decision_weights["special_requirements"]
        
        return max(0.0, min(1.0, score))  # Ensure score is between 0-1
    
    def _get_coverage_score(self, coverage_status: str) -> float:
        """Calculate score based on coverage status"""
        status_scores = {
            "COVERED": 1.0,
            "CONDITIONAL": 0.7,
            "REQUIRES_REVIEW": 0.5,
            "EXCLUDED": 0.0,
            "UNKNOWN": 0.3
        }
        return status_scores.get(coverage_status, 0.3)
    
    def _get_risk_score(self, risk_level: str) -> float:
        """Calculate score based on risk level"""
        risk_scores = {
            "LOW": 1.0,
            "MEDIUM": 0.6,
            "HIGH": 0.2
        }
        return risk_scores.get(risk_level, 0.6)
    
    def _get_cost_score(self, cost_compliance: Dict[str, Any]) -> float:
        """Calculate score based on cost compliance"""
        if not cost_compliance.get('compliant', True):
            return 0.0
        
        warnings = cost_compliance.get('warnings', [])
        if len(warnings) >= 2:
            return 0.3
        elif len(warnings) == 1:
            return 0.7
        else:
            return 1.0
    
    def _get_requirements_score(self, special_requirements: Dict[str, Any]) -> float:
        """Calculate score based on special requirements compliance"""
        if not special_requirements.get('compliant', True):
            return 0.0
        
        required_items = special_requirements.get('required_items', [])
        if len(required_items) > 3:
            return 0.5
        elif len(required_items) > 0:
            return 0.8
        else:
            return 1.0
    
    def _determine_decision_type(self, decision_score: float, policy_result: Dict[str, Any]) -> str:
        """Determine decision type based on score and policy results"""
        
        # Check PolicyChecker's recommended decision
        policy_decision = policy_result.get('final_decision', {}).get('decision', 'REQUIRES_REVIEW')
        
        # If PolicyChecker explicitly denies, deny directly
        if policy_decision == "DENIED":
            return "DENIED"
        
        # If high risk or requires manual review
        if policy_result.get('risk_level', {}).get('requires_manual_review', False):
            return "REQUIRES_REVIEW"
        
        # Decision based on score
        if decision_score >= self.decision_thresholds["auto_approve"]:
            return "APPROVED"
        elif decision_score >= self.decision_thresholds["manual_review"]:
            return "REQUIRES_REVIEW"
        else:
            return "DENIED"
    
    def _generate_decision_reason(self, policy_result: Dict[str, Any], decision_score: float) -> str:
        """Generate decision reason"""
        coverage_status = policy_result.get('coverage_status', {})
        risk_level = policy_result.get('risk_level', {})
        cost_compliance = policy_result.get('cost_compliance', {})
        
        reasons = []
        
        # Add coverage status reason
        if coverage_status.get('status') == 'COVERED':
            reasons.append(f"Service within Medicare coverage ({coverage_status.get('source', '')})")
        elif coverage_status.get('status') == 'CONDITIONAL':
            reasons.append(f"Conditional coverage, must meet specific requirements")
        elif coverage_status.get('status') == 'EXCLUDED':
            reasons.append(f"Service excluded by Medicare")
        
        # Add risk assessment reason
        risk_factors = risk_level.get('factors', [])
        if risk_factors:
            reasons.append(f"Risk factors: {', '.join(risk_factors[:2])}")
        
        # Add cost-related reason
        warnings = cost_compliance.get('warnings', [])
        if warnings:
            reasons.append(f"Cost warning: {warnings[0]}")
        
        # Add comprehensive score
        reasons.append(f"Comprehensive score: {decision_score:.2f}")
        
        return " | ".join(reasons)
    
    def _calculate_confidence(self, policy_result: Dict[str, Any], decision_score: float) -> float:
        """Calculate decision confidence"""
        base_confidence = decision_score
        
        # If there's a clear Medicare coverage decision, increase confidence
        coverage_status = policy_result.get('coverage_status', {}).get('status', '')
        if coverage_status in ['COVERED', 'EXCLUDED']:
            base_confidence += 0.1
        
        # If risk assessment is clear, increase confidence
        risk_level = policy_result.get('risk_level', {}).get('level', '')
        if risk_level in ['LOW', 'HIGH']:
            base_confidence += 0.05
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_recommendations(self, policy_result: Dict[str, Any], decision_type: str) -> list:
        """Generate recommended actions"""
        recommendations = []
        
        if decision_type == "APPROVED":
            recommendations.append("Approve claims application")
            recommendations.append("Process payment according to Medicare standards")
            
        elif decision_type == "DENIED":
            coverage_reason = policy_result.get('coverage_status', {}).get('reason', '')
            recommendations.append(f"Deny claim: {coverage_reason}")
            recommendations.append("Explain denial reason to patient")
            
        elif decision_type == "REQUIRES_REVIEW":
            recommendations.append("Submit for manual review")
            special_req = policy_result.get('special_requirements', {})
            if special_req.get('prior_authorization'):
                recommendations.append("Verify prior authorization documentation")
            if special_req.get('physician_certification'):
                recommendations.append("Request physician certification documents")
        
        # Add risk-related recommendations
        risk_level = policy_result.get('risk_level', {}).get('level', '')
        if risk_level == "HIGH":
            recommendations.append("High-risk case, recommend committee review")
        
        return recommendations 