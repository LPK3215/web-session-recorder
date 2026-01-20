# 安装配置指南

## 前置要求

- Python 3.10+
- Node.js 16+
- npm 或 yarn

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd web-session-recorder
```

### 2. 后端配置

**安装 Python 依赖**：
```bash
cd backend
pip install -r requirements.txt
```

**安装 Playwright 浏览器**：
```bash
playwright install
```

这将下载 Chromium、Firefox 和 WebKit 浏览器。

**依赖说明**：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `sqlalchemy` - ORM
- `playwright` - 浏览器自动化
- `pyyaml` - YAML 配置解析
- `websockets` - WebSocket 支持
- `pytest` - 测试框架

### 3. 前端配置

**安装 Node.js 依赖**：
```bash
cd frontend
npm install
```

**依赖说明**：
- `vue` - Vue 3 框架
- `vue-router` - 路由管理
- `element-plus` - UI 组件库
- `axios` - HTTP 客户端
- `vite` - 构建工具

### 4. 配置文件

所有配置文件位于 `backend/config/` 目录，使用 YAML 格式。

**backend/config/app.yaml** - 应用配置：
```yaml
app:
  debug: true
  name: Web Session Recorder
  version: 1.0.0

server:
  host: 127.0.0.1
  port: 8000
  reload: false  # Windows 上禁用
  cors_origins:
    - http://localhost:5173
    - http://localhost:3000
```

**backend/config/browser.yaml** - 浏览器配置：
```yaml
browser:
  default: chrome
  launch:
    timeout: 30000
    slow_mo: 0
    args: []
  context:
    viewport:
      width: 1920
      height: 1080
```

**backend/config/recorder.yaml** - 录制配置：
```yaml
recorder:
  privacy_mode: none  # none/partial/strict
  event_types:
    - click
    - input
    - navigation
    - dialog
    - download
  network:
    enabled: true
    capture_body: true
  screenshot:
    enabled: false
    event_types: []
```

## 启动项目

**1. 启动后端服务**（终端 1）：
```bash
cd backend
python run.py
```

后端将运行在：`http://127.0.0.1:8000`

**2. 启动前端服务**（终端 2）：
```bash
cd frontend
npm run dev
```

前端将运行在：`http://localhost:5173`

**3. 访问应用**：

打开浏览器访问 `http://localhost:5173`，开始录制你的第一个会话！

## 验证安装

访问以下 URL 验证安装：
- 后端健康检查：http://127.0.0.1:8000/health
- Swagger API 文档：http://127.0.0.1:8000/docs
- 前端界面：http://localhost:5173
