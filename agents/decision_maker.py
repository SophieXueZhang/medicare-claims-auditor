"""
Decision制定agent - 基于真实Medicareaudit结果制定最终Decision
综合考虑coverage状态、riskEvaluating、cost合规性等因素
"""

from typing import Dict, Any
from datetime import datetime

class DecisionMaker:
    """
    Decision制定agent
    基于PolicyChecker的Medicareaudit结果制定最终claimsDecision
    """
    
    def __init__(self):
        # Decision权重配置
        self.decision_weights = {
            "coverage_status": 0.40,    # coverage状态权重
            "risk_level": 0.25,         # risk等级权重
            "cost_compliance": 0.20,    # cost合规权重
            "special_requirements": 0.15 # 特殊要求权重
        }
        
        # Decision阈值
        self.decision_thresholds = {
            "auto_approve": 0.80,       # 自动approval阈值
            "manual_review": 0.50,      # 人工audit阈值
            "auto_deny": 0.20          # 自动denial阈值
        }
    
    def make_decision(self, extracted_info: Dict[str, Any], policy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于Medicareaudit结果制定最终Decision
        
        Args:
            extracted_info: 提取的claims信息
            policy_result: PolicyChecker的audit结果
            
        Returns:
            最终Decision结果
        """
        # 获取基本信息
        patient = extracted_info.get('patient', 'Unknown')
        cost = extracted_info.get('cost', 0)
        
        # CalculatingDecision分数
        decision_score = self._calculate_decision_score(policy_result)
        
        # 确定Decision
        decision_type = self._determine_decision_type(decision_score, policy_result)
        
        # GeneratingDecisionReason
        reason = self._generate_decision_reason(policy_result, decision_score)
        
        # CalculatingConfidence
        confidence = self._calculate_confidence(policy_result, decision_score)
        
        # Generating推荐行动
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
        """Calculating综合Decision分数"""
        score = 0.0
        
        # 1. coverage状态分数
        coverage_status = policy_result.get('coverage_status', {}).get('status', 'UNKNOWN')
        coverage_score = self._get_coverage_score(coverage_status)
        score += coverage_score * self.decision_weights["coverage_status"]
        
        # 2. risk等级分数
        risk_level = policy_result.get('risk_level', {}).get('level', 'MEDIUM')
        risk_score = self._get_risk_score(risk_level)
        score += risk_score * self.decision_weights["risk_level"]
        
        # 3. cost合规分数
        cost_compliance = policy_result.get('cost_compliance', {})
        cost_score = self._get_cost_score(cost_compliance)
        score += cost_score * self.decision_weights["cost_compliance"]
        
        # 4. 特殊要求分数
        special_requirements = policy_result.get('special_requirements', {})
        requirements_score = self._get_requirements_score(special_requirements)
        score += requirements_score * self.decision_weights["special_requirements"]
        
        return max(0.0, min(1.0, score))  # 确保分数在0-1之间
    
    def _get_coverage_score(self, coverage_status: str) -> float:
        """根据coverage状态Calculating分数"""
        status_scores = {
            "COVERED": 1.0,
            "CONDITIONAL": 0.7,
            "REQUIRES_REVIEW": 0.5,
            "EXCLUDED": 0.0,
            "UNKNOWN": 0.3
        }
        return status_scores.get(coverage_status, 0.3)
    
    def _get_risk_score(self, risk_level: str) -> float:
        """根据risk等级Calculating分数"""
        risk_scores = {
            "LOW": 1.0,
            "MEDIUM": 0.6,
            "HIGH": 0.2
        }
        return risk_scores.get(risk_level, 0.6)
    
    def _get_cost_score(self, cost_compliance: Dict[str, Any]) -> float:
        """根据cost合规性Calculating分数"""
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
        """根据特殊要求合规性Calculating分数"""
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
        """根据分数和policy结果确定Decision类型"""
        
        # CheckingPolicyChecker的建议Decision
        policy_decision = policy_result.get('final_decision', {}).get('decision', 'REQUIRES_REVIEW')
        
        # 如果PolicyChecker明确denial，直接denial
        if policy_decision == "DENIED":
            return "DENIED"
        
        # 如果是高risk或需要人工audit
        if policy_result.get('risk_level', {}).get('requires_manual_review', False):
            return "REQUIRES_REVIEW"
        
        # 基于分数Decision
        if decision_score >= self.decision_thresholds["auto_approve"]:
            return "APPROVED"
        elif decision_score >= self.decision_thresholds["manual_review"]:
            return "REQUIRES_REVIEW"
        else:
            return "DENIED"
    
    def _generate_decision_reason(self, policy_result: Dict[str, Any], decision_score: float) -> str:
        """GeneratingDecisionReason"""
        coverage_status = policy_result.get('coverage_status', {})
        risk_level = policy_result.get('risk_level', {})
        cost_compliance = policy_result.get('cost_compliance', {})
        
        reasons = []
        
        # 添加coverage状态Reason
        if coverage_status.get('status') == 'COVERED':
            reasons.append(f"服务在Medicarecoverage范围内 ({coverage_status.get('source', '')})")
        elif coverage_status.get('status') == 'CONDITIONAL':
            reasons.append(f"有条件coverage，需满足特定要求")
        elif coverage_status.get('status') == 'EXCLUDED':
            reasons.append(f"服务被Medicare排除")
        
        # 添加riskEvaluatingReason
        risk_factors = risk_level.get('factors', [])
        if risk_factors:
            reasons.append(f"risk因子: {', '.join(risk_factors[:2])}")
        
        # 添加cost相关Reason
        warnings = cost_compliance.get('warnings', [])
        if warnings:
            reasons.append(f"cost警告: {warnings[0]}")
        
        # 添加综合分数
        reasons.append(f"Comprehensive score: {decision_score:.2f}")
        
        return " | ".join(reasons)
    
    def _calculate_confidence(self, policy_result: Dict[str, Any], decision_score: float) -> float:
        """CalculatingDecisionConfidence"""
        base_confidence = decision_score
        
        # 如果有明确的Medicarecoverage决定，提高Confidence
        coverage_status = policy_result.get('coverage_status', {}).get('status', '')
        if coverage_status in ['COVERED', 'EXCLUDED']:
            base_confidence += 0.1
        
        # 如果riskEvaluating清晰，提高Confidence
        risk_level = policy_result.get('risk_level', {}).get('level', '')
        if risk_level in ['LOW', 'HIGH']:
            base_confidence += 0.05
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_recommendations(self, policy_result: Dict[str, Any], decision_type: str) -> list:
        """Generating推荐行动"""
        recommendations = []
        
        if decision_type == "APPROVED":
            recommendations.append("approvalclaims申请")
            recommendations.append("按Medicare标准支付")
            
        elif decision_type == "DENIED":
            coverage_reason = policy_result.get('coverage_status', {}).get('reason', '')
            recommendations.append(f"denialclaims: {coverage_reason}")
            recommendations.append("向patient解释denial原因")
            
        elif decision_type == "REQUIRES_REVIEW":
            recommendations.append("提交人工audit")
            special_req = policy_result.get('special_requirements', {})
            if special_req.get('prior_authorization'):
                recommendations.append("Validating事先授权文件")
            if special_req.get('physician_certification'):
                recommendations.append("要求医生认证文件")
        
        # 添加risk相关建议
        risk_level = policy_result.get('risk_level', {}).get('level', '')
        if risk_level == "HIGH":
            recommendations.append("高riskcases，建议委员会audit")
        
        return recommendations 