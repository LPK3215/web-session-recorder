# 录制过程详细分析

## 录制流程概述

```
用户点击"开始录制"
    ↓
创建会话状态（内存）
    ↓
创建会话文件夹（backend/runs/session_xxx/）
    ├── screenshots/
    └── network/
    ↓
启动浏览器（Playwright）
    ↓
注入 JavaScript 脚本（injector.js）
    ↓
设置事件监听器
    ├── 页面事件（click, input, navigation 等）
    ├── 网络请求监听
    └── 对话框监听
    ↓
【录制中】捕获所有交互
    ├── 事件 → 内存（同时 WebSocket 实时推送）
    ├── 截图 → screenshots/
    └── 网络数据 → network/
    ↓
用户点击"停止录制" 或 关闭浏览器
    ↓
停止采集并保存（停止录制不会主动关闭浏览器）
    ↓
生成 session.json（格式化）
    ↓
保存到会话文件夹
    ↓
录制完成
```

## 录制内容详解

### 1. 捕获的事件类型

**用户交互事件：**
- `click` - 鼠标点击
- `dblclick` - 双击
- `input` - 输入框输入
- `change` - 表单值改变
- `submit` - 表单提交
- `keydown` - 键盘按键

**页面事件：**
- `navigation` - 页面导航（URL 变化）
- `dialog` - 对话框（alert, confirm, prompt）
- `download` - 文件下载

**每个事件包含：**
- 时间戳
- 事件类型
- 页面 URL 和标题
- 目标元素信息（tagName, id, class, value 等）
- 元素定位器（多种策略：id, css, xpath, role 等）
- 网络请求数据（如果有）
- 截图路径（如果触发截图）

### 2. JavaScript 注入脚本

**文件位置：** `backend/scripts/injector.js`

**功能：**
- 在页面加载时自动注入
- 监听所有用户交互
- 捕获事件详情
- 通过 Playwright 通道发送到后端
- 支持 iframe 内的事件捕获

**注入时机：**
- 页面首次加载
- 每次导航后
- 新 iframe 创建时

### 3. 截图机制

**触发条件：**
- 配置文件中指定的事件类型
- 默认：`navigation`, `click`, `submit`

**配置位置：** `backend/config/recorder.yaml`
```yaml
recorder:
  screenshots:
    enabled: true  # 是否启用截图
    on_events:     # 哪些事件触发截图
      - navigation
      - click
      - submit
    quality: 90    # 截图质量 (1-100)
```

**截图流程：**
```
事件发生
    ↓
检查是否需要截图（event_type in on_events）
    ↓
调用 page.screenshot()
    ↓
保存到 screenshots/event_{seq}.png
    ↓
路径记录到事件的 screenshot_path 字段
```

**文件命名：** `event_{序列号}.png`
- 示例：`event_1.png`, `event_2.png`

**存储位置：** `backend/runs/session_xxx/screenshots/`

### 4. 网络数据捕获

**监听内容：**
- HTTP 请求和响应
- 请求方法（GET, POST 等）
- URL
- 状态码
- Content-Type
- 请求/响应 Headers
- 请求/响应 Body（大型 body 保存为文件）

**Body 存储：**
- 小型 body：直接存储在事件的 `network_data` JSON 字段
- 大型 body：保存为文件 `network/request_{id}_body.txt`

### 5. 元素定位器生成

**策略优先级：**
1. `role` - ARIA role（最稳定）
2. `label` - 表单标签
3. `placeholder` - 输入框占位符
4. `id` - 元素 ID
5. `css` - CSS 选择器
6. `xpath` - XPath 表达式

**每个元素生成多个定位器：**
```json
{
  "locators": [
    {
      "strategy": "id",
      "selector": "#username",
      "stability": "high"
    },
    {
      "strategy": "css",
      "selector": "input.login-input",
      "stability": "medium"
    }
  ]
}
```

## 保存的文件结构

### 会话文件夹

```
backend/runs/session_20260120_143526_e5879545/
├── session.json              # 主数据文件（格式化 JSON）
├── screenshots/              # 截图文件夹
│   ├── event_1.png          # 第 1 个事件的截图
│   ├── event_2.png          # 第 2 个事件的截图
│   ├── event_3.png
│   └── ...
└── network/                  # 网络数据文件夹
    ├── request_abc123_body.txt
    ├── request_def456_body.txt
    └── ...
```

