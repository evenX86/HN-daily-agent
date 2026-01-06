#  Hacker News Daily Digest (AI Agent)

![License](https://img.shields.io/github/license/GeYugong/HN-daily-agent)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-critical)

> 一个运行在 GitHub Actions 上的 AI 智能体。每天早上 6:00 自动抓取 Hacker News 热门文章和 GitHub Trending 项目，生成简报和原文链接，并推送至个人微信。

##  特性

- **自动抓取**：每天定时获取 Hacker News Top 榜单和 GitHub Trending 热门项目。
- **智能去广**：使用 Jina Reader 提取纯净网页内容。
- **深度总结**：调用 DeepSeek (OpenAI 接口) 生成中文技术简报。
- **微信推送**：通过 PushPlus 推送 Markdown 格式日报到手机。
- **零成本**：完全基于 GitHub Actions 免费运行，无需服务器。
- **模块化架构**：代码结构清晰，易于维护和扩展。


##  如何使用 

你不需要写任何代码，只需要 Fork 本项目并配置 Token。

### 1. Fork 本仓库
点击右上角的 **Fork** 按钮，将项目复刻到你的 GitHub 账号下。

### 2. 获取 API Key
- **DeepSeek API Key**: [点击申请](https://platform.deepseek.com/) （申请API并充值少量金额）
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

##  技术栈
- **Python 3.9+**
- **OpenAI SDK** (DeepSeek API 兼容)
- **DeepSeek** (LLM)
- **Jina Reader** (网页解析)
- **GitHub Actions** (自动化调度)

##  项目结构

```
.
├── config.py              # 环境配置和凭证管理
├── hn_fetcher.py          # Hacker News 抓取模块
├── github_trending.py     # GitHub Trending 抓取模块
├── summarizer.py          # 文章总结模块
├── notifier.py            # 微信推送模块
├── news_agent.py          # 主程序入口
└── requirements.txt       # 依赖列表
```

