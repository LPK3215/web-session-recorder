@echo off
REM 清理项目文件和旧数据

cd /d "%~dp0\.."

echo ========================================
echo 清理工具
echo ========================================
echo.
echo 选项:
echo   1. 清理项目文件 (node_modules, __pycache__, etc.)
echo   2. 管理会话数据 (runs/)
echo   3. 退出
echo.

set /p choice="请选择 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 清理项目文件...
    echo.
    
    REM Clean frontend
    if exist "..\frontend\node_modules" (
        echo 删除 frontend\node_modules...
        rmdir /s /q "..\frontend\node_modules"
    )
    
    if exist "..\frontend\dist" (
        echo 删除 frontend\dist...
        rmdir /s /q "..\frontend\dist"
    )
    
    REM Clean backend
    echo 删除 __pycache__ 目录...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
    
    if exist ".pytest_cache" (
        echo 删除 .pytest_cache...
        rmdir /s /q ".pytest_cache"
    )
    
    REM Clean dist
    if exist "..\dist" (
        echo 删除 dist...
        rmdir /s /q "..\dist"
    )
    
    echo.
    echo 清理完成!
    
) else if "%choice%"=="2" (
    echo.
    python scripts/manage_sessions.py
    
) else if "%choice%"=="3" (
    echo 退出
    exit /b 0
    
) else (
    echo 无效选择
    exit /b 1
)

echo.
pause
