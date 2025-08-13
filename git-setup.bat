@echo off
chcp 65001 >nul
echo ========================================
echo    GitHub Upload Automation Script
echo ========================================
echo.

REM Get user input
set /p GITHUB_USERNAME="GitHub username: "
set /p REPO_NAME="Repository name (default: fs-project): "

REM Set default value
if "%REPO_NAME%"=="" set REPO_NAME=fs-project

echo.
echo [1/5] Initializing Git repository...
git init

echo.
echo [2/5] Adding files...
git add .

echo.
echo [3/5] Creating first commit...
git commit -m "Initial commit: Financial Statement Visualization Web App"

echo.
echo [4/5] Setting main branch...
git branch -M main

echo.
echo [5/5] Connecting to GitHub...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo.
echo Uploading to GitHub...
git push -u origin main

echo.
echo ========================================
echo SUCCESS! Upload completed!
echo Repository URL: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo ========================================
echo.
echo Next steps:
echo 1. Open the URL above in your browser
echo 2. Verify the repository was created correctly
echo 3. Follow deploy-guide.md for deployment
echo.
pause
