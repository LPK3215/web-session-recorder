@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 快速启动
echo ========================================
echo.

echo 正在启动后端服务...
echo 后端地址: http://127.0.0.1:8000
echo Swagger 文档: http://127.0.0.1:8000/docs
echo.

echo 正在启动前端服务...
echo 前端地址: http://localhost:5173
echo.

echo ========================================
echo   提示: 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 启动后端（在新窗口）
start "Web Session Recorder - Backend" cmd /k "cd backend && python run.py"

REM 等待 3 秒让后端启动
timeout /t 3 /nobreak >nul

REM 启动前端（在新窗口）
start "Web Session Recorder - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ 服务已启动！
echo.
echo 后端窗口: Web Session Recorder - Backend
echo 前端窗口: Web Session Recorder - Frontend
echo.
echo 访问 http://localhost:5173 开始使用
echo.
pause
