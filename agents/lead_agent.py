"""
Lead Agent - 负责调度任务、调用子agent、整合结果
"""
from typing import Dict, Any
from datetime import datetime

class LeadAgent:
    """主导智能体，协调整个理赔审核流程"""
    
    def __init__(self):
        # 延迟导入避免循环依赖
        from agents.claim_extractor import ClaimExtractor
        from agents.policy_checker import PolicyChecker
        from agents.decision_maker import DecisionMaker
        
        self.claim_extractor = ClaimExtractor()
        self.policy_checker = PolicyChecker()
        self.decision_maker = DecisionMaker()
        
    def process_claim(self, claim_text: str) -> Dict[str, Any]:
        """
        处理理赔申请的完整流程
        基于真实Medicare NCD/LCD数据进行智能审核
        
        Args:
            claim_text: 理赔申请文本（中英文都支持）
            
        Returns:
            完整的审核结果
        """
        print("=== 开始理赔申请处理 ===")
        
        # Step 1: 信息提取
        print("1. 提取理赔信息...")
        extracted_info = self.claim_extractor.extract_claim_info(claim_text)
        print(f"提取结果: {extracted_info}")
        
        # Step 2: 保险条款检查 (使用真实Medicare规则)
        print("\n2. 检查保险条款合规性...")
        policy_result = self.policy_checker.check_policy_compliance(extracted_info)
        print(f"条款检查结果: {policy_result['final_decision']}")
        
        # Step 3: 决策制定
        print("\n3. 制定最终决策...")
        final_decision = self.decision_maker.make_decision(extracted_info, policy_result)
        print(f"最终决策: {final_decision['decision']}")
        
        # Step 4: 整合所有结果
        complete_result = {
            "claim_info": extracted_info,
            "policy_compliance": policy_result,
            "final_decision": final_decision,
            "processing_summary": {
                "total_cost": extracted_info.get('cost', 0),
                "patient_responsibility": policy_result['cost_compliance']['patient_responsibility'],
                "insurance_payment": policy_result['cost_compliance']['insurance_payment'],
                "medicare_coverage_status": policy_result['coverage_status']['status'],
                "applicable_ncds": policy_result['applicable_ncds'],
                "benefit_category": policy_result['benefit_category'],
                "risk_level": policy_result['risk_level']['level'],
                "requires_manual_review": policy_result['risk_level']['requires_manual_review'],
                "processing_timestamp": datetime.now().isoformat()
            }
        }
        
        print("=== 理赔处理完成 ===")
        return complete_result 