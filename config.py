"""
配置模块
负责环境变量加载和网络配置初始化
"""
import os
from dotenv import load_dotenv


def load_env():
    """加载 .env 环境变量"""
    load_dotenv()


def get_deepseek_key():
    """获取 DeepSeek API Key"""
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("环境变量 DEEPSEEK_API_KEY 未设置，请在 .env 文件中配置")
    return key


def get_pushplus_token():
    """获取 PushPlus Token"""
    token = os.getenv("PUSHPLUS_TOKEN")
    if not token:
        raise ValueError("环境变量 PUSHPLUS_TOKEN 未设置，请在 .env 文件中配置")
    return token


def get_no_proxy():
    """获取 NO_PROXY 配置字典，用于禁用代理"""
    return {
        "http": None,
        "https": None,
    }
