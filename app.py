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

# 안전한 숫자 변환 함수
def safe_convert(value, default=0):
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

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
        
        # 디버깅: 실제 응답 데이터 확인
        print(f"🔍 디버깅 - corp_code: {corp_code}, 연도: {start_year}-{end_year}")
        print(f"🔍 multi_year_data keys: {list(multi_year_data.keys())}")
        
        for year, data in multi_year_data.items():
            print(f"🔍 {year}년 데이터 길이: {len(data) if data else 0}")
            if data and len(data) > 0:
                print(f"🔍 {year}년 첫 번째 항목: {data[0]}")
                break
        
        # 연도별 지표 추출
        years = []
        values = []
        
        for year, data in multi_year_data.items():
            if data:  # 데이터가 있는 경우만
                try:
                    print(f"🔍 {year}년 데이터 파싱 시작...")
                    parsed = dart_api.parse_financial_data(data)
                    print(f"🔍 {year}년 파싱 완료. parsed keys: {list(parsed.keys())}")
                    
                    metrics = dart_api.get_key_financial_metrics(parsed)
                    print(f"🔍 {year}년 지표 계산 완료. metrics: {list(metrics.keys())}")
                    

                    
                    years.append(int(year))
                    
                    # 차트 타입에 따른 값 선택 (안전한 변환)
                    if chart_type == "revenue":
                        value = safe_convert(metrics.get('revenue', 0)) / 100000000
                    elif chart_type == "profit":
                        value = safe_convert(metrics.get('net_income', 0)) / 100000000
                    elif chart_type == "assets":
                        value = safe_convert(metrics.get('total_assets', 0)) / 100000000
                    elif chart_type == "equity":
                        value = safe_convert(metrics.get('total_equity', 0)) / 100000000
                    else:
                        value = 0
                    
                    values.append(round(value, 2))  # 소수점 2자리로 반올림
                    # chart_type에 따른 실제 metrics 키 매핑
                    metric_key_map = {
                        'revenue': 'revenue',
                        'profit': 'net_income', 
                        'assets': 'total_assets',
                        'equity': 'total_equity'
                    }
                    actual_key = metric_key_map.get(chart_type, 'revenue')
                    print(f"🔍 {year}년 {chart_type} 값: {value} (metrics[{actual_key}]: {metrics.get(actual_key, 0)})")
                    
                except Exception as e:
                    print(f"❌ {year}년 데이터 처리 오류: {e}")
                    print(f"❌ 에러 타입: {type(e).__name__}")
                    import traceback
                    print(f"❌ 상세 에러: {traceback.format_exc()}")
                    # 에러가 발생해도 연도는 추가하되 값은 0으로
                    years.append(int(year))
                    values.append(0)
        
        # 데이터가 없는 경우 처리
        if not years or all(v == 0 for v in values):
            return {
                "chart": None,
                "years": [],
                "values": [],
                "message": "해당 기간의 재무데이터를 찾을 수 없습니다."
            }
        
        # 차트 생성
        print(f"🔍 차트 생성 시작 - years: {years}, values: {values}, chart_type: {chart_type}")
        try:
            fig = create_financial_chart(years, values, chart_type)
            print(f"🔍 차트 생성 성공!")
        except Exception as chart_error:
            print(f"❌ 차트 생성 실패: {chart_error}")
            import traceback
            print(f"❌ 차트 생성 상세 에러: {traceback.format_exc()}")
            raise chart_error
        
        return {
            "chart": json.loads(fig.to_json()),
            "years": years,
            "values": values,
            "message": "성공"
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
    
    # 입력 데이터 검증
    if not years or not values:
        raise ValueError("연도 또는 값 데이터가 비어있습니다")
    
    if len(years) != len(values):
        raise ValueError(f"연도 개수({len(years)})와 값 개수({len(values)})가 일치하지 않습니다")
    
    print(f"🔍 차트 생성 함수 - years: {years}, values: {values}, chart_type: {chart_type}")
    
    chart_configs = {
        "revenue": {"title": "매출액 추이", "color": "#2E86AB", "unit": "억원"},
        "profit": {"title": "순이익 추이", "color": "#A23B72", "unit": "억원"},
        "assets": {"title": "총자산 추이", "color": "#F18F01", "unit": "억원"},
        "equity": {"title": "자본 추이", "color": "#C73E1D", "unit": "억원"}
    }
    
    config = chart_configs.get(chart_type, chart_configs["revenue"])
    print(f"🔍 차트 설정: {config}")
    
    try:
        fig = go.Figure()
        print(f"🔍 Figure 객체 생성 성공")
    except Exception as e:
        print(f"❌ Figure 객체 생성 실패: {e}")
        raise
    
    # 선 그래프 추가
    try:
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=config["title"],
            line=dict(color=config["color"], width=3),
            marker=dict(size=8, color=config["color"]),
            hovertemplate=f'<b>%{{x}}년</b><br>{config["title"]}: %{{y:,.0f}}{config["unit"]}<extra></extra>'
        ))
        print(f"🔍 Scatter trace 추가 성공")
    except Exception as e:
        print(f"❌ Scatter trace 추가 실패: {e}")
        raise
    
    # 레이아웃 설정
    try:
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
        print(f"🔍 레이아웃 설정 성공")
    except Exception as e:
        print(f"❌ 레이아웃 설정 실패: {e}")
        raise
    
    # 축 스타일 설정
    try:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        print(f"🔍 축 스타일 설정 성공")
    except Exception as e:
        print(f"❌ 축 스타일 설정 실패: {e}")
        raise
    
    print(f"🔍 차트 생성 함수 완료!")
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


