"""
MIMIC-III Data Processor - 从MIMIC-III数据库提取医疗数据并转换为理赔格式
"""
import json
import random
import csv
from typing import Dict, List, Any
from pathlib import Path

class MimicDataProcessor:
    """MIMIC-III数据处理器"""
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path
        # ICD-9诊断代码映射（示例）
        self.icd9_diagnoses = {
            "038.9": "Unspecified septicemia",
            "584.9": "Acute kidney failure, unspecified",
            "518.81": "Acute respiratory failure",
            "410.71": "Subendocardial infarction, initial episode",
            "428.0": "Congestive heart failure, unspecified",
            "507.0": "Pneumonitis due to inhalation of food or vomitus",
            "486": "Pneumonia, organism unspecified",
            "276.2": "Acidosis",
            "285.9": "Anemia, unspecified",
            "599.0": "Urinary tract infection, site not specified"
        }
        
        # ICD-9手术代码映射（示例）
        self.icd9_procedures = {
            "96.72": "Continuous mechanical ventilation for 96 consecutive hours or more",
            "96.04": "Insertion of endotracheal tube",
            "38.95": "Venous catheterization, not elsewhere classified",
            "89.54": "Monitoring of electrocardiogram",
            "96.6": "Enteral infusion of concentrated nutritional substances",
            "38.93": "Arterial catheterization",
            "57.94": "Insertion of indwelling urinary catheter",
            "96.71": "Continuous mechanical ventilation for less than 96 consecutive hours",
            "88.56": "Coronary arteriography using two catheters",
            "36.15": "Single internal mammary-coronary artery bypass"
        }
        
        # 成本估算（基于DRG和医院平均成本）
        self.cost_ranges = {
            "mechanical_ventilation": (15000, 45000),
            "cardiac_procedure": (25000, 80000),
            "respiratory_treatment": (8000, 25000),
            "diagnostic_procedure": (2000, 8000),
            "surgical_procedure": (12000, 60000),
            "monitoring": (1000, 5000),
            "default": (3000, 15000)
        }
    
    def load_mimic_data(self, diagnoses_file: str = None, procedures_file: str = None) -> Dict[str, Any]:
        """
        加载MIMIC-III数据文件
        如果没有提供文件路径，使用模拟数据
        """
        if diagnoses_file and procedures_file and Path(diagnoses_file).exists():
            return self._load_real_data(diagnoses_file, procedures_file)
        else:
            return self._generate_mock_data()
    
    def _load_real_data(self, diagnoses_file: str, procedures_file: str) -> Dict[str, Any]:
        """加载真实的MIMIC-III数据"""
        data = {"patients": {}}
        
        # 加载诊断数据
        try:
            with open(diagnoses_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subject_id = row['SUBJECT_ID']
                    hadm_id = row['HADM_ID']
                    icd9_code = row['ICD9_CODE']
                    
                    if subject_id not in data["patients"]:
                        data["patients"][subject_id] = {"diagnoses": [], "procedures": []}
                    
                    if icd9_code in self.icd9_diagnoses:
                        data["patients"][subject_id]["diagnoses"].append({
                            "code": icd9_code,
                            "description": self.icd9_diagnoses[icd9_code],
                            "hadm_id": hadm_id
                        })
        except Exception as e:
            print(f"Error loading diagnoses: {e}")
        
        # 加载手术数据
        try:
            with open(procedures_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subject_id = row['SUBJECT_ID']
                    hadm_id = row['HADM_ID']
                    icd9_code = row['ICD9_CODE']
                    
                    if subject_id in data["patients"] and icd9_code in self.icd9_procedures:
                        data["patients"][subject_id]["procedures"].append({
                            "code": icd9_code,
                            "description": self.icd9_procedures[icd9_code],
                            "hadm_id": hadm_id
                        })
        except Exception as e:
            print(f"Error loading procedures: {e}")
        
        return data
    
    def _generate_mock_data(self) -> Dict[str, Any]:
        """生成模拟的MIMIC-III格式数据"""
        mock_patients = {}
        
        # 生成20个模拟患者
        for i in range(1, 21):
            patient_id = f"PATIENT_{i:05d}"
            
            # 随机选择1-3个诊断
            num_diagnoses = random.randint(1, 3)
            diagnoses = random.sample(list(self.icd9_diagnoses.items()), num_diagnoses)
            
            # 随机选择1-2个手术
            num_procedures = random.randint(1, 2)
            procedures = random.sample(list(self.icd9_procedures.items()), num_procedures)
            
            mock_patients[patient_id] = {
                "diagnoses": [{"code": code, "description": desc, "hadm_id": f"HADM_{i}"} 
                             for code, desc in diagnoses],
                "procedures": [{"code": code, "description": desc, "hadm_id": f"HADM_{i}"} 
                              for code, desc in procedures]
            }
        
        return {"patients": mock_patients}
    
    def generate_claims(self, mimic_data: Dict[str, Any], num_claims: int = 10) -> List[Dict[str, Any]]:
        """从MIMIC数据生成理赔申请"""
        claims = []
        patients = list(mimic_data["patients"].items())
        
        for i in range(min(num_claims, len(patients))):
            patient_id, patient_data = patients[i]
            
            # 选择主要诊断
            primary_diagnosis = patient_data["diagnoses"][0] if patient_data["diagnoses"] else {
                "description": "Unspecified condition"
            }
            
            # 选择主要手术
            primary_procedure = patient_data["procedures"][0] if patient_data["procedures"] else {
                "description": "General treatment"
            }
            
            # 估算成本
            cost = self._estimate_cost(primary_procedure["description"])
            
            claim = {
                "patient": patient_id,
                "diagnosis": primary_diagnosis["description"],
                "procedure": primary_procedure["description"],
                "cost": round(cost, 2)
            }
            
            claims.append(claim)
        
        return claims
    
    def _estimate_cost(self, procedure_description: str) -> float:
        """基于手术描述估算成本"""
        procedure_lower = procedure_description.lower()
        
        if "ventilation" in procedure_lower or "mechanical" in procedure_lower:
            cost_range = self.cost_ranges["mechanical_ventilation"]
        elif "cardiac" in procedure_lower or "coronary" in procedure_lower or "heart" in procedure_lower:
            cost_range = self.cost_ranges["cardiac_procedure"]
        elif "respiratory" in procedure_lower or "pneumonia" in procedure_lower:
            cost_range = self.cost_ranges["respiratory_treatment"]
        elif "monitoring" in procedure_lower or "electrocardiogram" in procedure_lower:
            cost_range = self.cost_ranges["monitoring"]
        elif "surgery" in procedure_lower or "surgical" in procedure_lower:
            cost_range = self.cost_ranges["surgical_procedure"]
        elif "catheter" in procedure_lower or "insertion" in procedure_lower:
            cost_range = self.cost_ranges["diagnostic_procedure"]
        else:
            cost_range = self.cost_ranges["default"]
        
        return random.uniform(cost_range[0], cost_range[1])
    
    def save_claims_to_file(self, claims: List[Dict[str, Any]], filename: str = "mimic_claims.json"):
        """保存理赔数据到JSON文件"""
        with open(filename, 'w') as f:
            json.dump(claims, f, indent=2)
        print(f"Generated {len(claims)} claims saved to {filename}")

def main():
    """主函数 - 演示数据处理"""
    processor = MimicDataProcessor()
    
    print("🏥 MIMIC-III Data Processor")
    print("=" * 40)
    
    # 加载数据（如果没有真实数据文件，会生成模拟数据）
    print("📊 Loading MIMIC-III data...")
    mimic_data = processor.load_mimic_data()
    
    print(f"✅ Loaded data for {len(mimic_data['patients'])} patients")
    
    # 生成理赔申请
    print("\n💼 Generating claims...")
    claims = processor.generate_claims(mimic_data, num_claims=15)
    
    # 显示前5个理赔案例
    print("\n📋 Sample Claims:")
    for i, claim in enumerate(claims[:5]):
        print(f"\nClaim {i+1}:")
        print(f"  Patient: {claim['patient']}")
        print(f"  Diagnosis: {claim['diagnosis']}")
        print(f"  Procedure: {claim['procedure']}")
        print(f"  Cost: ${claim['cost']:,.2f}")
    
    # 保存到文件
    processor.save_claims_to_file(claims, "data/mimic_claims.json")
    
    return claims

if __name__ == "__main__":
    main() 