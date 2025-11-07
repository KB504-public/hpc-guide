# #!/usr/bin/env python3
# """
# 进程执行器模块
# 负责启动和管理子进程，捕获输出
# """
# import subprocess
# import threading
# import sys
# import platform
# from typing import List, Optional
# from pathlib import Path


# class ProcessExecutor:
#     """进程执行器，管理子进程的启动和输出捕获"""
    
#     def __init__(self, cmd: List[str], log_file: str, working_dir: Optional[str] = None, 
#                  new_window: bool = False):
#         """
#         初始化执行器
        
#         Args:
#             cmd: 要执行的命令列表
#             log_file: 日志文件路径
#             working_dir: 工作目录（可选）
#             new_window: 是否在新窗口运行（可选，默认 False）
#         """
#         self.cmd = cmd
#         self.log_file = Path(log_file)
#         self.working_dir = Path(working_dir) if working_dir else None
#         self.new_window = new_window
        
#         self.process: Optional[subprocess.Popen] = None
#         self.output_buffer: List[str] = []
#         self._log_handle = None
#         self._reader_thread: Optional[threading.Thread] = None
#         self._marker_file: Optional[Path] = None  # 新窗口模式的标记文件
    
#     def start(self) -> int:
#         """
#         启动进程
        
#         Returns:
#             进程 PID
            
#         Raises:
#             RuntimeError: 进程启动失败
#         """
#         # 确保日志目录存在
#         self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
#         if self.new_window:
#             # 在新窗口运行
#             return self._start_in_new_window()
#         else:
#             # 在当前窗口运行（捕获输出）
#             return self._start_with_capture()
    
#     def _start_with_capture(self) -> int:
#         """在当前窗口运行并捕获输出"""
#         # 打开日志文件
#         self._log_handle = open(self.log_file, 'w', encoding='utf-8')
        
#         try:
#             # 启动子进程
#             self.process = subprocess.Popen(
#                 self.cmd,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.STDOUT,
#                 bufsize=1,
#                 cwd=self.working_dir
#             )
            
#             # 启动输出读取线程
#             self._reader_thread = threading.Thread(
#                 target=self._read_output,
#                 args=(self.process.stdout, self.output_buffer, self._log_handle),
#                 daemon=True
#             )
#             self._reader_thread.start()
            
#             return self.process.pid
            
#         except Exception as e:
#             if self._log_handle:
#                 self._log_handle.close()
#             raise RuntimeError(f"进程启动失败: {e}")
    
#     def _start_in_new_window(self) -> int:
#         """在新终端窗口运行"""
#         import time
#         system = platform.system()
        
#         # 创建进程标记文件（用于跟踪新窗口中的进程）
#         # 使用绝对路径确保主进程和子进程访问同一个文件
#         marker_file = Path(self.log_file).parent.absolute() / '.training_running'
#         marker_file.parent.mkdir(parents=True, exist_ok=True)
        
#         # 立即创建标记文件
#         marker_file.touch()
        
#         # 构建命令字符串
#         cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in self.cmd)
        
#         # 训练完成后删除标记文件（使用绝对路径）
#         marker_path_str = str(marker_file.absolute())
#         full_cmd_str = f'{cmd_str} ; rm -f "{marker_path_str}"'
        
#         try:
#             if system == 'Darwin':  # macOS
#                 # 使用 osascript 打开 Terminal.app
#                 script = f'''
#                 tell application "Terminal"
#                     activate
#                     do script "cd {self.working_dir or '.'} && {full_cmd_str}"
#                 end tell
#                 '''
#                 self.process = subprocess.Popen(
#                     ['osascript', '-e', script],
#                     stdout=subprocess.PIPE,
#                     stderr=subprocess.PIPE
#                 )
                
#                 # 等待一下让终端窗口打开
#                 time.sleep(0.5)
                
#                 # 检查标记文件是否仍然存在（如果不存在说明训练可能启动失败）
#                 if marker_file.exists():
#                     print(f"✅ 新终端窗口已打开")
#                     print(f"📄 训练日志: {self.working_dir or '.'}/logs/train.log")
#                     print(f"💡 训练将在新窗口中运行")
#                 else:
#                     print(f"⚠️ 标记文件意外消失，可能训练启动失败")
#                     print(f"💡 请检查新窗口中是否有错误")
                
#                 # 保存标记文件路径供后续检查
#                 self._marker_file = marker_file
#                 # 返回一个虚拟 PID（新窗口模式下无法获取真实 PID）
#                 return 99999
                
#             elif system == 'Linux':
#                 # 尝试常见的 Linux 终端
#                 terminals = [
#                     ['gnome-terminal', '--', 'bash', '-c'],
#                     ['xterm', '-e'],
#                     ['konsole', '-e'],
#                 ]
                
#                 for term_cmd in terminals:
#                     try:
#                         full_cmd = term_cmd + [f'cd {self.working_dir or "."} && {full_cmd_str} ; read -p "Press Enter to close..."']
#                         self.process = subprocess.Popen(full_cmd)
                        
#                         # 等待标记文件出现
#                         print(f"⚠️ 等待新窗口中的训练启动...")
#                         for _ in range(30):
#                             if marker_file.exists():
#                                 print(f"✅ 训练已在新终端窗口启动（使用 {term_cmd[0]}）")
#                                 print(f"⚠️ 日志文件由训练脚本自己管理")
#                                 break
#                             time.sleep(0.1)
                        
#                         self._marker_file = marker_file
#                         return self.process.pid
#                     except FileNotFoundError:
#                         continue
                
