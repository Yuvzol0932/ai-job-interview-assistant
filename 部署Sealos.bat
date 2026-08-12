@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

rem Clear dead proxy vars inherited from some launchers
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=

echo ============================================
echo  Deploy to Sealos (free, domestic access)
echo  Image: ghcr.io/yuvzol0932/ai-job-interview-assistant:latest
echo ============================================

echo [1/4] Copy Docker image address to clipboard...
echo ghcr.io/yuvzol0932/ai-job-interview-assistant:latest | clip

echo [2/4] Open GitHub Actions page (check image build status)...
start "" "https://github.com/Yuvzol0932/ai-job-interview-assistant/actions"

echo [3/4] Open Sealos Cloud console...
start "" "https://cloud.sealos.io"

echo [4/4] Manual steps in Sealos:
echo   1. Register / login with GitHub or phone (no credit card needed).
echo   2. Go to "App Launchpad" - "Create App" (or edit the existing app).
echo   3. Choose Docker image, paste the image address from clipboard.
echo   4. Expose container port 7860.
echo   5. Add env vars: LLM_API_KEY = your key, LLM_MODE = real.
echo   6. Deploy and open the generated URL.
echo.
echo Image address is already in your clipboard.
pause
endlocal
