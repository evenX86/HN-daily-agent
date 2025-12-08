import os
import time
import requests
import httpx
import random
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# 1. 初始化设置
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
pushplus_token = os.getenv("PUSHPLUS_TOKEN")

# --- 全平台统一使用强力模式 ---
print("[网络] 正在初始化网络配置 (全平台统一模式)...")

# 无论在哪里，都强制不信任系统环境代理，直接直连
# timeout=120s 给 AI 足够的思考时间
http_client = httpx.Client(trust_env=False, timeout=120.0)

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com",
    http_client=http_client
)

# requests 库也强制禁用代理
NO_PROXY = {"http": None, "https": None}
# ------------------------------------------

def get_top_n_stories(n=5):
    """获取 Hacker News 排行榜前 N 名的文章"""
    print(f"[系统] 正在查询 HN 排行榜前 {n} 名...")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        # 使用 NO_PROXY
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", headers=headers, proxies=NO_PROXY, timeout=15).json()
        
        stories = []
        for sid in top_ids[:n]:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", headers=headers, proxies=NO_PROXY, timeout=15).json()
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
        response = requests.get(jina_url, proxies=NO_PROXY, timeout=30)
        return response.text
    except Exception as e:
        print(f"   -> 读取失败: {e}")
        return ""

def summarize_article(title, content):
    """单篇文章总结"""
    print(f"[思考] 正在总结: {title} ...")
    
    # 截取适量长度
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
    
    # 获取当前详细时间，防止 PushPlus 判重
    now = datetime.now()
    today_str = now.strftime("%m月%d日")
    time_str = now.strftime("%H:%M:%S")
    
    final_title = f"{today_str} Hacker News 日报"
    
    # 在正文里加上具体的生成时间，确保每次内容都不一样
    final_body = f"# Hacker News 精选 (Top {len(content_list)})\n"
    final_body += f"> 生成时间: {time_str}\n\n---\n"
    
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
        # 使用 NO_PROXY
        resp = requests.post(url, json=data, proxies=NO_PROXY, timeout=15)
        resp_json = resp.json()
        if resp_json.get("code") == 200:
            print(f"[成功] [{final_title}] 推送完成！")
        else:
            # 打印详细错误
            print(f"[失败] 推送被拒绝: {resp_json}")
    except Exception as e:
        print(f"[错误] 推送网络错误: {e}")

# --- 主程序 ---
if __name__ == "__main__":
    print("[系统] Agent 开始工作...")
    
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
        
        # 保持间隔，礼貌爬取
        time.sleep(2)

    if digest_data:
        send_wechat_digest(digest_data)
    else:
        print("[系统] 今天没有抓取到有效新闻。")