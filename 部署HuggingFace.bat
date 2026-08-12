@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

rem Clear dead proxy vars inherited from some launchers
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=

echo ============================================
echo  Deploy to Hugging Face Spaces
echo  Space: Yuvzol0932/ai-job-interview-assistant
echo ============================================

echo [1/3] Push latest commits to GitHub...
git push origin main

echo [2/3] Add Hugging Face remote...
git remote add hf https://huggingface.co/spaces/Yuvzol0932/ai-job-interview-assistant 2>nul

echo [3/3] Push to Hugging Face Space (first time: enter your HF username and access token)...
git push hf main

echo Done. Space URL: https://huggingface.co/spaces/Yuvzol0932/ai-job-interview-assistant
pause
endlocal
