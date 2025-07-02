"""
Claim Extractor Agent - Responsible for extracting key information from claims application text
Supports multiple formats: English, JSON, etc.
"""

import re
import json

class ClaimExtractor:
    """Claims information extraction agent"""
    
    def __init__(self):
        # English mode patterns
        self.english_patterns = {
            'patient': r'(?:Patient|Name):\s*([A-Za-z\s]+)',
            'diagnosis': r'(?:Diagnosis|Condition):\s*([^,\n]+)',
            'treatment': r'(?:Treatment|Procedure):\s*([^,\n]+)',
            'cost': r'(?:Cost|Amount|Price):\s*\$?([0-9,]+\.?\d*)'
        }
        
        # Additional patterns for flexible extraction
        self.flexible_patterns = {
            'patient': r'(?:patient|name|client)[\s:]*([A-Za-z\s]+?)(?:\s*,|\s*\n|$)',
            'diagnosis': r'(?:diagnosis|condition|disease)[\s:]*([^,\n]+?)(?:\s*,|\s*\n|$)',
            'treatment': r'(?:treatment|procedure|therapy|surgery)[\s:]*([^,\n]+?)(?:\s*,|\s*\n|$)',
            'cost': r'(?:cost|amount|price|fee)[\s:]*\$?([0-9,]+\.?\d*)'
        }
    
    def extract_claim_info(self, text):
        """
        Extract claims-related information from text
        Automatically detect format and extract information
        
        Args:
            text: Claims application text (supports English, JSON formats)
        
        Returns:
            Dictionary of extracted key information
        """
        # Try parsing JSON format
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return self._extract_from_json(data)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Detect language and extract
        extracted = self._extract_from_english(text)
        
        # Add risk assessment
        extracted['risk_level'] = self._assess_initial_risk(extracted)
        
        # If no information extracted, use example data (MVP version)
        if not any(extracted.values()):
            return self._get_fallback_data()
        
        return extracted
    
    def _extract_from_json(self, data):
        """Extract information from JSON data"""
        result = {
            'patient': data.get('patient', data.get('name', '')),
            'diagnosis': data.get('diagnosis', data.get('condition', '')),
            'treatment': data.get('treatment', data.get('procedure', '')),
            'cost': float(data.get('cost', data.get('amount', 0)))
        }
        return result
    
    def _extract_from_english(self, text):
        """Extract information from English text"""
        result = {
            'patient': '',
            'diagnosis': '',
            'treatment': '',
            'cost': 0.0
        }
        
        # First try standard patterns
        for key, pattern in self.english_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == 'cost':
                    result[key] = float(match.group(1).replace(',', ''))
                else:
                    result[key] = match.group(1).strip()
        
        # If no matches, try flexible patterns
        if not any(result.values()):
            for key, pattern in self.flexible_patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if key == 'cost':
                        result[key] = float(match.group(1).replace(',', ''))
                    else:
                        result[key] = match.group(1).strip()
        
        return result
    
    def _assess_initial_risk(self, extracted_info):
        """Assess initial risk level based on extracted information"""
        cost = extracted_info.get('cost', 0)
        diagnosis = extracted_info.get('diagnosis', '').lower()
        treatment = extracted_info.get('treatment', '').lower()
        
        # High-risk indicators
        high_risk_keywords = ['cancer', 'surgery', 'emergency', 'icu', 'intensive', 'transplant']
        high_risk_cost = cost > 50000
        
        # Medium-risk indicators  
        medium_risk_keywords = ['chronic', 'therapy', 'rehabilitation', 'specialist']
        medium_risk_cost = cost > 10000
        
        if high_risk_cost or any(keyword in diagnosis + treatment for keyword in high_risk_keywords):
            return "High Risk"
        elif medium_risk_cost or any(keyword in diagnosis + treatment for keyword in medium_risk_keywords):
            return "Medium Risk"
        else:
            return "Low Risk"
    
    def _get_fallback_data(self):
        """Fallback data when extraction fails"""
        return {
            'patient': 'Unknown Patient',
            'diagnosis': 'Unknown',
            'treatment': 'Unknown',
            'cost': 0.0,
            'risk_level': 'Medium Risk'
        } 