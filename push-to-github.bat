@echo off
REM ClawAgent GitHub Push Script for Windows

echo 🚀 Pushing ClawAgent to GitHub...
echo.

REM Check if git remote is configured
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Setting up GitHub remote...
    git remote add origin https://github.com/tuanthescientist/ClawAgent.git
)

echo Current branch:
git branch
echo.

echo Pushing to GitHub (master branch)...
git push -u origin master --force

if errorlevel 0 (
    echo.
    echo ✓ Successfully pushed to GitHub!
    echo Repository: https://github.com/tuanthescientist/ClawAgent
) else (
    echo.
    echo ✗ Push failed. Check your authentication:
    echo   1. Ensure you have a GitHub Personal Access Token
    echo   2. Set it as your git credential
    echo   3. Or use: git remote set-url origin git@github.com:tuanthescientist/ClawAgent.git
    exit /b 1
)

echo.
echo Done! 🎉
