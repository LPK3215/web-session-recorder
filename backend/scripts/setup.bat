@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 安装依赖
echo ========================================
echo.

REM 返回项目根目录
cd ..\..

echo [1/4] 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

echo ✅ Python 和 Node.js 已安装
echo.

echo [2/4] 安装后端依赖...
cd backend
echo 正在安装 Python 依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 后端依赖安装失败
    cd ..
    pause
    exit /b 1
)

echo 正在安装 Playwright 浏览器...
playwright install
if errorlevel 1 (
    echo ❌ Playwright 浏览器安装失败
    cd ..
    pause
    exit /b 1
)

echo ✅ 后端依赖安装完成
cd ..
echo.

echo [3/4] 安装前端依赖...
cd frontend
echo 正在安装 Node.js 依赖...
call npm install
if errorlevel 1 (
    echo ❌ 前端依赖安装失败
    cd ..
    pause
    exit /b 1
)

echo ✅ 前端依赖安装完成
cd ..
echo.

echo [4/4] 验证安装...
echo 检查后端配置文件...
if not exist "backend\config\app.yaml" (
    echo ❌ 错误: 后端配置文件不存在
    pause
    exit /b 1
)

echo 检查会话存储目录...
if not exist "backend\runs" (
    mkdir backend\runs
    echo ✅ 创建 runs 目录
)

echo.
echo ========================================
echo   ✅ 安装完成！
echo ========================================
echo.
echo 下一步:
echo   1. 运行 build.bat 构建和测试
echo   2. 或运行 start.bat 启动项目
echo.
pause
