# Changelog

本项目变更记录遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范。

## [Unreleased]

### Added
- 添加项目全景观览仪表盘（project_overview）
- 添加开源必备文件（LICENSE、CONTRIBUTING.md、CHANGELOG.md）

## [1.0.0] - 2024-01-20

### Added
- 基于 Playwright + FastAPI + Vue3 的浏览器会话录制核心功能
- 用户交互事件捕获（click、input、navigation 等）
- 网络请求/响应监控，支持 `all` / `minimal` 两种采集模式
- 可选截图功能（按事件触发）
- WebSocket 实时事件流推送
- 纯文件系统存储（`backend/runs/<run_id>/session.json`）
- Profiles 保存规范系统（`backend/config/profiles/*.yaml`）
- 会话管理 API（CRUD、分页、筛选、批量删除、标签、导出）
- 测试脚本自动生成（Playwright / Selenium）
- Vue3 前端：会话列表、详情、设置、验证页面
- Windows 一键脚本（`build.bat` / `start.bat` / `stop.bat`）
- 完整文档体系（安装、架构、配置、使用、API、故障排查）
