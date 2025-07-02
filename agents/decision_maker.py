"""
Decision Maker Agent - 负责综合所有信息做出最终的理赔决策
"""
from typing import Dict, Any, List

class DecisionMaker:
    """决策制定智能体"""
    
    def __init__(self):
        self.decision_weights = {
            "policy_compliance": 0.6,  # 条款符合性权重
            "risk_level": 0.3,         # 风险等级权重
            "amount_factor": 0.1       # 金额因素权重
        }
    
    def decide(self, claim_info: Dict[str, Any], policy_findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        做出最终的理赔决策
        
        Args:
            claim_info: 理赔信息
            policy_findings: 条款检查结果
            
        Returns:
            最终决策结果
        """
        # 基础决策逻辑
        base_decision = self._make_base_decision(policy_findings)
        
        # 风险调整
        risk_adjusted_decision = self._adjust_for_risk(base_decision, claim_info)
        
        # 生成详细的决策报告
        decision_report = self._generate_report(
            claim_info, policy_findings, risk_adjusted_decision
        )
        
        return decision_report
    
    def _make_base_decision(self, policy_findings: Dict[str, Any]) -> str:
        """基于条款检查结果做出基础决策"""
        if policy_findings.get("overall_compliance", False):
            return "批准"
        else:
            return "拒绝"
    
    def _adjust_for_risk(self, base_decision: str, claim_info: Dict[str, Any]) -> str:
        """根据风险等级调整决策"""
        risk_level = claim_info.get("risk_level", "低风险")
        
        if base_decision == "批准":
            if risk_level == "高风险":
                return "需要人工审核"
            elif risk_level == "中风险":
                return "条件批准"
            else:
                return "批准"
        else:
            return base_decision
    
    def _generate_report(self, claim_info: Dict[str, Any], 
                        policy_findings: Dict[str, Any], 
                        final_decision: str) -> Dict[str, Any]:
        """生成详细的决策报告"""
        return {
            "decision": final_decision,
            "patient_name": claim_info.get("patient_name", "未知"),
            "procedure": claim_info.get("procedure", "未知"),
            "amount": claim_info.get("amount", "0"),
            "risk_level": claim_info.get("risk_level", "未知"),
            "policy_compliance": policy_findings.get("overall_compliance", False),
            "reasons": self._get_decision_reasons(policy_findings, final_decision),
            "confidence": self._calculate_confidence(policy_findings),
            "timestamp": self._get_timestamp()
        }
    
    def _get_decision_reasons(self, policy_findings: Dict[str, Any], decision: str) -> List[str]:
        """获取决策理由"""
        reasons = []
        
        if decision == "批准":
            reasons.append("符合保险条款要求")
            if policy_findings.get("coverage_check"):
                reasons.append("治疗在承保范围内")
            if policy_findings.get("amount_check"):
                reasons.append("金额在保险限额内")
        elif decision == "拒绝":
            if not policy_findings.get("coverage_check"):
                reasons.append("治疗不在承保范围内")
            if not policy_findings.get("amount_check"):
                reasons.append("金额超过保险限额")
            if not policy_findings.get("exclusion_check"):
                reasons.append("属于排除条款")
        elif decision == "需要人工审核":
            reasons.append("高风险案例，建议人工复核")
        
        return reasons
    
    def _calculate_confidence(self, policy_findings: Dict[str, Any]) -> float:
        """计算决策置信度"""
        checks_passed = sum([
            policy_findings.get("coverage_check", False),
            policy_findings.get("amount_check", False),
            policy_findings.get("exclusion_check", False)
        ])
        return checks_passed / 3.0
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 