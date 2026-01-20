# 使用指南

## 基本使用流程

### 1. 启动服务

- 启动后端：`cd backend && python run.py`
- 启动前端：`cd frontend && npm run dev`

### 2. 访问应用

打开浏览器访问 `http://localhost:5173`

### 3. 开始录制

- 输入起始 URL（默认：https://www.baidu.com）
- 选择浏览器类型（Chrome/Edge/Firefox）
- 配置隐身模式（可选）
- 配置用户数据目录（可选，用于保留登录状态）
- 点击"开始录制"按钮

### 4. 浏览器操作

- 系统会打开一个新的浏览器窗口
- 在浏览器中进行任何操作
- 所有操作会实时显示在前端界面

### 5. 停止录制

- 方式 1：点击"停止录制"按钮
- 方式 2：直接关闭浏览器窗口（自动停止）

### 6. 查看会话

- 点击"会话列表"查看所有录制
- 点击具体会话查看详细信息
- 查看事件时间线和定位器

## 前端界面说明

### 1. 首页（录制控制台）

- **起始 URL**：输入要访问的网址（可选，默认 https://www.baidu.com）
- **浏览器**：选择 Chrome、Edge 或 Firefox
- **隐身模式**：启用后在无痕模式下启动浏览器
- **用户数据目录**：指定用户数据目录以保留登录状态
- **开始/停止录制**：控制录制状态
- **已捕获事件数**：实时显示事件计数
- **最近事件**：显示最近 10 个事件

### 2. 会话列表页

- 显示所有录制的会话
- 列：run_id、起始 URL、开始时间、持续时间、事件数、状态
- 支持分页和筛选
- 点击会话查看详情

### 3. 会话详情页

- **会话元数据**：run_id、浏览器类型、时间等
- **事件时间线**：按时间顺序显示所有事件
- **事件详情**：展开查看事件的完整信息
- **定位器**：显示为每个元素生成的所有定位器
- **网络数据**：显示请求/响应信息
- **截图**：如果启用，显示截图

### 4. 设置页

- 5 个配置文件的编辑器（app、browser、recorder、database、locators）
- YAML 语法高亮
- 保存前验证
- 重置为默认值

## 高级用法

### 自定义浏览器路径

编辑 `backend/config/browser.yaml`：
```yaml
browser:
  paths:
    chrome: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    edge: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    firefox: null  # 使用 Playwright 提供的
```

### 使用用户数据目录

保留登录状态和浏览器设置：
```javascript
// 在前端界面输入
用户数据目录: C:\Users\YourName\AppData\Local\Google\Chrome\User Data
```

或通过 API：
```json
{
  "url": "https://example.com",
  "browser": "chrome",
  "incognito": false,
  "user_data_dir": "C:\\Users\\YourName\\AppData\\Local\\Google\\Chrome\\User Data"
}
```

### 批量导出会话数据

```python
import sqlite3
import json

conn = sqlite3.connect('backend/database/recorder.db')
cursor = conn.cursor()

# 导出所有会话
cursor.execute("SELECT * FROM sessions")
sessions = cursor.fetchall()

# 导出为 JSON
with open('sessions_export.json', 'w') as f:
    json.dump(sessions, f, indent=2)
```
