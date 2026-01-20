# 自动化脚本使用指南

项目提供了多个自动化脚本，简化开发、测试和部署流程。所有脚本都位于项目根目录。

## 📋 脚本列表

### 核心脚本（根目录）

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `build.bat` | **构建一体化** | 智能检测、构建、测试一条龙（推荐） |
| `start.bat` | **启动一体化** | 启动前后端服务 |
| `stop.bat` | **停止一体化** | 停止所有运行的服务 |

### 辅助脚本（backend/scripts/）

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `setup.bat` | 安装依赖 | 首次安装或重新安装依赖 |
| `test.bat` | 运行测试 | 执行前后端测试 |
| `deploy.bat` | 部署构建 | 构建生产版本 |
| `clean.bat` | 清理项目 | 删除依赖和缓存 |

---

## 🔧 build.bat - 构建一体化（推荐）

### 功能
最智能的脚本，先尝试运行测试，如果失败则自动判断原因并执行构建，然后重新测试。

### 执行逻辑
```
1. 尝试运行测试
   ├─ 成功 → 显示结果，完成
   └─ 失败 → 继续
2. 检测失败原因
   ├─ 依赖未安装 → 自动安装依赖
   └─ 代码问题 → 显示错误信息
3. 重新运行测试
   ├─ 成功 → 询问是否启动服务
   └─ 失败 → 显示错误信息
```

### 使用方法
```bash
build.bat
```

### 适用场景
- **首次使用** - 自动检测并安装依赖
- **拉取代码后** - 自动检测依赖变化
- **不确定环境状态** - 智能判断并处理
- **最快速的方式** - 一个命令搞定一切

### 优势
- ✅ 智能检测 - 自动判断是否需要构建
- ✅ 节省时间 - 依赖正常时直接测试
- ✅ 自动修复 - 依赖问题自动安装
- ✅ 友好提示 - 清晰的错误信息和建议
- ✅ 可选启动 - 测试通过后可直接启动服务

### 示例输出
```
========================================
  Web Session Recorder - 构建一体化
========================================

[1] 尝试运行测试...

❌ 测试失败，可能是依赖未安装

[2] 自动执行构建...
========================================

检测到后端依赖未安装

正在安装依赖...

[2.1] 安装后端依赖...
✅ 后端依赖安装完成

[2.2] 安装前端依赖...
✅ 前端依赖安装完成

========================================
  ✅ 构建完成！
========================================

[3] 重新运行测试...

✅ 后端测试通过 (162/162)

========================================
  ✅ 构建和测试全部完成！
========================================

是否立即启动服务? (Y/N)
```

---

## ▶️ start.bat - 启动一体化

### 功能
自动安装所有依赖，包括后端 Python 依赖、Playwright 浏览器和前端 Node.js 依赖。

### 执行步骤
1. 检查 Python 和 Node.js 环境
2. 安装后端 Python 依赖（requirements.txt）
3. 安装 Playwright 浏览器
4. 安装前端 Node.js 依赖（npm install）
5. 创建必要的目录（database、screenshots）

### 使用方法
```bash
setup.bat
```

### 适用场景
- 首次克隆项目后
- 重新安装依赖
- 依赖更新后

### 注意事项
- 需要联网下载依赖
- 首次运行可能需要较长时间
- 确保已安装 Python 3.10+ 和 Node.js 16+

---

## 🚀 setup.bat - 安装依赖

**位置**：`backend/scripts/setup.bat`

### 功能
自动启动前后端服务，在两个独立的命令行窗口中运行。

### 执行步骤
1. 在新窗口启动后端服务（backend/run.py）
2. 等待 3 秒让后端启动
3. 在新窗口启动前端服务（npm run dev）

### 使用方法
```bash
start.bat
```

### 服务地址
- 后端：http://127.0.0.1:8000
- Swagger 文档：http://127.0.0.1:8000/docs
- 前端：http://localhost:5173

### 窗口标题
- 后端窗口：`Web Session Recorder - Backend`
- 前端窗口：`Web Session Recorder - Frontend`

### 停止服务
- 方式 1：运行 `stop.bat`
- 方式 2：在各自窗口按 `Ctrl+C`
- 方式 3：直接关闭窗口

### 注意事项
- 确保端口 8000 和 5173 未被占用
- 首次启动前需要运行 `setup.bat`

---

## ▶️ start.bat - 启动一体化

**位置**：根目录

### 功能
停止所有运行的前后端服务。

### 执行步骤
1. 根据窗口标题停止后端服务
2. 根据窗口标题停止前端服务
3. 可选：停止所有 Python 进程
4. 可选：停止所有 Node 进程

### 使用方法
```bash
stop.bat
```

### 交互提示
- 发现 Python 进程时会询问是否全部停止
- 发现 Node 进程时会询问是否全部停止

### 注意事项
- 会停止所有匹配窗口标题的进程
- 谨慎选择停止所有 Python/Node 进程（可能影响其他项目）

---

## ⏹️ stop.bat - 停止一体化

**位置**：根目录

### 功能
自动运行前后端的所有测试。

### 执行步骤
1. 运行后端测试（pytest tests/ -v）
2. 运行前端测试（npm run test）
3. 显示测试结果

### 使用方法
```bash
test.bat
```

### 测试覆盖
- 后端：162 个测试
  - 单元测试
  - 集成测试
  - API 测试
  - WebSocket 测试
- 前端：组件测试（如果配置）

### 测试失败处理
- 如果后端测试失败，脚本会停止并显示错误
- 如果前端测试失败，脚本会停止并显示错误

### 注意事项
- 测试前确保没有运行的服务占用端口
- 测试会创建临时数据库
- 测试完成后会自动清理

