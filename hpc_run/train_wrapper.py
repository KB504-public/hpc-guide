#!/usr/bin/env python3
"""
HPC 训练包装器 - 在计算节点运行
用于包装训练任务执行，完成后写入标记文件供监控程序检测

使用方式: python train_wrapper.py
配置文件: config/config.yaml
"""
import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目路径以导入 src 模块
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import ConfigLoader


def run_training(work_dir: Path, command: str, log_dir: Path, marker_file: str = '.train_complete.json') -> int:
    """
    执行训练任务
    
    Args:
        work_dir: 工作目录
        command: 训练命令
        log_dir: 日志目录
        marker_file: 完成标记文件名
        
    Returns:
        退出码
    """
    # 切换到工作目录
    work_dir = Path(work_dir).resolve()
    os.chdir(work_dir)
    
    # 准备日志目录
    log_dir = work_dir / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成日志文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"train_{timestamp}.log"
    
    print(f"[训练包装器] 工作目录: {work_dir}")
    print(f"[训练包装器] 执行命令: {command}")
    print(f"[训练包装器] 日志文件: {log_file}")
    print(f"[训练包装器] 完成标记: {marker_file}")
    print("-" * 60)
    
    # 记录开始时间
    start_time = time.time()
    start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 执行训练命令
    command_parts = command.split()
    
    # 智能处理 Python 命令
    if command_parts[0] in ("python", "python3"):
        # 尝试找到可用的 Python
        for py_cmd in ['python3', 'python', sys.executable]:
            if shutil.which(py_cmd):
                command_parts[0] = py_cmd
                break
        # 添加 -u 参数禁用缓冲
        if '-u' not in command_parts:
            command_parts.insert(1, '-u')
    
    # 启动训练进程，捕获输出
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"[训练开始] {start_time_str}\n")
        f.write(f"[命令] {command}\n")
        f.write(f"[工作目录] {work_dir}\n")
        f.write("-" * 60 + "\n\n")
        f.flush()
        
        process = subprocess.Popen(
            command_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 实时读取并保存输出
        if process.stdout:
            for line in process.stdout:
                # 打印到控制台
                print(line, end='')
                # 写入日志文件
                f.write(line)
                f.flush()
        
        # 等待进程结束
        return_code = process.wait()
    
    # 记录结束时间
    end_time = time.time()
    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elapsed = round(end_time - start_time, 2)
    
    # 追加结束信息到日志
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("\n" + "-" * 60 + "\n")
        f.write(f"[训练结束] {end_time_str}\n")
        f.write(f"[运行时长] {elapsed}s\n")
        f.write(f"[退出码] {return_code}\n")
    
    print("-" * 60)
    print(f"[训练包装器] 训练完成")
    print(f"[训练包装器] 运行时长: {elapsed}s")
    print(f"[训练包装器] 退出码: {return_code}")
    
    # 创建完成标记文件
    marker_path = work_dir / marker_file
    completion_info = {
        "status": "completed",
        "start_time": start_time_str,
        "end_time": end_time_str,
        "elapsed_seconds": elapsed,
        "return_code": return_code,
        "command": command,
        "work_dir": str(work_dir),
        "log_file": str(log_file),
        "timestamp": time.time()
    }
    
    with open(marker_path, 'w', encoding='utf-8') as f:
        json.dump(completion_info, f, indent=2, ensure_ascii=False)
    
    print(f"[训练包装器] 已创建完成标记: {marker_path}")
    
    return return_code


def main():
    """主函数 - 从配置文件读取参数并执行训练"""
    # 默认配置文件路径
    project_root = Path(__file__).parent
    config_path = project_root / "config" / "config.yaml"
    
    print(f"[训练包装器] 使用配置文件: {config_path}")
    
    # 加载配置
    loader = ConfigLoader(config_path)
    config = loader.load()
    
    if not loader.validate():
        print("[错误] 配置文件验证失败")
        return 1
    
    # 从配置文件读取参数
    work_dir = config['train']['work_dir']
    command = config['train']['command']
    log_dir = config['train']['log']['dir']
    marker_file = '.train_complete.json'  # 固定标记文件名
    
    # 执行训练
    return_code = run_training(work_dir, command, log_dir, marker_file)
    return return_code


if __name__ == "__main__":
    sys.exit(main())
