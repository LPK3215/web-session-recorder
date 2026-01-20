# 数据存储说明

## 概述

Web Session Recorder 使用**双重存储**策略：数据库存储（实时查询）+ 文件存储（完整备份）。每个录制会话都有独立的文件夹，包含格式化的 JSON、截图和网络数据。

## 存储位置

### 1. 会话文件夹（主要存储）

**位置：** `backend/runs/`

每个会话一个独立文件夹，命名格式：`session_YYYYMMDD_HHMMSS_xxxxxxxx`

**文件夹结构：**
```
backend/runs/
└── session_20260120_143526_e5879545/    # 会话文件夹
    ├── session.json                      # 会话数据和所有事件（格式化 JSON）
    ├── screenshots/                      # 截图文件夹
    │   ├── event_1.png                  # 事件 1 的截图
    │   ├── event_2.png                  # 事件 2 的截图
    │   └── event_3.png                  # 事件 3 的截图
    └── network/                          # 网络数据文件夹
        ├── request_abc123_body.txt      # 请求/响应 body
        └── request_def456_body.txt
```

### 2. 数据库文件（辅助存储）

**位置：** `backend/database/recorder.db`

**内容：**
- 会话（Sessions）记录
- 事件（Events）记录
- 配置（Configs）记录

**用途：** 实时查询、前端展示、数据过滤

## session.json 文件格式

JSON 文件使用 **2 空格缩进**，UTF-8 编码，格式化输出，易于阅读。

### 完整示例

```json
{
  "session": {
    "id": 1,
    "run_id": "session_20260120_143526_e5879545",
    "start_url": "https://www.baidu.com",
    "start_time": "2026-01-20T14:35:26.123456",
    "end_time": "2026-01-20T14:36:45.789012",
    "status": "stopped",
    "browser_type": "chrome",
    "incognito": false,
    "event_count": 5,
    "user_data_dir": null,
    "created_at": "2026-01-20T14:35:25.000000"
  },
  "events": [
    {
      "id": 1,
      "seq": 1,
      "timestamp": "2026-01-20T14:35:30.123456",
      "event_type": "navigation",
      "page_url": "https://www.baidu.com",
      "page_title": "百度一下，你就知道",
      "target_data": null,
      "locators": null,
      "network_data": null,
      "screenshot_path": "screenshots/event_1.png"
    }
  ],
  "metadata": {
    "total_events": 5,
    "saved_time": "2026-01-20T14:36:46.000000"
  }
}
```

## 数据生命周期

### 1. 录制开始
- 创建会话记录（数据库）
- 创建会话文件夹（`runs/session_xxx/`）
- 创建子文件夹（`screenshots/`、`network/`）

### 2. 录制过程中
- 事件实时保存到数据库
- 截图自动保存到 `screenshots/`
- 网络数据保存到 `network/`

### 3. 录制结束
- 更新会话状态（数据库）
- 从数据库导出所有数据
- 生成格式化的 `session.json`
- 保存到会话文件夹

## 截图配置

**配置文件：** `backend/config/recorder.yaml`

```yaml
recorder:
  screenshots:
    enabled: true  # 启用截图
    on_events:     # 在这些事件类型时截图
      - navigation
      - click
      - submit
    quality: 90    # 截图质量 (1-100)
```

**截图说明：**
- 自动截图：在指定事件类型时自动截图
- 文件命名：`event_{序列号}.png`
- 存储位置：会话文件夹的 `screenshots/` 子目录
- 路径记录：截图路径保存在事件的 `screenshot_path` 字段中

## 预设配置

**配置文件：** `backend/config/recorder.yaml`

### 默认网址预设

```yaml
recorder:
  default_urls:
    - name: 百度
      url: https://www.baidu.com
    - name: 淘宝
      url: https://www.taobao.com
    - name: 京东
      url: https://www.jd.com
    - name: GitHub
      url: https://github.com
    - name: 本地开发
      url: http://localhost:3000
    - name: 空白页
      url: ''
```

### 窗口大小预设（长方形）