def create_balance_sheet_box_chart(metrics: Dict, year: int):
    """재무상태표 박스 차트 생성 (자산 = 부채 + 자본)"""
    try:
        # 데이터 추출 (억원 단위)
        total_assets = metrics.get('total_assets', 0) / 100000000
        total_liabilities = metrics.get('total_liabilities', 0) / 100000000  
        total_equity = metrics.get('total_equity', 0) / 100000000
        
        # 유동/비유동 자산 (있는 경우)
        current_assets = metrics.get('current_assets', 0) / 100000000
        non_current_assets = metrics.get('non_current_assets', 0) / 100000000
        
        # 유동/비유동 부채 (있는 경우)
        current_liabilities = metrics.get('current_liabilities', 0) / 100000000
        non_current_liabilities = metrics.get('non_current_liabilities', 0) / 100000000
        
        # 최대값으로 정규화 (박스 높이 조절용)
        max_value = max(total_assets, total_liabilities + total_equity)
        if max_value == 0:
            max_value = 1  # 0으로 나누기 방지
        
        # Figure 생성
        fig = go.Figure()
        
        # 자산 박스 (좌측)
        assets_height = (total_assets / max_value) * 100
        
        # 유동자산 (밝은 파란색)
        if current_assets > 0:
            current_assets_height = (current_assets / max_value) * 100
            fig.add_trace(go.Bar(
                x=['자산'],
                y=[current_assets_height],
                name='유동자산',
                marker_color='#87CEEB',
                text=[f'{current_assets:,.0f}억원'],
                textposition='middle',
                hovertemplate='유동자산<br>%{text}<extra></extra>'
            ))
        
        # 비유동자산 (진한 파란색)
        if non_current_assets > 0:
            non_current_assets_height = (non_current_assets / max_value) * 100
            fig.add_trace(go.Bar(
                x=['자산'],
                y=[non_current_assets_height],
                name='비유동자산',
                marker_color='#4682B4',
                text=[f'{non_current_assets:,.0f}억원'],
                textposition='middle',
                base=[current_assets_height] if current_assets > 0 else [0],
                hovertemplate='비유동자산<br>%{text}<extra></extra>'
            ))
        
        # 자산이 세분화되지 않은 경우 전체 자산으로 표시
        if current_assets == 0 and non_current_assets == 0 and total_assets > 0:
            fig.add_trace(go.Bar(
                x=['자산'],
                y=[assets_height],
                name='총자산',
                marker_color='#4682B4',
                text=[f'{total_assets:,.0f}억원'],
                textposition='middle',
                hovertemplate='총자산<br>%{text}<extra></extra>'
            ))
        
        # 부채 박스 (우측 하단)
        if total_liabilities > 0:
            liabilities_height = (total_liabilities / max_value) * 100
            
            # 유동부채 (밝은 빨간색)
            if current_liabilities > 0:
                current_liabilities_height = (current_liabilities / max_value) * 100
                fig.add_trace(go.Bar(
                    x=['부채 + 자본'],
                    y=[current_liabilities_height],
                    name='유동부채',
                    marker_color='#FFB6C1',
                    text=[f'{current_liabilities:,.0f}억원'],
                    textposition='middle',
                    hovertemplate='유동부채<br>%{text}<extra></extra>'
                ))
            
            # 비유동부채 (진한 빨간색)
            if non_current_liabilities > 0:
                non_current_liabilities_height = (non_current_liabilities / max_value) * 100
                fig.add_trace(go.Bar(
                    x=['부채 + 자본'],
                    y=[non_current_liabilities_height],
                    name='비유동부채',
                    marker_color='#DC143C',
                    text=[f'{non_current_liabilities:,.0f}억원'],
                    textposition='middle',
                    base=[current_liabilities_height] if current_liabilities > 0 else [0],
                    hovertemplate='비유동부채<br>%{text}<extra></extra>'
                ))
            
            # 부채가 세분화되지 않은 경우 전체 부채로 표시
            if current_liabilities == 0 and non_current_liabilities == 0:
                fig.add_trace(go.Bar(
                    x=['부채 + 자본'],
                    y=[liabilities_height],
                    name='총부채',
                    marker_color='#DC143C',
                    text=[f'{total_liabilities:,.0f}억원'],
                    textposition='middle',
                    hovertemplate='총부채<br>%{text}<extra></extra>'
                ))
        
        # 자본 박스 (우측 상단)
        if total_equity > 0:
            equity_height = (total_equity / max_value) * 100
            base_height = (total_liabilities / max_value) * 100 if total_liabilities > 0 else 0
            
            fig.add_trace(go.Bar(
                x=['부채 + 자본'],
                y=[equity_height],
                name='자본',
                marker_color='#32CD32',
                text=[f'{total_equity:,.0f}억원'],
                textposition='middle',
                base=[base_height],
                hovertemplate='자본<br>%{text}<extra></extra>'
            ))
        
        # 레이아웃 설정
        fig.update_layout(
            title=f'{year}년 재무상태표 구조',
            font=dict(size=14),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
            margin=dict(t=80, b=50, l=50, r=50),
            barmode='stack',
            xaxis=dict(
                title="",
                tickfont=dict(size=16, color='#2F4F4F'),
                categoryorder='array',
                categoryarray=['자산', '부채 + 자본']
            ),
            yaxis=dict(
                title="금액 비율 (%)",
                tickfont=dict(size=12),
                range=[0, 105]
            ),
            plot_bgcolor='rgba(248,249,250,0.8)',
            paper_bgcolor='white'
        )
        
        # 등식 표시를 위한 annotation 추가
        fig.add_annotation(
            x=0.5,
            y=1.08,
            xref="paper",
            yref="paper",
            text=f"<b>자산 {total_assets:,.0f}억원 = 부채 {total_liabilities:,.0f}억원 + 자본 {total_equity:,.0f}억원</b>",
            showarrow=False,
            font=dict(size=16, color='#2F4F4F'),
            align="center"
        )
        
        return fig
        
    except Exception as e:
        print(f"❌ 재무상태표 박스 차트 생성 실패: {e}")
        raise


