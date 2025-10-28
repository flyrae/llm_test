"""数据验证工具"""
from typing import Optional
import re


def validate_api_endpoint(endpoint: Optional[str]) -> bool:
    """验证API端点格式"""
    if not endpoint:
        return True
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(endpoint) is not None


def encrypt_api_key(api_key: str) -> str:
    """加密API密钥（简单实现，生产环境应使用cryptography库）"""
    # TODO: 实现真正的加密
    return api_key


def decrypt_api_key(encrypted_key: str) -> str:
    """解密API密钥"""
    # TODO: 实现真正的解密
    return encrypted_key
