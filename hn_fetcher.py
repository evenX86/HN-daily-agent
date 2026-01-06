"""
HN抓取模块
负责从 Hacker News 获取排行榜和文章内容
"""
import requests
from config import get_no_proxy


class HNFetcher:
    """Hacker News 数据抓取器"""

    def __init__(self):
        self.no_proxy = get_no_proxy()

    def get_top_stories(self, n=5):
        """
        获取 Hacker News 排行榜前 N 名的文章

        Args:
            n: 获取文章数量，默认 5 篇

        Returns:
            list: 文章列表，每篇文章包含 title, url, score
        """
        print(f"[系统] 正在查询 HN 排行榜前 {n} 名...")
        try:
            top_ids = requests.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                proxies=self.no_proxy,
                timeout=10
            ).json()

            stories = []
            for sid in top_ids[:n]:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    proxies=self.no_proxy,
                    timeout=10
                ).json()
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

    def fetch_content(self, url):
        """
        使用 Jina Reader 抓取文章内容

        Args:
            url: 文章链接

        Returns:
            str: 抓取到的文章内容，失败返回空字符串
        """
        if not url:
            return ""
        print(f"[阅读] 正在抓取: {url} ...")
        jina_url = f"https://r.jina.ai/{url}"
        try:
            response = requests.get(jina_url, proxies=self.no_proxy, timeout=20)
            return response.text
        except Exception as e:
            print(f"   -> 读取失败: {e}")
            return ""
