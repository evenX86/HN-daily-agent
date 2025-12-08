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

# --- 🔍 环境与网络检测区 ---
print("="*50)
print("🛠️ 正在进行环境自检...")

# GitHub Actions 会默认包含这个变量
is_github_env = os.getenv("GITHUB_ACTIONS") == "true"

if is_github_env:
    print("☁️ 检测到环境: [GitHub Actions 云端]")
    print("✅ 策略: 使用原生网络配置 (无代理/无魔改)")
    
    # 【云端配置】最纯净的模式，完全依赖 SDK 默认行为
    # 不传递 http_client，也不强制设置 timeout (默认就是 10分钟)
    client = OpenAI(
        api_key=api_key, 
        base_url="https://api.deepseek.com"
    )
    
    # requests 使用系统默认
    REQUESTS_PROXIES = None 

else:
    print("🏠 检测到环境: [本地开发环境]")
    print("🛡️ 策略: 启用强力去代理模式 (trust_env=False)")
    
    # 【本地配置】你的电脑需要这个才能跑通
    custom_http_client = httpx.Client(trust_env=False, timeout=120.0)
    
    client = OpenAI(
        api_key=api_key, 
        base_url="https://api.deepseek.com",
        http_client=custom_http_client
    )
    
    # requests 强制禁用代理
    REQUESTS_PROXIES = {"http": None, "https": None}

print("="*50)
# ---------------------------

def get_top_n_stories(n=5):
    """获取 Hacker News 排行榜前 N 名的文章"""
    print(f"[系统] 正在查询 HN 排行榜前 {n} 名...")
    try:
        # 伪装成浏览器
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
    
    # 进一步缩短输入长度，提高成功率
    safe_content = content[:3000]
    
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
        # 在这里显式设置 timeout，给 API 足够的等待时间
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            timeout=120.0, 
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
    
    now = datetime.now()
    today_str = now.strftime("%m月%d日")
    # 加时间戳防止判重
    time_str = now.strftime("%H:%M:%S")
    
    final_title = f"{today_str} Hacker News 日报"
    
    final_body = f"# Hacker News 精选 (Top {len(content_list)})\n"
    final_body += f"> 更新时间: {time_str}\n\n---\n"
    
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
        # 兼容一下 PushPlus 有时候返回非 JSON 的情况
        try:
            resp_json = resp.json()
            if resp_json.get("code") == 200:
                print(f"[成功] [{final_title}] 推送完成！")
            else:
                print(f"[失败] 推送被拒绝: {resp_json}")
        except:
            print(f"[未知] 推送响应内容: {resp.text}")
            
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
        
        # 稳妥起见，间隔5秒，防止触发 DeepSeek 的速率限制
        time.sleep(5)

    if digest_data:
        send_wechat_digest(digest_data)
    else:
        print("[系统] 今天没有抓取到有效新闻。")