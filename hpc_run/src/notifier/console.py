"""
控制台通知器实现
用于测试或开发环境，直接打印到控制台
"""
from .base import Notifier


class ConsoleNotifier(Notifier):
    """控制台通知器（用于测试）"""
    
    def __init__(self, **kwargs):
        """初始化控制台通知器"""
        pass
    
    def send_markdown(self, content: str) -> None:
        """
        打印 Markdown 消息到控制台
        
        Args:
            content: Markdown 格式的消息内容
        """
        print("\n" + "="*60)
        print("📢 任务报告 (Console Notifier)")
        print("="*60)
        print(content)
        print("="*60 + "\n")
