"""
재무제표 시각화 웹 애플리케이션
FastAPI + Plotly를 사용한 대화형 재무제표 시각화
"""
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from datetime import datetime
from typing import Optional, List, Dict

from dart_api import DartAPI
from database import CompanyDatabase, Company
from financial_analyzer import FinancialAnalyzer

# FastAPI 앱 생성 (lifespan 적용은 나중에)
app = FastAPI(title="재무제표 시각화", description="DART API를 활용한 재무제표 시각화 웹앱")

# 정적 파일 및 템플릿 설정
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 전역 객체 초기화
try:
    dart_api = DartAPI()
    company_db = CompanyDatabase()
    
    # 데이터베이스가 비어있으면 JSON에서 로드
    if company_db.get_company_count() == 0:
        print("📂 데이터베이스가 비어있어 JSON에서 로드합니다...")
        try:
            company_db.load_from_json("corpCodes.json")
            print("✅ 회사 데이터 로드 완료")
        except FileNotFoundError:
            print("❌ corpCodes.json 파일을 찾을 수 없습니다.")
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
    
    print("✅ API 및 데이터베이스 초기화 완료")
    
    # AI 분석기 초기화 (선택사항)
    try:
        ai_analyzer = FinancialAnalyzer()
        print("✅ AI 분석기 초기화 완료")
    except Exception as e:
        print(f"⚠️ AI 분석기 초기화 실패 (선택기능): {e}")
        ai_analyzer = None
        
except Exception as e:
    print(f"❌ 초기화 실패: {e}")
    dart_api = None
    company_db = None
    ai_analyzer = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    # 인기 회사 목록 가져오기
    popular_companies = company_db.get_popular_companies(20) if company_db else []
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "popular_companies": popular_companies
    })

@app.get("/api/search_companies")
async def search_companies(q: str):
    """회사 검색 API"""
    if not company_db:
        raise HTTPException(status_code=500, detail="데이터베이스가 초기화되지 않았습니다")
    
    if len(q) < 1:
        return {"companies": []}
    
    try:
        companies = company_db.search_companies(q, limit=20)
        return {
            "companies": [
                {
                    "corp_code": company.corp_code,
                    "corp_name": company.corp_name,
                    "stock_code": company.stock_code
                }
                for company in companies
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")

@app.get("/api/company/{corp_code}")
async def get_company_info(corp_code: str):
    """회사 정보 조회 API"""
    if not company_db:
        raise HTTPException(status_code=500, detail="데이터베이스가 초기화되지 않았습니다")
    
    company = company_db.get_company_by_code(corp_code)
    if not company:
        raise HTTPException(status_code=404, detail="회사를 찾을 수 없습니다")
    
    return {
        "corp_code": company.corp_code,
        "corp_name": company.corp_name,
        "stock_code": company.stock_code,
        "modify_date": company.modify_date
    }

@app.get("/api/financial/{corp_code}")
async def get_financial_data(
    corp_code: str,
    year: int = 2023,
    report_type: str = "11011"
):
    """재무제표 데이터 조회 API"""
    if not dart_api:
        raise HTTPException(status_code=500, detail="DART API가 초기화되지 않았습니다")
    
    try:
        # 재무제표 데이터 조회
        result = dart_api.get_financial_statements(corp_code, str(year), report_type)
        
        if result['status'] != '000':
            raise HTTPException(status_code=400, detail=f"데이터 조회 실패: {result['message']}")
        
        # 데이터 파싱
        parsed_data = dart_api.parse_financial_data(result.get('list', []))
        
        # 주요 지표 계산
        key_metrics = dart_api.get_key_financial_metrics(parsed_data)
        
        return {
            "status": "success",
            "data": parsed_data,
            "metrics": key_metrics,
            "year": year,
            "report_type": report_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재무데이터 조회 실패: {str(e)}")

@app.get("/api/financial_chart/{corp_code}")
async def get_financial_chart(
    corp_code: str,
    start_year: int = 2020,
    end_year: int = 2023,
    chart_type: str = "revenue"
):
    """재무제표 차트 데이터 생성 API"""
    if not dart_api:
        raise HTTPException(status_code=500, detail="DART API가 초기화되지 않았습니다")
    
    try:
        # 여러 연도 데이터 조회
        multi_year_data = dart_api.get_multiple_year_financials(
            corp_code, start_year, end_year, '11011'
        )
        
        # 연도별 지표 추출
        years = []
        values = []
        
        for year, data in multi_year_data.items():
            if data:  # 데이터가 있는 경우만
                parsed = dart_api.parse_financial_data(data)
                metrics = dart_api.get_key_financial_metrics(parsed)
                
                years.append(int(year))
                
                # 차트 타입에 따른 값 선택
                if chart_type == "revenue":
                    values.append(metrics['revenue'] / 100000000)  # 억원 단위
                elif chart_type == "profit":
                    values.append(metrics['net_income'] / 100000000)
                elif chart_type == "assets":
                    values.append(metrics['total_assets'] / 100000000)
                elif chart_type == "equity":
                    values.append(metrics['total_equity'] / 100000000)
                else:
                    values.append(0)
        
        # 차트 생성
        fig = create_financial_chart(years, values, chart_type)
        
        return {
            "chart": json.loads(fig.to_json()),
            "years": years,
            "values": values
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 생성 실패: {str(e)}")

@app.get("/company/{corp_code}", response_class=HTMLResponse)
async def company_detail(request: Request, corp_code: str):
    """회사 상세 페이지"""
    if not company_db:
        raise HTTPException(status_code=500, detail="데이터베이스가 초기화되지 않았습니다")
    
    company = company_db.get_company_by_code(corp_code)
    if not company:
        raise HTTPException(status_code=404, detail="회사를 찾을 수 없습니다")
    
    return templates.TemplateResponse("company_detail.html", {
        "request": request,
        "company": company
    })

def create_financial_chart(years: List[int], values: List[float], chart_type: str):
    """재무 차트 생성"""
    
    chart_configs = {
        "revenue": {"title": "매출액 추이", "color": "#2E86AB", "unit": "억원"},
        "profit": {"title": "순이익 추이", "color": "#A23B72", "unit": "억원"},
        "assets": {"title": "총자산 추이", "color": "#F18F01", "unit": "억원"},
        "equity": {"title": "자본 추이", "color": "#C73E1D", "unit": "억원"}
    }
    
    config = chart_configs.get(chart_type, chart_configs["revenue"])
    
    fig = go.Figure()
    
    # 선 그래프 추가
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        mode='lines+markers',
        name=config["title"],
        line=dict(color=config["color"], width=3),
        marker=dict(size=8, color=config["color"]),
        hovertemplate=f'<b>%{{x}}년</b><br>{config["title"]}: %{{y:,.0f}}{config["unit"]}<extra></extra>'
    ))
    
    # 레이아웃 설정
    fig.update_layout(
        title={
            'text': config["title"],
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2C3E50'}
        },
        xaxis_title="연도",
        yaxis_title=f"{config['title']} ({config['unit']})",
        template="plotly_white",
        height=400,
        hovermode='x unified',
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # 축 스타일 설정
    fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig

def create_financial_pie_chart(metrics: Dict[str, float], chart_type: str = "assets"):
    """재무 파이 차트 생성"""
    if chart_type == "assets":
        # 자산 구성 (자산 = 부채 + 자본)
        labels = ['부채', '자본']
        values = [metrics['total_liabilities'], metrics['total_equity']]
        colors = ['#FF6B6B', '#4ECDC4']
        title = "자산 구성"
    else:
        # 기본값
        labels = ['부채', '자본']
        values = [metrics['total_liabilities'], metrics['total_equity']]
        colors = ['#FF6B6B', '#4ECDC4']
        title = "자산 구성"
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        hovertemplate='<b>%{label}</b><br>금액: %{value:,.0f}억원<br>비율: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2C3E50'}
        },
        template="plotly_white",
        height=400,
        font=dict(family="Arial, sans-serif", size=12)
    )
    
    return fig

