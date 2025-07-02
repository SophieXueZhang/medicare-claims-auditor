"""
Claim Extractor Agent - 负责从理赔申请文本中提取关键信息
支持多种格式：中文、英文、JSON等
"""
import re
import json
from typing import Dict, Any

class ClaimExtractor:
    """理赔信息提取智能体"""
    
    def __init__(self):
        # 中文模式
        self.chinese_patterns = {
            'patient_name': r'患者[：:]?\s*([A-Za-z\u4e00-\u9fa5]+)',
            'diagnosis': r'诊断[：:]?\s*([A-Za-z\u4e00-\u9fa5\s]+)',
            'procedure': r'治疗[：:]?\s*([A-Za-z\u4e00-\u9fa5\s]+)',
            'amount': r'费用[：:]?\s*(\d+\.?\d*)'
        }
        
        # 英文模式
        self.english_patterns = {
            'patient_name': r'Patient[：:]?\s*([A-Za-z0-9_\s]+?)(?=,|$)',
            'diagnosis': r'Diagnosis[：:]?\s*([A-Za-z\s,]+?)(?=,\s*Treatment|,\s*Cost|$)',
            'procedure': r'(?:Treatment|Procedure)[：:]?\s*([A-Za-z\s,]+?)(?=,\s*Cost|$)',
            'amount': r'(?:Cost|Amount)[：:]?\s*\$?(\d+\.?\d*)'
        }
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取理赔相关信息
        自动检测格式并提取信息
        
        Args:
            text: 理赔申请文本（支持中文、英文、JSON格式）
            
        Returns:
            提取的关键信息字典
        """
        # 尝试解析JSON格式
        if text.strip().startswith('{'):
            try:
                json_data = json.loads(text)
                return self._extract_from_json(json_data)
            except json.JSONDecodeError:
                pass
        
        # 检测语言并提取
        if self._is_chinese_text(text):
            extracted_info = self._extract_with_patterns(text, self.chinese_patterns)
        else:
            extracted_info = self._extract_with_patterns(text, self.english_patterns)
        
        # 如果没有提取到信息，使用示例数据（MVP版本）
        if not extracted_info:
            extracted_info = {
                "patient_name": "Unknown Patient",
                "diagnosis": "Unknown Condition",
                "procedure": "Unknown Treatment",
                "amount": "0"
            }
        
        # 标准化数据格式
        extracted_info = self._normalize_data(extracted_info)
        
        # 添加风险评估
        extracted_info["risk_level"] = self._assess_risk(extracted_info)
        
        return extracted_info
    
    def _extract_from_json(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据中提取信息"""
        return {
            "patient_name": json_data.get("patient", "Unknown"),
            "diagnosis": json_data.get("diagnosis", "Unknown"),
            "procedure": json_data.get("procedure", "Unknown"),
            "amount": str(json_data.get("cost", 0))
        }
    
    def _is_chinese_text(self, text: str) -> bool:
        """检测文本是否包含中文字符"""
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', text)
        return len(chinese_chars) > 0
    
    def _extract_with_patterns(self, text: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """使用正则表达式模式提取信息"""
        extracted_info = {}
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_info[key] = match.group(1).strip()
        
        return extracted_info
    
    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化数据格式"""
        # 清理金额数据
        if 'amount' in data:
            amount_str = str(data['amount'])
            # 移除货币符号和逗号
            amount_str = re.sub(r'[,$￥]', '', amount_str)
            data['amount'] = amount_str
        
        # 清理空白字符
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        
        return data
    
    def _assess_risk(self, info: Dict[str, Any]) -> str:
        """风险评估（支持中英文）"""
        try:
            amount = float(info.get('amount', 0))
        except (ValueError, TypeError):
            amount = 0
        
        # 获取诊断和治疗信息进行风险评估
        diagnosis = info.get('diagnosis', '').lower()
        procedure = info.get('procedure', '').lower()
        
        # 高风险条件
        high_risk_keywords = [
            'sepsis', 'septicemia', 'cardiac', 'heart', 'brain', 'tumor', 
            'cancer', 'surgery', 'ventilation', 'intensive', 'icu',
            '脓毒症', '心脏', '脑', '肿瘤', '癌症', '手术', '重症'
        ]
        
        # 检查高风险关键词
        is_high_risk_condition = any(
            keyword in diagnosis or keyword in procedure 
            for keyword in high_risk_keywords
        )
        
        if amount > 100000 or is_high_risk_condition:
            return "High Risk" if not self._is_chinese_text(diagnosis + procedure) else "高风险"
        elif amount > 50000:
            return "Medium Risk" if not self._is_chinese_text(diagnosis + procedure) else "中风险"
        else:
            return "Low Risk" if not self._is_chinese_text(diagnosis + procedure) else "低风险" 