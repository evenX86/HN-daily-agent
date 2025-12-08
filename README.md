#  Hacker News Daily Digest (AI Agent)

![License](https://img.shields.io/github/license/GeYugong/HN-daily-agent)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-critical)

> 一个运行在 GitHub Actions 上的 AI 智能体。每天早上 6:00 自动抓取 Hacker News 热门文章，利用 DeepSeek 进行深度总结，并推送到你的微信。

##  特性

- **自动抓取**：每天定时获取 Hacker News Top 榜单。
- **智能去广**：使用 Jina Reader 提取纯净网页内容。
- **深度总结**：调用 DeepSeek V3 (OpenAI 接口) 生成中文技术简报。
- **微信推送**：通过 PushPlus 推送 Markdown 格式日报到手机。
- **零成本**：完全基于 GitHub Actions 免费运行，无需服务器。


##  如何使用 

你不需要写任何代码，只需要 Fork 本项目并配置 Token。

### 1. Fork 本仓库
点击右上角的 **Fork** 按钮，将项目复刻到你的 GitHub 账号下。

### 2. 获取 API Key
- **DeepSeek API Key**: [点击申请](https://platform.deepseek.com/) 
- **PushPlus Token**: [点击获取](http://www.pushplus.plus/) (微信扫码)

### 3. 配置 GitHub Secrets
在你的 GitHub 仓库页面：
1. 点击 `Settings` -> `Secrets and variables` -> `Actions`。
2. 点击 `New repository secret`，添加以下两个变量：
   - `DEEPSEEK_API_KEY`: 粘贴你的 DeepSeek 密钥。
   - `PUSHPLUS_TOKEN`: 粘贴你的 PushPlus Token。

### 4. 启用自动运行
1. 点击仓库上方的 `Actions` 标签。
2. 如果看到警告，点击 "I understand my workflows, go ahead and enable them"。
3. 你可以点击左侧 `Daily HN Digest` -> `Run workflow` 手动测试一次。

以后每天北京时间 06:00，它会自动运行。

## 🛠️ 技术栈
- **Python 3.9**
- **LangChain / OpenAI SDK**
- **DeepSeek V3** (LLM)
- **Jina Reader** (Web Parsing)
- **GitHub Actions** (CI/CD)

