@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Git 快速推送脚本（简化版）
echo ========================================
echo.

REM 设置代理（如果需要）
git config --local http.proxy http://127.0.0.1:7897
git config --local https.proxy http://127.0.0.1:7897

REM 初始化仓库（如果还没有）
if not exist ".git" (
    echo 初始化 Git 仓库...
    git init
    echo.
)

REM 创建 README.md（如果还没有）
if not exist "README.md" (
    echo # web-session-recorder > README.md
    echo 已创建 README.md
    echo.
)

REM 添加所有文件
echo 添加文件...
git add .

REM 提交
echo 提交更改...
git commit -m "first commit"

REM 设置主分支为 main
echo 设置主分支...
git branch -M main

REM 添加远程仓库（如果还没有）
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 添加远程仓库...
    git remote add origin https://github.com/LPK3215/web-session-recorder.git
)

REM 推送
echo 推送到 GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo 可能原因：
    echo 1. 网络问题（检查代理设置）
    echo 2. 仓库不存在（需要先在 GitHub 创建）
    echo 3. 没有权限（检查 SSH 密钥或访问令牌）
    echo.
) else (
    echo.
    echo [成功] 推送完成！
    echo.
)

pause
