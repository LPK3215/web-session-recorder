# 文档目录

欢迎查看 Web Session Recorder 的详细文档。

## 📚 文档列表

### 快速开始
- **[安装配置](installation.md)** - 详细的安装和配置步骤
- **[使用指南](usage.md)** - 基本使用流程和界面说明
- **[自动化脚本](scripts.md)** - 快速构建、启动、测试、部署脚本

### 开发文档
- **[开发指南](development.md)** - 代码规范、测试、添加新功能
- **[技术架构](architecture.md)** - 系统架构和技术栈
- **[API 文档](api.md)** - REST API 和 WebSocket 端点

### 配置和问题
- **[配置说明](configuration.md)** - 所有配置选项的详细说明（包含预设配置）
- **[数据存储](data-storage.md)** - 数据存储位置、会话文件夹结构、导出方法
- **[录制过程分析](recording-process-analysis.md)** - 详细的录制流程、技术实现、文件说明
- **[常见问题](troubleshooting.md)** - 问题排查和性能优化

### 规格说明
- **[需求文档](../.kiro/specs/web-session-recorder/requirements.md)** - 完整的需求规格
- **[设计文档](../.kiro/specs/web-session-recorder/design.md)** - 详细的设计文档
- **[任务列表](../.kiro/specs/web-session-recorder/tasks.md)** - 实施计划和任务

## 🔍 快速查找

### 我想...

**安装和启动项目**
→ [安装配置](installation.md) 或使用 `setup.bat` + `start.bat`

**了解如何使用**
→ [使用指南](usage.md)

**使用自动化脚本**
→ [自动化脚本](scripts.md)

**查看 API 文档**
→ [API 文档](api.md) 或启动后端后访问 http://127.0.0.1:8000/docs

**配置系统**
→ [配置说明](configuration.md)

**查看数据存储**
→ [数据存储](data-storage.md) 或运行 `backend/check_sessions.py`

**了解录制过程**
→ [录制过程分析](recording-process-analysis.md) - 详细的技术实现和文件说明

**解决问题**
→ [常见问题](troubleshooting.md)

**参与开发**
→ [开发指南](development.md)

**了解架构**
→ [技术架构](architecture.md)

## 📖 推荐阅读顺序

### 新用户
1. [自动化脚本](scripts.md) - 了解快速启动方式
2. [安装配置](installation.md) - 安装依赖和配置环境（或直接运行 `setup.bat`）
3. [使用指南](usage.md) - 学习如何使用系统
4. [配置说明](configuration.md) - 自定义配置选项

### 开发者
1. [自动化脚本](scripts.md) - 了解开发工作流程
2. [技术架构](architecture.md) - 了解系统架构
3. [开发指南](development.md) - 学习开发规范
4. [API 文档](api.md) - 查看 API 接口
5. 规格说明（.kiro/specs/）- 查看需求和设计

## 🔗 相关链接

- **项目主页**：[../README.md](../README.md)
- **后端代码**：`../backend/`
- **前端代码**：`../frontend/`
- **测试代码**：`../backend/tests/`

---

**最后更新**：2026-01-20
