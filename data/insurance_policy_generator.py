"""
MedicareinsurancepolicyauditrulesGenerating器
基于真实的NCD (National Coverage Determinations) 和 LCD (Local Coverage Determinations) 数据
Generating智能auditrules供多agentclaims系统使用
"""

import pandas as pd
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class MedicareQueuePolicyGenerator:
    """MedicareinsurancepolicyrulesGenerating器"""
    
    def __init__(self, policy_data_path: str = "data/insurance policy"):
        self.policy_path = Path(policy_data_path)
        self.ncd_rules = {}
        self.lcd_rules = {}
        self.coverage_categories = {}
        self.hcpcs_codes = {}
        self.coverage_rules = {
            "covered": [],          # coverage项目
            "conditional": [],      # 有条件coverage
            "excluded": [],         # 排除项目
            "limits": {},          # cost限制
            "requirements": {},    # 特殊要求
            "geographic": {}       # 地理限制
        }
        
    def load_ncd_data(self):
        """Loading国家coverage决定数据"""
        ncd_file = self.policy_path / "ncd" / "ncd_csv" / "ncd_trkg.csv"
        if ncd_file.exists():
            try:
                # 尝试不同的编码格式
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                ncd_df = None
                
                for encoding in encodings:
                    try:
                        ncd_df = pd.read_csv(ncd_file, encoding=encoding)
                        print(f"成功使用 {encoding} 编码LoadingNCD数据")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if ncd_df is None:
                    print("无法以任何编码格式LoadingNCD数据")
                    return
                
                for _, row in ncd_df.iterrows():
                    ncd_id = row['NCD_id']
                    coverage_level = row['cvrg_lvl_cd']
                    title = str(row.get('NCD_mnl_sect_title', '')).strip()
                    indication = str(row.get('indctn_lmtn', '')).strip()
                    
                    # 解析coverage级别
                    if coverage_level == 1:  # coverage
                        coverage_type = "covered"
                    elif coverage_level == 2:  # 有条件coverage
                        coverage_type = "conditional"
                    elif coverage_level == 3:  # 不coverage
                        coverage_type = "excluded"
                    else:
                        coverage_type = "unknown"
                    
                    self.ncd_rules[ncd_id] = {
                        "title": title,
                        "coverage_type": coverage_type,
                        "indication": indication,
                        "description": str(row.get('itm_srvc_desc', '')),
                    }
                    
                print(f"已Loading {len(self.ncd_rules)} 条NCDrules")
            except Exception as e:
                print(f"LoadingNCD数据时出错: {e}")
    
    def load_lcd_data(self):
        """Loading本地coverage决定数据"""
        lcd_codes_file = self.policy_path / "current_lcd" / "current_lcd_csv" / "lcd_x_hcpc_code.csv"
        if lcd_codes_file.exists():
            try:
                # 尝试不同的编码格式
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                lcd_df = None
                
                for encoding in encodings:
                    try:
                        lcd_df = pd.read_csv(lcd_codes_file, encoding=encoding)
                        print(f"成功使用 {encoding} 编码LoadingLCD数据")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if lcd_df is None:
                    print("无法以任何编码格式LoadingLCD数据")
                    return
                
                # 打印列名以调试
                print(f"LCD数据文件列名: {list(lcd_df.columns)}")
                
                for _, row in lcd_df.iterrows():
                    # 修复列名问题
                    hcpcs_code = row.get('hcpc_code') or row.get('hcpc_code_id')
                    if not hcpcs_code:
                        continue
                        
                    description = str(row.get('long_description', '')).strip()
                    
                    self.hcpcs_codes[hcpcs_code] = {
                        "description": description,
                        "short_desc": str(row.get('short_description', '')),
                        "lcd_id": str(row.get('lcd_id', '')),
                        "group": str(row.get('hcpc_code_group', ''))
                    }
                    
                print(f"已Loading {len(self.hcpcs_codes)} 条HCPCS代码")
            except Exception as e:
                print(f"LoadingLCD数据时出错: {e}")
                import traceback
                traceback.print_exc()
    
    def load_benefit_categories(self):
        """Loading福利类别数据"""
        benefit_file = self.policy_path / "ncd" / "ncd_csv" / "ncd_bnft_ctgry_ref.csv"
        if benefit_file.exists():
            try:
                benefit_df = pd.read_csv(benefit_file)
                for _, row in benefit_df.iterrows():
                    self.coverage_categories[row['bnft_ctgry_cd']] = row['bnft_ctgry_desc']
                print(f"已Loading {len(self.coverage_categories)} 个福利类别")
            except Exception as e:
                print(f"Loading福利类别数据时出错: {e}")
    
    def generate_coverage_rules(self):
        """基于真实Medicare数据Generatingcoveragerules"""
        
        # 从NCD数据Generatingrules
        for ncd_id, ncd_data in self.ncd_rules.items():
            title = ncd_data['title'].lower()
            coverage_type = ncd_data['coverage_type']
            indication = ncd_data.get('indication', '').lower()
            
            rule = {
                "source": f"NCD_{ncd_id}",
                "title": ncd_data['title'],
                "condition": self._extract_medical_conditions(title, indication),
                "procedure": self._extract_procedures(title, indication),
                "notes": indication[:200] + "..." if len(indication) > 200 else indication
            }
            
            if coverage_type == "covered":
                self.coverage_rules["covered"].append(rule)
            elif coverage_type == "conditional":
                self.coverage_rules["conditional"].append(rule)
            elif coverage_type == "excluded":
                self.coverage_rules["excluded"].append(rule)
        
        # 从HCPCS代码Generatingrules
        self._generate_hcpcs_rules()
        
        # Generatingcost限制rules
        self._generate_cost_limits()
        
        # Generating特殊要求rules
        self._generate_special_requirements()
    
    def _extract_medical_conditions(self, title: str, indication: str) -> List[str]:
        """从标题和适应症中提取medical条件"""
        conditions = []
        text = f"{title} {indication}".lower()
        
        # 定义medical条件关键词
        condition_patterns = [
            r'cancer|tumor|carcinoma|malignancy',
            r'diabetes|diabetic',
            r'heart|cardiac|cardiovascular',
            r'kidney|renal|dialysis',
            r'lung|pulmonary|respiratory',
            r'stroke|cerebral|brain',
            r'arthritis|joint|orthopedic',
            r'wound|ulcer|pressure sore',
            r'infection|sepsis|bacteremia',
            r'fracture|broken bone',
            r'pregnancy|prenatal|maternal',
            r'mental health|psychiatric|depression',
            r'pain|chronic pain',
            r'obesity|weight loss',
            r'hypertension|high blood pressure'
        ]
        
        for pattern in condition_patterns:
            if re.search(pattern, text):
                conditions.append(pattern.split('|')[0])
        
        return conditions
    
    def _extract_procedures(self, title: str, indication: str) -> List[str]:
        """从标题和适应症中提取medical程序"""
        procedures = []
        text = f"{title} {indication}".lower()
        
        # 定义medical程序关键词
        procedure_patterns = [
            r'surgery|surgical|operation',
            r'therapy|treatment|rehabilitation',
            r'screening|test|examination',
            r'imaging|x-ray|ct|mri|ultrasound',
            r'injection|infusion|medication',
            r'device|implant|prosthetic',
            r'dialysis|transfusion',
            r'transplant|graft',
            r'biopsy|sample|culture',
            r'monitoring|observation'
        ]
        
        for pattern in procedure_patterns:
            if re.search(pattern, text):
                procedures.append(pattern.split('|')[0])
        
        return procedures
    
    def _generate_hcpcs_rules(self):
        """从HCPCS代码Generating具体的程序rules"""
        # 根据HCPCS代码类别Generatingrules
        dme_codes = {k: v for k, v in self.hcpcs_codes.items() if k.startswith('E')}  # 耐用medical设备
        drug_codes = {k: v for k, v in self.hcpcs_codes.items() if k.startswith('J')}  # 药物
        orthotic_codes = {k: v for k, v in self.hcpcs_codes.items() if k.startswith('L')}  # 矫形器具
        
        self.coverage_rules["covered"].extend([
            {
                "source": "HCPCS_DME",
                "title": "Durable Medical Equipment",
                "condition": ["chronic illness", "disability"],
                "procedure": ["equipment", "device"],
                "hcpcs_codes": list(dme_codes.keys())[:50],  # 限制数量
                "notes": "Coverage for medically necessary durable medical equipment"
            },
            {
                "source": "HCPCS_DRUGS",
                "title": "Injectable Drugs and Biologicals",
                "condition": ["various medical conditions"],
                "procedure": ["injection", "infusion"],
                "hcpcs_codes": list(drug_codes.keys())[:50],
                "notes": "Coverage for FDA-approved injectable medications"
            }
        ])
    
    def _generate_cost_limits(self):
        """Generatingcost限制rules"""
        self.coverage_rules["limits"] = {
            "annual_deductible": 1600,  # 2024年Medicare Part B免赔额
            "coinsurance_rate": 0.20,   # 20%共同insurance
            "max_therapy_visits": {
                "physical_therapy": 36,
                "occupational_therapy": 36,
                "speech_therapy": 36
            },
            "dme_rental_periods": {
                "wheelchair": 13,
                "hospital_bed": 13,
                "oxygen": 36
            },
            "geographic_variations": {
                "rural_bonus": 1.10,
                "metropolitan_standard": 1.00,
                "frontier_bonus": 1.05
            }
        }
    
    def _generate_special_requirements(self):
        """Generating特殊要求rules"""
        self.coverage_rules["requirements"] = {
            "prior_authorization": [
                "expensive imaging (>$1000)",
                "experimental procedures",
                "cosmetic surgery",
                "certain durable medical equipment"
            ],
            "physician_certification": [
                "home health services",
                "hospice care",
                "skilled nursing facility",
                "durable medical equipment"
            ],
            "documentation_required": [
                "medical necessity justification",
                "treatment plan",
                "progress notes",
                "diagnostic reports"
            ],
            "frequency_limits": {
                "routine_screening": "annual",
                "diagnostic_imaging": "as medically necessary",
                "preventive_services": "per Medicare guidelines"
            }
        }
    
    def create_audit_rules(self) -> Dict[str, Any]:
        """创建用于claimsaudit的rules"""
        return {
            "coverage_matrix": {
                "always_covered": [
                    {
                        "conditions": ["emergency", "life-threatening"],
                        "max_cost": None,
                        "requirements": ["physician_certification"]
                    },
                    {
                        "conditions": ["preventive_care", "screening"],
                        "max_cost": 500,
                        "requirements": ["age_appropriate", "frequency_limits"]
                    }
                ],
                "conditionally_covered": [
                    {
                        "conditions": ["experimental_treatment"],
                        "max_cost": 10000,
                        "requirements": ["clinical_trial", "informed_consent"]
                    },
                    {
                        "conditions": ["elective_surgery"],
                        "max_cost": 25000,
                        "requirements": ["prior_authorization", "medical_necessity"]
                    }
                ],
                "never_covered": [
                    {
                        "conditions": ["cosmetic_surgery"],
                        "exceptions": ["reconstructive_after_accident", "congenital_defect"]
                    },
                    {
                        "conditions": ["alternative_medicine"],
                        "exceptions": ["acupuncture_for_chronic_pain"]
                    }
                ]
            },
            "risk_assessment": {
                "high_risk_indicators": [
                    "cost > $50000",
                    "experimental_procedure",
                    "multiple_providers",
                    "frequent_claims_same_patient"
                ],
                "medium_risk_indicators": [
                    "cost > $10000",
                    "elective_procedure",
                    "out_of_network_provider"
                ],
                "low_risk_indicators": [
                    "routine_care",
                    "preventive_services",
                    "established_provider"
                ]
            },
            "approval_thresholds": {
                "auto_approve": {"max_cost": 1000, "conditions": ["routine", "preventive"]},
                "manual_review": {"max_cost": 10000, "conditions": ["complex", "high_cost"]},
                "committee_review": {"max_cost": None, "conditions": ["experimental", "very_high_cost"]}
            }
        }
    
    def save_rules(self, output_file: str = "data/medicare_audit_rules.json"):
        """SavingGenerating的auditrules"""
        audit_rules = self.create_audit_rules()
        
        # 合并所有rules
        complete_rules = {
            "metadata": {
                "source": "Medicare NCD/LCD Database",
                "generated_date": pd.Timestamp.now().isoformat(),
                "ncd_count": len(self.ncd_rules),
                "hcpcs_count": len(self.hcpcs_codes),
                "benefit_categories": len(self.coverage_categories)
            },
            "coverage_rules": self.coverage_rules,
            "audit_rules": audit_rules,
            "benefit_categories": self.coverage_categories
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_rules, f, ensure_ascii=False, indent=2)
        
        print(f"auditrules已Saving到: {output_file}")
        return complete_rules
    
    def generate_summary_report(self):
        """Generatingrules总结报告"""
        covered_count = len(self.coverage_rules["covered"])
        conditional_count = len(self.coverage_rules["conditional"])
        excluded_count = len(self.coverage_rules["excluded"])
        
        report = f"""
MedicareinsurancepolicyauditrulesGenerating报告
=====================================

数据源统计:
- NCDrules数量: {len(self.ncd_rules)}
- HCPCS代码数量: {len(self.hcpcs_codes)}
- 福利类别数量: {len(self.coverage_categories)}

coveragerules统计:
- 完全coverage项目: {covered_count}
- 有条件coverage项目: {conditional_count}
- 排除项目: {excluded_count}

主要福利类别:
"""
        # 显示前10个福利类别
        for i, (code, desc) in enumerate(list(self.coverage_categories.items())[:10]):
            report += f"- {desc}\n"
        
        report += f"""
cost限制rules:
- 年度免赔额: ${self.coverage_rules['limits']['annual_deductible']}
- 共同insurance率: {self.coverage_rules['limits']['coinsurance_rate']*100}%
- 物理treatment年限制: {self.coverage_rules['limits']['max_therapy_visits']['physical_therapy']}次

特殊要求:
- 需要事先授权的项目: {len(self.coverage_rules['requirements']['prior_authorization'])}项
- 需要医生认证的项目: {len(self.coverage_rules['requirements']['physician_certification'])}项
"""
        
        return report

def main():
    """主函数：Generating完整的Medicareauditrules"""
    generator = MedicareQueuePolicyGenerator()
    
    print("正在LoadingMedicareinsurancepolicy数据...")
    generator.load_ncd_data()
    generator.load_lcd_data()
    generator.load_benefit_categories()
    
    print("正在Generatingcoveragerules...")
    generator.generate_coverage_rules()
    
    print("正在Savingauditrules...")
    rules = generator.save_rules()
    
    print("Generatingrules总结报告...")
    report = generator.generate_summary_report()
    print(report)
    
    # Saving报告
    with open("data/medicare_rules_summary.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    return rules

if __name__ == "__main__":
    main() 