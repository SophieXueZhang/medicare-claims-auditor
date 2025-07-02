"""
保险条款检查智能体 - 基于真实Medicare NCD/LCD数据
负责验证理赔申请是否符合保险条款和覆盖政策
"""

import json
import re
from pathlib import Path

class PolicyChecker:
    """
    保险条款检查智能体
    基于真实Medicare NCD (National Coverage Determinations) 和 
    LCD (Local Coverage Determinations) 数据进行覆盖决定
    """
    
    def __init__(self):
        self.medicare_rules = self._load_medicare_rules()
        self.coverage_matrix = self.medicare_rules.get("audit_rules", {}).get("coverage_matrix", {})
        self.benefit_categories = self.medicare_rules.get("benefit_categories", {})
        
    def _load_medicare_rules(self):
        """加载真实的Medicare审核规则"""
        rules_file = Path("data/medicare_audit_rules.json")
        if rules_file.exists():
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载Medicare规则时出错: {e}")
                return self._get_fallback_rules()
        else:
            print("Medicare规则文件不存在，使用备用规则")
            return self._get_fallback_rules()
    
    def _get_fallback_rules(self):
        """备用规则（如果无法加载真实规则）"""
        return {
            "coverage_rules": {
                "covered": [],
                "conditional": [],
                "excluded": [],
                "limits": {
                    "annual_deductible": 1600,
                    "coinsurance_rate": 0.20,
                    "max_therapy_visits": {"physical_therapy": 36}
                }
            },
            "audit_rules": {
                "coverage_matrix": {
                    "always_covered": [],
                    "conditionally_covered": [],
                    "never_covered": []
                }
            },
            "benefit_categories": {}
        }
    
    def check_policy_compliance(self, extracted_info):
        """
        检查理赔申请的保险条款合规性
        基于真实Medicare覆盖决定数据
        """
        patient = extracted_info.get('patient', 'Unknown')
        diagnosis = extracted_info.get('diagnosis', '').lower()
        treatment = extracted_info.get('treatment', '').lower()
        cost = extracted_info.get('cost', 0)
        
        # 获取覆盖规则
        coverage_rules = self.medicare_rules.get("coverage_rules", {})
        audit_rules = self.medicare_rules.get("audit_rules", {})
        
        # 检查覆盖状态
        coverage_status = self._determine_coverage_status(diagnosis, treatment, coverage_rules)
        
        # 检查费用限制
        cost_compliance = self._check_cost_limits(cost, coverage_rules.get("limits", {}))
        
        # 检查特殊要求
        special_requirements = self._check_special_requirements(diagnosis, treatment, coverage_rules.get("requirements", {}))
        
        # 风险评估
        risk_level = self._assess_risk_level(cost, diagnosis, treatment, audit_rules.get("risk_assessment", {}))
        
        # 确定最终决策
        final_decision = self._make_coverage_decision(
            coverage_status, cost_compliance, special_requirements, risk_level, cost
        )
        
        return {
            "patient": patient,
            "coverage_status": coverage_status,
            "cost_compliance": cost_compliance,
            "special_requirements": special_requirements,
            "risk_level": risk_level,
            "final_decision": final_decision,
            "applicable_ncds": self._find_applicable_ncds(diagnosis, treatment),
            "benefit_category": self._determine_benefit_category(treatment),
            "compliance_details": {
                "deductible_applicable": True,
                "coinsurance_rate": coverage_rules.get("limits", {}).get("coinsurance_rate", 0.20),
                "geographic_considerations": "Standard metropolitan area",
                "prior_authorization_required": "prior authorization" in str(special_requirements).lower()
            }
        }
    
    def _determine_coverage_status(self, diagnosis, treatment, coverage_rules):
        """基于真实Medicare规则确定覆盖状态"""
        
        # 检查完全覆盖项目
        covered_rules = coverage_rules.get("covered", [])
        for rule in covered_rules:
            if self._matches_rule(diagnosis, treatment, rule):
                return {
                    "status": "COVERED",
                    "source": rule.get("source", "Unknown"),
                    "title": rule.get("title", ""),
                    "reason": f"符合Medicare覆盖决定: {rule.get('title', '')}"
                }
        
        # 检查有条件覆盖项目
        conditional_rules = coverage_rules.get("conditional", [])
        for rule in conditional_rules:
            if self._matches_rule(diagnosis, treatment, rule):
                return {
                    "status": "CONDITIONAL",
                    "source": rule.get("source", "Unknown"),
                    "title": rule.get("title", ""),
                    "reason": f"有条件覆盖，需满足特定要求: {rule.get('title', '')}"
                }
        
        # 检查排除项目
        excluded_rules = coverage_rules.get("excluded", [])
        for rule in excluded_rules:
            if self._matches_rule(diagnosis, treatment, rule):
                return {
                    "status": "EXCLUDED",
                    "source": rule.get("source", "Unknown"), 
                    "title": rule.get("title", ""),
                    "reason": f"明确排除项目: {rule.get('title', '')}"
                }
        
        # 默认需要人工审核
        return {
            "status": "REQUIRES_REVIEW",
            "source": "Policy_Default",
            "title": "Manual Review Required",
            "reason": "未找到明确的覆盖决定，需要人工审核"
        }
    
    def _matches_rule(self, diagnosis, treatment, rule):
        """检查诊断和治疗是否匹配特定规则"""
        conditions = rule.get("condition", [])
        procedures = rule.get("procedure", [])
        
        # 检查诊断匹配
        diagnosis_match = False
        if not conditions:  # 如果没有特定条件，则认为匹配
            diagnosis_match = True
        else:
            for condition in conditions:
                if condition.lower() in diagnosis.lower():
                    diagnosis_match = True
                    break
        
        # 检查治疗匹配
        treatment_match = False
        if not procedures:  # 如果没有特定程序，则认为匹配
            treatment_match = True
        else:
            for procedure in procedures:
                if procedure.lower() in treatment.lower():
                    treatment_match = True
                    break
        
        return diagnosis_match or treatment_match
    
    def _check_cost_limits(self, cost, limits):
        """检查费用限制"""
        annual_deductible = limits.get("annual_deductible", 1600)
        coinsurance_rate = limits.get("coinsurance_rate", 0.20)
        
        # 计算患者责任
        patient_responsibility = annual_deductible + (cost - annual_deductible) * coinsurance_rate
        insurance_payment = cost - patient_responsibility
        
        # 检查是否超出特定限制
        warnings = []
        if cost > 50000:
            warnings.append("高额费用，需要特殊审核")
        if cost > 100000:
            warnings.append("超高额费用，需要委员会审核")
        
        return {
            "total_cost": cost,
            "deductible": annual_deductible,
            "patient_responsibility": round(patient_responsibility, 2),
            "insurance_payment": round(insurance_payment, 2),
            "coinsurance_rate": coinsurance_rate,
            "warnings": warnings,
            "compliant": True  # Medicare通常没有绝对的费用上限
        }
    
    def _check_special_requirements(self, diagnosis, treatment, requirements):
        """检查特殊要求"""
        required_items = []
        
        prior_auth_items = requirements.get("prior_authorization", [])
        for item in prior_auth_items:
            if any(keyword in treatment.lower() for keyword in item.lower().split()):
                required_items.append(f"需要事先授权: {item}")
        
        physician_cert_items = requirements.get("physician_certification", [])
        for item in physician_cert_items:
            if any(keyword in treatment.lower() for keyword in item.lower().split()):
                required_items.append(f"需要医生认证: {item}")
        
        documentation_items = requirements.get("documentation_required", [])
        if documentation_items:
            required_items.extend([f"需要文档: {item}" for item in documentation_items[:2]])
        
        return {
            "required_items": required_items,
            "prior_authorization": any("事先授权" in item for item in required_items),
            "physician_certification": any("医生认证" in item for item in required_items),
            "additional_documentation": any("文档" in item for item in required_items),
            "compliant": True  # 假设申请包含了必要信息
        }
    
    def _assess_risk_level(self, cost, diagnosis, treatment, risk_assessment):
        """评估理赔风险等级"""
        high_risk = risk_assessment.get("high_risk_indicators", [])
        medium_risk = risk_assessment.get("medium_risk_indicators", [])
        low_risk = risk_assessment.get("low_risk_indicators", [])
        
        risk_score = 0
        risk_factors = []
        
        # 检查高风险指标
        if cost > 50000:
            risk_score += 3
            risk_factors.append("高额费用")
        
        if any(keyword in treatment.lower() for keyword in ["experimental", "investigational", "试验"]):
            risk_score += 3
            risk_factors.append("实验性治疗")
        
        # 检查中等风险指标
        if cost > 10000:
            risk_score += 2
            risk_factors.append("较高费用")
        
        if any(keyword in treatment.lower() for keyword in ["elective", "选择性"]):
            risk_score += 2
            risk_factors.append("选择性程序")
        
        # 检查低风险指标
        if any(keyword in treatment.lower() for keyword in ["routine", "preventive", "常规", "预防"]):
            risk_score -= 1
            risk_factors.append("常规护理")
        
        # 确定风险等级
        if risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 2:
            risk_level = "MEDIUM" 
        else:
            risk_level = "LOW"
        
        return {
            "level": risk_level,
            "score": risk_score,
            "factors": risk_factors,
            "requires_manual_review": risk_level in ["HIGH", "MEDIUM"]
        }
    
    def _make_coverage_decision(self, coverage_status, cost_compliance, special_requirements, risk_level, cost):
        """基于所有因素做出最终覆盖决定"""
        
        status = coverage_status.get("status", "REQUIRES_REVIEW")
        risk = risk_level.get("level", "MEDIUM")
        
        # 排除项目直接拒绝
        if status == "EXCLUDED":
            return {
                "decision": "DENIED",
                "reason": coverage_status.get("reason", "服务被排除在覆盖范围外"),
                "confidence": 0.95
            }
        
        # 明确覆盖的低风险项目自动批准
        if status == "COVERED" and risk == "LOW" and cost < 5000:
            return {
                "decision": "APPROVED",
                "reason": "符合Medicare覆盖标准，风险低",
                "confidence": 0.90
            }
        
        # 有条件覆盖需要检查要求
        if status == "CONDITIONAL":
            if special_requirements.get("compliant", True):
                return {
                    "decision": "APPROVED",
                    "reason": "满足有条件覆盖要求",
                    "confidence": 0.80
                }
            else:
                return {
                    "decision": "PENDING",
                    "reason": "需要满足额外要求",
                    "confidence": 0.60
                }
        
        # 高风险或高费用需要人工审核
        if risk == "HIGH" or cost > 25000:
            return {
                "decision": "REQUIRES_REVIEW",
                "reason": "高风险或高费用，需要人工审核",
                "confidence": 0.50
            }
        
        # 默认批准（符合基本条件）
        return {
            "decision": "APPROVED",
            "reason": "符合基本覆盖条件",
            "confidence": 0.75
        }
    
    def _find_applicable_ncds(self, diagnosis, treatment):
        """查找适用的NCD规则"""
        applicable_ncds = []
        coverage_rules = self.medicare_rules.get("coverage_rules", {})
        
        for category in ["covered", "conditional", "excluded"]:
            rules = coverage_rules.get(category, [])
            for rule in rules:
                if self._matches_rule(diagnosis, treatment, rule):
                    applicable_ncds.append({
                        "source": rule.get("source", ""),
                        "title": rule.get("title", ""),
                        "category": category
                    })
        
        return applicable_ncds[:3]  # 限制返回数量
    
    def _determine_benefit_category(self, treatment):
        """确定福利类别"""
        treatment_lower = treatment.lower()
        
        # 基于治疗类型确定福利类别
        if any(keyword in treatment_lower for keyword in ["surgery", "surgical", "手术"]):
            return "Inpatient Hospital Services"
        elif any(keyword in treatment_lower for keyword in ["therapy", "rehabilitation", "治疗", "康复"]):
            return "Outpatient Physical Therapy Services"
        elif any(keyword in treatment_lower for keyword in ["imaging", "x-ray", "ct", "mri", "影像", "检查"]):
            return "Diagnostic X-Ray Tests"
        elif any(keyword in treatment_lower for keyword in ["drug", "medication", "injection", "药物", "注射"]):
            return "Drugs and Biologicals"
        elif any(keyword in treatment_lower for keyword in ["device", "equipment", "设备", "器械"]):
            return "Durable Medical Equipment"
        else:
            return "Physicians' Services" 