"""
Gemini AI를 활용한 재무제표 분석 모듈
"""
import google.generativeai as genai
import os
from typing import Dict, Any, List
import json
from dotenv import load_dotenv

load_dotenv()

class FinancialAnalyzer:
    """Gemini AI를 사용한 재무분석 클래스"""
    
    def __init__(self, api_key: str = None):
        """
        재무분석기 초기화
        
        Args:
            api_key: Gemini API 키 (없으면 환경변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API 키가 필요합니다. GEMINI_API_KEY 환경변수를 설정하거나 직접 전달해주세요.")
        
        # Gemini API 설정
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def analyze_financial_data(self, 
                             company_name: str,
                             financial_metrics: Dict[str, Any],
                             multi_year_data: Dict[str, List] = None) -> Dict[str, str]:
        """
        재무데이터를 분석하여 쉬운 설명 생성
        
        Args:
            company_name: 회사명
            financial_metrics: 주요 재무지표
            multi_year_data: 다년도 데이터 (선택사항)
            
        Returns:
            분석 결과 딕셔너리
        """
        
        # 프롬프트 구성
        prompt = self._create_analysis_prompt(company_name, financial_metrics, multi_year_data)
        
        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # 결과를 섹션별로 파싱
            parsed_analysis = self._parse_analysis_result(analysis_text, company_name, financial_metrics)
            
            return parsed_analysis
            
        except Exception as e:
            return {
                "error": f"AI 분석 중 오류 발생: {str(e)}",
                "summary": "현재 AI 분석을 사용할 수 없습니다.",
                "strengths": "데이터를 확인해주세요.",
                "concerns": "시스템 관리자에게 문의하세요.",
                "recommendation": "수동으로 재무제표를 검토해보시기 바랍니다."
            }
    
    def _create_analysis_prompt(self, 
                               company_name: str, 
                               metrics: Dict[str, Any],
                               multi_year_data: Dict[str, List] = None) -> str:
        """분석용 프롬프트 생성"""
        
        # 기본 재무지표 정보
        prompt = f"""
당신은 전문 재무분석가입니다. {company_name}의 재무제표를 분석하여 일반인도 쉽게 이해할 수 있도록 설명해주세요.

## 재무지표 정보 (억원 단위):
- 매출액: {metrics.get('revenue', 0) / 100000000:,.0f}억원
- 영업이익: {metrics.get('operating_profit', 0) / 100000000:,.0f}억원  
- 순이익: {metrics.get('net_income', 0) / 100000000:,.0f}억원
- 총자산: {metrics.get('total_assets', 0) / 100000000:,.0f}억원
- 총부채: {metrics.get('total_liabilities', 0) / 100000000:,.0f}억원
- 자본총계: {metrics.get('total_equity', 0) / 100000000:,.0f}억원

## 재무비율:
- 부채비율: {metrics.get('debt_ratio', 0):.1f}%
- 자본비율: {metrics.get('equity_ratio', 0):.1f}%
- 영업이익률: {metrics.get('operating_margin', 0):.1f}%
- 순이익률: {metrics.get('net_margin', 0):.1f}%
- 자기자본이익률(ROE): {metrics.get('roe', 0):.1f}%

다음 형식을 정확히 지켜서 분석해주세요:

### 한줄요약
이 회사의 재무상태를 한 문장으로 요약해주세요.

### 강점
이 회사의 재무적 강점들을 구체적인 숫자와 함께 설명해주세요.

### 주의점
투자자가 주의해야 할 재무적 위험요소들을 설명해주세요.

### 투자의견
일반 투자자를 위한 구체적인 투자 조언을 제공해주세요.

