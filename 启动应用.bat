@echo off
cd /d "%~dp0"

echo ============================================
echo   AI 求职面试助手 启动器
echo ============================================

if not exist "app.py" (
    echo [错误] 找不到 app.py 文件，请确认是从项目文件夹启动。
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [错误] 找不到运行环境，请先安装依赖再启动。
    pause
    exit /b 1
)

rem 检查 8501 端口是否被旧程序占用
netstat -ano | findstr ":8501" | findstr "LISTENING" >nul
if %errorlevel%==0 (
    echo [提示] 检测到 8501 端口已被旧的应用占用。
    echo 请先关闭旧的黑色窗口，再重新双击本程序。
    pause
    exit /b 1
)

rem 自动跳过 Streamlit 首次运行的邮箱提示，避免卡在 Email 输入
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
    echo [general]> "%USERPROFILE%\.streamlit\credentials.toml"
    echo email = "">> "%USERPROFILE%\.streamlit\credentials.toml"
)

echo 正在启动应用，请稍候...
echo.
echo 启动成功后浏览器会自动打开；如果没有自动打开，请手动访问：
echo   http://127.0.0.1:8501
echo.
echo 关闭本黑色窗口即可停止应用。
echo.

".venv\Scripts\python.exe" -m streamlit run app.py

echo.
echo 应用已停止。按任意键关闭本窗口。
pause >nul