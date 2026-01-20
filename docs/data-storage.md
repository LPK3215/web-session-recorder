# 数据存储说明（纯 JSON / 文件系统）

## 概述

Web Session Recorder 使用**纯文件系统存储**，不使用数据库。每个录制会话对应一个独立文件夹，包含：
- `session.json`：会话元数据 + 全部事件（可读的格式化 JSON）
- `screenshots/`：事件截图（可选）
- `network/`：网络请求/响应体（可选，按配置落盘）

## 存储位置与结构

**位置：** `backend/runs/`

**结构：**
```
backend/runs/
└── session_YYYYMMDD_HHMMSS_xxxxxxxx/
    ├── session.json
    ├── screenshots/
    │   ├── event_1.png
    │   └── ...
    └── network/
        ├── request_..._body.txt
        └── ...
```

## session.json 格式

文件内容由 3 部分组成：
- `session`：会话元数据（`run_id`、起止时间、浏览器类型、事件数量等）
- `events`：按序记录的事件数组（`seq`、`event_type`、`page_url`、定位器、原始数据等）
- `metadata`：保存时间、总事件数等

实际字段以运行时保存为准；该文件是系统的**唯一权威数据源**。

## 导出与备份

- **导出单个会话 JSON**：调用 `GET /api/sessions/{run_id}/export`（前端也提供“预览/导出”）
- **备份全部会话**：直接复制 `backend/runs/` 目录即可

## 清理会话数据

- 推荐使用 `backend/scripts/manage_sessions.py` 进行查看/清理/导出（交互式）
- 也可以直接删除 `backend/runs/<run_id>/` 文件夹来删除某个会话

## 相关文档

- 更详细的存储架构说明：`backend/STORAGE.md`

## 静态访问（截图/资源）

后端会把 `backend/runs/` 挂载到 `/runs`，可直接访问截图等文件：

- `http://127.0.0.1:8000/runs/<run_id>/screenshots/event_1.png`
