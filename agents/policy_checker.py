"""
Policy Checker Agent - 负责检查理赔申请是否符合保险条款
"""
from typing import Dict, Any, List

class PolicyChecker:
    """保险条款检查智能体"""
    
    def __init__(self):
        # 保险条款规则（支持中英文，包含MIMIC-III常见程序）
        self.policy_rules = {
            "coverage_procedures": [
                # 中文程序
                "膝关节置换手术", "心脏搭桥手术", "白内障手术", 
                "阑尾炎手术", "胆囊切除术",
                # 英文程序（MIMIC-III常见）
                "mechanical ventilation", "ventilation", "coronary artery bypass", 
                "cardiac catheterization", "coronary arteriography", "catheterization",
                "insertion of endotracheal tube", "monitoring", "electrocardiogram",
                "arterial catheterization", "venous catheterization", "urinary catheter",
                "nutritional infusion", "enteral infusion", "knee replacement",
                "cataract surgery", "appendectomy", "gallbladder surgery"
            ],
            "max_amount": 200000,
            "waiting_period_exempt": [
                "意外伤害", "急性疾病", "emergency", "acute", "trauma"
            ],
            "excluded_conditions": [
                "美容手术", "实验性治疗", "非必要检查",
                "cosmetic surgery", "experimental treatment", "unnecessary examination",
                "routine checkup", "cosmetic"
            ]
        }
    
    def check(self, claim_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查理赔申请是否符合保险条款
        
        Args:
            claim_info: 提取的理赔信息
            
        Returns:
            条款检查结果
        """
        results = {
            "coverage_check": self._check_coverage(claim_info),
            "amount_check": self._check_amount(claim_info),
            "exclusion_check": self._check_exclusions(claim_info),
            "overall_compliance": True,
            "issues": []
        }
        
        # 汇总检查结果
        if not all([results["coverage_check"], results["amount_check"], results["exclusion_check"]]):
            results["overall_compliance"] = False
        
        return results
    
    def _check_coverage(self, claim_info: Dict[str, Any]) -> bool:
        """检查治疗是否在承保范围内"""
        procedure = claim_info.get('procedure', '')
        is_covered = any(covered in procedure for covered in self.policy_rules["coverage_procedures"])
        
        if not is_covered:
            return False
        return True
    
    def _check_amount(self, claim_info: Dict[str, Any]) -> bool:
        """检查理赔金额是否超过上限"""
        try:
            amount = float(claim_info.get('amount', 0))
            if amount > self.policy_rules["max_amount"]:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def _check_exclusions(self, claim_info: Dict[str, Any]) -> bool:
        """检查是否有排除条款"""
        procedure = claim_info.get('procedure', '')
        diagnosis = claim_info.get('diagnosis', '')
        
        for excluded in self.policy_rules["excluded_conditions"]:
            if excluded in procedure or excluded in diagnosis:
                return False
        return True 