# 录制配置档（Profiles）

在开始录制前可以选择一个 profile，用来控制“要采集/要保存哪些信息”的规则。

## 文件位置

- `backend/config/recorder.yaml`：合并基座（不作为“选项”展示）
- `backend/config/profiles/*.yaml`：可选 profile（名称为文件名，例如 `mbx_minimal.yaml` → `mbx_minimal`）

## 文件格式

profile 文件支持两类内容：

1) 元数据（可选）
```yaml
profile:
  name: minimal
  description: 最小化保存（示例）
```

2) 覆盖项（可选，按需写，未写的字段会从默认 `recorder.yaml` 继承）
```yaml
recorder:
  privacy_mode: strict
  screenshots:
    enabled: false
  network:
    capture_body: false
  storage:
    include_raw_data: false
```

说明：
- 当前 profile 仅作用于“录制器 recorder 配置”（不会覆盖 `app.yaml/browser.yaml/locators.yaml`）。
