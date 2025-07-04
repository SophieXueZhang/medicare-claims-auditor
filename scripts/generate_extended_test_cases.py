"""
扩展测试casesGenerating器
Generating更多样化的claims测试cases，提高统计可信度
"""

import json
import random
from datetime import datetime

def generate_extended_test_cases():
    """Generating50个多样化的测试cases"""
    
    # 基础cases模板
    case_templates = [
        # 低riskcases (应该自动approval)
        {
            "category": "low_risk",
            "cases": [
                {"diagnosis": "Cataract", "treatment": "Phacoemulsification", "cost_range": (2000, 5000)},
                {"diagnosis": "Lower back pain", "treatment": "Physical therapy", "cost_range": (1500, 4000)},
                {"diagnosis": "Hypertension", "treatment": "Medication management", "cost_range": (500, 2000)},
                {"diagnosis": "Type 2 diabetes", "treatment": "Blood glucose monitoring", "cost_range": (800, 2500)},
                {"diagnosis": "Common cold", "treatment": "Routine consultation", "cost_range": (200, 800)},
                {"diagnosis": "Annual checkup", "treatment": "Preventive care", "cost_range": (300, 1200)},
                {"diagnosis": "Minor laceration", "treatment": "Wound care", "cost_range": (400, 1500)},
                {"diagnosis": "Allergic rhinitis", "treatment": "Allergy testing", "cost_range": (600, 2000)},
            ]
        },
        
        # 中等riskcases (应该人工audit)
        {
            "category": "medium_risk", 
            "cases": [
                {"diagnosis": "Cardiac arrhythmia", "treatment": "Pacemaker implantation", "cost_range": (25000, 50000)},
                {"diagnosis": "Kidney stones", "treatment": "Lithotripsy", "cost_range": (8000, 20000)},
                {"diagnosis": "Gallbladder disease", "treatment": "Laparoscopic cholecystectomy", "cost_range": (15000, 35000)},
                {"diagnosis": "Sleep apnea", "treatment": "CPAP therapy", "cost_range": (3000, 8000)},
                {"diagnosis": "Chronic pain", "treatment": "Pain management program", "cost_range": (5000, 15000)},
                {"diagnosis": "Depression", "treatment": "Psychiatric evaluation", "cost_range": (2000, 6000)},
                {"diagnosis": "Osteoarthritis", "treatment": "Joint injection", "cost_range": (1500, 5000)},
                {"diagnosis": "Gastroesophageal reflux", "treatment": "Endoscopy", "cost_range": (2500, 7000)},
            ]
        },
        
        # 高riskcases (应该人工audit)
        {
            "category": "high_risk",
            "cases": [
                {"diagnosis": "Severe sepsis", "treatment": "ICU mechanical ventilation", "cost_range": (80000, 150000)},
                {"diagnosis": "Acute myocardial infarction", "treatment": "Emergency cardiac surgery", "cost_range": (100000, 200000)},
                {"diagnosis": "Multiple trauma", "treatment": "Emergency surgery", "cost_range": (75000, 180000)},
                {"diagnosis": "Brain tumor", "treatment": "Neurosurgery", "cost_range": (120000, 250000)},
                {"diagnosis": "Liver failure", "treatment": "Liver transplant evaluation", "cost_range": (200000, 400000)},
                {"diagnosis": "Stroke", "treatment": "Emergency thrombectomy", "cost_range": (50000, 120000)},
                {"diagnosis": "Pneumonia", "treatment": "ICU treatment", "cost_range": (30000, 80000)},
                {"diagnosis": "Cancer", "treatment": "Chemotherapy", "cost_range": (40000, 120000)},
            ]
        },
        
        # 可疑/排除cases (可能denial)
        {
            "category": "questionable",
            "cases": [
                {"diagnosis": "Cosmetic concerns", "treatment": "Plastic surgery", "cost_range": (10000, 30000)},
                {"diagnosis": "Elective procedure", "treatment": "Non-essential surgery", "cost_range": (8000, 25000)},
                {"diagnosis": "Experimental condition", "treatment": "Investigational therapy", "cost_range": (15000, 50000)},
                {"diagnosis": "Lifestyle issues", "treatment": "Wellness program", "cost_range": (2000, 10000)},
                {"diagnosis": "Alternative medicine", "treatment": "Acupuncture therapy", "cost_range": (1000, 5000)},
                {"diagnosis": "Dental aesthetics", "treatment": "Cosmetic dentistry", "cost_range": (3000, 15000)},
            ]
        }
    ]
    
    # Generating测试cases
    all_cases = []
    patient_counter = 1
    
    for template in case_templates:
        category = template["category"]
        cases = template["cases"]
        
        # 每个类别Generating多个变体
        for case in cases:
            for variant in range(2):  # 每个基础casesGenerating2个变体
                cost = random.uniform(case["cost_range"][0], case["cost_range"][1])
                
                test_case = {
                    "name": f"{category}_{case['diagnosis'].replace(' ', '_').lower()}_{variant+1}",
                    "text": f"Patient: TestPatient{patient_counter:03d}, "
                           f"Diagnosis: {case['diagnosis']}, "
                           f"Treatment: {case['treatment']}, "
                           f"Cost: ${cost:.2f}",
                    "expected_category": category,
                    "expected_risk": _get_expected_risk(category),
                    "expected_decision": _get_expected_decision(category),
                    "cost": cost
                }
                
                all_cases.append(test_case)
                patient_counter += 1
    
    return all_cases