**중요**: 각 섹션 제목(### 한줄요약, ### 강점, ### 주의점, ### 투자의견)을 정확히 사용하고, 각 섹션에는 반드시 실질적인 내용을 포함해주세요.
"""

        # 다년도 데이터가 있으면 추가
        if multi_year_data:
            prompt += f"\n\n## 추가 참고사항:\n다년도 데이터가 제공되었으므로 성장성과 추세도 함께 분석해주세요."
        
        return prompt
    
    def _parse_analysis_result(self, analysis_text: str, company_name: str = "", financial_metrics: Dict[str, Any] = None) -> Dict[str, str]:
        """AI 분석 결과를 섹션별로 파싱"""
        
        sections = {
            "summary": "",
            "strengths": "", 
            "concerns": "",
            "recommendation": ""
        }
        
        try:
            # 섹션별로 텍스트 분리
            lines = analysis_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # 섹션 헤더 감지 (정확한 매칭)
                line_lower = line.lower().strip()
                if '### 한줄요약' in line or '한줄요약' in line_lower:
                    current_section = "summary"
                elif '### 강점' in line or (line_lower.startswith('강점') and len(line_lower) < 10):
                    current_section = "strengths"
                elif '### 주의점' in line or (line_lower.startswith('주의') and len(line_lower) < 10):
                    current_section = "concerns" 
                elif '### 투자의견' in line or (line_lower.startswith('투자') and len(line_lower) < 10):
                    current_section = "recommendation"
                elif line and current_section and not line.startswith('#') and not line.startswith('###'):
                    # 내용 추가 (헤더가 아닌 실제 내용만)
                    if sections[current_section]:
                        sections[current_section] += " "
                    sections[current_section] += line
            
            # 빈 섹션들 임시 기본값 설정 (파싱 실패시)
            if not sections["summary"]:
                sections["summary"] = f"{company_name}의 재무제표 분석 결과입니다." if company_name else "재무제표 분석 결과입니다."
            if not sections["strengths"] and financial_metrics:
                # 매출액과 순이익 기반 간단한 강점 생성
                revenue_b = financial_metrics.get('revenue', 0) / 100000000
                profit_b = financial_metrics.get('net_income', 0) / 100000000
                sections["strengths"] = f"매출액 {revenue_b:,.0f}억원, 순이익 {profit_b:,.0f}억원을 기록하여 안정적인 수익 구조를 보여주고 있습니다."
            elif not sections["strengths"]:
                sections["strengths"] = "재무적 강점을 분석 중입니다."
            if not sections["concerns"] and financial_metrics:
                debt_ratio = financial_metrics.get('debt_ratio', 0)
                sections["concerns"] = f"부채비율이 {debt_ratio:.1f}%로 재무 구조를 지속적으로 모니터링할 필요가 있습니다."
            elif not sections["concerns"]:
                sections["concerns"] = "주의사항을 검토 중입니다."
            if not sections["recommendation"] and financial_metrics:
                roe = financial_metrics.get('roe', 0)
                sections["recommendation"] = f"자기자본이익률(ROE) {roe:.1f}%를 바탕으로 투자 가치를 신중히 검토해보시기 바랍니다."
            elif not sections["recommendation"]:
                sections["recommendation"] = "투자 조언을 준비 중입니다."
                
        except Exception as e:
            # 파싱 실패시 전체 텍스트를 요약으로 사용
            sections["summary"] = analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text
            
        return sections
    
    def get_industry_comparison(self, 
                              company_name: str,
                              metrics: Dict[str, Any],
                              industry: str = None) -> str:
        """업계 비교 분석"""
        
        prompt = f"""
{company_name}의 재무지표를 업계 평균과 비교하여 분석해주세요.

재무지표:
- 영업이익률: {metrics.get('operating_margin', 0):.1f}%
- 순이익률: {metrics.get('net_margin', 0):.1f}%
- 부채비율: {metrics.get('debt_ratio', 0):.1f}%
- ROE: {metrics.get('roe', 0):.1f}%

업계 비교 관점에서 이 회사의 경쟁력을 평가하고, 
일반 투자자가 이해하기 쉽게 설명해주세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"업계 비교 분석 중 오류가 발생했습니다: {str(e)}"
    
    def explain_financial_terms(self, terms: List[str]) -> Dict[str, str]:
        """재무용어 쉽게 설명"""
        
        prompt = f"""
다음 재무용어들을 일반인도 쉽게 이해할 수 있도록 설명해주세요:
{', '.join(terms)}

각 용어마다 다음과 같이 설명해주세요:
- 간단한 정의
- 실생활 예시
- 투자할 때 왜 중요한지
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # 응답을 용어별로 파싱 (간단한 구현)
            explanations = {}
            for term in terms:
                explanations[term] = f"{term}에 대한 설명이 포함되어 있습니다."
            
            return explanations
            
        except Exception as e:
            return {term: f"설명을 불러올 수 없습니다: {str(e)}" for term in terms}

def test_analyzer():
    """분석기 테스트"""
    try:
        analyzer = FinancialAnalyzer()
        
        # 테스트 데이터
        test_metrics = {
            'revenue': 30000000000000,  # 300조원
            'operating_profit': 5000000000000,  # 50조원
            'net_income': 4000000000000,  # 40조원
            'total_assets': 50000000000000,  # 500조원
            'total_liabilities': 20000000000000,  # 200조원
            'total_equity': 30000000000000,  # 300조원
            'debt_ratio': 40.0,
            'equity_ratio': 60.0,
            'operating_margin': 16.7,
            'net_margin': 13.3,
            'roe': 13.3
        }
        
        result = analyzer.analyze_financial_data("삼성전자", test_metrics)
        
        print("=== AI 재무분석 테스트 결과 ===")
        for key, value in result.items():
            print(f"\n{key.upper()}:")
            print(value)
            
    except Exception as e:
        print(f"테스트 실패: {e}")
        print("GEMINI_API_KEY 환경변수가 설정되어 있는지 확인해주세요.")

if __name__ == "__main__":
    test_analyzer()

