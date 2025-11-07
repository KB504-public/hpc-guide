"""
通知器模块
提供多种通知方式的抽象接口和具体实现
"""
from .base import Notifier, build_notifier

__all__ = ['Notifier', 'build_notifier']
