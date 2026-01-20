# 常见问题

## Q1：浏览器启动失败

排查步骤：
1. 确保已运行 `playwright install`
2. 检查 `backend/config/browser.yaml` 中的浏览器路径（如需指定）
3. 尝试切换浏览器类型（chrome/edge/firefox）
4. 查看后端日志输出

## Q2：前端提示无法连接后端

1. 确保后端运行在 `http://127.0.0.1:8000`
2. 检查 `backend/config/app.yaml` 的 CORS 配置

## Q3：实时事件不显示（WebSocket）

1. 打开浏览器开发者工具，查看 Console 是否有 ws 报错
2. 确认后端 WebSocket 端点可达：`ws://127.0.0.1:8000/ws/sessions/<run_id>`

## Q4：点击“停止录制”后浏览器没关闭

这是设计行为：**停止录制只会停止采集并保存，不会主动关闭浏览器**。

如果你关闭浏览器/页面，系统会自动停止录制并保存。

## Q5：截图不显示 / 详情页看不到图片

1. 确认开启截图：
```yaml
recorder:
  screenshots:
    enabled: true
    on_events: [navigation, click]
```
2. 确认后端静态挂载正常：访问 `http://127.0.0.1:8000/runs/`（应能列目录/返回 404 以外的静态响应）
3. 事件接口会把截图路径转换成 `/runs/<run_id>/...`，前端用该 URL 直接展示

## Q6：incognito / user_data_dir 没效果

- `incognito=true`：使用临时上下文（不会复用用户数据目录）
- `incognito=false + user_data_dir`：使用持久化上下文（可保留登录态）

## 性能建议：网络 body 太大

在 profile 或 `backend/config/recorder.yaml` 中开启截断：
```yaml
recorder:
  network:
    max_body_text_len: 200000
```

**最后更新**：2026-01-20