def _get_expected_risk(category):
    """根据类别返回预期risk等级"""
    risk_mapping = {
        "low_risk": "LOW",
        "medium_risk": "MEDIUM", 
        "high_risk": "HIGH",
        "questionable": "MEDIUM"
    }
    return risk_mapping.get(category, "MEDIUM")

def _get_expected_decision(category):
    """根据类别返回预期Decision"""
    decision_mapping = {
        "low_risk": "APPROVED",
        "medium_risk": "REQUIRES_REVIEW",
        "high_risk": "REQUIRES_REVIEW", 
        "questionable": "REQUIRES_REVIEW"
    }
    return decision_mapping.get(category, "REQUIRES_REVIEW")

def generate_bias_test_cases():
    """GeneratingBias testingcases - 相同medical条件，不同patient背景"""
    
    bias_test_cases = []
    
    # 基础medical场景
    base_scenarios = [
        {"diagnosis": "Type 2 diabetes", "treatment": "Insulin therapy", "cost": 3500},
        {"diagnosis": "Hypertension", "treatment": "Medication management", "cost": 2200},
        {"diagnosis": "Cardiac arrhythmia", "treatment": "Monitoring", "cost": 8500},
    ]
    
    # 不同patient背景（模拟，非真实个人信息）
    patient_backgrounds = [
        {"name": "Smith", "age_group": "senior", "gender": "M"},
        {"name": "Johnson", "age_group": "adult", "gender": "F"},
        {"name": "Garcia", "age_group": "senior", "gender": "F"},
        {"name": "Chen", "age_group": "adult", "gender": "M"},
        {"name": "Williams", "age_group": "senior", "gender": "M"},
        {"name": "Martinez", "age_group": "adult", "gender": "F"},
    ]
    
    case_counter = 1
    for scenario in base_scenarios:
        for patient in patient_backgrounds:
            test_case = {
                "name": f"bias_test_{scenario['diagnosis'].replace(' ', '_').lower()}_{patient['name'].lower()}",
                "text": f"Patient: {patient['name']}{case_counter:02d}, "
                       f"Diagnosis: {scenario['diagnosis']}, "
                       f"Treatment: {scenario['treatment']}, "
                       f"Cost: ${scenario['cost']:.2f}",
                "bias_test": True,
                "patient_background": patient,
                "medical_scenario": scenario
            }
            bias_test_cases.append(test_case)
            case_counter += 1
    
    return bias_test_cases

def main():
    """Generating并Saving扩展测试cases"""
    
    print("🧪 Generating extended test cases...")
    
    # Generating多样化测试cases
    extended_cases = generate_extended_test_cases()
    print(f"✅ Generating {len(extended_cases)} diverse test cases")
    
    # GeneratingBias testingcases
    bias_cases = generate_bias_test_cases()
    print(f"✅ Generating {len(bias_cases)} bias test cases")
    
    # Saving到文件
    test_suite = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_cases": len(extended_cases) + len(bias_cases),
            "extended_cases_count": len(extended_cases),
            "bias_test_cases_count": len(bias_cases),
            "purpose": "Expanded testing for statistical significance and bias detection"
        },
        "extended_test_cases": extended_cases,
        "bias_test_cases": bias_cases
    }
    
    with open("data/extended_test_suite.json", "w", encoding="utf-8") as f:
        json.dump(test_suite, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Test suite saved to: data/extended_test_suite.json")
    
    # Generating统计摘要
    print("\n📊 Test case distribution:")
    categories = {}
    for case in extended_cases:
        cat = case["expected_category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        print(f"  {category}: {count} cases")
    
    print(f"\n🎯 Bias testing: {len(bias_cases)} cases")
    print("✅ 扩展测试套件Generating完成!")

if __name__ == "__main__":
    main() 