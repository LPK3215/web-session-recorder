# Web Session Recorder

<div align="center">

一个功能强大的浏览器会话录制工具，可以捕获和记录所有浏览器交互、网络请求和用户操作。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [文档](#-文档) • [技术栈](#-技术栈) • [贡献](#-贡献)

</div>

---

## ✨ 功能特性

### 🎯 核心功能

- **多浏览器支持** - Chrome、Edge、Firefox
- **全面事件捕获** - DOM 事件、导航、对话框、下载、iframe
- **智能元素定位** - 自动生成 7 种定位策略（Role、Label、TestID、CSS、XPath 等）
- **网络监控** - 捕获所有 HTTP/HTTPS 请求和响应
- **实时流式传输** - WebSocket 实时推送事件到前端
- **隐私保护** - 三级数据脱敏（none/partial/strict）
- **可选截图** - 为特定事件类型自动截图
- **配置驱动** - 所有行为通过 YAML 文件配置

### 🎨 用户界面

- **录制控制台** - 启动/停止录制，实时事件计数
- **会话列表** - 查看所有录制会话，支持排序、筛选、批量操作
- **会话详情** - 事件时间线、定位器、网络数据
- **会话验证** - 检测并清理损坏的会话数据
- **数据预览** - 在线预览完整的 session.json 数据
- **批量管理** - 批量删除、标签管理
- **统计面板** - 会话统计和数据可视化
- **脚本生成** - 自动生成 Playwright/Selenium 测试脚本
- **在线配置** - 通过 Web 界面编辑配置文件

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- npm 或 yarn

### 方式一：使用自动化脚本（推荐）

```bash
# 构建一体化 - 智能检测并构建测试
build.bat

# 启动一体化 - 自动启动前后端
start.bat

# 停止一体化 - 停止所有服务
stop.bat
```

### 方式二：手动安装

```bash
# 克隆项目
git clone <repository-url>
cd web-session-recorder

# 安装后端依赖
cd backend
pip install -r requirements.txt
playwright install

# 安装前端依赖
cd ../frontend
npm install
```

### 启动

```bash
# 使用脚本启动（推荐）
start.bat

# 或手动启动
# 终端 1 - 启动后端
cd backend
python run.py

# 终端 2 - 启动前端
cd frontend
npm run dev
```

访问 `http://localhost:5173` 开始使用！

---

## 📖 文档

完整文档请查看 [docs](docs/) 目录：

- **[安装配置](docs/installation.md)** - 详细的安装和配置步骤
- **[使用指南](docs/usage.md)** - 基本使用流程和界面说明
- **[API 文档](docs/api.md)** - REST API 和 WebSocket 端点
- **[配置说明](docs/configuration.md)** - 所有配置选项的详细说明
- **[技术架构](docs/architecture.md)** - 系统架构和技术栈
- **[开发指南](docs/development.md)** - 代码规范、测试、添加新功能
- **[常见问题](docs/troubleshooting.md)** - 问题排查和性能优化

---

## 🏗️ 技术栈

### 后端
- **FastAPI** - 现代 Python Web 框架
- **Playwright** - 浏览器自动化
- **文件存储** - 基于文件系统的会话数据存储
- **WebSockets** - 实时通信
- **YAML** - 配置管理

### 前端
- **Vue 3** - 渐进式 JavaScript 框架（Composition API）
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 UI 组件库
- **Axios** - HTTP 客户端
- **Composables** - 可复用的业务逻辑层

---

## 📁 项目结构

```
web-session-recorder/
├── backend/                # Python FastAPI 后端
│   ├── app/               # 应用代码
│   │   ├── api/          # REST API 端点
│   │   ├── core/         # 核心业务逻辑
│   │   └── models/       # 数据模型
│   ├── config/            # YAML 配置文件
│   ├── runs/              # 会话数据存储（文件系统）
│   └── run.py             # 启动脚本
├── frontend/              # Vue 3 前端
│   ├── src/               # 源代码
│   │   ├── api/          # API 客户端
│   │   ├── composables/  # 可复用业务逻辑
│   │   ├── components/   # Vue 组件
│   │   ├── views/        # 页面视图
│   │   └── router/       # 路由配置
│   └── package.json
└── README.md              # 本文档
```

---

## 🎯 使用场景

- **自动化测试** - 录制用户操作生成测试脚本
- **Bug 复现** - 记录完整的操作步骤和网络请求
- **用户行为分析** - 分析用户交互模式
- **性能监控** - 监控页面加载和网络请求
- **开发调试** - 记录开发过程中的操作

---

## 🧪 开发与测试

```bash
# 前端开发
cd frontend
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览生产构建

# 后端开发
cd backend
python run.py        # 启动开发服务器
```

**代码质量**
- ✅ 前端构建成功验证
- ✅ 代码重构完成（减少 ~290 行重复代码）
- ✅ 使用 Composables 模式提升可维护性
- ✅ DRY 原则应用（代码重复率从 40% 降至 5%）

## 🛠️ 自动化脚本

### 核心脚本（根目录）

| 脚本 | 说明 |
|------|------|
| `build.bat` | **构建一体化** - 智能检测、构建、测试一条龙 |
| `start.bat` | **启动一体化** - 自动启动前后端服务 |
| `stop.bat` | **停止一体化** - 停止所有运行的服务 |

### 辅助脚本（backend/scripts/）

| 脚本 | 说明 |
|------|------|
| `setup.bat` | 安装依赖 - 安装所有依赖 |
| `test.bat` | 运行测试 - 执行所有测试 |
| `deploy.bat` | 部署构建 - 构建生产版本 |
| `clean.bat` | 清理项目 - 删除依赖和缓存 |

### 使用示例

```bash
# 首次使用（推荐）
build.bat          # 构建一体化

# 日常开发
start.bat          # 启动服务
stop.bat           # 停止服务

# 其他操作
backend\scripts\test.bat     # 单独运行测试
backend\scripts\deploy.bat   # 构建部署包
backend\scripts\clean.bat    # 清理项目
```

详细说明请查看 [脚本文档](docs/scripts.md)。

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

详细信息请查看 [开发指南](docs/development.md)。

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🌟 项目状态

- ✅ 核心功能完成
- ✅ 前端界面完成（4个主要页面）
- ✅ 后端 API 完成（完整 REST API）
- ✅ 高级功能（批量操作、验证、统计、脚本生成）
- ✅ 代码重构完成（Composables 架构）
- ✅ 前端构建验证通过
- ✅ 生产就绪

**最近更新**
- 🎯 代码重构：减少 290 行重复代码
- 🏗️ 架构优化：引入 Composables 模式
- 🧹 清理遗留：移除数据库相关文件
- ✨ 功能增强：批量操作、会话验证、统计面板

---

## 📞 支持

- 📖 [文档](docs/)
- 🐛 [问题反馈](../../issues)
- 💬 [讨论区](../../discussions)

---

<div align="center">

**开始使用**：访问 http://localhost:5173 开始录制你的第一个会话！🚀

Made with ❤️ by [Your Name]

</div>
