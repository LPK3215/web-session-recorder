# Web Session Recorder

一个基于 **Playwright + FastAPI + Vue3** 的浏览器会话录制工具：
- 录制用户交互事件、网络请求、可选截图
- 实时 WebSocket 推送到前端
- 纯 JSON / 文件系统存储，便于频繁查看与备份

## 快速开始（Windows）

```bat
build.bat
start.bat
```

访问：`http://localhost:5173`

停止服务：`stop.bat`

## 核心概念

### 纯文件存储（runs）

- 会话数据存储在：`backend/runs/<run_id>/session.json`
- 截图/网络落盘文件也在同一目录下
- 后端把 `backend/runs/` 挂载到 `/runs`，可直接访问：
  - `http://127.0.0.1:8000/runs/<run_id>/screenshots/event_1.png`

### 保存规范（Profiles）

- 所有可选 profile 文件都放在：`backend/config/profiles/`
- profile 名称 = 文件名（不含扩展名）
- 录制前在前端选择 profile，用于控制：
  - 预设起始 URL / 窗口大小
  - 网络采集模式（all/minimal）与过滤规则
  - session.json 最终保存哪些字段

## 常用脚本

- `build.bat`：检查环境 → 必要时安装依赖 → 后端检查 + 前端构建
- `start.bat`：启动前后端（新窗口）
- `stop.bat`：停止服务
- `backend\\scripts\\test.bat`：后端 smoke 检查 + 前端 build
- `backend\\scripts\\manage_sessions.py`：管理 `backend/runs/`（查看/清理/导出）

## 项目结构

```
web-session-recorder/
├── backend/
│   ├── app/                 # FastAPI 应用
│   ├── config/              # YAML 配置（含 profiles）
│   ├── runs/                # 录制数据（session.json/截图/网络）
│   ├── scripts/             # 脚本 + injector.js
│   └── run.py               # 后端启动
├── frontend/
│   └── src/                 # Vue3 前端
├── docs/                    # 文档
├── build.bat
├── start.bat
└── stop.bat
```

## 文档

入口：`docs/README.md`

