"""
Lead Agent - Orchestrates the complete Medicare claims audit workflow
Coordinates collaboration between specialized agents for intelligent claims processing
"""

from typing import Dict, Any
from .claim_extractor import ClaimExtractor
from .policy_checker import PolicyChecker
from .decision_maker import DecisionMaker

class LeadAgent:
    """
    Lead Agent - Main orchestrator for Medicare claims audit workflow
    Manages the complete process from claim extraction to final decision
    """
    
    def __init__(self):
        # Initialize specialized agents
        self.claim_extractor = ClaimExtractor()
        self.policy_checker = PolicyChecker()
        self.decision_maker = DecisionMaker()
    
    def process_claim(self, claim_text: str) -> Dict[str, Any]:
        """
        Process a complete claims audit workflow
        
        Args:
            claim_text: Raw claim text (supports multiple formats)
            
        Returns:
            Complete audit results including final decision
        """
        print("=== Starting Claims Application Processing ===")
        
        # Step 1: Extract claims information
        print("1. Extracting Claims Information...")
        claim_info = self.claim_extractor.extract_claim_info(claim_text)
        print(f"Extraction Result: {claim_info}")
        
        # Step 2: Check insurance policy compliance
        print("2. Checking Insurance Policy Compliance...")
        policy_result = self.policy_checker.check_policy_compliance(claim_info)
        print(f"Policy Check Result: {policy_result}")
        
        # Step 3: Make final decision
        print("3. Making Final Decision...")
        final_decision = self.decision_maker.make_decision(claim_info, policy_result)
        print(f"Final Decision: {final_decision['decision']}")
        print("=== Claims Processing Completed ===")
        
        return {
            "claim_info": claim_info,
            "policy_compliance": policy_result,
            "final_decision": final_decision
        } 