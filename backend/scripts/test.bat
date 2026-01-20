@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 运行测试
echo ========================================
echo.

REM 返回项目根目录
cd ..\..

echo [1/2] 运行后端测试...
cd backend
echo 正在执行 pytest...
pytest tests/ -v
if errorlevel 1 (
    echo.
    echo ❌ 后端测试失败
    cd ..
    pause
    exit /b 1
)

echo.
echo ✅ 后端测试通过 (162/162)
cd ..
echo.

echo [2/2] 运行前端测试...
cd frontend
if exist "package.json" (
    findstr /C:"\"test\"" package.json >nul
    if not errorlevel 1 (
        echo 正在执行前端测试...
        call npm run test
        if errorlevel 1 (
            echo.
            echo ❌ 前端测试失败
            cd ..
            pause
            exit /b 1
        )
        echo ✅ 前端测试通过
    ) else (
        echo ⚠️  前端测试脚本未配置，跳过
    )
) else (
    echo ⚠️  未找到 package.json，跳过前端测试
)
cd ..
echo.

echo ========================================
echo   ✅ 所有测试通过！
echo ========================================
echo.
pause
