@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 构建一体化
echo ========================================
echo.

REM 返回项目根目录（如果从其它目录启动）
cd /d "%~dp0"

echo [1/3] 运行检查（无需启动服务）...
python backend\scripts\smoke_test.py >nul 2>&1
set BACKEND_SMOKE_RESULT=%errorlevel%
if exist "frontend\\node_modules" (
    pushd frontend
    call npm run build >nul 2>&1
    set FRONTEND_BUILD_RESULT=%errorlevel%
    popd
) else (
    set FRONTEND_BUILD_RESULT=1
)

if %BACKEND_SMOKE_RESULT%==0 if %FRONTEND_BUILD_RESULT%==0 (
    echo ? 后端检查通过
    echo ? 前端构建通过
    echo.
    echo ========================================
    echo   ? 环境正常，无需构建
    echo ========================================
    echo.
    echo 是否立即启动服务? (Y/N)
    set /p start_choice=
    if /i "%start_choice%"=="Y" (
        call start.bat
    ) else (
        echo.
        echo 提示: 运行 start.bat 启动服务
        echo.
        pause
    )
    exit /b 0
)

echo ? 检测到依赖未安装或构建失败，开始安装依赖...
echo.

echo [2/3] 安装依赖...
REM 后端依赖
pushd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ? 后端依赖安装失败
    popd
    pause
    exit /b 1
)
playwright install
if errorlevel 1 (
    echo ? Playwright 浏览器安装失败
    popd
    pause
    exit /b 1
)
if not exist "runs" mkdir runs
popd

REM 前端依赖
pushd frontend
call npm install
if errorlevel 1 (
    echo ? 前端依赖安装失败
    popd
    pause
    exit /b 1
)
popd

echo.
echo [3/3] 重新运行检查...
python backend\scripts\smoke_test.py
if errorlevel 1 (
    echo.
    echo ? 后端检查失败，请查看错误信息
    pause
    exit /b 1
)

pushd frontend
call npm run build
if errorlevel 1 (
    echo.
    echo ? 前端构建失败，请查看错误信息
    popd
    pause
    exit /b 1
)
popd

echo.
echo ========================================
echo   ? 构建和检查全部完成！
echo ========================================
echo.
echo 是否立即启动服务? (Y/N)
set /p start_choice=
if /i "%start_choice%"=="Y" (
    call start.bat
) else (
    echo.
    echo 提示: 运行 start.bat 启动服务
    echo.
    pause
)
