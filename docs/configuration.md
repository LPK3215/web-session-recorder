# 配置说明

所有配置文件位于 `backend/config/`，采用 YAML 格式。

## 1. Profiles（保存规范）

- 目录：`backend/config/profiles/`
- 选项来源：所有 `*.yaml/*.yml` 文件都会出现在前端“保存规范”下拉框
- 合并逻辑：profile 内容会覆盖到 `backend/config/recorder.yaml` 之上（未写的字段继承基座）

profile 文件示例：
```yaml
profile:
  name: mbx_minimal
  description: Gemini batchexecute 最小化网络录制

recorder:
  default_urls:
    - name: "空白页"
      url: ""
  screenshots:
    enabled: false
  network:
    capture_mode: minimal
    include_url_patterns:
      - "^https://business\\.gemini\\.google/.*/data/batchexecute"
  storage:
    include_raw_data: false
```

## 2. recorder.yaml（录制器基座配置）

### 截图配置

```yaml
recorder:
  screenshots:
    enabled: false
    on_events:
      - navigation
      - click
    quality: 90
```

截图会保存到：`backend/runs/<run_id>/screenshots/`，事件中记录相对路径 `screenshots/event_<seq>.png`。

### 网络采集配置

```yaml
recorder:
  network:
    enabled: true
    capture_mode: all       # all|minimal
    include_url_patterns: [] # capture_mode=minimal 时启用
    capture_request: true
    capture_response: true
    capture_body: true
    max_body_size: 1048576
    max_body_text_len: 0
    store_bodies: false
```

### 预设（起始 URL / 窗口大小）

```yaml
recorder:
  default_urls:
    - name: "空白页"
      url: ""
  window_sizes:
    - name: "小窗口 (1280×720)"
      width: 1280
      height: 720
```

注意：前端会根据所选 profile 调用 `GET /api/config/presets?profile=<name>` 加载预设。

### 存储字段控制（保存内容规范）

```yaml
recorder:
  storage:
    include_raw_data: true
    include_network_data: true
    include_locators: true
    include_target_data: true
    include_iframe_context: true
    include_page_title: true
    include_screenshot_path: true
```

## 3. browser.yaml（浏览器配置）

- 可配置浏览器可执行文件路径、启动参数

## 4. locators.yaml（定位器策略）

- 可配置定位器策略优先级与开关

**最后更新**：2026-01-20
