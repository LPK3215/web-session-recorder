@echo off
chcp 65001 >nul
echo ========================================
echo   Web Session Recorder - 部署构建
echo ========================================
echo.

REM 返回项目根目录
cd ..\..

echo [1/5] 清理旧文件...
if exist "dist" (
    echo 删除旧的 dist 目录...
    rmdir /s /q dist
)
mkdir dist
echo ✅ 清理完成
echo.

echo [2/5] 构建前端...
cd frontend
echo 正在构建前端生产版本...
call npm run build
if errorlevel 1 (
    echo ❌ 前端构建失败
    cd ..
    pause
    exit /b 1
)
echo ✅ 前端构建完成
cd ..
echo.

echo [3/5] 复制前端构建文件...
if exist "frontend\dist" (
    xcopy /E /I /Y frontend\dist dist\frontend >nul
    echo ✅ 前端文件已复制到 dist\frontend
) else (
    echo ❌ 错误: 前端构建目录不存在
    pause
    exit /b 1
)
echo.

echo [4/5] 复制后端文件...
echo 复制后端代码...
xcopy /E /I /Y backend dist\backend >nul

REM 排除不需要的文件
if exist "dist\backend\__pycache__" rmdir /s /q dist\backend\__pycache__
if exist "dist\backend\.pytest_cache" rmdir /s /q dist\backend\.pytest_cache
if exist "dist\backend\tests" rmdir /s /q dist\backend\tests
if exist "dist\backend\docs" rmdir /s /q dist\backend\docs

echo ✅ 后端文件已复制到 dist\backend
echo.

echo [5/5] 创建部署说明...
(
echo # 部署说明
echo.
echo ## 部署步骤
echo.
echo 1. 将 dist 目录上传到服务器
echo 2. 安装 Python 依赖: cd dist/backend ^&^& pip install -r requirements.txt
echo 3. 安装 Playwright: playwright install
echo 4. 配置 backend/config/ 中的 YAML 文件
echo 5. 启动后端: cd dist/backend ^&^& python run.py
echo 6. 配置 Nginx 或其他 Web 服务器指向 dist/frontend
echo.
echo ## 环境要求
echo.
echo - Python 3.10+
echo - Node.js 16+ ^(仅构建时需要^)
echo - Playwright 浏览器
echo.
echo ## 配置文件
echo.
echo 修改 dist/backend/config/ 中的配置文件:
echo - app.yaml: 服务器地址和端口
echo - browser.yaml: 浏览器路径
echo - recorder.yaml: 录制配置
echo.
echo ## 生产环境建议
echo.
echo 1. 使用 gunicorn 或 uvicorn 运行后端
echo 2. 使用 Nginx 作为反向代理
echo 3. 配置 HTTPS
echo 4. 设置会话数据备份 ^(runs/^)
echo 5. 配置日志轮转
echo.
) > dist\DEPLOY.md

echo ✅ 部署说明已创建: dist\DEPLOY.md
echo.

echo ========================================
echo   ✅ 部署包构建完成！
echo ========================================
echo.
echo 部署文件位置: dist\
echo 部署说明: dist\DEPLOY.md
echo.
echo 目录结构:
echo   dist\
echo   ├── frontend\     (前端静态文件)
echo   └── backend\      (后端 Python 代码)
echo.
pause
