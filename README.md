# AI 求职面试助手

面向校园求职场景的网页应用，帮助学生：**简历诊断优化 → 模拟面试 → 面试报告**，一站式备战求职。

> 当前主版本为 **React 独立前端**（`web/` + FastAPI 网关 `api/`）。
> 旧版 Streamlit 界面保留在 `feat/ui-redesign-v2` 分支作为兜底演示，不随主版本更新。

## 功能

- **简历诊断**：粘贴文本或上传 PDF / Word 简历，AI 给出整体评价、优势、不足、修改建议和优化示例。
- **模拟面试**：选择岗位方向（产品经理、市场营销、运营、财务、人力资源、行政文秘、通用管培生或自定义），AI 逐题提问并记录你的回答。
- **面试报告**：按五个维度打分（内容准确性、逻辑条理、表达清晰度、岗位匹配度、临场应变），附亮点、短板、参考回答和提升建议；报告自动保存在本地可回看。

## 快速开始

### 方式一：新版 React 前端（推荐）

1. 安装 Python 3.10+ 与 Node.js 18+。
2. 首次使用先安装依赖：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd web
npm install
cd ..
```

3. 复制 `.env.example` 为 `.env`，按需填写 `LLM_API_KEY`（留空则进入模拟演示模式）。
4. **双击 `启动新版前端.bat`**，浏览器打开 `http://localhost:5173`。

> 关闭两个黑色小窗口，服务即停止；再次体验时重新双击即可。

### 方式二：旧版 Streamlit（兜底）

1. 安装 Python 3.10 或更高版本。
2. 双击项目文件夹里的 `启动应用.bat`，浏览器会自动打开应用。

如果双击无效，再手动在项目目录执行：

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

3. 复制 `.env.example` 为 `.env`，按需填写 `LLM_API_KEY`（留空则进入模拟演示模式）。
4. 启动应用：

```bash
streamlit run app.py
```

5. 浏览器会自动打开 `http://localhost:8501`。

> 关闭那个黑色小窗口，应用就会停止；重新体验时再次双击 `启动应用.bat` 即可。

## 目录结构

```text
app.py        界面入口（Streamlit）
ui/           界面层：首页、简历诊断、模拟面试、面试报告
api/          FastAPI 网关：把业务层暴露给 React 前端
web/          React 前端（Vite + TypeScript + Tailwind CSS）
services/     业务层：解析、诊断、面试、报告、存储
llm/          模型接口层：配置、统一客户端、提示词
models/       数据结构定义（各层之间的"接口契约"）
docs/         开发文档、架构文档、路线图、开发规范
tests/        自动化测试
data/reports/ 本地报告存储（不入库）
```

### API 网关（api/）

- `POST /api/resume/parse` 粘贴文本或上传 PDF/Word
- `POST /api/resume/clarify` AI 提取简历待确认项
- `POST /api/resume/diagnose` 生成专属优化方案
- `POST /api/interview/start|answer|followup|followup-answer|next|finish` 面试状态机（状态快照往返）
- `POST /api/reports/generate`、`GET/DELETE /api/reports[/{id}]` 复盘生成与本地历史
- `GET /api/health`、`GET /api/jobs` 健康检查与岗位目录

## 隐私说明

应用不会把简历原文上传到服务器数据库；面试报告仅保存在使用者本地设备，可随时删除。

## 部署（第 4 周）

### 推送到 GitHub

双击 `推送GitHub.bat`（脚本会自动安装 GitHub CLI、登录、创建公开仓库并推送 `main` 分支与全部标签）。

### 免费托管（Sealos，推荐）

> Hugging Face Spaces 的 Docker SDK 现在需要付费专业版；静态空间虽然免费，但跑不了 FastAPI 后端，因此改用 **Sealos**（国内平台、访问快、无需信用卡，注册赠送 7 天免费试用；轻量配置按小时计费，演示期间暂停不计费）。

1. 确保 GitHub 仓库已推送（双击 `推送GitHub.bat`）。
2. 双击 `部署Sealos.bat`，脚本会把仓库地址复制到剪贴板并打开 Sealos 控制台。
3. 在 Sealos 控制台（`cloud.sealos.io`）注册/登录（GitHub 或手机号均可，无需信用卡）。
4. 进入「应用管理 / App Launchpad」→「创建应用」，选择 **GitHub 导入**，粘贴仓库地址 `Yuvzol0932/ai-job-interview-assistant`，分支 `main`。
5. Sealos 会自动识别仓库内的 `Dockerfile` 并构建；在端口配置中暴露容器端口 **7860**。
6. 在应用的环境变量中配置：

```text
LLM_API_KEY=你的密钥
LLM_MODE=real
```

> 不配置 `LLM_API_KEY` 时默认进入 mock 演示模式，可先验证部署是否成功。

7. 点击部署，等待首次构建完成（约 5–15 分钟），打开生成的公网地址验证。

> 若试用期后仍需长期在线：演示/验收期间开机，其余时间暂停即可，费用通常为每小时几分钱；也可以完全不充值，用本地演示兜底。

### 国内访问与兜底

- 电脑与手机分别打开 Sealos 部署链接验证；若访问慢或不可用，以「本地运行 + 录屏演示 + 演示视频」作为正式演示路径。
- 本地运行：双击 `启动新版前端.bat`，打开 `http://localhost:5173`。

### 真机回归

服务启动后执行 `scripts\真实模型回归.py`，会以真实模型完整跑通“解析 → 补全 → 诊断 → 3 题面试 + 追问 → 复盘 → 历史清理”，并打印每步耗时。

## 参赛说明

本作品参加第一届 AI 应用开发大赛，详细规划见 `docs/` 目录。
