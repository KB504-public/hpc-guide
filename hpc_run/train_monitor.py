#!/usr/bin/env python3
"""
HPC 训练监控器 - 在登录节点运行
轮询检测训练完成标记文件，发现完成后发送通知

使用方式: python train_monitor.py
配置文件: config/config.yaml
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 添加项目路径以导入 src 模块
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import ConfigLoader
from src.core.reporter import ReportGenerator
from src.notifier.console import ConsoleNotifier
from src.notifier.xxtui import XxtuiNotifier


def check_marker_file(work_dir: Path, marker_file: str) -> dict:
    """
    检查完成标记文件是否存在
    
    Args:
        work_dir: 工作目录
        marker_file: 标记文件名
        
    Returns:
        完成信息字典，如果文件不存在则返回 None
    """
    marker_path = work_dir / marker_file
    
    if not marker_path.exists():
        return None
    
    try:
        with open(marker_path, 'r', encoding='utf-8') as f:
            completion_info = json.load(f)
        return completion_info
    except Exception as e:
        print(f"[错误] 读取标记文件失败: {e}")
        return None


def send_notification(notifier_config: dict, report: str):
    """
    发送通知
    
    Args:
        notifier_config: 通知器配置
        report: 报告内容
    """
    notifier_type = notifier_config.get('type', 'console').lower()
    
    if notifier_type == 'console':
        notifier = ConsoleNotifier()
    elif notifier_type == 'xxtui':
        xxtui_config = notifier_config.get('xxtui', {})
        # 优先从配置读取，其次从环境变量
        api_key = xxtui_config.get('api_key') or os.getenv('XXTUI_KEY')
        if not api_key:
            print("[错误] 未配置 xxtui API 密钥")
            return
        
        timeout = xxtui_config.get('timeout', 8)
        notifier = XxtuiNotifier(api_key=api_key, timeout=timeout)
    else:
        print(f"[错误] 未知的通知器类型: {notifier_type}")
        return
    
    # 发送通知
    title = "训练完成通知"
    try:
        notifier.send_markdown(report)
        print(f"[监控器] 通知已发送 (类型: {notifier_type})")
    except Exception as e:
        print(f"[错误] 发送通知失败: {e}")


def monitor_training(work_dir: Path, notifier_config: dict, 
                     marker_file: str = '.train_complete.json',
                     interval: int = 60):
    """
    监控训练任务
    
    Args:
        work_dir: 工作目录
        notifier_config: 通知器配置
        marker_file: 标记文件名
        interval: 检查间隔（秒）
    """
    work_dir = Path(work_dir).resolve()
    
    print(f"[监控器] 工作目录: {work_dir}")
    print(f"[监控器] 标记文件: {marker_file}")
    print(f"[监控器] 检查间隔: {interval}秒")
    print("-" * 60)
    
    check_count = 0
    
    while True:
        check_count += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[监控器] 第 {check_count} 次检查 ({current_time})")
        
        # 检查标记文件
        completion_info = check_marker_file(work_dir, marker_file)
        
        if completion_info:
            print(f"[监控器] 检测到训练完成！")
            print(f"[监控器] 开始时间: {completion_info.get('start_time')}")
            print(f"[监控器] 结束时间: {completion_info.get('end_time')}")
            print(f"[监控器] 运行时长: {completion_info.get('elapsed_seconds')}s")
            print(f"[监控器] 退出码: {completion_info.get('return_code')}")
            
            # 读取日志文件最后几行
            log_file = completion_info.get('log_file')
            last_lines = []
            if log_file and Path(log_file).exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_lines = lines[-50:]  # 取最后 50 行
                except Exception as e:
                    print(f"[警告] 读取日志文件失败: {e}")
            
            # 生成报告
            process_info = {
                "pid": "N/A",  # HPC 模式下没有本地 PID
                "command": completion_info.get('command'),
                "work_dir": completion_info.get('work_dir'),
                "start_time": completion_info.get('start_time'),
                "end_time": completion_info.get('end_time'),
                "elapsed": completion_info.get('elapsed_seconds'),
                "return_code": completion_info.get('return_code')
            }
            
            generator = ReportGenerator()
            report = generator.generate_markdown(process_info)
            
            # 如果有日志，追加最后几行
            if last_lines:
                report += "\n\n### 日志摘要（最后 50 行）\n\n```\n"
                report += "".join(last_lines)
                report += "\n```"
            
            print("\n" + "=" * 60)
            print(report)
            print("=" * 60 + "\n")
            
            # 发送通知
            send_notification(notifier_config, report)
            
            # 清理标记文件
            marker_path = work_dir / marker_file
            try:
                marker_path.unlink()
                print(f"[监控器] 已删除标记文件: {marker_path}")
            except Exception as e:
                print(f"[警告] 删除标记文件失败: {e}")
            
            print(f"[监控器] 监控完成")
            break
        
        else:
            print(f"[监控器] 训练尚未完成，等待 {interval} 秒...")
        
        # 等待下一次检查
        time.sleep(interval)


def main():
    """主函数 - 从配置文件读取参数并监控训练"""
    # 默认配置文件路径
    project_root = Path(__file__).parent
    config_path = project_root / "config" / "config.yaml"
    
    print(f"[监控器] 使用配置文件: {config_path}")
    
    # 加载配置
    loader = ConfigLoader(config_path)
    config = loader.load()
    
    if not loader.validate():
        print("[错误] 配置文件验证失败")
        return 1
    
    # 从配置文件读取参数
    work_dir = config['train']['work_dir']
    notifier_config = config.get('notification', {})
    
    # 固定参数
    marker_file = '.train_complete.json'
    interval = 60  # 检查间隔 60 秒
    
    # 开始监控
    monitor_training(
        work_dir=work_dir,
        notifier_config=notifier_config,
        marker_file=marker_file,
        interval=interval
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
