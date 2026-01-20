@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 运行检查
echo ========================================
echo.

REM 返回项目根目录
cd ..\..

echo [1/2] 后端检查（导入 + API smoke）...
python backend\scripts\smoke_test.py
if errorlevel 1 (
    echo.
    echo ? 后端检查失败
    pause
    exit /b 1
)
echo ? 后端检查通过
echo.

echo [2/2] 前端检查（构建）...
cd frontend
call npm run build
if errorlevel 1 (
    echo.
    echo ? 前端构建失败
    cd ..
    pause
    exit /b 1
)
cd ..
echo.

echo ========================================
echo   ? 所有检查通过！
echo ========================================
echo.
pause
