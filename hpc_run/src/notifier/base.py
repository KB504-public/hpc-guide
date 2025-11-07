"""
通知器基类和工厂函数
"""
from abc import ABC, abstractmethod


class Notifier(ABC):
    """通知器抽象基类"""
    
    @abstractmethod
    def send_markdown(self, content: str) -> None:
        """
        发送 Markdown 格式的消息
        
        Args:
            content: Markdown 格式的消息内容
        """
        pass


def build_notifier(name: str, **kwargs) -> Notifier:
    """
    通知器工厂函数
    
    Args:
        name: 通知器类型名称（如 'xxtui'）
        **kwargs: 通知器初始化参数
        
    Returns:
        通知器实例
        
    Raises:
        ValueError: 不支持的通知器类型
    """
    name = (name or 'xxtui').lower()
    
    if name == 'xxtui':
        from .xxtui import XxtuiNotifier
        return XxtuiNotifier(**kwargs)
    elif name == 'console':
        from .console import ConsoleNotifier
        return ConsoleNotifier(**kwargs)
    
    raise ValueError(f'不支持的通知器类型: {name}')
