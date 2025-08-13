# 🚀 GitHub 업로드 완전 가이드

## 📋 준비사항 체크리스트

### 1. GitHub 계정 준비
- [ ] [GitHub.com](https://github.com) 가입 완료
- [ ] 이메일 인증 완료

### 2. Git 설치 확인
```bash
git --version
```
만약 Git이 설치되지 않았다면:
- **Windows**: [Git for Windows](https://git-scm.com/download/win) 다운로드
- **Mac**: `brew install git` 또는 Xcode Command Line Tools
- **Linux**: `sudo apt install git` (Ubuntu/Debian)

---

## 🎯 방법 1: 자동화 스크립트 사용 (추천!)

### Windows 사용자
```bash
# PowerShell 또는 명령 프롬프트에서 실행
git-setup.bat
```

### Mac/Linux 사용자
```bash
# 터미널에서 실행
chmod +x git-setup.sh
./git-setup.sh
```

### 스크립트가 하는 일
1. ✅ Git 저장소 초기화
2. ✅ 모든 파일 추가
3. ✅ 첫 번째 커밋 생성
4. ✅ GitHub 저장소 연결
5. ✅ 자동 업로드

---

## 🎯 방법 2: 수동으로 단계별 진행

### 1단계: GitHub에서 새 저장소 생성
1. [GitHub.com](https://github.com) 로그인
2. 우측 상단 "+" 버튼 → "New repository"
3. 저장소 이름: `fs-project` (또는 원하는 이름)
4. Public으로 설정 (무료 배포를 위해)
5. "Create repository" 클릭

### 2단계: 로컬에서 Git 설정
```bash
# 프로젝트 폴더에서 실행
cd C:\dev\fs-project

# Git 초기화
git init

# 모든 파일 추가
git add .

# 첫 번째 커밋
git commit -m "Initial commit: 재무제표 시각화 웹앱"

# 브랜치 이름을 main으로 설정
git branch -M main

# GitHub 저장소 연결 (YOUR_USERNAME을 실제 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/fs-project.git

# 업로드
git push -u origin main
```

---

## 🔧 문제 해결

### 인증 오류 발생 시
```bash
# GitHub Personal Access Token 사용
# Settings → Developer settings → Personal access tokens → Generate new token
# repo 권한 체크 후 생성된 토큰을 비밀번호로 사용
```

### 이미 저장소가 있다고 나올 때
```bash
# 기존 remote 제거 후 다시 추가
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/fs-project.git
git push -u origin main
```

### 파일이 너무 클 때
```bash
# .gitignore에 대용량 파일 추가 후 다시 시도
echo "*.db" >> .gitignore
echo "large_file.xlsx" >> .gitignore
git add .gitignore
git commit -m "Add gitignore"
```

---

## ✅ 업로드 확인 방법

### 성공한 경우
```
✅ GitHub 저장소 페이지에서 파일들이 보임
✅ 모든 배포 설정 파일들이 업로드됨
✅ README.md가 자동으로 표시됨
```

### 확인할 파일들
- [ ] `app.py` - 메인 애플리케이션
- [ ] `requirements.txt` - 의존성 파일
- [ ] `render.yaml` - Render 배포 설정
- [ ] `railway.toml` - Railway 배포 설정
- [ ] `vercel.json` - Vercel 배포 설정
- [ ] `deploy-guide.md` - 배포 가이드

---

## 🎉 업로드 후 다음 단계

1. **GitHub 저장소 URL 복사**
   ```
   https://github.com/YOUR_USERNAME/fs-project
   ```

2. **배포 서비스 선택**
   - Render (추천)
   - Railway  
   - Vercel

3. **deploy-guide.md 파일 참고하여 배포 진행**

---

## 💡 팁

### Git 사용이 처음이라면
- [GitHub Desktop](https://desktop.github.com/) 사용 권장
- GUI 환경에서 쉽게 업로드 가능

### 자주 사용할 Git 명령어
```bash
git status          # 현재 상태 확인
git add .           # 모든 변경사항 추가
git commit -m "메시지"  # 커밋 생성
git push            # 업로드
git pull            # 다운로드
```

문제가 있으면 언제든 도움 요청하세요! 🚀
