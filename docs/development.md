# 开发指南

## 本地启动

```bash
cd backend
python run.py
```

```bash
cd frontend
npm run dev
```

## 快速检查（推荐）

项目当前不依赖 pytest 测试集，使用“smoke 检查”验证基本可用性：

```bash
backend\\scripts\\test.bat
```

它会做两件事：
- 后端：导入 + FastAPI TestClient 请求关键接口（不需要启动服务）
- 前端：`npm run build`

## 常见开发点

### 新增/调整保存规范（Profiles）

- 在 `backend/config/profiles/` 新建或修改 `*.yaml`
- 前端录制前选择该 profile
- 重点可调字段：
  - `recorder.default_urls` / `recorder.window_sizes`
  - `recorder.network.*`（特别是 `capture_mode` / `include_url_patterns`）
  - `recorder.storage.*`（决定 session.json 保存哪些字段）

### 新增事件类型

- `backend/scripts/injector.js`：前端注入脚本采集事件
- `backend/app/core/event_capturer.py`：后端落库/落盘结构
- `backend/config/recorder.yaml`：配置截图等策略

### 网络采集最小化

- 通过 profile 设置：
  - `recorder.network.capture_mode: minimal`
  - `recorder.network.include_url_patterns: [...]`

**最后更新**：2026-01-20
