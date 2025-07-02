"""
主运行脚本 - 演示多智能体协作审核理赔申请
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.lead_agent import LeadAgent

def main():
    """主函数"""
    print("🏥 医疗保险理赔智能审核系统")
    print("=" * 50)
    
    # 示例理赔申请
    sample_claims = [
        {
            "name": "示例1 - 正常理赔",
            "text": "患者：张三，诊断：膝关节炎，治疗：膝关节置换手术，费用：45000元"
        },
        {
            "name": "示例2 - 超额理赔", 
            "text": "患者：李四，诊断：心脏病，治疗：心脏搭桥手术，费用：250000元"
        },
        {
            "name": "示例3 - 排除条款",
            "text": "患者：王五，诊断：外貌不满，治疗：美容手术，费用：30000元"
        }
    ]
    
    # 初始化主导智能体
    lead_agent = LeadAgent()
    
    # 处理每个示例
    for i, claim in enumerate(sample_claims, 1):
        print(f"\n📋 处理 {claim['name']}")
        print("-" * 30)
        print(f"申请内容: {claim['text']}")
        print()
        
        try:
            # 运行审核流程
            result = lead_agent.run(claim['text'])
            
            # 显示结果
            print("\n📊 审核结果:")
            print(f"决策: {result['decision']}")
            print(f"患者: {result['patient_name']}")
            print(f"治疗: {result['procedure']}")
            print(f"金额: {result['amount']}元")
            print(f"风险等级: {result['risk_level']}")
            print(f"条款符合性: {'是' if result['policy_compliance'] else '否'}")
            print(f"置信度: {result['confidence']:.2%}")
            print(f"决策理由: {', '.join(result['reasons'])}")
            
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {str(e)}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 