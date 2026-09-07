# Web Session Recorder

> 基于 **Playwright + FastAPI + Vue3** 的浏览器会话录制工具，支持用户交互事件捕获、网络请求监控、可选截图，并通过 WebSocket 实时推送到前端。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-42b883.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)

## 核心能力

- 🎬 **会话录制**：自动启动浏览器并注入捕获脚本，记录用户交互事件（click、input、navigation 等）
- 🌐 **网络监控**：支持 `all` / `minimal` 两种网络采集模式，请求/响应体可落盘
- 📸 **可选截图**：按事件触发截图（navigation、click 等），质量可配置
- ⚡ **实时推送**：WebSocket 实时事件流，前端即时展示
- 💾 **纯文件存储**：JSON + 文件系统存储，便于频繁查看与备份
- 📋 **保存规范（Profiles）**：通过 YAML 配置档控制录制行为，支持预设 URL / 窗口大小 / 网络过滤
- 🧪 **测试脚本生成**：从录制会话自动生成 Playwright / Selenium 测试脚本
- 🏷️ **会话管理**：分页列表、筛选、标签、批量删除、JSON 导出

## 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| 后端框架 | FastAPI | 0.109.0 |
| 浏览器自动化 | Playwright | 1.41.0 |
| WebSocket | websockets | 12.0 |
| 前端框架 | Vue 3 | 3.4+ |
| UI 组件库 | Element Plus | 2.5+ |
| 前端构建 | Vite | 5.0+ |
| HTTP 客户端 | Axios | 1.6+ |
| 状态管理 | Pinia | 2.1+ |
| 配置管理 | PyYAML | 6.0.1 |

## 项目结构

```
web-session-recorder/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── api/
│   │   │   ├── sessions.py      # 会话 CRUD API
│   │   │   ├── websocket.py     # WebSocket 实时推送
│   │   │   ├── profiles.py      # Profile 管理
│   │   │   ├── config.py        # 配置 API
│   │   │   ├── schemas.py       # Pydantic 模型
│   │   │   └── middleware.py    # 异常处理
│   │   └── core/
│   │       ├── session_manager.py    # 会话生命周期
│   │       ├── browser.py            # Playwright 浏览器管理
│   │       ├── event_capturer.py     # 事件捕获
│   │       ├── network_monitor.py    # 网络监控
│   │       ├── storage_manager.py    # 文件存储
│   │       ├── profile_manager.py    # Profile 合并
│   │       └── locators.py          # 元素定位器生成
│   ├── config/
│   │   ├── app.yaml             # 应用配置
│   │   ├── browser.yaml         # 浏览器配置
│   │   ├── recorder.yaml        # 录制基座配置
│   │   ├── locators.yaml        # 定位器策略
│   │   └── profiles/            # 保存规范
│   │       ├── default.yaml
│   │       └── mbx_minimal.yaml
│   ├── scripts/
│   │   ├── injector.js          # 页面注入捕获脚本
│   │   ├── manage_sessions.py   # 会话管理工具
│   │   ├── smoke_test.py        # 冒烟测试
│   │   ├── setup.bat            # 环境初始化
│   │   ├── test.bat             # 测试脚本
│   │   └── deploy.bat            # 部署脚本
│   ├── runs/                    # 录制数据（gitignore）
│   ├── requirements.txt
│   └── run.py                   # 后端启动
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── api/                 # API 封装
│   │   ├── composables/         # 组合式函数
│   │   ├── router/
│   │   └── views/               # 页面组件
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── docs/                        # 完整文档
│   ├── README.md
│   ├── architecture.md
│   ├── installation.md
│   ├── usage.md
│   ├── configuration.md
│   ├── api.md
│   ├── data-storage.md
│   ├── development.md
│   ├── scripts.md
│   ├── troubleshooting.md
│   └── recording-process-analysis.md
├── build.bat                    # 构建脚本
├── start.bat                    # 启动脚本
├── stop.bat                     # 停止脚本
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md
```

## 快速开始（Windows）

### 前置要求

- Python 3.9+
- Node.js 18+
- Playwright 浏览器（运行 `playwright install` 安装）

### 安装与运行

```bat
:: 构建项目（检查环境、安装依赖、构建前端）
build.bat

:: 启动前后端服务
start.bat
```

前端访问：`http://localhost:5173`
后端 API：`http://localhost:8000`

```bat
:: 停止服务
stop.bat
```

### 手动启动（开发模式）

```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install
python run.py

# 前端（另一个终端）
cd frontend
npm install
npm run dev
```

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

| 脚本 | 用途 |
|---|---|
| `build.bat` | 检查环境 → 安装依赖 → 后端检查 + 前端构建 |
| `start.bat` | 启动前后端（新窗口） |
| `stop.bat` | 停止服务 |
| `backend\scripts\test.bat` | 后端 smoke 检查 + 前端 build |
| `backend\scripts\manage_sessions.py` | 管理 `backend/runs/`（查看/清理/导出） |

## API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/sessions/start` | 启动录制会话 |
| POST | `/api/sessions/{id}/stop` | 停止录制 |
| GET | `/api/sessions` | 会话列表（分页/筛选） |
| GET | `/api/sessions/{id}` | 会话详情 |
| GET | `/api/sessions/{id}/events` | 事件列表（分页） |
| GET | `/api/sessions/{id}/export` | 导出 JSON |
| DELETE | `/api/sessions/{id}` | 删除会话 |
| POST | `/api/sessions/batch-delete` | 批量删除 |
| PATCH | `/api/sessions/{id}` | 更新会话元数据 |
| GET | `/api/sessions/{id}/generate-script` | 生成测试脚本 |
| WS | `/ws/sessions/{id}` | WebSocket 实时事件流 |
| GET | `/api/config/presets` | 获取预设配置 |
| GET | `/api/profiles` | 获取 Profile 列表 |
| GET | `/health` | 健康检查 |

## 文档

入口：[`docs/README.md`](docs/README.md)

| 文档 | 说明 |
|---|---|
| [安装指南](docs/installation.md) | 环境准备与安装步骤 |
| [架构设计](docs/architecture.md) | 技术架构与模块说明 |
| [使用指南](docs/usage.md) | 录制流程与操作说明 |
| [配置说明](docs/configuration.md) | YAML 配置详解 |
| [API 文档](docs/api.md) | REST API 接口说明 |
| [数据存储](docs/data-storage.md) | session.json 结构说明 |
| [开发指南](docs/development.md) | 开发环境与扩展 |
| [脚本工具](docs/scripts.md) | 辅助脚本说明 |
| [故障排查](docs/troubleshooting.md) | 常见问题与解决 |

## 贡献

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程。

## 许可证

[MIT License](LICENSE) © 2024-2026 LPK3215
