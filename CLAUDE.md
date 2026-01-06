# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an AI agent that runs on GitHub Actions to deliver a daily Hacker News digest to WeChat. The workflow:
1. Fetches top 5 stories from Hacker News API
2. Extracts clean content using Jina Reader
3. Summarizes each article using DeepSeek V3 (via OpenAI-compatible API)
4. Pushes a Markdown-formatted digest to WeChat via PushPlus

## Commands

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variables in .env file:
# DEEPSEEK_API_KEY=your_key_here
# PUSHPLUS_TOKEN=your_token_here

# Run the agent
python news_agent.py
```

### GitHub Actions
- Workflow: `.github/workflows/daily_run.yml`
- Schedule: Daily at UTC 22:00 (Beijing 06:00)
- Manual trigger: Go to Actions tab → Daily HN Digest → Run workflow
- Required secrets: `DEEPSEEK_API_KEY`, `PUSHPLUS_TOKEN`

## Architecture

**Single-file design**: All logic is in `news_agent.py`

**Network configuration** (lines 16-28):
- Uses `httpx.Client(trust_env=False)` to bypass system proxy settings
- `NO_PROXY` dict is passed to all `requests.get()` calls to prevent proxy interference
- DeepSeek client uses the custom http_client

**Main functions**:
- `get_top_n_stories(n)`: Fetches HN top stories via Firebase API
- `fetch_content_with_jina(url)`: Uses Jina Reader API (`https://r.jina.ai/{url}`) for content extraction
- `summarize_article(title, content)`: Calls DeepSeek "deepseek-chat" model for Chinese summarization
- `send_wechat_digest(content_list)`: Sends Markdown digest via PushPlus API

**Execution flow** (main section, lines 130-157):
1. Fetch top 5 stories
2. For each story: fetch content via Jina → summarize via DeepSeek → append to digest
3. Push final digest to WeChat

## Key Implementation Details

- The agent skips HN posts that don't have external URLs (e.g., "Ask HN" text-only posts)
- Content shorter than 100 characters is considered a fetch failure and falls back to a generic message
- A 1-second sleep between articles prevents rate limiting
- All HTTP requests use explicit `timeout` parameters
- The OpenAI client is configured for DeepSeek's API endpoint (`https://api.deepseek.com`)
