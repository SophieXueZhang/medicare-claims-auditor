"""
Lead Agent - 负责调度任务、调用子agent、整合结果
"""
from typing import Dict, Any

class LeadAgent:
    """主导智能体，协调整个理赔审核流程"""
    
    def __init__(self):
        # 延迟导入避免循环依赖
        from agents.claim_extractor import ClaimExtractor
        from agents.policy_checker import PolicyChecker
        from agents.decision_maker import DecisionMaker
        
        self.extractor = ClaimExtractor()
        self.checker = PolicyChecker()
        self.decider = DecisionMaker()
        
    def run(self, input_text: str) -> Dict[str, Any]:
        """
        运行完整的理赔审核流程
        
        Args:
            input_text: 理赔申请的文本描述
            
        Returns:
            最终的审核决策结果
        """
        print("🔄 开始理赔审核流程...")
        
        # Step 1: 提取理赔信息
        print("📋 Step 1: 提取理赔信息...")
        claim_info = self.extractor.extract(input_text)
        print(f"✅ 提取完成: {claim_info}")
        
        # Step 2: 检查保险条款
        print("📖 Step 2: 检查保险条款...")
        policy_findings = self.checker.check(claim_info)
        print(f"✅ 条款检查完成: {policy_findings}")
        
        # Step 3: 做出最终决策
        print("⚖️ Step 3: 做出最终决策...")
        final_decision = self.decider.decide(claim_info, policy_findings)
        print(f"✅ 决策完成: {final_decision}")
        
        return final_decision 