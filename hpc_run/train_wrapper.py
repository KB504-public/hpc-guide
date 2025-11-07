#!/usr/bin/env python3
"""
训练包装器 - 在计算节点运行
负责：
1. 套壳执行训练脚本
2. 捕获训练输出
3. 训练完成后保存完成标记文件（包含执行信息）
"""
import sys
import os
import subprocess
import time
import json
import argparse
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description='训练任务包装器')
    parser.add_argument('--work-dir', required=True, help='训练脚本所在目录')
    parser.add_argument('--command', required=True, help='训练命令')
    parser.add_argument('--log-dir', default='logs', help='日志保存目录')
    parser.add_argument('--marker-file', default='.train_complete.json', 
                       help='完成标记文件名')
    args = parser.parse_args()
    
    # 切换到工作目录
    work_dir = Path(args.work_dir).resolve()
    os.chdir(work_dir)
    
    # 准备日志目录
    log_dir = work_dir / args.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成日志文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"train_{timestamp}.log"
    
    print(f"[训练包装器] 工作目录: {work_dir}")
    print(f"[训练包装器] 执行命令: {args.command}")
    print(f"[训练包装器] 日志文件: {log_file}")
    print(f"[训练包装器] 完成标记: {args.marker_file}")
    print("-" * 60)
    
    # 记录开始时间
    start_time = time.time()
    start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 执行训练命令
    command_parts = args.command.split()
    
    # 智能处理 Python 命令
    if command_parts[0] in ("python", "python3"):
        import shutil
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
        f.write(f"[命令] {args.command}\n")
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
    marker_file = work_dir / args.marker_file
    completion_info = {
        "status": "completed",
        "start_time": start_time_str,
        "end_time": end_time_str,
        "elapsed_seconds": elapsed,
        "return_code": return_code,
        "command": args.command,
        "work_dir": str(work_dir),
        "log_file": str(log_file),
        "timestamp": time.time()
    }
    
    with open(marker_file, 'w', encoding='utf-8') as f:
        json.dump(completion_info, f, indent=2, ensure_ascii=False)
    
    print(f"[训练包装器] 已创建完成标记: {marker_file}")
    
    return return_code


if __name__ == "__main__":
    sys.exit(main())