```yaml
recorder:
  window_sizes:
    - name: 小窗口 (1280×720)
      width: 1280
      height: 720
    - name: 标准 (1440×900)
      width: 1440
      height: 900
    - name: 高清 (1920×1080)
      width: 1920
      height: 1080
    - name: 2K (2560×1440)
      width: 2560
      height: 1440
    - name: 超宽 (1920×1200)
      width: 1920
      height: 1200
    - name: 自定义
      width: 0
      height: 0
```

## 查看数据

### 方法 1：直接查看文件

```bash
# 查看会话文件夹
explorer backend\runs

# 查看 JSON（已格式化，易读）
type backend\runs\session_xxx\session.json

# 查看截图
explorer backend\runs\session_xxx\screenshots
```

### 方法 2：使用检查脚本

```bash
cd backend
python check_sessions.py
```

输出示例：
```
============================================================
会话文件夹检查
============================================================
找到 3 个会话文件夹:

📂 session_20260120_143526_e5879545
   ✅ session.json 存在 (12.45 KB)
      - 会话 ID: 1
      - 起始 URL: https://www.baidu.com
      - 状态: stopped
      - 事件数: 5
   ✅ 截图: 5 张
      总大小: 2.34 MB
   📊 总大小: 2.35 MB
```

### 方法 3：通过前端界面

1. 打开 http://localhost:5173
2. 点击"查看数据"按钮
3. 查看所有会话列表
4. 点击"导出"下载 JSON 文件

### 方法 4：通过 API

```bash
# 获取所有会话
curl http://127.0.0.1:8000/api/sessions

# 导出特定会话
curl http://127.0.0.1:8000/api/sessions/1/export -o session.json
```

## 导出数据

### 系统内部存储

**位置：** `backend/runs/` （永久保存）

每个会话文件夹包含完整数据，可以直接复制到其他位置。

### 导出到其他目录

**方法 1：复制整个会话文件夹**

```bash
# 复制到其他位置
xcopy backend\runs\session_20260120_143526_e5879545 D:\exports\session_20260120_143526_e5879545 /E /I
```

**方法 2：通过前端导出 JSON**

1. 点击"查看数据"
2. 点击"导出"按钮
3. 浏览器会下载 JSON 文件到默认下载目录

**方法 3：使用 Python 脚本批量导出**

```python
import shutil
from pathlib import Path

# 源目录
runs_dir = Path('backend/runs')

# 目标目录
export_dir = Path('D:/exports')
export_dir.mkdir(parents=True, exist_ok=True)

# 复制所有会话
for session_folder in runs_dir.iterdir():
    if session_folder.is_dir():
        target = export_dir / session_folder.name
        shutil.copytree(session_folder, target, dirs_exist_ok=True)
        print(f'已导出: {session_folder.name}')
```

## 数据管理

### 清理旧数据

```bash
# 删除特定会话
rmdir /s /q backend\runs\session_20260120_143526_e5879545

# 删除所有会话
rmdir /s /q backend\runs
```

### 备份数据

```bash
# 备份整个 runs 目录
xcopy backend\runs D:\backups\runs_%date:~0,4%%date:~5,2%%date:~8,2% /E /I
```

## 数据完整性

### 双重存储策略

1. **数据库存储**（`backend/database/recorder.db`）
   - 实时存储
   - 支持查询和过滤
   - 用于前端展示

2. **文件存储**（`backend/runs/`）
   - 录制结束时生成
   - 完整的会话数据
   - 易于备份和分享
   - 格式化的 JSON，易读

### 数据一致性

- 录制过程中：数据实时写入数据库
- 录制结束时：从数据库导出到 JSON 文件
- JSON 文件是数据库的**完整快照**

## 注意事项

1. **磁盘空间** - 截图会占用较多空间，建议定期清理
2. **JSON 格式** - 使用 2 空格缩进，UTF-8 编码，支持中文
3. **路径引用** - 截图路径是相对路径（`screenshots/event_1.png`）
4. **文件夹命名** - 包含时间戳，按时间排序
5. **数据完整性** - JSON 文件包含所有事件，无分页

## 常见问题

**Q: 数据保存在哪里？**
A: 主要保存在 `backend/runs/` 目录，每个会话一个文件夹。

