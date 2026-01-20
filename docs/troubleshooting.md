# 常见问题

## Q1: 浏览器启动失败

**问题**：点击"开始录制"后浏览器无法启动

**解决方案**：
1. 确保已运行 `playwright install`
2. 检查 `backend/config/browser.yaml` 中的浏览器路径
3. 尝试使用不同的浏览器类型
4. 查看后端日志获取详细错误信息

## Q2: 无法连接到后端

**问题**：前端显示"无法连接到后端服务器"

**解决方案**：
1. 确保后端正在运行（`http://127.0.0.1:8000`）
2. 检查 `backend/config/app.yaml` 中的 CORS 配置
3. 确认防火墙没有阻止端口 8000

## Q3: WebSocket 连接失败

**问题**：实时事件不显示

**解决方案**：
1. 检查浏览器控制台的 WebSocket 错误
2. 确认后端 WebSocket 端点正常
3. 检查网络代理设置

## Q4: 事件捕获不完整

**问题**：某些操作没有被记录

**解决方案**：
1. 检查 `backend/config/recorder.yaml` 中的事件类型配置
2. 某些动态加载的内容可能需要等待
3. iframe 内的事件需要确保脚本注入成功

## Q5: 数据库错误

**问题**：数据库锁定或损坏

**解决方案**：
```bash
# 备份数据库
cp backend/database/recorder.db backend/database/recorder.db.backup

# 检查数据库完整性
sqlite3 backend/database/recorder.db "PRAGMA integrity_check;"

# 如果损坏，删除并重新创建
rm backend/database/recorder.db
# 重启后端会自动创建新数据库
```

## Q6: Windows 兼容性问题

**问题**：在 Windows 上出现 `NotImplementedError`

**解决方案**：
- 已在代码中修复，设置了 `WindowsProactorEventLoopPolicy`
- 确保 `backend/config/app.yaml` 中 `reload: false`
- 修改代码后需要手动重启服务器

## Q7: 截图功能不工作

**问题**：启用截图后没有生成截图文件

**解决方案**：
1. 确保 `backend/screenshots/` 目录存在且可写
2. 检查 `backend/config/recorder.yaml` 中的截图配置
3. 确认事件类型在配置的截图列表中

## 调试技巧

### 后端调试

```bash
# 启用详细日志
cd backend
python run.py  # 查看控制台输出
```

### 前端调试

- 使用浏览器开发者工具
- 查看 Network 标签页的 WebSocket 连接
- 查看 Console 标签页的日志

### 数据库查看

```bash
sqlite3 backend/database/recorder.db
.tables
SELECT * FROM sessions;
SELECT * FROM events WHERE session_id = 1;
```

## 性能优化

### 数据库优化

**定期清理旧数据**：
```sql
-- 删除 30 天前的会话
DELETE FROM sessions WHERE start_time < datetime('now', '-30 days');

-- 清理孤立事件
DELETE FROM events WHERE session_id NOT IN (SELECT id FROM sessions);

-- 重建索引
REINDEX;

-- 优化数据库
VACUUM;
```

### 网络数据优化

**限制响应体大小**（`backend/config/recorder.yaml`）：
```yaml
recorder:
  network:
    body_size_threshold: 1048576  # 1MB
    max_body_size: 10485760       # 10MB
```

### 前端性能

**分页加载事件**：
```javascript
// 默认每页 100 个事件
const events = await sessionAPI.getSessionEvents(sessionId, {
  page: 1,
  page_size: 100
})
```
