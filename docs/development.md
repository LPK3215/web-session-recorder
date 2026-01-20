# 开发指南

## 运行测试

### 后端测试（162 个测试）

```bash
cd backend
pytest tests/
```

测试覆盖：
- 单元测试：各组件独立测试
- 集成测试：API 端点测试
- 数据库测试：CRUD 操作测试
- WebSocket 测试：实时通信测试

### 前端测试

```bash
cd frontend
npm run test
```

## 代码结构规范

### 后端

- 使用 Python 类型提示
- 遵循 PEP 8 代码风格
- 使用 async/await 异步编程
- 日志记录使用 logging 模块

### 前端

- 使用 Vue 3 Composition API
- 使用 `<script setup>` 语法
- 使用 Element Plus 组件
- 遵循 Vue 风格指南

## 添加新功能

### 1. 添加新的事件类型

- 修改 `backend/scripts/injector.js` 添加事件监听
- 修改 `backend/app/core/event_capturer.py` 处理新事件
- 更新 `backend/config/recorder.yaml` 配置

### 2. 添加新的定位器策略

- 修改 `backend/app/core/locators.py` 添加生成方法
- 更新 `backend/config/locators.yaml` 配置优先级

### 3. 添加新的 API 端点

- 在 `backend/app/api/` 创建新的路由文件
- 在 `backend/app/main.py` 注册路由
- 添加对应的测试

## 项目结构

```
web-session-recorder/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由和端点
│   │   ├── core/              # 核心功能模块
│   │   ├── db/                # 数据库层
│   │   └── main.py            # FastAPI 应用入口
│   ├── config/                # YAML 配置文件
│   ├── database/              # SQLite 数据库
│   ├── screenshots/           # 截图存储目录
│   ├── scripts/               # JavaScript 注入脚本
│   ├── tests/                 # 测试文件
│   ├── requirements.txt       # Python 依赖
│   └── run.py                 # 启动脚本
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── api/               # API 客户端
│   │   ├── router/            # Vue Router
│   │   └── main.js            # 入口文件
│   └── package.json
├── docs/                       # 项目文档
└── README.md                   # 项目说明
```

## 自定义事件过滤

修改 `backend/app/core/event_capturer.py`：

```python
def should_capture_event(self, event_type: str, target_info: dict) -> bool:
    """自定义事件过滤逻辑"""
    # 例如：忽略某些元素的点击
    if event_type == 'click' and target_info.get('class') == 'ignore-me':
        return False
    return True
```

## 监控和日志

### 日志配置

编辑 `backend/config/app.yaml`：
```yaml
logging:
  level: INFO  # DEBUG/INFO/WARNING/ERROR
  file: logs/app.log
  max_size: 10MB
  backup_count: 5
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/app.log

# 搜索错误
grep ERROR logs/app.log

# 查看特定会话的日志
grep "session_20260120" logs/app.log
```

### 监控指标

- 活跃会话数
- 事件捕获速率
- WebSocket 连接数
- 数据库大小
- 磁盘使用量

## 安全建议

### 1. 数据隐私

- 使用 `privacy_mode: strict` 处理敏感数据
- 定期清理录制数据
- 不要在生产环境录制真实用户数据

### 2. 网络安全

- 仅在受信任的网络环境使用
- 配置 CORS 限制访问来源
- 使用 HTTPS（生产环境）

### 3. 文件权限

```bash
# 限制数据库文件权限
chmod 600 backend/database/recorder.db

# 限制配置文件权限
chmod 600 backend/config/*.yaml
```

## 贡献指南

### 报告问题

1. 检查是否已有相同问题
2. 提供详细的错误信息和日志
3. 说明复现步骤
4. 提供环境信息（OS、Python 版本、Node 版本）

### 提交代码

1. Fork 项目
2. 创建功能分支
3. 编写测试
4. 提交 Pull Request
