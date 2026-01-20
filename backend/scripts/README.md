# 辅助脚本

这个目录包含项目的辅助脚本，用于开发、测试和部署。

## 📋 脚本列表

| 脚本 | 功能 | 说明 |
|------|------|------|
| `setup.bat` | 安装依赖 | 安装后端和前端的所有依赖 |
| `test.bat` | 运行检查 | 后端 smoke 检查 + 前端 build |
| `deploy.bat` | 部署构建 | 构建生产版本到 dist 目录 |
| `clean.bat` | 清理项目 | 删除依赖、缓存和构建文件 |
| `manage_sessions.py` | 管理会话 | 查看、清理和导出会话数据 |
| `smoke_test.py` | 后端检查 | 导入 + FastAPI TestClient 请求关键接口 |

## 🚀 使用方法

### 快速使用

```bash
# 从 backend/scripts 目录运行管理工具
cd backend\scripts
python manage_sessions.py    # 管理会话（交互式）
```

### 从项目根目录运行

推荐使用根目录的核心脚本：

```bash
# 构建一体化（智能检测并构建测试）
build.bat

# 启动一体化（启动前后端服务）
start.bat

# 停止一体化（停止所有服务）
stop.bat
```

### 从 backend/scripts 目录运行

如果需要单独执行某个功能：

```bash
cd backend\scripts

# 安装依赖
setup.bat

# 运行测试
test.bat

# 部署构建
deploy.bat

# 清理项目
clean.bat
```

## 📝 脚本说明

### setup.bat - 安装依赖

安装项目所需的所有依赖：
- 后端 Python 依赖（requirements.txt）
- Playwright 浏览器
- 前端 Node.js 依赖（npm install）
- 创建必要的目录

**使用场景**：
- 首次克隆项目
- 依赖更新后
- 清理后重新安装

### test.bat - 运行检查

运行检查（不依赖 pytest 测试集）：
- 后端：导入 + FastAPI TestClient smoke
- 前端：`npm run build`

**使用场景**：
- 验证代码修改
- 提交代码前
- CI/CD 流程

### deploy.bat - 部署构建

构建生产版本：
- 构建前端（npm run build）
- 复制前端静态文件到 dist/frontend
- 复制后端代码到 dist/backend
- 排除测试和缓存文件
- 生成部署说明文档

**使用场景**：
- 准备生产部署
- 打包发布版本

### clean.bat - 清理项目

删除以下内容:
- 前端 node_modules
- 前端 dist
- 后端 __pycache__
- 后端 .pytest_cache
- 部署 dist 目录

**使用场景**：
- 重新安装依赖
- 清理磁盘空间
- 解决依赖冲突

### manage_sessions.py - 管理会话

管理会话文件：
- 查看所有会话列表
- 查看会话详细信息
- 删除指定天数前的会话
- 删除所有会话（需确认）
- 显示文件夹大小

**使用方法**：

```bash
# 交互式菜单（推荐）
python manage_sessions.py
```

**使用场景**：
- 查看录制的会话
- 定期清理旧数据
- 释放磁盘空间
- 数据维护

## 💡 提示

1. **所有脚本都会自动切换到项目根目录**，无论从哪里运行都能正常工作
2. **推荐使用根目录的核心脚本**（build.bat、start.bat、stop.bat）
3. **这些辅助脚本主要用于特定场景**，如单独测试、部署等

## 🔗 相关文档

- [完整脚本文档](../../docs/scripts.md)
- [项目 README](../../README.md)
