"""
决策制定智能体 - 基于真实Medicare审核结果制定最终决策
综合考虑覆盖状态、风险评估、费用合规性等因素
"""

from typing import Dict, Any
from datetime import datetime

class DecisionMaker:
    """
    决策制定智能体
    基于PolicyChecker的Medicare审核结果制定最终理赔决策
    """
    
    def __init__(self):
        # 决策权重配置
        self.decision_weights = {
            "coverage_status": 0.40,    # 覆盖状态权重
            "risk_level": 0.25,         # 风险等级权重
            "cost_compliance": 0.20,    # 费用合规权重
            "special_requirements": 0.15 # 特殊要求权重
        }
        
        # 决策阈值
        self.decision_thresholds = {
            "auto_approve": 0.80,       # 自动批准阈值
            "manual_review": 0.50,      # 人工审核阈值
            "auto_deny": 0.20          # 自动拒绝阈值
        }
    
    def make_decision(self, extracted_info: Dict[str, Any], policy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于Medicare审核结果制定最终决策
        
        Args:
            extracted_info: 提取的理赔信息
            policy_result: PolicyChecker的审核结果
            
        Returns:
            最终决策结果
        """
        # 获取基本信息
        patient = extracted_info.get('patient', 'Unknown')
        cost = extracted_info.get('cost', 0)
        
        # 计算决策分数
        decision_score = self._calculate_decision_score(policy_result)
        
        # 确定决策
        decision_type = self._determine_decision_type(decision_score, policy_result)
        
        # 生成决策理由
        reason = self._generate_decision_reason(policy_result, decision_score)
        
        # 计算置信度
        confidence = self._calculate_confidence(policy_result, decision_score)
        
        # 生成推荐行动
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
        """计算综合决策分数"""
        score = 0.0
        
        # 1. 覆盖状态分数
        coverage_status = policy_result.get('coverage_status', {}).get('status', 'UNKNOWN')
        coverage_score = self._get_coverage_score(coverage_status)
        score += coverage_score * self.decision_weights["coverage_status"]
        
        # 2. 风险等级分数
        risk_level = policy_result.get('risk_level', {}).get('level', 'MEDIUM')
        risk_score = self._get_risk_score(risk_level)
        score += risk_score * self.decision_weights["risk_level"]
        
        # 3. 费用合规分数
        cost_compliance = policy_result.get('cost_compliance', {})
        cost_score = self._get_cost_score(cost_compliance)
        score += cost_score * self.decision_weights["cost_compliance"]
        
        # 4. 特殊要求分数
        special_requirements = policy_result.get('special_requirements', {})
        requirements_score = self._get_requirements_score(special_requirements)
        score += requirements_score * self.decision_weights["special_requirements"]
        
        return max(0.0, min(1.0, score))  # 确保分数在0-1之间
    
    def _get_coverage_score(self, coverage_status: str) -> float:
        """根据覆盖状态计算分数"""
        status_scores = {
            "COVERED": 1.0,
            "CONDITIONAL": 0.7,
            "REQUIRES_REVIEW": 0.5,
            "EXCLUDED": 0.0,
            "UNKNOWN": 0.3
        }
        return status_scores.get(coverage_status, 0.3)
    
    def _get_risk_score(self, risk_level: str) -> float:
        """根据风险等级计算分数"""
        risk_scores = {
            "LOW": 1.0,
            "MEDIUM": 0.6,
            "HIGH": 0.2
        }
        return risk_scores.get(risk_level, 0.6)
    
    def _get_cost_score(self, cost_compliance: Dict[str, Any]) -> float:
        """根据费用合规性计算分数"""
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
        """根据特殊要求合规性计算分数"""
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
        """根据分数和政策结果确定决策类型"""
        
        # 检查PolicyChecker的建议决策
        policy_decision = policy_result.get('final_decision', {}).get('decision', 'REQUIRES_REVIEW')
        
        # 如果PolicyChecker明确拒绝，直接拒绝
        if policy_decision == "DENIED":
            return "DENIED"
        
        # 如果是高风险或需要人工审核
        if policy_result.get('risk_level', {}).get('requires_manual_review', False):
            return "REQUIRES_REVIEW"
        
        # 基于分数决策
        if decision_score >= self.decision_thresholds["auto_approve"]:
            return "APPROVED"
        elif decision_score >= self.decision_thresholds["manual_review"]:
            return "REQUIRES_REVIEW"
        else:
            return "DENIED"
    
    def _generate_decision_reason(self, policy_result: Dict[str, Any], decision_score: float) -> str:
        """生成决策理由"""
        coverage_status = policy_result.get('coverage_status', {})
        risk_level = policy_result.get('risk_level', {})
        cost_compliance = policy_result.get('cost_compliance', {})
        
        reasons = []
        
        # 添加覆盖状态理由
        if coverage_status.get('status') == 'COVERED':
            reasons.append(f"服务在Medicare覆盖范围内 ({coverage_status.get('source', '')})")
        elif coverage_status.get('status') == 'CONDITIONAL':
            reasons.append(f"有条件覆盖，需满足特定要求")
        elif coverage_status.get('status') == 'EXCLUDED':
            reasons.append(f"服务被Medicare排除")
        
        # 添加风险评估理由
        risk_factors = risk_level.get('factors', [])
        if risk_factors:
            reasons.append(f"风险因子: {', '.join(risk_factors[:2])}")
        
        # 添加费用相关理由
        warnings = cost_compliance.get('warnings', [])
        if warnings:
            reasons.append(f"费用警告: {warnings[0]}")
        
        # 添加综合分数
        reasons.append(f"综合评分: {decision_score:.2f}")
        
        return " | ".join(reasons)
    
    def _calculate_confidence(self, policy_result: Dict[str, Any], decision_score: float) -> float:
        """计算决策置信度"""
        base_confidence = decision_score
        
        # 如果有明确的Medicare覆盖决定，提高置信度
        coverage_status = policy_result.get('coverage_status', {}).get('status', '')
        if coverage_status in ['COVERED', 'EXCLUDED']:
            base_confidence += 0.1
        
        # 如果风险评估清晰，提高置信度
        risk_level = policy_result.get('risk_level', {}).get('level', '')
        if risk_level in ['LOW', 'HIGH']:
            base_confidence += 0.05
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_recommendations(self, policy_result: Dict[str, Any], decision_type: str) -> list:
        """生成推荐行动"""
        recommendations = []
        
        if decision_type == "APPROVED":
            recommendations.append("批准理赔申请")
            recommendations.append("按Medicare标准支付")
            
        elif decision_type == "DENIED":
            coverage_reason = policy_result.get('coverage_status', {}).get('reason', '')
            recommendations.append(f"拒绝理赔: {coverage_reason}")
            recommendations.append("向患者解释拒绝原因")
            
        elif decision_type == "REQUIRES_REVIEW":
            recommendations.append("提交人工审核")
            special_req = policy_result.get('special_requirements', {})
            if special_req.get('prior_authorization'):
                recommendations.append("验证事先授权文件")
            if special_req.get('physician_certification'):
                recommendations.append("要求医生认证文件")
        
        # 添加风险相关建议
        risk_level = policy_result.get('risk_level', {}).get('level', '')
        if risk_level == "HIGH":
            recommendations.append("高风险案例，建议委员会审核")
        
        return recommendations 