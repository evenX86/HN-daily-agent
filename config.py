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
    return os.getenv("DEEPSEEK_API_KEY")


def get_pushplus_token():
    """获取 PushPlus Token"""
    return os.getenv("PUSHPLUS_TOKEN")


def get_no_proxy():
    """获取 NO_PROXY 配置字典，用于禁用代理"""
    return {
        "http": None,
        "https": None,
    }
