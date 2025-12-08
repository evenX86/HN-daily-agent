import os
import time
import requests
import httpx
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# 1. 初始化设置
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
pushplus_token = os.getenv("PUSHPLUS_TOKEN")

# --- 完全隔离本地和云端的配置 ---
# GitHub Actions 会自动注入这个变量
is_github_env = os.getenv("GITHUB_ACTIONS") == "true"

if is_github_env:
    print("[网络] 检测到 GitHub Actions 云端环境：使用原生配置")
    # ☁️ 云端：完全不传递 http_client，使用 SDK 默认行为，仅设置超时
    # 这样可以避免我们手动配置的客户端与云端网络环境冲突
    client = OpenAI(
        api_key=api_key, 
        base_url="https://api.deepseek.com",
        timeout=120.0 
    )
    # requests 使用默认设置
    REQUESTS_PROXIES = None 

else:
    print("[网络] 检测到本地开发环境：启用强力去代理模式")
    # 🏠 本地：必须强制禁用代理，否则连不上
    http_client = httpx.Client(trust_env=False, timeout=120.0)
    
    client = OpenAI(
        api_key=api_key, 
        base_url="https://api.deepseek.com",
        http_client=http_client, # 注入自定义客户端
        timeout=120.0
    )
    # requests 强制禁用代理
    REQUESTS_PROXIES = {"http": None, "https": None}
# --------------------------------

def get_top_n_stories(n=5):
    """获取 Hacker News 排行榜前 N 名的文章"""
    print(f"[系统] 正在查询 HN 排行榜前 {n} 名...")
    try:
        # 增加 headers 伪装成浏览器，防止 HN API 有时候拒绝脚本请求
        headers = {"User-Agent": "Mozilla/5.0"}
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", headers=headers, proxies=REQUESTS_PROXIES, timeout=15).json()
        
        stories = []
        for sid in top_ids[:n]:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", headers=headers, proxies=REQUESTS_PROXIES, timeout=15).json()
            if 'url' in item:
                stories.append({
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'score': item.get('score', 0)
                })
            else:
                print(f"[跳过] 无链接文章: {item.get('title')}")
        
        return stories
    except Exception as e:
        print(f"[错误] 获取列表失败: {e}")
        return []

def fetch_content_with_jina(url):
    """利用 Jina Reader 抓取内容"""
    if not url: return ""
    print(f"[阅读] 正在抓取: {url} ...")
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(jina_url, proxies=REQUESTS_PROXIES, timeout=30)
        return response.text
    except Exception as e:
        print(f"   -> 读取失败: {e}")
        return ""

def summarize_article(title, content):
    """单篇文章总结"""
    print(f"[思考] 正在总结: {title} ...")
    
    # 缩短内容长度，防止 DeepSeek 因为内容过长而处理超时
    # Hacker News 评论区有时候非常长，截取前 4000 字符通常足够概括核心
    safe_content = content[:4000]
    
    prompt = f"""
    请为 Hacker News 的热门文章撰写微型简报。
    标题: {title}
    内容: {safe_content} 
    
    请输出 Markdown 格式，包含：
    1. **一句话核心**：它是什么？
    2. **关键点**：3个以内的技术要点或观点。
    (保持简洁，不要废话，不要使用任何表情符号)
    """

    try:
        # 增加重试机制：如果失败，自动重试一次
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[DeepSeek报错] {e}") 
        return f"总结失败: {e}"

def send_wechat_digest(content_list):
    """汇总推送所有日报到微信"""
    if not pushplus_token:
        print("[警告] 未配置 PUSHPLUS_TOKEN，跳过推送。")
        return

    print("[推送] 正在生成日报并推送...")
    
    today_str = datetime.now().strftime("%m月%d日")
    final_title = f"{today_str} Hacker News 日报"
    
    final_body = f"# Hacker News 精选 (Top {len(content_list)})\n---\n"
    
    for idx, item in enumerate(content_list, 1):
        final_body += f"## {idx}. {item['title']}\n"
        final_body += f"[原文链接]({item['url']})\n\n"
        final_body += f"{item['summary']}\n"
        final_body += "---\n\n" 

    url = "http://www.pushplus.plus/send"
    data = {
        "token": pushplus_token,
        "title": final_title,
        "content": final_body,
        "template": "markdown"
    }
    
    try:
        resp = requests.post(url, json=data, proxies=REQUESTS_PROXIES, timeout=15)
        if resp.json().get("code") == 200:
            print(f"[成功] [{final_title}] 推送完成！")
        else:
            print(f"[失败] 推送被拒绝: {resp.text}")
    except Exception as e:
        print(f"[错误] 推送网络错误: {e}")

# --- 主程序 ---
if __name__ == "__main__":
    print("[系统] Agent 开始工作...")
    
    # 获取前 5 篇
    stories = get_top_n_stories(n=5)
    
    digest_data = []
    
    for story in stories:
        content = fetch_content_with_jina(story['url'])
        
        if len(content) < 100:
            summary = "无法抓取正文，请直接点击链接查看。"
        else:
            summary = summarize_article(story['title'], content)
            
        digest_data.append({
            'title': story['title'],
            'url': story['url'],
            'summary': summary
        })
        
        # 增加间隔到 5 秒，DeepSeek API 有时候对并发有限制
        time.sleep(5)

    if digest_data:
        send_wechat_digest(digest_data)
    else:
        print("[系统] 今天没有抓取到有效新闻。")