# 安装配置指南

## 前置要求

- Python 3.10+
- Node.js 16+
- npm

本项目使用 **纯 JSON / 文件系统存储**，不需要安装数据库。

## 安装步骤

### 1) 克隆项目

```bash
git clone <repository-url>
cd web-session-recorder
```

### 2) 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
playwright install
```

后端主要依赖：
- `fastapi` / `uvicorn`：Web 服务
- `playwright`：浏览器自动化
- `pyyaml`：配置文件解析
- `websockets`：实时推送

### 3) 安装前端依赖

```bash
cd frontend
npm install
```

## 启动项目

### 方式一：脚本（推荐）

```bash
build.bat
start.bat
```

### 方式二：手动启动

终端 1（后端）：
```bash
cd backend
python run.py
```

终端 2（前端）：
```bash
cd frontend
npm run dev
```

访问：`http://localhost:5173`

## 配置文件位置

所有配置在 `backend/config/`：

- `backend/config/app.yaml`：服务端口/CORS/日志
- `backend/config/browser.yaml`：浏览器路径与启动参数
- `backend/config/recorder.yaml`：录制器基座配置（事件/截图/网络/预设）
- `backend/config/locators.yaml`：定位器策略

### Profiles（保存规范）

可选 profile 文件都放在 `backend/config/profiles/`，录制前在前端选择。

## 静态文件（截图/落盘资源）

后端会把 `backend/runs/` 作为静态目录挂载到 `/runs`：
- 例如：`http://127.0.0.1:8000/runs/<run_id>/screenshots/event_1.png`

**最后更新**：2026-01-20
