# 脚本说明

项目提供一组 bat 脚本，方便在 Windows 上快速安装/检查/启动。

## 根目录脚本

| 脚本 | 作用 |
|------|------|
| `build.bat` | 检查环境 → 必要时安装依赖 → 后端 smoke 检查 + 前端 build |
| `start.bat` | 启动后端（新窗口）+ 启动前端（新窗口） |
| `stop.bat` | 停止通过窗口标题启动的后端/前端进程 |

## backend/scripts/

| 脚本 | 作用 |
|------|------|
| `setup.bat` | 安装后端依赖 + Playwright 浏览器 + 前端依赖 |
| `test.bat` | 后端 smoke 检查 + 前端 build（不依赖 pytest） |
| `deploy.bat` | 生成 `dist/` 部署包（前端静态文件 + 后端代码） |
| `clean.bat` | 清理 node_modules/dist/cache，并提供会话数据管理入口 |
| `manage_sessions.py` | 交互式管理 `backend/runs/`（查看/清理/导出） |
| `smoke_test.py` | 后端 smoke 检查（供脚本调用） |

## 推荐工作流

1. 首次使用：`build.bat`
2. 日常开发：`start.bat` / `stop.bat`
3. 想检查当前是否可跑：`backend\\scripts\\test.bat`

**最后更新**：2026-01-20
