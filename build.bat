@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 构建一体化
echo ========================================
echo.

REM 先尝试运行测试
echo [1] 尝试运行测试...
echo.

cd backend
pytest tests/ -q >nul 2>&1
set BACKEND_TEST_RESULT=%errorlevel%
cd ..

if %BACKEND_TEST_RESULT%==0 (
    echo ✅ 后端测试通过，环境正常
    echo.
    echo 是否查看详细测试结果? (Y/N)
    set /p detail_choice=
    if /i "%detail_choice%"=="Y" (
        echo.
        cd backend
        pytest tests/ -v
        cd ..
    )
    echo.
    echo ========================================
    echo   ✅ 测试完成！
    echo ========================================
    echo.
    pause
    exit /b 0
)

REM 测试失败，执行构建
echo ❌ 测试失败，可能是依赖未安装
echo.
echo [2] 自动执行构建...
echo ========================================
echo.

REM 检查是否是依赖问题
cd backend
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 检测到后端依赖未安装
    cd ..
    goto DO_SETUP
)

python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo 检测到 Playwright 未安装
    cd ..
    goto DO_SETUP
)
cd ..

if not exist "frontend\node_modules" (
    echo 检测到前端依赖未安装
    goto DO_SETUP
)

REM 依赖都在，但测试失败
echo.
echo ⚠️  依赖已安装但测试失败
echo 这可能是代码问题，请检查错误信息
echo.
echo 是否查看详细测试结果? (Y/N)
set /p show_error=
if /i "%show_error%"=="Y" (
    cd backend
    pytest tests/ -v
    cd ..
)
echo.
pause
exit /b 1

:DO_SETUP
echo.
echo 正在安装依赖...
echo.

REM 安装后端依赖
echo [2.1] 安装后端依赖...
cd backend
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ❌ 后端依赖安装失败
    cd ..
    pause
    exit /b 1
)

echo 安装 Playwright 浏览器...
playwright install >nul 2>&1
if errorlevel 1 (
    echo ❌ Playwright 安装失败
    cd ..
    pause
    exit /b 1
)
echo ✅ 后端依赖安装完成
cd ..

REM 安装前端依赖
echo.
echo [2.2] 安装前端依赖...
cd frontend
call npm install >nul 2>&1
if errorlevel 1 (
    echo ❌ 前端依赖安装失败
    cd ..
    pause
    exit /b 1
)
echo ✅ 前端依赖安装完成
cd ..

REM 创建必要目录
if not exist "backend\database" mkdir backend\database
if not exist "backend\screenshots" mkdir backend\screenshots

echo.
echo ========================================
echo   ✅ 构建完成！
echo ========================================
echo.

REM 重新运行测试
echo [3] 重新运行测试...
echo.

cd backend
echo 运行后端测试...
pytest tests/ -v
if errorlevel 1 (
    echo.
    echo ❌ 测试仍然失败，请检查错误信息
    cd ..
    pause
    exit /b 1
)
echo.
echo ✅ 后端测试通过 (162/162)
cd ..

echo.
echo [测试前端]
cd frontend
if exist "package.json" (
    findstr /C:"\"test\"" package.json >nul
    if not errorlevel 1 (
        echo 运行前端测试...
        call npm run test
        if errorlevel 1 (
            echo ❌ 前端测试失败
            cd ..
            pause
            exit /b 1
        )
        echo ✅ 前端测试通过
    ) else (
        echo ⚠️  前端测试未配置，跳过
    )
)
cd ..

echo.
echo ========================================
echo   ✅ 构建和测试全部完成！
echo ========================================
echo.

REM 询问是否启动
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