**Q: 为什么有些会话没有 session.json？**
A: 只有录制结束（停止录制或浏览器关闭）后才会生成 JSON 文件。

**Q: 截图保存在哪里？**
A: 在会话文件夹的 `screenshots/` 子目录中。

**Q: 如何修改截图质量？**
A: 编辑 `backend/config/recorder.yaml`，修改 `recorder.screenshots.quality` 值（1-100）。

**Q: 可以禁用截图吗？**
A: 可以，在配置文件中设置 `recorder.screenshots.enabled: false`。

**Q: JSON 文件可以直接编辑吗？**
A: 可以，但建议不要修改，因为数据库中的数据不会同步更新。

**Q: 如何分享录制数据？**
A: 直接复制整个会话文件夹，或通过前端导出 JSON 文件。

**Q: 如何导出数据到其他目录？**
A: 可以直接复制会话文件夹，或通过前端"查看数据"→"导出"按钮下载 JSON。

## 相关文档

- [录制过程分析](recording-process-analysis.md) - 详细的录制流程和技术实现
- [配置说明](configuration.md) - 所有配置选项详解
- [API 文档](api.md) - REST API 和 WebSocket 端点
- [使用指南](usage.md) - 基本使用流程


**位置：** `backend/database/recorder.db`

**内容：**
- 会话（Sessions）记录
- 事件（Events）记录
- 配置（Configs）记录

**格式：** SQLite 数据库

**配置文件：** `backend/config/database.yaml`

```yaml
database:
  path: database/recorder.db  # 数据库文件路径
  type: sqlite
```

**数据表结构：**

- **sessions** - 录制会话表
  - id: 会话 ID
  - run_id: 唯一运行 ID
  - start_url: 起始 URL
  - start_time: 开始时间
  - end_time: 结束时间
  - status: 状态（started, stopped, error）
  - browser_type: 浏览器类型
  - incognito: 是否隐身模式
  - event_count: 事件数量
  - user_data_dir: 用户数据目录
  - created_at: 创建时间

- **events** - 事件记录表
  - id: 事件 ID
  - session_id: 所属会话 ID
  - seq: 序列号
  - timestamp: 时间戳
  - event_type: 事件类型（click, input, navigation 等）
  - page_url: 页面 URL
  - page_title: 页面标题
  - target_data: 目标元素数据（JSON）
  - locators: 定位器信息（JSON）
  - network_data: 网络数据（JSON）
  - screenshot_path: 截图路径

### 2. 截图文件

**位置：** `backend/screenshots/`

**命名规则：** `session_{session_id}_event_{seq}.png`

**示例：** `session_1_event_5.png`

**配置文件：** `backend/config/app.yaml`

```yaml
output:
  screenshots_dir: screenshots
```

**说明：**
- 每个事件可能会有对应的截图
- 截图文件名包含会话 ID 和事件序列号
- 截图路径存储在数据库的 `events.screenshot_path` 字段中

### 3. 网络数据文件

**位置：** `backend/network/`

**命名规则：** `session_{session_id}_request_{request_id}_body.txt`

**配置文件：** `backend/config/app.yaml`

```yaml
output:
  network_dir: network
```

**说明：**
- 存储 HTTP 请求和响应的 body 内容
- 大型请求/响应体会保存为单独文件
- 文件路径存储在数据库的 `events.network_data` JSON 字段中

### 4. 日志文件

**位置：** `backend/logs/app.log`

**配置文件：** `backend/config/app.yaml`

```yaml
logging:
  file: logs/app.log
  level: INFO
  max_size: 10MB
  backup_count: 5
```

**说明：**
- 记录应用运行日志
- 日志文件达到 10MB 时自动轮转
- 保留最近 5 个备份文件

### 5. 运行数据目录

**位置：** `backend/runs/`

**配置文件：** `backend/config/app.yaml`

```yaml
output:
  runs_dir: runs
```

**说明：**
- 预留目录，用于存储会话运行时的临时数据
- 目前未使用

## 目录结构

