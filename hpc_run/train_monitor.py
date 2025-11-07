#!/usr/bin/env python3
"""
训练监控器 - 在登录节点运行
负责：
1. 定期检查训练完成标记文件
2. 发现标记文件后读取训练信息
3. 生成报告并推送通知
4. 清理标记文件
"""
import sys
import os
import time
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加 src 到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from utils.config_loader import ConfigLoader
from core.reporter import ReportGenerator
from notifier.base import build_notifier


def check_marker_file(marker_path: Path) -> dict:
    """
    检查完成标记文件是否存在并读取
    
    Returns:
        如果存在返回完成信息字典，否则返回 None
    """
    if not marker_path.exists():
        return None
    
    try:
        with open(marker_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        return info
    except Exception as e:
        print(f"[ERROR] 读取标记文件失败: {e}")
        return None


def send_notification(completion_info: dict, config: dict):
    """发送完成通知"""
    # 生成报告
    reporter = ReportGenerator()
    
    # 将完成信息转换为 process_info 格式
    process_info = {
        "pid": "N/A",
        "command": completion_info.get("command", "unknown"),
        "work_dir": completion_info.get("work_dir", "unknown"),
        "start_time": completion_info.get("start_time", ""),
        "end_time": completion_info.get("end_time", ""),
        "elapsed": completion_info.get("elapsed_seconds", 0),
        "return_code": completion_info.get("return_code", -1),
    }
    
    # 添加日志文件信息
    log_file = completion_info.get("log_file")
    if log_file:
        process_info["log_file"] = log_file
    
    markdown_report = reporter.generate_markdown(process_info)
    
    # 添加日志文件路径到报告
    if log_file:
        markdown_report += f"\n**日志文件:** `{log_file}`"
    
    # 发送通知
    notifier_type = config['notification']['type']
    print(f"[监控器] 使用通知器: {notifier_type}")
    
    if notifier_type.lower() == 'console':
        # console: 在终端打印
        print("\n" + "="*60)
        print(markdown_report)
        print("="*60)
    else:
        # xxtui 或其他: 推送通知
        try:
            # 构建通知器配置
            notifier_config = config['notification'].get(notifier_type.lower(), {})
            
            # 如果是 xxtui，检查 API 密钥
            if notifier_type.lower() == 'xxtui':
                api_key = notifier_config.get('api_key', '') or os.getenv('XXTUI_KEY', '')
                if api_key:
                    notifier_config['api_key'] = api_key
            
            # 创建通知器并发送
            notifier = build_notifier(notifier_type, **notifier_config)
            notifier.send_markdown(markdown_report)
            print(f"[监控器] 通知发送成功")
        except Exception as e:
            print(f"[ERROR] 发送通知失败: {e}")
            print("\n" + "="*60)
            print(markdown_report)
            print("="*60)


def main():
    parser = argparse.ArgumentParser(description='训练监控器 - 检测训练完成并发送通知')
    parser.add_argument('--work-dir', required=True, help='训练脚本所在目录（需监控的目录）')
    parser.add_argument('--marker-file', default='.train_complete.json',
                       help='完成标记文件名')
    parser.add_argument('--interval', type=int, default=10,
                       help='检查间隔（秒）')
    parser.add_argument('--config', default='config/config.yaml',
                       help='配置文件路径')
    parser.add_argument('--once', action='store_true',
                       help='只检查一次（不循环）')
    args = parser.parse_args()
    
    # 加载配置
    config_path = project_root / args.config
    if not config_path.exists():
        print(f"[ERROR] 配置文件不存在: {config_path}")
        return 1
    
    loader = ConfigLoader(config_path)
    try:
        config = loader.load()
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return 1
    
    # 验证通知配置
    if 'notification' not in config:
        print("[ERROR] 配置文件缺少 notification 配置")
        return 1
    
    # 准备监控路径
    work_dir = Path(args.work_dir).resolve()
    marker_file = work_dir / args.marker_file
    
    print(f"[监控器] 监控目录: {work_dir}")
    print(f"[监控器] 标记文件: {marker_file}")
    print(f"[监控器] 检查间隔: {args.interval}s")
    print(f"[监控器] 通知方式: {config['notification']['type']}")
    
    if args.once:
        print(f"[监控器] 单次检查模式")
        print("-" * 60)
        
        # 单次检查
        completion_info = check_marker_file(marker_file)
        if completion_info:
            print(f"[监控器] 发现完成标记！")
            send_notification(completion_info, config)
            
            # 删除标记文件
            try:
                marker_file.unlink()
                print(f"[监控器] 已清理标记文件")
            except Exception as e:
                print(f"[WARN] 清理标记文件失败: {e}")
            
            return 0
        else:
            print(f"[监控器] 未发现完成标记")
            return 1
    else:
        print(f"[监控器] 开始循环监控...")
        print("-" * 60)
        
        check_count = 0
        try:
            while True:
                check_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                completion_info = check_marker_file(marker_file)
                if completion_info:
                    print(f"\n[{timestamp}] 发现完成标记！")
                    send_notification(completion_info, config)
                    
                    # 删除标记文件
                    try:
                        marker_file.unlink()
                        print(f"[监控器] 已清理标记文件")
                    except Exception as e:
                        print(f"[WARN] 清理标记文件失败: {e}")
                    
                    print(f"[监控器] 监控任务完成，退出")
                    return 0
                else:
                    # 只在前几次检查时打印，避免刷屏
                    if check_count <= 3 or check_count % 30 == 0:
                        print(f"[{timestamp}] 第 {check_count} 次检查 - 未发现完成标记，继续等待...")
                
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print(f"\n[监控器] 用户中断，退出监控")
            return 0


if __name__ == "__main__":
    sys.exit(main())
