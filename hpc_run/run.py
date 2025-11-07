#!/usr/bin/env python3
"""
HPC Run - 主程序
监控训练任务执行，完成后发送通知
"""
import sys
from pathlib import Path

# 添加 src 到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from utils.config_loader import ConfigLoader, Logger
from core.executor import ProcessExecutor
from core.reporter import ReportGenerator
from notifier.base import build_notifier


def main():
    """主函数"""
    # 1. 加载配置文件
    print("[INFO] 加载配置文件...")
    config_path = project_root / "config" / "config.yaml"
    loader = ConfigLoader(config_path)
    
    try:
        config = loader.load()
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return
    
    # 验证配置
    if not loader.validate():
        print("[ERROR] 配置验证失败，请检查配置文件")
        return
    
    print("[INFO] 配置加载成功\n")
    
    # 2. 创建日志记录器
    logger = Logger(enable_console=True)
    logger.info("开始任务执行流程")
    
    # 3. 从配置构建训练配置（直接使用配置中的 command）
    train_config = {
        "work_dir": config['train']['work_dir'],
        "command": config['train']['command']
    }
    
    logger.info(f"工作目录: {train_config['work_dir']}")
    logger.info(f"执行命令: {train_config['command']}")
    logger.info(f"通知方式: {config['notification']['type']}")
    
    confirm = input("\n是否确认执行任务？(y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        logger.info("用户取消执行。任务未启动。")
        return
    print("\n");logger.info("用户确认，开始创建子进程并运行指令...")

    # 4. 创建进程执行器并运行
    executor = ProcessExecutor(train_config, logger=logger)
    
    # 获取日志保存路径
    log_path = config['train'].get('log', {}).get('dir', 'logs')
    save_log = config['train'].get('log', {}).get('save', True)
    
    process_info = executor.run(save_log=save_log, log_path=log_path)
    
    # 5. 生成报告
    print("\n");logger.info("生成任务报告...")
    reporter = ReportGenerator()
    
    # 生成 Markdown 格式报告
    markdown_report = reporter.generate_markdown(process_info)
    
    # 6. 发送通知
    notifier_type = config['notification']['type']
    logger.info(f"使用通知器: {notifier_type}")
    
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
                import os
                api_key = notifier_config.get('api_key', '') or os.getenv('XXTUI_KEY', '')
                if api_key:
                    notifier_config['api_key'] = api_key
            
            # 创建通知器并发送
            notifier = build_notifier(notifier_type, **notifier_config)
            notifier.send_markdown(markdown_report)
        except Exception as e:
            logger.warn(f"发送通知失败: {e}")
            print("\n[WARN] 通知发送失败，以下是报告内容：")
            print("\n" + "="*60)
            print(markdown_report)
            print("="*60)
    
    # 7. 显示结果
    if process_info['return_code'] == 0:
        logger.info("任务执行成功！")
    else:
        logger.warn(f"任务执行失败，退出码: {process_info['return_code']}")


if __name__ == "__main__":
    main()
