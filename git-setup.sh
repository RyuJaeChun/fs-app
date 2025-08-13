#!/bin/bash

echo "========================================"
echo "    GitHub 업로드 자동화 스크립트"
echo "========================================"
echo

# 사용자 이름 입력 받기
read -p "GitHub 사용자명을 입력하세요: " GITHUB_USERNAME
read -p "저장소 이름을 입력하세요 (기본: fs-project): " REPO_NAME

# 기본값 설정
if [ -z "$REPO_NAME" ]; then
    REPO_NAME="fs-project"
fi

echo
echo "🚀 Git 저장소 초기화 중..."
git init

echo
echo "📝 파일 추가 중..."
git add .

echo
echo "💾 첫 번째 커밋 생성 중..."
git commit -m "Initial commit: 재무제표 시각화 웹앱"

echo
echo "🌿 기본 브랜치를 main으로 설정..."
git branch -M main

echo
echo "🔗 GitHub 저장소 연결 중..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo
echo "⬆️ GitHub에 업로드 중..."
git push -u origin main

echo
echo "========================================"
echo "✅ 완료!"
echo "📍 저장소 주소: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "========================================"
echo
echo "다음 단계:"
echo "1. 브라우저에서 위 주소로 이동"
echo "2. 저장소가 제대로 생성되었는지 확인"
echo "3. deploy-guide.md 파일을 참고하여 배포 진행"
echo
