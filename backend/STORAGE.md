# 存储架构说明

## 概述

本系统使用**纯文件系统存储**，不依赖任何数据库。所有会话数据都保存在文件夹中，便于管理、备份和迁移。

## 存储结构

```
backend/
└── runs/
    ├── session_20260120_103000_abc123/
    │   ├── session.json          # 会话元数据和所有事件
    │   ├── screenshots/           # 截图文件
    │   │   ├── event_1.png
    │   │   ├── event_2.png
    │   │   └── ...
    │   └── network/               # 网络请求/响应体
    │       ├── request_xxx_body.txt
    │       └── ...
    ├── session_20260120_104500_def456/
    │   └── ...
    └── ...
```

## session.json 格式

每个会话文件夹包含一个 `session.json` 文件，包含完整的会话信息：

```json
{
  "session": {
    "run_id": "session_20260120_103000_abc123",
    "start_url": "https://example.com",
    "start_time": "2026-01-20T10:30:00",
    "end_time": "2026-01-20T10:35:00",
    "status": "stopped",
    "browser_type": "chrome",
    "incognito": false,
    "event_count": 15,
    "user_data_dir": null
  },
  "events": [
    {
      "seq": 1,
      "timestamp": "2026-01-20T10:30:05",
      "event_type": "click",
      "page_url": "https://example.com",
      "page_title": "Example Page",
      "target_data": {...},
      "locators": [...],
      "network_data": {...},
      "screenshot_path": "screenshots/event_1.png"
    },
    ...
  ],
  "metadata": {
    "total_events": 15,
    "saved_time": "2026-01-20T10:35:00"
  }
}
```

## 优势

### 1. 简单直观
- 无需数据库安装和配置
- 数据以人类可读的 JSON 格式存储
- 文件夹结构清晰，易于理解

### 2. 易于备份
- 直接复制 `runs/` 文件夹即可备份所有数据
- 支持增量备份
- 可以使用任何文件同步工具（如 Dropbox、OneDrive）

### 3. 便于迁移
- 无需导出/导入数据库
- 直接移动文件夹到新环境
- 跨平台兼容（Windows、Linux、macOS）

### 4. 独立性强
- 每个会话完全独立
- 删除会话只需删除对应文件夹
- 不会影响其他会话

### 5. 易于调试
- 可以直接打开 JSON 文件查看数据
- 可以手动编辑数据（如果需要）
- 截图和网络数据直接可访问

## 管理工具

使用 `manage_sessions.py` 脚本管理会话：

```bash
# 交互式菜单
python backend/scripts/manage_sessions.py
```

功能：
- 查看所有会话列表
- 查看会话详细信息
- 删除指定天数前的会话
- 删除所有会话
- 显示文件夹大小

## API 说明

### 会话标识

系统使用 `run_id` 作为会话的唯一标识符，格式为：
```
session_YYYYMMDD_HHMMSS_<8位随机字符>
```

例如：`session_20260120_103000_abc123`

### API 端点

所有 API 端点都使用 `run_id` 而不是数字 ID：

- `POST /api/sessions/start` - 开始录制
- `POST /api/sessions/{run_id}/stop` - 停止录制
- `GET /api/sessions` - 列出所有会话
- `GET /api/sessions/{run_id}` - 获取会话详情
- `GET /api/sessions/{run_id}/events` - 获取会话事件
- `GET /api/sessions/{run_id}/export` - 导出会话 JSON

### WebSocket

WebSocket 端点也使用 `run_id`：
```
ws://localhost:8000/ws/sessions/{run_id}
```

## 性能考虑

### 读取性能
- 会话列表：扫描文件夹名称（O(n)）
- 会话详情：读取单个 JSON 文件（O(1)）
- 事件列表：从 JSON 文件中提取（O(1)）

### 写入性能
- 录制期间：事件存储在内存中
- 停止录制：一次性写入 JSON 文件
- 截图：实时写入文件系统

### 扩展性
- 适合中小规模使用（< 10000 个会话）
- 如果会话数量过多，建议定期归档旧数据
- 可以按日期组织文件夹结构（如需要）

## 数据清理

定期清理旧数据以释放磁盘空间：

```bash
# 使用管理脚本
python backend/scripts/manage_sessions.py

# 选择选项 3 或 4 删除旧会话
```

建议：
- 每月清理 30 天前的数据
- 重要会话可以导出备份
- 监控 `runs/` 文件夹大小

## 迁移说明

### 从旧版本（数据库版本）迁移

如果你之前使用的是数据库版本，数据已经自动保存在 `runs/` 文件夹中的 `session.json` 文件里。

旧的数据库文件（`database/recorder.db`）已被删除，但所有数据都已保存在文件系统中。

### 备份数据

```bash
# 备份所有会话
xcopy backend\runs backup\runs /E /I

# 或使用 robocopy（Windows）
robocopy backend\runs backup\runs /E

# Linux/macOS
cp -r backend/runs backup/runs
```

### 恢复数据

```bash
# 恢复会话
xcopy backup\runs backend\runs /E /I
```

## 故障排除

### 会话列表为空
- 检查 `backend/runs/` 文件夹是否存在
- 检查文件夹权限
- 查看日志文件

### 无法读取会话
- 检查 `session.json` 文件是否存在
- 验证 JSON 格式是否正确
- 检查文件编码（应为 UTF-8）

### 磁盘空间不足
- 运行管理脚本清理旧数据
- 导出重要会话后删除
- 考虑增加磁盘空间或使用外部存储

## 最佳实践

1. **定期备份**：每周备份 `runs/` 文件夹
2. **定期清理**：每月清理旧数据
3. **监控空间**：关注磁盘使用情况
4. **导出重要数据**：将关键会话导出为 JSON
5. **使用版本控制**：不要将 `runs/` 文件夹加入 Git（已在 .gitignore 中）
