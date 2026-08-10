@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  AI 求职面试助手 · React 新版前端
echo  后端 API：http://127.0.0.1:8000
echo  前端页面：http://localhost:5173
echo ============================================

echo [1/2] 启动后端 API...
start "AI求职助手-后端" cmd /k ".venv\Scripts\python.exe -m uvicorn api.app:app --host 127.0.0.1 --port 8000"

echo [2/2] 启动前端（首次编译需要一点时间）...
start "AI求职助手-前端" cmd /k "cd /d web && npm run dev"

echo 浏览器打开 http://localhost:5173
echo 提示：模型默认读取 .env 配置；未配置密钥时为模拟演示模式。
pause
