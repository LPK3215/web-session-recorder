# API 文档

后端默认地址：`http://127.0.0.1:8000`

## REST API

### Profiles（保存规范）

#### GET /api/profiles

返回可选的 profile 列表（来自 `backend/config/profiles/*.yaml`）：
```json
[
  { "name": "default", "description": "通用全量录制（默认）", "source": "backend/config/profiles/default.yaml" }
]
```

### 配置

#### GET /api/config

返回加载后的配置（app/browser/recorder/locators）。

#### GET /api/config/presets?profile=<name>

返回“起始 URL / 窗口大小”预设，且会随 profile 变化。

### 会话

#### POST /api/sessions/start

请求：
```json
{
  "url": "",
  "browser": "chrome",
  "incognito": false,
  "user_data_dir": null,
  "window_width": 1280,
  "window_height": 720,
  "profile": "default"
}
```

响应（`session_id` 与 `run_id` 相同）：
```json
{
  "session_id": "session_20260120_031711_e8c876ae",
  "run_id": "session_20260120_031711_e8c876ae",
  "status": "started"
}
```

#### POST /api/sessions/{run_id}/stop

停止采集并保存（不会主动关闭浏览器）。

#### GET /api/sessions

获取会话列表（支持分页与筛选）。

#### GET /api/sessions/{run_id}

获取单个会话元数据。

#### GET /api/sessions/{run_id}/events

获取事件列表（事件中的 `screenshot_path` 会被转换为可直接访问的 URL：`/runs/<run_id>/...`）。

#### GET /api/sessions/{run_id}/export

导出 `session.json`（原始保存内容）。

## WebSocket

### WS /ws/sessions/{run_id}

实时事件流（用于首页“实时事件”表格）。

## 健康检查

### GET /health

```json
{ "status": "healthy" }
```

**最后更新**：2026-01-20