#                 raise RuntimeError("未找到可用的终端模拟器")
                
#             elif system == 'Windows':
#                 # Windows 使用 start 命令
#                 full_cmd_win = f'cd /d {self.working_dir or "."} && type nul > "{marker_file}" && {cmd_str} & del "{marker_file}"'
#                 full_cmd = ['start', 'cmd', '/k', full_cmd_win]
#                 self.process = subprocess.Popen(full_cmd, shell=True)
                
#                 # 等待标记文件出现
#                 print(f"⚠️ 等待新窗口中的训练启动...")
#                 for _ in range(30):
#                     if marker_file.exists():
#                         print(f"✅ 训练已在新 CMD 窗口启动")
#                         print(f"⚠️ 日志文件由训练脚本自己管理")
#                         break
#                     time.sleep(0.1)
                
#                 self._marker_file = marker_file
#                 return self.process.pid
                
#             else:
#                 raise RuntimeError(f"不支持的操作系统: {system}")
                
#         except Exception as e:
#             raise RuntimeError(f"在新窗口启动进程失败: {e}")
    
#     def _read_output(self, stream, buffer: List[str], log_file):
#         """
#         读取进程输出流
        
#         Args:
#             stream: 输出流
#             buffer: 输出缓冲区
#             log_file: 日志文件句柄
#         """
#         for line in iter(stream.readline, b''):
#             text = line.decode('utf-8', errors='replace')
#             # 实时打印到终端
#             print(text, end='')
#             # 保存到缓冲区
#             buffer.append(text)
#             # 写入日志文件
#             if log_file:
#                 log_file.write(text)
#                 log_file.flush()
        
#         stream.close()
    
#     def wait(self) -> int:
#         """
#         等待进程结束
        
#         Returns:
#             进程退出码
#         """
#         if not self.process:
#             raise RuntimeError("进程尚未启动")
        
#         # 新窗口模式：等待标记文件消失
#         if self.new_window and self._marker_file:
#             import time
#             print("⏳ 等待新窗口中的训练完成...")
#             while self._marker_file.exists():
#                 time.sleep(1)
#             print("✅ 训练已完成（标记文件已删除）")
#             return 0  # 新窗口模式无法获取真实退出码
        
#         # 当前窗口模式：等待进程结束
#         exit_code = self.process.wait()
        
#         # 等待读取线程结束（最多等待1秒）
#         if self._reader_thread:
#             self._reader_thread.join(timeout=1)
        
#         # 关闭日志文件
#         if self._log_handle:
#             self._log_handle.close()
        
#         return exit_code
    
#     def is_running(self) -> bool:
#         """
#         检查进程是否还在运行
        
#         Returns:
#             进程是否运行中
#         """
#         if not self.process:
#             return False
        
#         # 新窗口模式：检查标记文件是否存在
#         if self.new_window and self._marker_file:
#             return self._marker_file.exists()
        
#         # 当前窗口模式：检查进程状态
#         return self.process.poll() is None
    
#     def get_output(self) -> str:
#         """
#         获取进程的终端输出
        
#         Returns:
#             输出字符串
#         """
#         return ''.join(self.output_buffer)
    
#     def get_pid(self) -> Optional[int]:
#         """
#         获取进程 PID
        
#         Returns:
#             PID 或 None
#         """
#         return self.process.pid if self.process else None


#!/usr/bin/env python3
"""
进程执行器模块
负责启动和管理子进程，捕获输出
"""
import subprocess
import os
import time
import sys
from pathlib import Path
from typing import Dict, Optional

# 导入工具类
sys.path.append(str(Path(__file__).parent.parent))
from utils.config_loader import ConfigLoader, Logger


# ----------------------------
# 进程执行器（核心类）
# ----------------------------
class ProcessExecutor:
    """进程执行器，管理子进程的启动和输出捕获"""

    def __init__(self, config: dict, logger: Optional[Logger] = None):
        """
        初始化执行器
        
        Args:
            config: 配置字典，必须包含 'work_dir' 和 'command' 字段
            logger: 日志记录器（可选）
        """
        self.work_dir = config["work_dir"]
        self.command = config["command"]
        self.logger = logger or Logger()
        self.process_info = {}

    def run(self, save_log: bool = False, log_path: Optional[str] = None) -> Dict:
        """
        执行子进程命令
        
        Args:
            save_log: 是否保存日志到文件
            log_path: 日志文件路径或目录
            
        Returns:
            进程信息字典
        """
        os.chdir(self.work_dir)
        parts = self.command.split()
        if parts[0] == "python" and "-u" not in parts:
            parts.insert(1, "-u")

        start_time = time.time()
        start_str = time.strftime("%Y-%m-%d %H:%M:%S")

        process = subprocess.Popen(
            parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # self.logger.info(f"先进入工作目录 {self.work_dir}，启动 PID={process.pid} 进程")
        # self.logger.info(f"执行命令：{self.command}\n")

        if process.stdout:
            for line in process.stdout:
                self.logger.write_child(line)

        process.wait()
        end_time = time.time()
        end_str = time.strftime("%Y-%m-%d %H:%M:%S")

        self.process_info = {
            "pid": process.pid,
            "command": self.command,
            "work_dir": self.work_dir,
            "start_time": start_str,
            "end_time": end_str,
            "elapsed": round(end_time - start_time, 2),
            "return_code": process.returncode,
        }

        if save_log and log_path:
            self.logger.save(log_path, self.process_info)

        return self.process_info