@app.get("/api/balance_sheet_box/{corp_code}")
async def get_balance_sheet_box(corp_code: str, year: int = 2023):
    """재무상태표 박스 차트 API"""
    if not dart_api:
        raise HTTPException(status_code=500, detail="DART API가 초기화되지 않았습니다")
    
    try:
        print(f"📊 재무상태표 박스 차트 요청: {corp_code}, {year}년")
        
        # 재무제표 데이터 조회
        result = dart_api.get_financial_statements(corp_code, str(year), '11011')
        
        if result['status'] != '000':
            raise HTTPException(status_code=400, detail=f"데이터 조회 실패: {result['message']}")
        
        # 데이터 파싱 및 지표 계산
        parsed_data = dart_api.parse_financial_data(result.get('list', []))
        metrics = dart_api.get_key_financial_metrics(parsed_data)
        
        print(f"🔍 재무상태표 지표: 자산={metrics.get('total_assets', 0)/100000000:.0f}억, "
              f"부채={metrics.get('total_liabilities', 0)/100000000:.0f}억, "
              f"자본={metrics.get('total_equity', 0)/100000000:.0f}억")
        
        # 박스 차트 생성
        fig = create_balance_sheet_box_chart(metrics, year)
        
        return {
            "chart": json.loads(fig.to_json()),
            "metrics": {
                "total_assets": metrics.get('total_assets', 0),
                "total_liabilities": metrics.get('total_liabilities', 0),
                "total_equity": metrics.get('total_equity', 0),
                "current_assets": metrics.get('current_assets', 0),
                "non_current_assets": metrics.get('non_current_assets', 0),
                "current_liabilities": metrics.get('current_liabilities', 0),
                "non_current_liabilities": metrics.get('non_current_liabilities', 0)
            },
            "year": year
        }
        
    except Exception as e:
        print(f"❌ 재무상태표 박스 차트 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"박스 차트 생성 실패: {str(e)}")


@app.get("/api/financial_charts_batch/{corp_code}")
async def get_financial_charts_batch(corp_code: str, start_year: int = 2019, end_year: int = 2023, base_year: int = 2023):
    """모든 차트 데이터를 한 번에 반환"""
    if not dart_api:
        raise HTTPException(status_code=500, detail="DART API가 초기화되지 않았습니다")
    
    try:
        print(f"📊 배치 차트 요청: {corp_code}, {start_year}-{end_year}년, 파이차트: {base_year}년")
        
        # 결과를 저장할 딕셔너리
        result = {
            "line_charts": {},
            "pie_chart": None,
            "success": True,
            "message": "모든 차트 데이터를 성공적으로 로드했습니다."
        }
        
        # 라인 차트들 (매출액, 순이익, 총자산)
        chart_types = ['revenue', 'profit', 'assets']
        
        for chart_type in chart_types:
            try:
                print(f"🔍 {chart_type} 차트 생성 중...")
                
                years = []
                values = []
                
                # 연도별 데이터 수집
                for year in range(start_year, end_year + 1):
                    try:
                        # 재무제표 데이터 조회
                        financial_result = dart_api.get_financial_statements(corp_code, str(year), '11011')
                        
                        if financial_result['status'] == '000' and financial_result.get('list'):
                            # 데이터 파싱 및 지표 계산
                            parsed_data = dart_api.parse_financial_data(financial_result.get('list', []))
                            metrics = dart_api.get_key_financial_metrics(parsed_data)
                            
                            years.append(year)
                            
                            # 차트 타입에 따른 값 선택 (억원 단위)
                            if chart_type == "revenue":
                                value = safe_convert(metrics.get('revenue', 0)) / 100000000
                            elif chart_type == "profit":
                                value = safe_convert(metrics.get('net_income', 0)) / 100000000
                            elif chart_type == "assets":
                                value = safe_convert(metrics.get('total_assets', 0)) / 100000000
                            else:
                                value = 0
                            
                            values.append(round(value, 2))
                            print(f"✅ {year}년 {chart_type}: {value}억원")
                            
                    except Exception as e:
                        print(f"❌ {year}년 {chart_type} 데이터 처리 오류: {e}")
                        continue
                
                # 데이터가 있으면 차트 생성
                if years and values and not all(v == 0 for v in values):
                    fig = create_financial_chart(years, values, chart_type)
                    result["line_charts"][chart_type] = {
                        "chart": json.loads(fig.to_json()),
                        "years": years,
                        "values": values
                    }
                    print(f"✅ {chart_type} 차트 생성 완료")
                else:
                    result["line_charts"][chart_type] = {
                        "chart": None,
                        "message": f"{chart_type} 데이터를 찾을 수 없습니다."
                    }
                    print(f"❌ {chart_type} 데이터 없음")
                    
            except Exception as e:
                print(f"❌ {chart_type} 차트 생성 실패: {e}")
                result["line_charts"][chart_type] = {
                    "chart": None,
                    "message": f"{chart_type} 차트 생성 중 오류가 발생했습니다."
                }
        
        # 파이 차트 (자산 구성)
        try:
            print(f"🥧 파이 차트 생성 중... ({base_year}년)")
            
            # 재무제표 데이터 조회
            financial_result = dart_api.get_financial_statements(corp_code, str(base_year), '11011')
            
            if financial_result['status'] == '000' and financial_result.get('list'):
                # 데이터 파싱 및 지표 계산
                parsed_data = dart_api.parse_financial_data(financial_result.get('list', []))
                metrics = dart_api.get_key_financial_metrics(parsed_data)
                
                # 억원 단위로 변환
                for key in ['total_assets', 'total_liabilities', 'total_equity']:
                    metrics[key] = metrics[key] / 100000000
                
                # 파이 차트 생성
                fig = create_financial_pie_chart(metrics, "assets")
                
                result["pie_chart"] = {
                    "chart": json.loads(fig.to_json()),
                    "metrics": metrics
                }
                print(f"✅ 파이 차트 생성 완료")
            else:
                result["pie_chart"] = {
                    "chart": None, 
                    "message": "자산 구성 데이터를 찾을 수 없습니다."
                }
                print(f"❌ 파이 차트 데이터 없음")
                
        except Exception as e:
            print(f"❌ 파이 차트 생성 실패: {e}")
            result["pie_chart"] = {
                "chart": None, 
                "message": "파이 차트 생성 중 오류가 발생했습니다."
            }
        
        print(f"✅ 배치 차트 생성 완료!")
        return result
        
    except Exception as e:
        print(f"❌ 배치 차트 생성 전체 실패: {e}")
        raise HTTPException(status_code=500, detail=f"차트 생성 중 오류가 발생했습니다: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
