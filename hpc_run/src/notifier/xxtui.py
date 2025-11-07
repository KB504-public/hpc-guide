"""
Xxtui 通知器实现
支持通过 xxtui.com 发送通知
"""
import os
import requests
from typing import Optional
from .base import Notifier


class XxtuiNotifier(Notifier):
    """Xxtui 通知器"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 8):
        """
        初始化 Xxtui 通知器
        
        Args:
            api_key: API 密钥（可从环境变量 XXTUI_KEY 读取）
            timeout: 请求超时时间（秒）
            
        Raises:
            ValueError: API 密钥缺失
        """
        self.api_key = api_key or os.getenv('XXTUI_KEY', '')
        if not self.api_key:
            raise ValueError(
                'Xxtui API 密钥缺失！\n'
                '请设置环境变量 XXTUI_KEY 或在配置文件中指定 notifier.api_key'
            )
        self.timeout = timeout
        self.url = f'https://www.xxtui.com/xxtui/{self.api_key}'
    
    def send_markdown(self, content: str) -> None:
        """
        发送 Markdown 消息
        
        Args:
            content: Markdown 格式的消息内容
            
        Raises:
            RuntimeError: API 返回错误
            requests.HTTPError: 请求失败
        """
        payload = {
            'content': content,
            'type': 'markdown'
        }
        
        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )
            
            # 检查 HTTP 状态码
            response.raise_for_status()
            
            # 解析响应内容
            try:
                result = response.json()
                # 检查业务状态码
                if 'code' in result and result['code'] != 0:
                    error_msg = result.get('msg', '未知错误')
                    print(f'[xxtui] ❌ 发送失败: {error_msg} (code: {result["code"]})')
                    raise RuntimeError(f'Xxtui API 返回错误: {error_msg}')
                else:
                    print(f'[xxtui] ✅ 发送成功')
            except ValueError:
                # 如果不是 JSON 响应，打印原始内容
                print(f'[xxtui] 响应: {response.status_code} - {response.text}')
                
        except requests.RequestException as e:
            print(f'[xxtui] ❌ 网络请求失败: {e}')
            raise
