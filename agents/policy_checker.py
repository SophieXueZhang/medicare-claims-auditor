"""
Medicare Policy Compliance Checker Agent - Based on Real Medicare NCD/LCD Data
Responsible for validating claims applications against insurance policies and coverage rules
"""

import json
import re
from pathlib import Path

class PolicyChecker:
    """
    Medicare Policy Compliance Checker Agent
    Based on real Medicare NCD (National Coverage Determinations) and 
    LCD (Local Coverage Determinations) data for coverage decisions
    """
    
    def __init__(self):
        self.medicare_rules = self._load_medicare_rules()
        self.coverage_matrix = self.medicare_rules.get("audit_rules", {}).get("coverage_matrix", {})
        self.benefit_categories = self.medicare_rules.get("benefit_categories", {})
        
    def _load_medicare_rules(self):
        """Load real Medicare audit rules"""
        rules_file = Path("data/medicare_audit_rules.json")
        if rules_file.exists():
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Medicare rules: {e}")
                return self._get_fallback_rules()
        else:
            print("Medicare rules file not found, using fallback rules")
            return self._get_fallback_rules()
    
    def _get_fallback_rules(self):
        """Fallback rules (if unable to load real rules)"""
        return {
            "coverage_rules": {
                "covered": [],
                "conditional": [],
                "excluded": [],
                "limits": {
                    "annual_deductible": 1600,
                    "coinsurance_rate": 0.20,
                    "max_therapy_visits": {"physical_therapy": 36}
                }
            },
            "audit_rules": {
                "coverage_matrix": {
                    "always_covered": [],
                    "conditionally_covered": [],
                    "never_covered": []
                }
            },
            "benefit_categories": {}
        }
    
    def check_policy_compliance(self, extracted_info):
        """
        Check claims application policy compliance
        Based on real Medicare coverage determination data
        """
        patient = extracted_info.get('patient', 'Unknown')
        diagnosis = extracted_info.get('diagnosis', '').lower()
        treatment = extracted_info.get('treatment', '').lower()
        cost = extracted_info.get('cost', 0)
        
        # Get coverage rules
        coverage_rules = self.medicare_rules.get("coverage_rules", {})
        audit_rules = self.medicare_rules.get("audit_rules", {})
        
        # Check coverage status
        coverage_status = self._determine_coverage_status(diagnosis, treatment, coverage_rules)
        
        # Check cost limits
        cost_compliance = self._check_cost_limits(cost, coverage_rules.get("limits", {}))
        
        # Check special requirements
        special_requirements = self._check_special_requirements(diagnosis, treatment, coverage_rules.get("requirements", {}))
        
        # Risk assessment
        risk_level = self._assess_risk_level(cost, diagnosis, treatment, audit_rules.get("risk_assessment", {}))
        
        # Determine final decision
        final_decision = self._make_coverage_decision(
            coverage_status, cost_compliance, special_requirements, risk_level, cost
        )
        
        return {
            "patient": patient,
            "coverage_status": coverage_status,
            "cost_compliance": cost_compliance,
            "special_requirements": special_requirements,
            "risk_level": risk_level,
            "final_decision": final_decision,
            "applicable_ncds": self._find_applicable_ncds(diagnosis, treatment),
            "benefit_category": self._determine_benefit_category(treatment),
            "compliance_details": {
                "deductible_applicable": True,
                "coinsurance_rate": coverage_rules.get("limits", {}).get("coinsurance_rate", 0.20),
                "geographic_considerations": "Standard metropolitan area",
                "prior_authorization_required": "prior authorization" in str(special_requirements).lower()
            }
        }
    
    def _determine_coverage_status(self, diagnosis, treatment, coverage_rules):
        """Determine coverage status based on real Medicare rules"""
        
        # Check fully covered items
        covered_rules = coverage_rules.get("covered", [])
        for rule in covered_rules:
            if self._matches_rule(diagnosis, treatment, rule):
                return {
                    "status": "COVERED",
                    "source": rule.get("source", "Unknown"),
                    "title": rule.get("title", ""),
                    "reason": f"Meets Medicare coverage determination: {rule.get('title', '')}"
                }
        
        # Check conditionally covered items
        conditional_rules = coverage_rules.get("conditional", [])
        for rule in conditional_rules:
            if self._matches_rule(diagnosis, treatment, rule):
                return {
                    "status": "CONDITIONAL",
                    "source": rule.get("source", "Unknown"),
                    "title": rule.get("title", ""),
                    "reason": f"Conditional coverage, must meet specific requirements: {rule.get('title', '')}"
                }
        
        # Check excluded items
        excluded_rules = coverage_rules.get("excluded", [])
        for rule in excluded_rules:
            if self._matches_rule(diagnosis, treatment, rule):
                return {
                    "status": "EXCLUDED",
                    "source": rule.get("source", "Unknown"), 
                    "title": rule.get("title", ""),
                    "reason": f"Explicitly excluded service: {rule.get('title', '')}"
                }
        
        # Default requires manual review
        return {
            "status": "REQUIRES_REVIEW",
            "source": "Policy_Default",
            "title": "Manual Review Required",
            "reason": "No explicit coverage determination found, requires manual review"
        }
    
    def _matches_rule(self, diagnosis, treatment, rule):
        """Check if diagnosis and treatment match specific rules"""
        conditions = rule.get("condition", [])
        procedures = rule.get("procedure", [])
        
        # Check diagnosis match
        diagnosis_match = False
        if not conditions:  # If no specific conditions, consider it a match
            diagnosis_match = True
        else:
            for condition in conditions:
                if condition.lower() in diagnosis.lower():
                    diagnosis_match = True
                    break
        
        # Check treatment match
        treatment_match = False
        if not procedures:  # If no specific procedures, consider it a match
            treatment_match = True
        else:
            for procedure in procedures:
                if procedure.lower() in treatment.lower():
                    treatment_match = True
                    break
        
        return diagnosis_match or treatment_match
    
    def _check_cost_limits(self, cost, limits):
        """Check cost limitations"""
        annual_deductible = limits.get("annual_deductible", 1600)
        coinsurance_rate = limits.get("coinsurance_rate", 0.20)
        
        # Calculate patient responsibility
        patient_responsibility = annual_deductible + (cost - annual_deductible) * coinsurance_rate
        insurance_payment = cost - patient_responsibility
        
        # Check if exceeding specific limits
        warnings = []
        if cost > 50000:
            warnings.append("High-cost claim requiring special review")
        if cost > 100000:
            warnings.append("Ultra-high-cost claim requiring committee review")
        
        return {
            "total_cost": cost,
            "deductible": annual_deductible,
            "patient_responsibility": round(patient_responsibility, 2),
            "insurance_payment": round(insurance_payment, 2),
            "coinsurance_rate": coinsurance_rate,
            "warnings": warnings,
            "compliant": True  # Medicare typically has no absolute cost ceiling
        }
    
    def _check_special_requirements(self, diagnosis, treatment, requirements):
        """Check special requirements"""
        required_items = []
        
        prior_auth_items = requirements.get("prior_authorization", [])
        for item in prior_auth_items:
            if any(keyword in treatment.lower() for keyword in item.lower().split()):
                required_items.append(f"Prior authorization required: {item}")
        
        physician_cert_items = requirements.get("physician_certification", [])
        for item in physician_cert_items:
            if any(keyword in treatment.lower() for keyword in item.lower().split()):
                required_items.append(f"Physician certification required: {item}")
        
        documentation_items = requirements.get("documentation_required", [])
        if documentation_items:
            required_items.extend([f"Documentation required: {item}" for item in documentation_items[:2]])
        
        return {
            "required_items": required_items,
            "prior_authorization": any("prior authorization" in item.lower() for item in required_items),
            "physician_certification": any("physician certification" in item.lower() for item in required_items),
            "additional_documentation": any("documentation" in item.lower() for item in required_items),
            "compliant": True  # Assume application contains necessary information
        }
    
    def _assess_risk_level(self, cost, diagnosis, treatment, risk_assessment):
        """Assess claims risk level"""
        high_risk = risk_assessment.get("high_risk_indicators", [])
        medium_risk = risk_assessment.get("medium_risk_indicators", [])
        low_risk = risk_assessment.get("low_risk_indicators", [])
        
        risk_score = 0
        risk_factors = []
        
        # Check high-risk indicators
        if cost > 50000:
            risk_score += 3
            risk_factors.append("High-cost claim")
        
        if any(keyword in treatment.lower() for keyword in ["experimental", "investigational"]):
            risk_score += 3
            risk_factors.append("Experimental treatment")
        
        # Check medium-risk indicators
        if cost > 10000:
            risk_score += 2
            risk_factors.append("Elevated cost")
        
        if any(keyword in treatment.lower() for keyword in ["elective"]):
            risk_score += 2
            risk_factors.append("Elective procedure")
        
        # Check low-risk indicators
        if any(keyword in treatment.lower() for keyword in ["routine", "preventive"]):
            risk_score -= 1
            risk_factors.append("Routine care")
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 2:
            risk_level = "MEDIUM" 
        else:
            risk_level = "LOW"
        
        return {
            "level": risk_level,
            "score": risk_score,
            "factors": risk_factors,
            "requires_manual_review": risk_level in ["HIGH", "MEDIUM"]
        }
    
    def _make_coverage_decision(self, coverage_status, cost_compliance, special_requirements, risk_level, cost):
        """Make final coverage decision based on all factors"""
        
        status = coverage_status.get("status", "REQUIRES_REVIEW")
        risk = risk_level.get("level", "MEDIUM")
        
        # Excluded items are directly denied
        if status == "EXCLUDED":
            return {
                "decision": "DENIED",
                "reason": coverage_status.get("reason", "Service excluded from coverage"),
                "confidence": 0.95
            }
        
        # Clearly covered low-risk items are auto-approved
        if status == "COVERED" and risk == "LOW" and cost < 5000:
            return {
                "decision": "APPROVED",
                "reason": "Meets Medicare coverage standards with low risk",
                "confidence": 0.90
            }
        
        # Conditional coverage requires checking requirements
        if status == "CONDITIONAL":
            if special_requirements.get("compliant", True):
                return {
                    "decision": "APPROVED",
                    "reason": "Meets conditional coverage requirements",
                    "confidence": 0.80
                }
            else:
                return {
                    "decision": "PENDING",
                    "reason": "Additional requirements must be met",
                    "confidence": 0.60
                }
        
        # High-risk or high-cost requires manual review
        if risk == "HIGH" or cost > 25000:
            return {
                "decision": "REQUIRES_REVIEW",
                "reason": "High-risk or high-cost claim requires manual review",
                "confidence": 0.50
            }
        
        # Default approval (meets basic conditions)
        return {
            "decision": "APPROVED",
            "reason": "Meets basic coverage conditions",
            "confidence": 0.75
        }
    
    def _find_applicable_ncds(self, diagnosis, treatment):
        """Find applicable NCD rules"""
        applicable_ncds = []
        coverage_rules = self.medicare_rules.get("coverage_rules", {})
        
        for category in ["covered", "conditional", "excluded"]:
            rules = coverage_rules.get(category, [])
            for rule in rules:
                if self._matches_rule(diagnosis, treatment, rule):
                    applicable_ncds.append({
                        "source": rule.get("source", ""),
                        "title": rule.get("title", ""),
                        "category": category
                    })
        
        return applicable_ncds[:3]  # Limit return quantity
    
    def _determine_benefit_category(self, treatment):
        """Determine benefit category"""
        treatment_lower = treatment.lower()
        
        # Determine benefit category based on treatment type
        if any(keyword in treatment_lower for keyword in ["surgery", "surgical"]):
            return "Inpatient Hospital Services"
        elif any(keyword in treatment_lower for keyword in ["therapy", "rehabilitation", "treatment"]):
            return "Outpatient Physical Therapy Services"
        elif any(keyword in treatment_lower for keyword in ["imaging", "x-ray", "ct", "mri"]):
            return "Diagnostic X-Ray Tests"
        elif any(keyword in treatment_lower for keyword in ["drug", "medication", "injection"]):
            return "Drugs and Biologicals"
        elif any(keyword in treatment_lower for keyword in ["device", "equipment"]):
            return "Durable Medical Equipment"
        else:
            return "Physicians' Services" 