### session.json 文件内容

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
      "network_data": {
        "method": "GET",
        "url": "https://www.baidu.com",
        "status": 200,
        "contentType": "text/html"
      },
      "screenshot_path": "screenshots/event_1.png"
    },
    {
      "id": 2,
      "seq": 2,
      "timestamp": "2026-01-20T14:35:35.456789",
      "event_type": "click",
      "page_url": "https://www.baidu.com",
      "page_title": "百度一下，你就知道",
      "target_data": {
        "tagName": "INPUT",
        "id": "kw",
        "className": "s_ipt",
        "name": "wd",
        "type": "text",
        "value": "",
        "placeholder": "请输入关键词"
      },
      "locators": [
        {
          "strategy": "id",
          "selector": "#kw",
          "stability": "high"
        },
        {
          "strategy": "placeholder",
          "selector": "getByPlaceholder('请输入关键词')",
          "stability": "high"
        },
        {
          "strategy": "css",
          "selector": "input.s_ipt",
          "stability": "medium"
        }
      ],
      "network_data": null,
      "screenshot_path": "screenshots/event_2.png"
    }
  ],
  "metadata": {
    "total_events": 5,
    "saved_time": "2026-01-20T14:36:46.000000"
  }
}
```

## 数据存储位置

### 1. 实时存储（录制中）

**会话状态：** 内存中累积
- 会话信息（run_id/start_time/status/...）
- 事件数组（events）
- 网络事件（network_events）
- 通过 WebSocket 实时推送到前端

**截图：** `backend/runs/session_xxx/screenshots/`
- 实时保存
- PNG 格式
- 质量可配置

**网络数据：** `backend/runs/session_xxx/network/`
- 大型 body 实时保存
- 文本格式

### 2. 最终存储（录制结束）

**session.json：** `backend/runs/session_xxx/session.json`
- 从内存聚合并一次性落盘
- 格式化 JSON（2 空格缩进）
- UTF-8 编码
- 包含所有事件和会话信息

## 技术实现细节

### 1. 浏览器控制

**使用：** Playwright
- 支持 Chrome, Edge, Firefox
- 完整的浏览器自动化
- 支持隐身模式
- 可配置用户数据目录

**启动参数：**
```python
browser = await playwright.chromium.launch(
    channel="chrome",  # 使用本地 Chrome
    headless=False,    # 非无头模式
    args=[...],        # 自定义参数
    timeout=30000      # 启动超时
)
```

### 2. 事件捕获

**前端（JavaScript）：**
- 注入脚本监听 DOM 事件
- 捕获事件详情
- 通过 `window.__playwright__` 通道发送

**后端（Python）：**
- 接收事件数据
- 生成定位器
- 保存到内存（最终落盘为 session.json）
- 触发截图（如果需要）
- 通过 WebSocket 推送到前端

### 3. WebSocket 实时通信

**连接：** `ws://127.0.0.1:8000/ws/sessions/{run_id}`

**用途：**
- 实时推送事件到前端
- 更新事件计数
- 显示最近事件列表

**断开处理：**
- 检查会话状态
- 如果浏览器关闭，更新前端 UI
- 否则尝试重连

### 4. 截图实现

```python
async def capture_screenshot(page, event_type, seq):
    if event_type not in screenshot_on_events:
        return None
    
    filename = f"event_{seq}.png"
    filepath = screenshot_folder / filename
    
    await page.screenshot(
        path=str(filepath),
        type='png',
        quality=screenshot_quality
    )
    
    return f"screenshots/{filename}"
```

## 配置选项

### recorder.yaml

```yaml
recorder:
  # 截图配置
  screenshots:
    enabled: true          # 启用/禁用截图
    on_events:            # 触发截图的事件类型
      - navigation
      - click
      - submit
    quality: 90           # 截图质量 (1-100)
  
  # 隐私模式
  privacy_mode: none      # none, mask_sensitive, full
  
  # 默认网址
  default_urls:
    - name: 百度
      url: https://www.baidu.com
  
  # 窗口大小预设
  window_sizes:
    - name: 高清 (1920×1080)
      width: 1920
      height: 1080
```

## 性能考虑

### 1. 截图性能

**影响因素：**
- 截图质量（quality 参数）
- 页面大小
- 触发频率

**优化建议：**
- 只在关键事件截图
- 降低质量到 80-90
- 定期清理旧截图

### 2. 文件存储与内存

**说明：**
- 录制过程中事件主要在内存累积
- 停止录制或浏览器关闭时写入 `session.json`
- 截图与大型网络 body 会实时写入文件系统（按配置）

### 3. 磁盘空间

**估算：**
- 每个截图：~100-500 KB
- 每个事件：~1-5 KB（JSON）
- 每小时录制：~50-200 MB

## 常见问题

**Q: 截图是自动触发还是手动？**
A: 自动触发。在配置的事件类型（navigation, click, submit）发生时自动截图。

**Q: 所有事件都会截图吗？**
A: 不是。只有配置文件中 `screenshots.on_events` 列表中的事件类型才会截图。

**Q: 截图保存在哪里？**
A: `backend/runs/session_xxx/screenshots/event_{序列号}.png`

**Q: 如何禁用截图？**
A: 在 `backend/config/recorder.yaml` 中设置 `screenshots.enabled: false`

**Q: 网络数据都保存吗？**
A: 是的。所有 HTTP 请求/响应都会记录。大型 body 保存为单独文件。

**Q: 如何修改截图质量？**
A: 修改 `recorder.yaml` 中的 `screenshots.quality` 值（1-100）

**Q: iframe 中的事件能捕获吗？**
A: 能。注入脚本会自动处理 iframe。

**Q: 录制会影响页面性能吗？**
A: 影响很小。主要开销在截图和网络监听。

## 相关文件

**核心代码：**
- `backend/app/core/session_manager.py` - 会话管理
- `backend/app/core/event_capturer.py` - 事件捕获
- `backend/app/core/browser.py` - 浏览器控制
- `backend/app/core/storage_manager.py` - 文件存储
- `backend/scripts/injector.js` - JavaScript 注入脚本

**配置文件：**
- `backend/config/recorder.yaml` - 录制配置
- `backend/config/browser.yaml` - 浏览器配置

**数据文件：**
- `backend/runs/<run_id>/session.json` - 会话 JSON（含事件）
- `backend/runs/` - 会话文件夹
