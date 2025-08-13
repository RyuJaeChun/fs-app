# 🚀 무료 배포 가이드

당신의 재무제표 시각화 앱을 무료로 배포하는 3가지 방법입니다!

## 📋 배포 전 준비사항

### 1. 환경변수 준비
- `DART_API_KEY`: [DART 홈페이지](https://opendart.fss.or.kr/)에서 발급
- `GEMINI_API_KEY`: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급 (선택사항)

### 2. GitHub 저장소 생성
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/fs-project.git
git push -u origin main
```

---

## 🎯 옵션 1: Render (가장 추천!)

### 장점
- ✅ FastAPI 완벽 지원
- ✅ PostgreSQL 무료 제공
- ✅ 자동 HTTPS/SSL
- ✅ 무료 750시간/월

### 배포 단계
1. [Render.com](https://render.com) 가입
2. "New +" → "Web Service" 선택
3. GitHub 저장소 연결
4. 설정:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.11.0`
5. 환경변수 추가:
   - `DART_API_KEY`: 발급받은 키
   - `GEMINI_API_KEY`: AI 분석용 (선택)
6. "Deploy Web Service" 클릭

### 데이터베이스 추가 (선택)
1. "New +" → "PostgreSQL" 선택
2. 무료 플랜 선택
3. 생성된 `DATABASE_URL`을 웹서비스에 추가

---

## 🚄 옵션 2: Railway

### 장점
- ✅ 매우 간단한 설정
- ✅ 자동 도메인 제공
- ✅ 500시간/월 무료

### 배포 단계
1. [Railway.app](https://railway.app) 가입
2. "Deploy from GitHub repo" 선택
3. 저장소 선택
4. 자동 감지된 설정 확인
5. 환경변수 추가:
   - `DART_API_KEY`: 발급받은 키
   - `GEMINI_API_KEY`: AI 분석용 (선택)
6. 자동 배포 시작

### 데이터베이스 추가
1. 프로젝트에서 "Add Service" → "Database" → "PostgreSQL"
2. 자동으로 `DATABASE_URL` 생성

---

## ⚡ 옵션 3: Vercel

### 장점
- ✅ 무제한 무료
- ✅ 초고속 배포
- ✅ 글로벌 CDN

### 제약사항
- ⚠️ 서버리스 (10초 실행 제한)
- ⚠️ 파일 저장 불가
- ⚠️ 데이터베이스 별도 설정 필요

### 배포 단계
1. [Vercel.com](https://vercel.com) 가입
2. GitHub 저장소 가져오기
3. Framework: "Other" 선택
4. Build Command: 비워두기
5. 환경변수 추가:
   - `DART_API_KEY`: 발급받은 키
   - `GEMINI_API_KEY`: AI 분석용 (선택)
6. Deploy 클릭

---

## 🔧 문제 해결

### 공통 이슈
- **빌드 실패**: `requirements.txt` 확인
- **포트 오류**: 환경변수 `PORT` 사용하도록 수정됨
- **API 키 오류**: 환경변수 올바른지 확인

### 데이터베이스 이슈
- **SQLite 제한**: 클라우드에서는 PostgreSQL 권장
- **연결 오류**: `DATABASE_URL` 환경변수 확인

## 📊 성능 비교

| 서비스 | 무료 시간 | 데이터베이스 | 도메인 | 추천도 |
|--------|-----------|--------------|--------|---------|
| **Render** | 750시간/월 | PostgreSQL 무료 | render.com | ⭐⭐⭐⭐⭐ |
| **Railway** | 500시간/월 | PostgreSQL 무료 | railway.app | ⭐⭐⭐⭐ |
| **Vercel** | 무제한 | 별도 설정 | vercel.app | ⭐⭐⭐ |

## 🎉 배포 후 확인사항

1. **웹사이트 접속 테스트**
2. **API 엔드포인트 테스트**
3. **회사 검색 기능 테스트**
4. **차트 생성 테스트**
5. **AI 분석 기능 테스트** (설정한 경우)

---

💡 **추천**: 처음이시라면 **Render**로 시작하세요! 가장 안정적이고 완전한 기능을 제공합니다.

문제가 있으면 언제든 도움 요청하세요! 🚀