@app.get("/api/financial_pie/{corp_code}")
async def get_financial_pie_chart(corp_code: str, year: int = 2023):
    """재무 파이 차트 API"""
    if not dart_api:
        raise HTTPException(status_code=500, detail="DART API가 초기화되지 않았습니다")
    
    try:
        # 재무제표 데이터 조회
        result = dart_api.get_financial_statements(corp_code, str(year), '11011')
        
        if result['status'] != '000':
            raise HTTPException(status_code=400, detail=f"데이터 조회 실패: {result['message']}")
        
        # 데이터 파싱 및 지표 계산
        parsed_data = dart_api.parse_financial_data(result.get('list', []))
        metrics = dart_api.get_key_financial_metrics(parsed_data)
        
        # 억원 단위로 변환
        for key in ['total_assets', 'total_liabilities', 'total_equity']:
            metrics[key] = metrics[key] / 100000000
        
        # 파이 차트 생성
        fig = create_financial_pie_chart(metrics, "assets")
        
        return {
            "chart": json.loads(fig.to_json()),
            "metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파이 차트 생성 실패: {str(e)}")

@app.get("/api/ai_analysis/{corp_code}")
async def get_ai_analysis(corp_code: str, year: int = 2023):
    """AI 재무분석 API"""
    if not ai_analyzer:
        raise HTTPException(status_code=503, detail="AI 분석 서비스를 사용할 수 없습니다. Gemini API 키를 확인해주세요.")
    
    if not dart_api or not company_db:
        raise HTTPException(status_code=500, detail="시스템이 초기화되지 않았습니다.")
    
    try:
        # 회사 정보 조회
        company = company_db.get_company_by_code(corp_code)
        if not company:
            raise HTTPException(status_code=404, detail="회사를 찾을 수 없습니다.")
        
        # 재무데이터 조회
        result = dart_api.get_financial_statements(corp_code, str(year), '11011')
        if result['status'] != '000':
            raise HTTPException(status_code=400, detail=f"재무데이터 조회 실패: {result['message']}")
        
        # 데이터 파싱 및 지표 계산
        parsed_data = dart_api.parse_financial_data(result.get('list', []))
        metrics = dart_api.get_key_financial_metrics(parsed_data)
        
        # AI 분석 실행
        analysis_result = ai_analyzer.analyze_financial_data(
            company_name=company.corp_name,
            financial_metrics=metrics
        )
        
        return {
            "status": "success",
            "company_name": company.corp_name,
            "analysis_year": year,
            "analysis": analysis_result,
            "metrics": {
                "revenue_billions": round(metrics['revenue'] / 100000000, 1),
                "profit_billions": round(metrics['net_income'] / 100000000, 1),
                "assets_billions": round(metrics['total_assets'] / 100000000, 1),
                "operating_margin": round(metrics['operating_margin'], 1),
                "roe": round(metrics['roe'], 1)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 실패: {str(e)}")

@app.get("/api/financial_terms")
async def explain_financial_terms():
    """재무용어 설명 API"""
    if not ai_analyzer:
        raise HTTPException(status_code=503, detail="AI 분석 서비스를 사용할 수 없습니다.")
    
    common_terms = [
        "영업이익률", "순이익률", "부채비율", "자기자본이익률(ROE)", 
        "매출액", "영업이익", "순이익", "총자산", "자본총계"
    ]
    
    try:
        explanations = ai_analyzer.explain_financial_terms(common_terms)
        return {
            "status": "success",
            "explanations": explanations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"용어 설명 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
