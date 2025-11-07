#!/usr/bin/env python3
"""
报告生成模块
负责生成任务执行的基础报告
"""
from typing import Dict


class ReportGenerator:
    """基础报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        pass
    
    def generate(self, process_info: Dict) -> str:
        """
        生成基础任务报告
        
        Args:
            process_info: 进程信息字典，包含以下字段：
                - pid: 进程 ID
                - command: 执行的命令
                - work_dir: 工作目录
                - start_time: 开始时间
                - end_time: 结束时间
                - elapsed: 运行时长（秒）
                - return_code: 退出码
            
        Returns:
            格式化的报告字符串
        """
        # 构建基础报告
        report = f"""## [任务完成通知]

[命令] {process_info['command']}
[PID] {process_info['pid']}
[工作目录] {process_info['work_dir']}

[开始时间] {process_info['start_time']}
[结束时间] {process_info['end_time']}
[运行时长] {process_info['elapsed']}s
[退出码] {process_info['return_code']}
"""
        
        return report
    
    def generate_markdown(self, process_info: Dict) -> str:
        """
        生成 Markdown 格式的任务报告
        
        Args:
            process_info: 进程信息字典
            
        Returns:
            Markdown 格式的报告字符串
        """
        # 构建 Markdown 报告
        report = f"""## 任务完成通知

**命令:** `{process_info['command']}`  
**PID:** {process_info['pid']}  
**工作目录:** `{process_info['work_dir']}`

**开始时间:** {process_info['start_time']}  
**结束时间:** {process_info['end_time']}  
**运行时长:** {process_info['elapsed']}s  
**退出码:** {process_info['return_code']}
"""
        
        return report
