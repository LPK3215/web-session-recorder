# 技术架构

本项目由 **FastAPI + Playwright 后端** 与 **Vue3 前端** 组成，核心目标是“录制浏览器会话并落盘为可直接查看的 JSON + 资源文件”。

## 总览

- 后端：负责启动浏览器、捕获事件/网络、保存到 `backend/runs/`，并通过 WebSocket 实时推送
- 前端：负责选择录制参数（浏览器/隐身/用户数据目录/窗口/保存规范 profile）、展示实时事件、会话列表与详情

## 数据与文件（纯文件系统存储）

- 每个会话对应一个 run 目录：`backend/runs/<run_id>/`
  - `session.json`：会话元数据 + 事件数组（唯一权威数据）
  - `screenshots/`：截图文件（可选）
  - `network/`：网络 body 落盘文件（可选）
- 后端提供静态文件服务：
  - `GET /runs/...` → 映射到 `backend/runs/...`
  - 前端详情页可直接用 `/runs/<run_id>/screenshots/...` 显示图片

## Profiles（保存规范）

- 所有可选配置档都来自：`backend/config/profiles/*.yaml`
  - profile 名称 = 文件名（不含扩展名），例如 `mbx_minimal.yaml` → `mbx_minimal`
- 合并基座：`backend/config/recorder.yaml`（不作为“选项”展示）
- 后端会把 profile 文件覆盖到基座之上，得到“本次录制的 effective recorder config”
- 预设（起始 URL / 窗口大小）也会随 profile 变化：
  - `GET /api/config/presets?profile=<name>`

## 关键模块（后端）

- `backend/app/core/session_manager.py`：会话生命周期、WebSocket 推送、落盘保存、会话列表/筛选
- `backend/app/core/browser.py`：Playwright browser/context 创建（`incognito`/`user_data_dir` 生效）
- `backend/app/core/event_capturer.py`：注入脚本、捕获交互事件、可选截图（路径为 `screenshots/...`）
- `backend/app/core/network_monitor.py`：捕获网络请求/响应；支持 `capture_mode: all|minimal` 与 body 截断/落盘
- `backend/app/core/profile_manager.py`：profiles 列表与配置合并
- `backend/app/core/storage_manager.py`：创建/读取 `runs/<run_id>/session.json`

## 录制流程

1. 前端调用 `POST /api/sessions/start`（携带 `profile`、`url`、`browser`、`incognito`、`user_data_dir`、窗口大小）
2. 后端创建 `run_id` 并创建 `backend/runs/<run_id>/`
3. 启动浏览器并创建 context；导航到起始 URL（空字符串表示空白页）
4. 注入 `backend/scripts/injector.js`，开始捕获；同时 WebSocket 推送实时事件
5. 用户点击“停止录制”：停止采集并保存（不会主动关闭浏览器）
6. 用户关闭浏览器/页面：后端监听到关闭事件后自动停止并保存

## 前端与代理（开发模式）

开发模式下前端通过 Vite 代理访问后端：
- `/api/*` → 后端 API
- `/runs/*` → 后端静态文件（截图/网络落盘文件）

**最后更新**：2026-01-20