```
backend/
├── database/
│   └── recorder.db          # SQLite 数据库
├── screenshots/
│   ├── session_1_event_1.png
│   ├── session_1_event_2.png
│   └── ...
├── network/
│   ├── session_1_request_1_body.txt
│   └── ...
├── logs/
│   ├── app.log
│   ├── app.log.1
│   └── ...
└── runs/
    └── (临时数据)
```

## 数据查看

### 查看数据库

你可以使用 SQLite 客户端工具查看数据库：

**命令行工具：**
```bash
cd backend
sqlite3 database/recorder.db

# 查看所有会话
SELECT * FROM sessions;

# 查看某个会话的所有事件
SELECT * FROM events WHERE session_id = 1;

# 查看事件统计
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
```

**图形化工具：**
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [DBeaver](https://dbeaver.io/)
- [SQLiteStudio](https://sqlitestudio.pl/)

### 通过 API 查看

**获取所有会话：**
```bash
curl http://127.0.0.1:8000/api/sessions
```

**获取特定会话：**
```bash
curl http://127.0.0.1:8000/api/sessions/1
```

**获取会话的所有事件：**
```bash
curl http://127.0.0.1:8000/api/sessions/1/events
```

### 通过前端查看

访问 http://localhost:5173 并导航到：
- **会话列表页面** - 查看所有录制会话
- **会话详情页面** - 查看特定会话的详细信息和事件列表

## 数据清理

### 手动清理

**删除所有数据：**
```bash
cd backend

# 删除数据库
del database\recorder.db

# 删除截图
del /Q screenshots\*

# 删除网络数据
del /Q network\*

# 删除日志
del /Q logs\*
```

**删除特定会话的数据：**
```sql
-- 使用 SQLite 命令行
sqlite3 database/recorder.db

-- 删除会话及其事件
DELETE FROM events WHERE session_id = 1;
DELETE FROM sessions WHERE id = 1;
```

### 自动清理（配置）

在 `backend/config/database.yaml` 中配置自动清理：

```yaml
database:
  retention:
    enabled: true          # 启用自动清理
    days: 30              # 保留天数
    auto_cleanup: true    # 自动清理
```

**注意：** 目前自动清理功能尚未实现，需要手动清理。

## 数据备份

### 备份数据库

```bash
cd backend

# 备份数据库
copy database\recorder.db database\recorder_backup_%date:~0,4%%date:~5,2%%date:~8,2%.db

# 或使用 SQLite 命令
sqlite3 database\recorder.db ".backup database\recorder_backup.db"
```

### 备份所有数据

```bash
cd backend

# 创建备份目录
mkdir backup_%date:~0,4%%date:~5,2%%date:~8,2%

# 复制所有数据
xcopy database backup_%date:~0,4%%date:~5,2%%date:~8,2%\database /E /I
xcopy screenshots backup_%date:~0,4%%date:~5,2%%date:~8,2%\screenshots /E /I
xcopy network backup_%date:~0,4%%date:~5,2%%date:~8,2%\network /E /I
xcopy logs backup_%date:~0,4%%date:~5,2%%date:~8,2%\logs /E /I
```

## 数据迁移

如果需要迁移到其他机器：

1. 复制整个 `backend` 目录
2. 或者只复制数据目录：
   - `backend/database/`
   - `backend/screenshots/`
   - `backend/network/`

## 注意事项

1. **数据库文件** - SQLite 数据库是单文件，可以直接复制备份
2. **截图文件** - 可能会占用较多磁盘空间，建议定期清理
3. **网络数据** - 大型请求/响应会保存为文件，注意磁盘空间
4. **相对路径** - 所有路径都相对于 `backend` 目录
5. **权限问题** - 确保应用有读写权限

## 常见问题

**Q: 数据库文件在哪里？**
A: `backend/database/recorder.db`

**Q: 如何查看录制的截图？**
A: 在 `backend/screenshots/` 目录中，或通过前端界面查看

**Q: 数据会自动清理吗？**
A: 目前不会，需要手动清理

**Q: 如何导出数据？**
A: 可以直接复制数据库文件，或使用 SQLite 工具导出为 CSV/JSON

**Q: 数据库损坏了怎么办？**
A: 使用 SQLite 的 `.recover` 命令尝试恢复，或从备份恢复
