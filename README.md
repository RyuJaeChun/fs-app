# DART Open API 공시검색 프로젝트

한국 금융감독원의 DART(Data Analysis, Retrieval and Transfer System) Open API를 사용하여 상장회사의 공시 정보를 검색하고 다운로드하는 Python 프로젝트입니다.

## 📋 기능

- 🔍 **공시 검색**: 다양한 조건으로 공시 정보 검색
- 💾 **다양한 저장 형식**: CSV, JSON, Excel 형태로 데이터 저장
- 📊 **데이터 분석**: pandas DataFrame으로 데이터 처리
- 🏢 **회사별 검색**: 특정 회사의 공시만 검색
- 📅 **기간별 검색**: 원하는 기간의 공시 검색
- 🏛️ **시장별 검색**: 유가증권시장, 코스닥시장 등 시장별 검색
- 📂 **회사 코드 다운로드**: 전체 상장회사 고유번호 및 정보 다운로드
- 🔎 **회사명 검색**: 회사명으로 고유번호 및 종목코드 검색

## 📦 설치

1. **저장소 클론 및 의존성 설치**
```bash
cd fs-project
pip install -r requirements.txt
```

2. **DART API 키 발급**
   - [DART 홈페이지](https://opendart.fss.or.kr/)에서 회원가입
   - 인증키 신청 후 승인 대기 (보통 1-2일 소요)

3. **환경 설정**
```bash
python config_setup.py
```
또는 수동으로 `.env` 파일 생성:
```
DART_API_KEY=your_40_character_api_key_here
```

## 🚀 사용법

### 기본 사용법

```python
from dart_api import DartAPI, get_recent_date_range

# API 인스턴스 생성
dart = DartAPI()

# 최근 7일간의 유가증권시장 공시 검색
bgn_de, end_de = get_recent_date_range(7)
disclosures = dart.get_all_disclosures(
    bgn_de=bgn_de,
    end_de=end_de,
    corp_cls='Y'  # 유가증권시장
)

# 다양한 형식으로 저장
dart.save_data(disclosures, 'recent_disclosures', 'csv')    # CSV 저장
dart.save_data(disclosures, 'recent_disclosures', 'json')   # JSON 저장
dart.save_data(disclosures, 'recent_disclosures', 'excel')  # Excel 저장
dart.save_data(disclosures, 'recent_disclosures', 'all')    # 모든 형식
```

### 회사 코드 다운로드

```python
# 전체 상장회사 고유번호 다운로드
corp_codes = dart.download_corp_codes(save_json=True)

# 저장된 회사 코드 로드
corp_codes = dart.load_corp_codes()

# 회사명으로 검색
samsung_results = dart.search_company("삼성전자")
if samsung_results:
    samsung = samsung_results[0]
    print(f"회사명: {samsung['corp_name']}")
    print(f"고유번호: {samsung['corp_code']}")
    print(f"종목코드: {samsung['stock_code']}")
```

### 특정 회사 검색

```python
# 회사명으로 고유번호 찾기
samsung_results = dart.search_company("삼성전자")
if samsung_results:
    corp_code = samsung_results[0]['corp_code']
    
    # 해당 회사의 최근 30일 공시
    disclosures = dart.get_all_disclosures(
        corp_code=corp_code,
        bgn_de='20240101',
        end_de='20240131'
    )
```

### 공시 유형별 검색

```python
# 정기공시만 검색
disclosures = dart.get_all_disclosures(
    pblntf_ty='A',  # 정기공시
    corp_cls='Y',   # 유가증권시장
    bgn_de='20240101',
    end_de='20240131'
)
```

## 📚 주요 파라미터

### 공시 유형 (pblntf_ty)
- `A`: 정기공시
- `B`: 주요사항보고
- `C`: 발행공시
- `D`: 지분공시
- `E`: 기타공시
- `F`: 외부감사관련
- `G`: 펀드공시
- `H`: 자산유동화
- `I`: 거래소공시
- `J`: 공정위공시

### 법인 구분 (corp_cls)
- `Y`: 유가증권시장
- `K`: 코스닥시장
- `N`: 코넥스시장
- `E`: 기타

### 저장 형식
- **CSV**: Excel에서 바로 열기 가능, 데이터 분석에 적합
- **JSON**: 프로그래밍에서 사용 편리, API 연동에 적합
- **Excel**: 일반 사용자 친화적, 보고서 작성에 적합

#### 저장 형식 사용법
```python
# 단일 형식 저장
dart.save_data(disclosures, 'filename', 'csv')    # CSV만
dart.save_data(disclosures, 'filename', 'json')   # JSON만  
dart.save_data(disclosures, 'filename', 'excel')  # Excel만

# 모든 형식으로 한번에 저장
dart.save_data(disclosures, 'filename', 'all')    # CSV, JSON, Excel 모두

# 기존 방식도 지원
dart.save_to_csv(disclosures, 'file.csv')
dart.save_to_json(disclosures, 'file.json')
dart.save_to_excel(disclosures, 'file.xlsx')
```

## 📁 파일 구조

```
fs-project/
├── dart_api.py          # 메인 API 클래스
├── example_usage.py     # 사용 예시 스크립트
├── corp_codes_example.py # 회사 코드 다운로드 및 검색 예시
├── save_format_example.py # 다양한 저장 형식 예시
├── config_setup.py      # 설정 도우미 스크립트
├── quick_start.py       # 빠른 시작 가이드
├── requirements.txt     # 의존성 패키지
├── env_example.txt      # 환경변수 예시
├── corpCodes.json       # 회사 코드 파일 (다운로드 후 생성)
└── README.md           # 프로젝트 설명서
```

## 🔧 예시 스크립트 실행

### 1. 설정 도우미 실행
```bash
python config_setup.py
```
- API 키 설정
- 연결 테스트
- 상태 코드 및 유형 정보 확인

### 2. 사용 예시 실행
```bash
python example_usage.py
```
- 다양한 검색 예시 실행
- 파일 저장 예시
- 데이터 분석 예시

### 3. 회사 코드 다운로드 및 검색
```bash
python corp_codes_example.py
```
- 전체 상장회사 고유번호 다운로드
- 회사명으로 검색 기능
- Excel 파일로 회사 목록 저장

### 4. 저장 형식 예시
```bash
python save_format_example.py
```
- CSV, JSON, Excel 저장 방식 비교
- 형식별 특징 및 사용법 안내

### 5. 직접 실행
```bash
python dart_api.py
```
- 최근 7일간 유가증권시장 공시 검색
- CSV 및 JSON 파일로 자동 저장

## ⚠️ 주의사항

1. **API 사용 제한**
   - 일반적으로 일일 20,000건 제한
   - 과도한 요청 시 일시적 차단 가능

2. **검색 기간 제한**
   - 고유번호 없이 검색 시 최대 3개월

3. **데이터 처리**
   - 대량 데이터 검색 시 메모리 사용량 주의
   - 페이지별 처리로 메모리 효율성 확보

## 🐛 문제 해결

### API 키 관련 오류
- `010`: 등록되지 않은 키 → API 키 재확인
- `011`: 사용할 수 없는 키 → 키 상태 확인
- `012`: 접근할 수 없는 IP → IP 등록 확인

### 검색 결과 관련
- `013`: 조회된 데이터 없음 → 검색 조건 변경
- `020`: 요청 제한 초과 → 잠시 후 재시도
- `021`: 조회 가능한 회사 개수 초과 → 검색 범위 축소

## 📞 지원

- **DART 고객센터**: opendart@fss.or.kr
- **DART 개발가이드**: [https://opendart.fss.or.kr/guide/](https://opendart.fss.or.kr/guide/)

## 📄 라이선스

이 프로젝트는 DART Open API의 이용약관을 준수합니다.

---

*이 프로젝트는 금융감독원 DART Open API를 활용한 비공식 라이브러리입니다.*
