@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 停止服务
echo ========================================
echo.

echo 正在停止后端服务...
taskkill /FI "WINDOWTITLE eq Web Session Recorder - Backend*" /F >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未找到运行中的后端服务
) else (
    echo ✅ 后端服务已停止
)

echo.
echo 正在停止前端服务...
taskkill /FI "WINDOWTITLE eq Web Session Recorder - Frontend*" /F >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未找到运行中的前端服务
) else (
    echo ✅ 前端服务已停止
)

echo.
echo 正在停止相关 Python 进程...
tasklist | findstr "python.exe" >nul
if not errorlevel 1 (
    echo 发现 Python 进程，是否全部停止? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        taskkill /IM python.exe /F >nul 2>&1
        echo ✅ Python 进程已停止
    )
)

echo.
echo 正在停止相关 Node 进程...
tasklist | findstr "node.exe" >nul
if not errorlevel 1 (
    echo 发现 Node 进程，是否全部停止? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        taskkill /IM node.exe /F >nul 2>&1
        echo ✅ Node 进程已停止
    )
)

echo.
echo ========================================
echo   ✅ 服务已停止
echo ========================================
echo.
pause
