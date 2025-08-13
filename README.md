# 📊 재무제표 시각화 웹 애플리케이션

DART Open API를 활용한 상장회사 재무제표 분석 및 시각화 웹 서비스입니다.

## 🌟 주요 기능

### 📈 차트 시각화
- **매출액 추이**: 연도별 매출 성장률 분석
- **순이익 추이**: 수익성 변화 추적  
- **총자산 추이**: 자산 규모 변화 분석
- **자산 구성**: 파이차트로 자산 포트폴리오 시각화
- **재무상태표 구조**: 좌우 분할 박스 차트로 자산 = 부채 + 자본 시각화

### 💰 핵심 재무지표
- **수익성 지표**: 영업이익률, 순이익률, ROE
- **재무안정성**: 부채비율, 자기자본비율
- **유동성 분석**: 유동자산/비유동자산, 유동부채/비유동부채 구분

### 🎨 사용자 경험
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 최적화
- **배치 차트 로딩**: 한 번의 API 호출로 모든 차트 데이터 로드
- **실시간 데이터**: DART Open API를 통한 최신 공시 정보

## 🚀 라이브 데모

**🌐 배포된 서비스**: https://fs-app-tmbv.onrender.com/

### 샘플 기업 링크
- [삼성전자](https://fs-app-tmbv.onrender.com/company/00126380)
- [SK하이닉스](https://fs-app-tmbv.onrender.com/company/00164779)
- [NAVER](https://fs-app-tmbv.onrender.com/company/00113570)

## 🛠️ 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLite**: 경량 데이터베이스
- **DART Open API**: 금융감독원 공시 데이터
- **Plotly**: 인터랙티브 차트 생성

### Frontend
- **Bootstrap 5**: 반응형 UI 프레임워크
- **Plotly.js**: 클라이언트 사이드 차트 렌더링
- **FontAwesome**: 아이콘 라이브러리

### Deployment
- **Render**: 클라우드 배포 플랫폼
- **Docker**: 컨테이너화 지원

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/RyuJaeChun/fs-app.git
cd fs-app
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
# .env 파일 생성
DART_API_KEY=your_dart_api_key_here
PORT=8000
```

### 4. 로컬 서버 실행
```bash
# 개발 서버
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# 또는 테스트 서버
python test_local.py
```

### 5. 웹 브라우저에서 접속
```
http://localhost:8000
```

## 🗂️ 프로젝트 구조

```
fs-app/
├── 📁 static/                    # 정적 파일
│   └── style.css                 # 스타일시트
├── 📁 templates/                 # HTML 템플릿
│   ├── index.html                # 메인 페이지
│   └── company_detail.html       # 기업 상세 페이지
├── 📄 app.py                     # FastAPI 메인 애플리케이션
├── 📄 dart_api.py                # DART API 클라이언트
├── 📄 database.py                # 데이터베이스 관리
├── 📄 financial_analyzer.py      # 재무 분석 로직
├── 📄 test_local.py              # 로컬 테스트 서버
├── 📄 corpCodes.json             # 상장회사 목록 데이터
├── 📄 companies.db               # SQLite 데이터베이스
├── 📄 requirements.txt           # Python 의존성
├── 📄 Dockerfile                 # Docker 설정
└── 📄 README.md                  # 프로젝트 문서
```

## 🎯 핵심 기능 상세

### 재무상태표 박스 차트
```
┌─────────────┐    =    ┌─────────────┐
│             │         │    자본     │
│ 비유동자산   │         │   (75.7%)   │
│ (76.9%)     │         │             │
│             │         ├─────────────┤
├─────────────┤         │ 비유동부채   │
│             │         │  (10.2%)    │
│ 유동자산     │         ├─────────────┤
│ (23.1%)     │         │ 유동부채     │
│             │         │  (14.1%)    │
└─────────────┘         └─────────────┘
    자산                  부채 + 자본
```

### 반응형 메트릭 표시
- **데스크톱**: 큰 폰트와 상세 정보
- **태블릿**: 중간 크기 최적화
- **모바일**: 작은 화면에 맞는 축약 표시

### 배치 API 최적화
```python
# 기존: 4번의 개별 API 호출
GET /api/financial_chart/revenue/{corp_code}
GET /api/financial_chart/profit/{corp_code}  
GET /api/financial_chart/assets/{corp_code}
GET /api/financial_pie/{corp_code}

# 개선: 1번의 배치 API 호출
GET /api/financial_charts_batch/{corp_code}
```

## 🔧 API 엔드포인트

### 메인 페이지
- `GET /`: 상장회사 목록 및 검색

### 기업 상세 페이지  
- `GET /company/{corp_code}`: 기업 상세 정보 및 차트

### 데이터 API
- `GET /api/financial/{corp_code}`: 재무 데이터
- `GET /api/financial_charts_batch/{corp_code}`: 모든 차트 데이터
- `GET /api/balance_sheet_box/{corp_code}`: 재무상태표 박스 차트

### 분석 API
- `GET /api/analyze/{corp_code}`: AI 재무 분석 (Gemini)
- `GET /api/terms/{term}`: 재무용어 설명

## 💡 사용법

### 1. 기업 검색
메인 페이지에서 회사명 또는 종목코드로 검색

### 2. 재무 분석
- 상단 메트릭에서 핵심 지표 확인
- 4개 차트에서 추세 및 구성 분석
- 재무상태표 박스 차트에서 재무구조 파악

### 3. 연도 변경
드롭다운에서 분석 연도 선택 (2019-2023)

### 4. AI 분석
"AI 분석 보기" 버튼으로 Gemini AI의 재무 분석 리포트 확인

## 🎨 디자인 시스템

### 색상 팔레트
- **매출액**: `#2E86AB` (파란색)
- **순이익**: `#A23B72` (자주색)  
- **총자산**: `#F18F01` (주황색)
- **유동자산**: `#87CEEB` (밝은 파란색)
- **비유동자산**: `#4682B4` (진한 파란색)
- **유동부채**: `#FFB6C1` (밝은 빨간색)
- **비유동부채**: `#DC143C` (진한 빨간색)
- **자본**: `#32CD32` (초록색)

### 반응형 브레이크포인트
- **XS**: < 576px (모바일)
- **SM**: 576px - 768px (큰 모바일)
- **MD**: 768px - 992px (태블릿)
- **LG**: 992px - 1200px (작은 데스크톱)
- **XL**: > 1200px (큰 데스크톱)

## 🔒 보안 및 성능

### 보안
- **환경 변수**: API 키 및 민감 정보 보호
- **HTTPS**: 배포 환경에서 SSL 적용
- **입력 검증**: FastAPI 자동 데이터 검증

### 성능 최적화
- **배치 API**: 네트워크 요청 최소화
- **캐싱**: 정적 파일 브라우저 캐싱
- **압축**: Gzip 압축 적용
- **비동기 처리**: FastAPI async/await 활용

## 📊 데이터 소스

### DART Open API
- **제공처**: 금융감독원
- **데이터**: 상장회사 공시 정보
- **업데이트**: 실시간 공시 반영
- **범위**: 2019-2023년 재무제표

### 포함 데이터
- **손익계산서**: 매출액, 영업이익, 순이익
- **재무상태표**: 자산, 부채, 자본 (유동/비유동 구분)
- **재무비율**: 수익성, 안정성, 유동성 지표

## 🤝 기여하기

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- **금융감독원**: DART Open API 제공
- **Plotly**: 뛰어난 차트 라이브러리
- **FastAPI**: 현대적인 웹 프레임워크
- **Render**: 무료 클라우드 호스팅

---

📧 **문의사항**: GitHub Issues 또는 [이메일](mailto:your-email@example.com)

⭐ **이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**