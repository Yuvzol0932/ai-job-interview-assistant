@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  Push to GitHub (one-click)
echo  Repo name : ai-job-interview-assistant
echo ============================================

where gh >nul 2>nul
if errorlevel 1 (
    echo [1/4] GitHub CLI not found, installing...
    winget install --id GitHub.cli -e --accept-source-agreements --accept-package-agreements
)

gh auth status >nul 2>nul
if errorlevel 1 (
    echo [2/4] Refreshing GitHub login, please complete it in the browser...
    gh auth refresh -h github.com
    if errorlevel 1 (
        echo Please log in to GitHub in the browser window...
        gh auth login --web
    )
)

echo [3/4] Creating remote repo and pushing...
gh repo create ai-job-interview-assistant --public --source . --remote origin --push

echo [4/4] Pushing tags...
git push origin main --tags

echo Done. Check: https://github.com/settings/repositories
pause
endlocal
