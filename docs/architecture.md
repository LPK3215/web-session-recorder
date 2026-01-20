# 技术架构

## 后端架构

```
FastAPI Application
├── API Layer (REST + WebSocket)
│   ├── Session Management
│   ├── Configuration Management
│   └── WebSocket Streaming
├── Core Layer
│   ├── Session Manager (协调器)
│   ├── Browser Controller (Playwright)
│   ├── Event Capturer (事件捕获)
│   ├── Locator Generator (定位器生成)
│   ├── Network Monitor (网络监控)
│   └── Config Manager (配置管理)
└── Data Layer
    ├── SQLAlchemy ORM
    ├── Database Models
    └── CRUD Operations
```

## 前端架构

```
Vue 3 Application
├── Views (页面组件)
│   ├── Home (录制控制台)
│   ├── SessionList (会话列表)
│   ├── SessionDetail (会话详情)
│   └── Settings (配置编辑)
├── API Client
│   ├── Session API
│   ├── Config API
│   └── WebSocket Client
└── Router (Vue Router)
```

## 数据流

```
用户操作
  ↓
浏览器 (Playwright)
  ↓
JavaScript 注入脚本
  ↓
Event Capturer
  ↓
Locator Generator + Network Monitor
  ↓
Session Manager
  ├→ Database (SQLite)
  └→ WebSocket (实时推送)
       ↓
     前端界面
```

## 数据库模型

### sessions 表

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    run_id VARCHAR UNIQUE NOT NULL,
    start_url VARCHAR,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    status VARCHAR NOT NULL,
    browser_type VARCHAR NOT NULL,
    incognito BOOLEAN DEFAULT 0,
    event_count INTEGER DEFAULT 0,
    user_data_dir VARCHAR,
    created_at DATETIME NOT NULL
);
```

### events 表

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    seq INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    page_url VARCHAR(2048) NOT NULL,
    page_title VARCHAR(512),
    target_data JSON,
    locators JSON,
    network_data JSON,
    raw_data JSON NOT NULL,
    screenshot_path VARCHAR(1024),
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_session_seq ON events(session_id, seq);
CREATE INDEX idx_session_timestamp ON events(session_id, timestamp);
CREATE INDEX idx_event_type ON events(event_type);
```

## 技术栈

### 后端
- Python 3.11+
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Pydantic (data validation)
- Playwright (browser automation)
- PyYAML (configuration parsing)
- WebSockets (real-time streaming)

### 前端
- Vue 3 (Composition API)
- Vite (build tool)
- Element Plus (UI components)
- Axios (HTTP client)
- WebSocket API (real-time communication)

### 数据库
- SQLite (embedded database)

### 配置
- YAML files in config/ directory
