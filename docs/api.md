# API 文档

## REST API 端点

### 会话管理

#### POST /api/sessions/start - 开始录制

**请求**：
```json
{
  "url": "https://example.com",  // 可选
  "browser": "chrome",            // chrome/edge/firefox
  "incognito": false,             // 是否隐身模式
  "user_data_dir": null           // 用户数据目录（可选）
}
```

**响应**：
```json
{
  "session_id": 1,
  "run_id": "session_20260120_031711_e8c876ae",
  "status": "started"
}
```

#### POST /api/sessions/{id}/stop - 停止录制

**响应**：
```json
{
  "session_id": 1,
  "run_id": "session_20260120_031711_e8c876ae",
  "status": "stopped",
  "event_count": 42
}
```

#### GET /api/sessions - 获取会话列表

**查询参数**：
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）
- `status`: 状态筛选（started/stopped/error）
- `browser_type`: 浏览器筛选（chrome/edge/firefox）

#### GET /api/sessions/{id} - 获取会话详情

**响应**：
```json
{
  "id": 1,
  "run_id": "session_20260120_031711_e8c876ae",
  "start_url": "https://example.com",
  "start_time": "2026-01-20T03:17:11",
  "end_time": "2026-01-20T03:20:30",
  "status": "stopped",
  "browser_type": "chrome",
  "incognito": false,
  "event_count": 42
}
```

#### GET /api/sessions/{id}/events - 获取会话事件

**查询参数**：
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 100）

### 配置管理

#### GET /api/config - 获取所有配置

**响应**：
```json
{
  "app": { /* app.yaml 内容 */ },
  "browser": { /* browser.yaml 内容 */ },
  "recorder": { /* recorder.yaml 内容 */ },
  "database": { /* database.yaml 内容 */ },
  "locators": { /* locators.yaml 内容 */ }
}
```

#### PUT /api/config - 更新配置

**请求**：
```json
{
  "file": "recorder",  // app/browser/recorder/database/locators
  "content": "privacy_mode: partial\n..."  // YAML 内容
}
```

**响应**：
```json
{
  "status": "success",
  "message": "Configuration updated successfully"
}
```

## WebSocket 端点

### WS /ws/sessions/{id} - 实时事件流

连接后会实时接收事件：

```json
{
  "id": 1,
  "session_id": 1,
  "seq": 1,
  "timestamp": "2026-01-20T03:17:15",
  "event_type": "click",
  "page_url": "https://example.com",
  "page_title": "Example Domain",
  "target_data": {
    "tag": "button",
    "id": "submit-btn",
    "text": "Submit"
  },
  "locators": [
    {
      "strategy": "role",
      "selector": "getByRole('button', { name: 'Submit' })"
    },
    {
      "strategy": "testid",
      "selector": "getByTestId('submit-btn')"
    }
  ],
  "network_data": null,
  "raw_data": { /* 原始事件数据 */ }
}
```

## 健康检查

### GET /health - 健康检查

```json
{
  "status": "healthy"
}
```

### GET / - API 信息

```json
{
  "name": "Web Session Recorder",
  "version": "1.0.0",
  "status": "running"
}
```

## Swagger 文档

启动后端后访问：`http://127.0.0.1:8000/docs`

可以在 Swagger UI 中测试所有 API 端点。
