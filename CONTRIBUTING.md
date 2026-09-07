# 贡献指南

感谢您对 Web Session Recorder 项目的关注！以下是参与贡献的流程。

## 开发环境准备

1. **克隆仓库**

   ```bash
   git clone https://github.com/LPK3215/web-session-recorder.git
   cd web-session-recorder
   ```

2. **安装后端依赖**

   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   playwright install
   ```

3. **安装前端依赖**

   ```bash
   cd ../frontend
   npm install
   ```

4. **构建并启动**

   ```bat
   :: 回到项目根目录
   cd ..
   build.bat
   start.bat
   ```

   前端运行在 `http://localhost:5173`，后端在 `http://localhost:8000`。

## 分支策略

- `main`：稳定发布分支
- `dev`：开发集成分支（如存在）
- 功能分支命名：`feature/<简述>`、修复分支：`fix/<简述>`

## 提交规范

使用 Conventional Commits 格式：

| 类型 | 说明 |
|---|---|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `refactor` | 代码重构（无功能变化） |
| `chore` | 构建/工具/依赖变更 |
| `test` | 测试相关 |

示例：`feat: add screenshot compression support`

## 代码规范

### Python（后端）

- 使用 `black` 格式化代码
- 类型注解：公共 API 必须有类型标注
- 文档字符串：公共函数/类使用 docstring

### JavaScript/Vue（前端）

- 使用 ESLint + Prettier
- Vue 组件采用 `<script setup>` 语法
- 组件命名使用 PascalCase

## 测试

```bash
# 后端 smoke test
cd backend
python scripts/smoke_test.py

# 前端构建验证
cd ../frontend
npm run build
```

## Pull Request 流程

1. Fork 仓库并创建功能分支
2. 确保代码通过本地测试
3. 提交 PR 并描述变更内容
4. 等待 CI 检查通过
5. 代码审查通过后合并

## 报告 Bug / 提建议

请通过 [GitHub Issues](https://github.com/LPK3215/web-session-recorder/issues) 提交，描述：

- 复现步骤
- 期望行为与实际行为
- 环境信息（OS、浏览器版本、Python 版本）

## 许可证

贡献的代码将遵循项目许可证（MIT）。