---

## 🧪 test.bat - 运行测试

**位置**：`backend/scripts/test.bat`

### 功能
构建生产版本，生成可部署的文件。

### 执行步骤
1. 清理旧的 dist 目录
2. 构建前端生产版本（npm run build）
3. 复制前端构建文件到 dist/frontend
4. 复制后端代码到 dist/backend
5. 排除测试和缓存文件
6. 创建部署说明文档

### 使用方法
```bash
deploy.bat
```

### 输出结构
```
dist/
├── frontend/          # 前端静态文件
│   ├── index.html
│   ├── assets/
│   └── ...
├── backend/           # 后端 Python 代码
│   ├── app/
│   ├── config/
│   ├── database/
│   ├── requirements.txt
│   └── run.py
└── DEPLOY.md          # 部署说明
```

### 部署步骤
1. 将 dist 目录上传到服务器
2. 安装后端依赖：`cd dist/backend && pip install -r requirements.txt`
3. 安装 Playwright：`playwright install`
4. 配置 YAML 文件
5. 启动后端：`python run.py`
6. 配置 Nginx 指向 dist/frontend

### 注意事项
- 构建前确保前端代码无错误
- 检查 dist/DEPLOY.md 了解详细部署步骤
- 生产环境建议使用 gunicorn 或 uvicorn

---

## 📦 deploy.bat - 部署构建

**位置**：`backend/scripts/deploy.bat`

### 功能
删除依赖、缓存和构建文件，清理项目。

### 执行步骤
1. 删除前端 node_modules
2. 删除前端 dist
3. 删除后端 __pycache__
4. 删除后端 .pytest_cache
5. 删除部署 dist 目录
6. 可选：删除数据库文件

### 使用方法
```bash
clean.bat
```

### 交互提示
- 开始前会询问是否继续
- 删除数据库时会单独询问确认

### 清理内容
- `frontend/node_modules` - 前端依赖
- `frontend/dist` - 前端构建文件
- `backend/**/__pycache__` - Python 缓存
- `backend/.pytest_cache` - 测试缓存
- `dist/` - 部署构建目录
- `backend/database/recorder.db` - 数据库（可选）
- `backend/screenshots/` - 截图（可选）

### 注意事项
- 删除数据库会丢失所有录制的会话
- 清理后需要重新运行 `setup.bat`
- 谨慎操作，删除的文件无法恢复

---

## 🧹 clean.bat - 清理项目

**位置**：`backend/scripts/clean.bat`

### 🔄 典型工作流程

### 首次使用（推荐）
```bash
build.bat    # 构建一体化 - 自动检测并处理一切
```

### 拉取代码后
```bash
build.bat    # 自动检测依赖变化并处理
```

### 日常开发
```bash
start.bat    # 启动服务
# 开发...
stop.bat     # 停止服务
```

### 单独测试
```bash
backend\scripts\test.bat    # 运行所有测试
```

### 部署
```bash
backend\scripts\deploy.bat  # 构建生产版本
```

### 部署流程
```bash
# 1. 运行测试确保代码正常
test.bat

# 2. 构建生产版本
deploy.bat

# 3. 上传 dist 目录到服务器
# 4. 按照 dist/DEPLOY.md 部署
```

### 清理重建
```bash
# 1. 清理项目
clean.bat

# 2. 重新安装依赖
setup.bat

# 3. 启动服务
start.bat
```

---

## ⚠️ 常见问题

### Q1: setup.bat 提示找不到 Python 或 Node.js

**解决方案**：
- 确保已安装 Python 3.10+ 和 Node.js 16+
- 确保 Python 和 Node.js 已添加到系统 PATH
- 重启命令行窗口

### Q2: start.bat 启动后端失败

**解决方案**：
- 检查端口 8000 是否被占用
- 确保已运行 `setup.bat` 安装依赖
- 查看后端窗口的错误信息

### Q3: test.bat 测试失败

**解决方案**：
- 确保没有运行的服务占用端口
- 检查数据库文件是否损坏
- 查看具体的测试错误信息

### Q4: deploy.bat 构建失败

**解决方案**：
- 确保前端代码无语法错误
- 检查 Node.js 版本是否符合要求
- 查看构建错误信息

### Q5: stop.bat 无法停止服务

**解决方案**：
- 手动关闭服务窗口
- 使用任务管理器结束进程
- 重启计算机

---

## 💡 高级技巧

### 自定义启动端口

编辑 `backend/config/app.yaml`：
```yaml
server:
  host: 127.0.0.1
  port: 8000  # 修改为其他端口
```

编辑 `frontend/vite.config.js`：
```javascript
export default {
  server: {
    port: 5173  // 修改为其他端口
  }
}
```

### 后台运行服务

修改 `start.bat`，将 `start` 改为 `start /min`：
```batch
start /min "Web Session Recorder - Backend" cmd /k "cd backend && python run.py"
start /min "Web Session Recorder - Frontend" cmd /k "cd frontend && npm run dev"
```

### 自动打开浏览器

在 `start.bat` 末尾添加：
```batch
timeout /t 5 /nobreak >nul
start http://localhost:5173
```

### 生产环境启动

创建 `start-prod.bat`：
```batch
@echo off
cd backend
start "Backend" uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📝 脚本维护

### 修改脚本

所有脚本都是纯文本文件，可以用任何文本编辑器打开修改。

### 添加新脚本

参考现有脚本的格式，创建新的 `.bat` 文件。

### 脚本编码

所有脚本使用 UTF-8 编码，开头包含 `chcp 65001` 以支持中文显示。

---

**提示**：所有脚本都会在执行完成后暂停，按任意键继续。这样可以查看执行结果和错误信息。
