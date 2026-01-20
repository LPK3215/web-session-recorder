# 配置说明

所有配置文件位于 `backend/config/` 目录，使用 YAML 格式。

## 隐私模式

在 `backend/config/recorder.yaml` 中配置：

### none - 保存所有数据（默认）

```yaml
recorder:
  privacy_mode: none
```

- 保存所有字段，包括密码、token 等敏感信息

### partial - 部分脱敏

```yaml
recorder:
  privacy_mode: partial
```

- 保留字段结构
- 脱敏敏感字段（password、token、credit_card 等）
- 保留字段长度和类型信息

### strict - 严格脱敏

```yaml
recorder:
  privacy_mode: strict
```

- 完全排除敏感字段
- 不保存任何可能包含敏感信息的数据

## 截图配置

在 `backend/config/recorder.yaml` 中配置：

```yaml
recorder:
  screenshot:
    enabled: true
    event_types:
      - click
      - submit
      - navigation
```

截图将保存到 `backend/screenshots/` 目录，文件名格式：
```
backend/screenshots/session_{session_id}_event_{seq}.png
```

## 网络数据存储

在 `backend/config/recorder.yaml` 中配置：

```yaml
recorder:
  network:
    enabled: true
    capture_body: true
    store_large_bodies: true
    body_size_threshold: 1048576  # 1MB
```

大型响应体将保存到 `backend/network/` 目录。

## 定位器优先级

在 `backend/config/locators.yaml` 中配置：

```yaml
locators:
  strategies:
    - role
    - label
    - testid
    - placeholder
    - text
    - css
    - xpath
  priorities:
    role: high
    label: high
    testid: high
    placeholder: medium
    text: medium
    css: low
    xpath: low
```

## 浏览器配置

在 `backend/config/browser.yaml` 中配置：

```yaml
browser:
  default: chrome
  paths:
    chrome: null  # 使用系统默认路径
    edge: null
    firefox: null
  launch:
    timeout: 30000
    slow_mo: 0
    args: []
  context:
    viewport:
      width: 1920
      height: 1080
    user_agent: null
    locale: zh-CN
```

## 数据库配置

在 `backend/config/database.yaml` 中配置：

```yaml
database:
  path: database/recorder.db
  retention:
    enabled: true
    days: 30  # 保留 30 天
```

## 应用配置

在 `backend/config/app.yaml` 中配置：

```yaml
app:
  debug: true
  name: Web Session Recorder
  version: 1.0.0

server:
  host: 127.0.0.1
  port: 8000
  reload: false  # Windows 上禁用
  cors_origins:
    - http://localhost:5173
    - http://localhost:3000

logging:
  level: INFO  # DEBUG/INFO/WARNING/ERROR
  file: logs/app.log
  max_size: 10MB
  backup_count: 5
```
