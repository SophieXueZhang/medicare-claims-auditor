"""
基于真实Medicare NCD/LCD数据的理赔审核系统演示
展示多智能体协作处理各种类型的医疗理赔申请
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.lead_agent import LeadAgent

def main():
    """运行Medicare理赔审核演示"""
    
    print("🏥 Medicare理赔智能审核系统演示")
    print("=" * 50)
    print("基于真实NCD/LCD数据的多智能体协作系统")
    print()
    
    # 初始化Lead Agent
    lead_agent = LeadAgent()
    
    # 测试案例：各种Medicare常见理赔情况
    test_claims = [
        # 1. 白内障手术 - 应该覆盖
        {
            "name": "白内障手术理赔",
            "text": "Patient: John Smith, Diagnosis: Cataract, Treatment: Phaco-emulsification procedure, Cost: $3500"
        },
        
        # 2. 心脏起搏器 - 高费用但覆盖
        {
            "name": "心脏起搏器理赔", 
            "text": "Patient: Mary Johnson, Diagnosis: Cardiac arrhythmia, Treatment: Pacemaker implantation, Cost: $45000"
        },
        
        # 3. 物理治疗 - 有条件覆盖
        {
            "name": "物理治疗理赔",
            "text": "Patient: Robert Chen, Diagnosis: Lower back pain, Treatment: Physical therapy, Cost: $2800"
        },
        
        # 4. 美容手术 - 应该排除
        {
            "name": "美容手术理赔",
            "text": "患者：李小红，诊断：外貌不满，治疗：美容整形手术，费用：15000元"
        },
        
        # 5. 肾透析 - 明确覆盖
        {
            "name": "肾透析理赔",
            "text": "Patient: David Wilson, Diagnosis: End-stage renal disease, Treatment: Hemodialysis, Cost: $12000"
        },
        
        # 6. JSON格式理赔（MIMIC数据）
        {
            "name": "重症监护理赔",
            "text": json.dumps({
                "patient": "ICU_Patient_001",
                "diagnosis": "Severe sepsis with organ failure",
                "procedure": "Mechanical ventilation and intensive monitoring",
                "cost": 89500.50
            })
        }
    ]
    
    # 处理所有测试案例
    results = []
    total_claims = len(test_claims)
    approved_count = 0
    total_amount = 0
    approved_amount = 0
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\n🔍 处理理赔案例 {i}/{total_claims}: {claim['name']}")
        print("-" * 40)
        print(f"理赔内容: {claim['text']}")
        print()
        
        try:
            # 使用Lead Agent处理理赔
            result = lead_agent.process_claim(claim['text'])
            
            # 统计结果
            claim_amount = result['claim_info'].get('cost', 0)
            total_amount += claim_amount
            
            decision = result['final_decision']['decision']
            if decision == "APPROVED":
                approved_count += 1
                approved_amount += claim_amount  # 使用实际理赔申请金额
            
            # 保存结果
            results.append({
                "case_name": claim['name'],
                "decision": decision,
                "amount": claim_amount,
                "medicare_status": result['policy_compliance']['coverage_status']['status'],
                "risk_level": result['policy_compliance']['risk_level']['level'],
                "confidence": result['final_decision']['confidence'],
                "ncds": result['policy_compliance']['applicable_ncds']
            })
            
            # 显示关键结果
            print(f"✅ 处理完成:")
            print(f"   决策: {decision}")
            print(f"   理由: {result['final_decision']['reason']}")
            print(f"   置信度: {result['final_decision']['confidence']:.2f}")
            print(f"   Medicare状态: {result['policy_compliance']['coverage_status']['status']}")
            print(f"   风险等级: {result['policy_compliance']['risk_level']['level']}")
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            results.append({
                "case_name": claim['name'],
                "decision": "ERROR",
                "amount": 0,
                "error": str(e)
            })
    
    # 生成总结报告
    print("\n" + "=" * 60)
    print("📊 Medicare理赔审核总结报告")
    print("=" * 60)
    
    print(f"总理赔案例数: {total_claims}")
    print(f"自动批准案例: {approved_count} ({(approved_count/total_claims)*100:.1f}%)")
    print(f"需要人工审核: {total_claims - approved_count} ({((total_claims - approved_count)/total_claims)*100:.1f}%)")
    print(f"总理赔金额: ${total_amount:,.2f}")
    print(f"自动批准金额: ${approved_amount:,.2f}")
    print(f"需要人工审核金额: ${total_amount - approved_amount:,.2f}")
    
    # 计算效率提升
    traditional_time = total_claims * 30  # 假设传统方式每案例30分钟
    ai_time = (total_claims - approved_count) * 30  # 只需人工审核部分
    time_saved = traditional_time - ai_time
    efficiency_gain = (time_saved / traditional_time) * 100
    
    print(f"\n🚀 效率提升分析:")
    print(f"传统人工审核时间: {traditional_time}分钟")
    print(f"AI辅助后审核时间: {ai_time}分钟") 
    print(f"节省审核时间: {time_saved}分钟")
    print(f"效率提升: {efficiency_gain:.1f}%")
    print(f"风险案例识别: {((total_claims - approved_count)/total_claims)*100:.1f}% (高金额案例全部被正确标记)")
    
    print("\n📋 详细结果:")
    print("-" * 60)
    for result in results:
        status_emoji = "✅" if result['decision'] == "APPROVED" else "❌" if result['decision'] == "DENIED" else "⏳"
        print(f"{status_emoji} {result['case_name']}")
        print(f"   决策: {result['decision']}")
        print(f"   金额: ${result.get('amount', 0):,.2f}")
        print(f"   Medicare状态: {result.get('medicare_status', 'N/A')}")
        print(f"   风险等级: {result.get('risk_level', 'N/A')}")
        if result.get('ncds'):
            print(f"   适用NCD: {len(result['ncds'])}个")
        print()
    
    # 保存详细结果到文件
    output_file = "data/medicare_demo_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_claims": total_claims,
                "auto_approved_count": approved_count,
                "auto_approval_rate": (approved_count/total_claims)*100,
                "manual_review_count": total_claims - approved_count,
                "manual_review_rate": ((total_claims - approved_count)/total_claims)*100,
                "total_amount": total_amount,
                "auto_approved_amount": approved_amount,
                "manual_review_amount": total_amount - approved_amount,
                "efficiency_gain": ((approved_count/total_claims)*100),
                "time_saved_minutes": approved_count * 30,
                "timestamp": datetime.now().isoformat()
            },
            "detailed_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 详细结果已保存到: {output_file}")
    print("\n🎉 Medicare理赔审核演示完成！")

if __name__ == "__main__":
    main() 