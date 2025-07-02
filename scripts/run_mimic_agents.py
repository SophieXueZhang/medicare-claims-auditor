"""
使用MIMIC-III数据运行多智能体理赔审核系统
"""
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.lead_agent import LeadAgent
from data.mimic_data_processor import MimicDataProcessor

def format_claim_text(claim: dict) -> str:
    """将JSON格式的理赔数据转换为文本格式"""
    return f"Patient: {claim['patient']}, Diagnosis: {claim['diagnosis']}, Treatment: {claim['procedure']}, Cost: ${claim['cost']}"

def main():
    """主函数"""
    print("🏥 医疗保险理赔智能审核系统 (MIMIC-III数据)")
    print("=" * 60)
    
    # 初始化MIMIC数据处理器
    print("📊 初始化MIMIC-III数据处理器...")
    processor = MimicDataProcessor()
    
    # 生成或加载理赔数据
    print("🔄 生成理赔数据...")
    mimic_data = processor.load_mimic_data()
    claims = processor.generate_claims(mimic_data, num_claims=10)
    
    # 保存理赔数据
    processor.save_claims_to_file(claims, "data/mimic_claims.json")
    
    # 初始化主导智能体
    print("🤖 初始化智能体系统...")
    lead_agent = LeadAgent()
    
    # 处理理赔申请
    print(f"\n📋 处理 {len(claims)} 个真实理赔案例")
    print("=" * 60)
    
    results = []
    
    for i, claim in enumerate(claims, 1):
        print(f"\n📋 处理理赔案例 {i}")
        print("-" * 40)
        print(f"患者ID: {claim['patient']}")
        print(f"诊断: {claim['diagnosis']}")
        print(f"治疗: {claim['procedure']}")
        print(f"费用: ${claim['cost']:,.2f}")
        print()
        
        # 转换为文本格式供智能体处理
        claim_text = format_claim_text(claim)
        
        try:
            # 运行审核流程
            result = lead_agent.run(claim_text)
            
            # 显示结果
            print("\n📊 审核结果:")
            print(f"决策: {result['decision']}")
            print(f"患者: {result['patient_name']}")
            print(f"治疗: {result['procedure']}")
            print(f"金额: ${result['amount']}")
            print(f"风险等级: {result['risk_level']}")
            print(f"条款符合性: {'是' if result['policy_compliance'] else '否'}")
            print(f"置信度: {result['confidence']:.2%}")
            print(f"决策理由: {', '.join(result['reasons'])}")
            
            # 保存结果
            results.append({
                "claim": claim,
                "decision": result
            })
            
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {str(e)}")
        
        print("\n" + "="*60)
    
    # 保存所有结果
    with open("data/audit_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 统计分析
    print("\n📈 审核统计:")
    print("-" * 30)
    
    decisions = [r["decision"]["decision"] for r in results if "decision" in r]
    decision_counts = {}
    for decision in decisions:
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
    
    for decision, count in decision_counts.items():
        percentage = (count / len(results)) * 100
        print(f"{decision}: {count} 案例 ({percentage:.1f}%)")
    
    total_cost = sum(claim["cost"] for claim in claims)
    approved_cost = sum(
        claim["cost"] for i, claim in enumerate(claims) 
        if i < len(results) and results[i].get("decision", {}).get("decision") == "批准"
    )
    
    print(f"\n💰 财务分析:")
    print(f"总申请金额: ${total_cost:,.2f}")
    print(f"批准金额: ${approved_cost:,.2f}")
    print(f"节省金额: ${total_cost - approved_cost:,.2f}")
    print(f"批准率: {(approved_cost/total_cost)*100:.1f}%")

if __name__ == "__main__":
    main() 