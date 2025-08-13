@echo off
REM UTF-8 인코딩 설정
chcp 65001 >nul

echo ========================================
echo    GitHub 업로드 자동화 스크립트
echo ========================================
echo.

REM 사용자 이름 입력 받기
set /p GITHUB_USERNAME="GitHub 사용자명을 입력하세요: "
set /p REPO_NAME="저장소 이름을 입력하세요 (기본: fs-project): "

REM 기본값 설정
if "%REPO_NAME%"=="" set REPO_NAME=fs-project

echo.
echo [1/5] Git 저장소 초기화 중...
git init

echo.
echo [2/5] 파일 추가 중...
git add .

echo.
echo [3/5] 첫 번째 커밋 생성 중...
git commit -m "Initial commit: 재무제표 시각화 웹앱"

echo.
echo [4/5] 기본 브랜치를 main으로 설정...
git branch -M main

echo.
echo [5/5] GitHub 저장소 연결 중...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo.
echo GitHub에 업로드 중...
git push -u origin main

echo.
echo ========================================
echo ✅ 완료! 업로드 성공!
echo 📍 저장소 주소: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo ========================================
echo.
echo 다음 단계:
echo 1. 브라우저에서 위 주소로 이동
echo 2. 저장소가 제대로 생성되었는지 확인  
echo 3. deploy-guide.md 파일을 참고하여 배포 진행
echo.
pause
