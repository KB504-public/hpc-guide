#!/usr/bin/env python3
"""
配置加载器和日志模块
负责加载和解析 YAML 配置文件，以及日志打印和保存
"""
import os
import sys
import yaml
import time
from pathlib import Path
from typing import Dict, Any, Union, Optional


class ConfigLoader:
    """配置加载器类，处理配置文件的加载、路径解析和验证"""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录的 config/config.yaml
        """
        if config_path is None:
            # 默认配置文件路径：项目根目录/config/config.yaml
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.project_root = self.config_path.parent.parent if self.config_path.name == "config.yaml" else Path.cwd()
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            解析后的配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 格式错误
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 处理路径和环境变量
        self._process_config()
        
        return self.config
    
    def _process_config(self):
        """处理配置中的路径和环境变量"""
        # 处理训练配置
        if 'train' in self.config:
            train = self.config['train']
            
            # 解析工作目录（必需）
            if 'work_dir' in train:
                train['work_dir'] = self._resolve_path(train['work_dir'])
            
            # 解析日志目录（相对于工作目录）
            if 'log' in train and 'dir' in train['log'] and 'work_dir' in train:
                work_dir = Path(train['work_dir'])
                log_dir = work_dir / train['log']['dir']
                train['log']['dir'] = str(log_dir.resolve())
    
    def _resolve_path(self, path_str: str) -> str:
        """
        解析路径，支持环境变量和相对路径
        
        Args:
            path_str: 原始路径字符串
            
        Returns:
            解析后的绝对路径字符串
        """
        # 替换环境变量
        path_str = os.path.expandvars(path_str)
        
        # 转换为 Path 对象
        path = Path(path_str)
        
        # 如果是相对路径，相对于项目根目录解析
        if not path.is_absolute():
            path = self.project_root / path
        
        # 返回跨平台的路径字符串
        return str(path.resolve())
    

    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键（支持点号分隔的多级键，如 'runtime.log_file'）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate(self) -> bool:
        """
        验证配置完整性
        
        Returns:
            配置是否有效
        """
        import os
        
        # 1. 验证训练配置（必需）
        if 'train' not in self.config:
            print("[ERROR] 配置错误: 缺失必需的 'train' 配置项")
            return False
        
        # 验证工作目录
        if not self.get('train.work_dir'):
            print("[ERROR] 配置错误: 缺失必需项 'train.work_dir'（工作目录）")
            return False
        
        # 验证工作目录是否存在
        work_dir = Path(self.get('train.work_dir'))
        if not work_dir.exists():
            print(f"[ERROR] 配置错误: 工作目录不存在: {work_dir}")
            return False
        
        # 验证命令
        if not self.get('train.command'):
            print("[ERROR] 配置错误: 缺失必需项 'train.command'（训练命令）")
            return False
        
        # 2. 验证通知器配置（必需）
        if 'notification' not in self.config:
            print("[ERROR] 配置错误: 缺失必需的 'notification' 配置项")
            print("       本工具的核心功能是训练完成后发送通知")
            return False
        
        notifier_type = self.get('notification.type', '').lower()
        if not notifier_type:
            print("[ERROR] 配置错误: 缺失必需项 'notification.type'")
            print("       可选值: 'console'（控制台）或 'xxtui'（推送通知）")
            return False
        
        # 验证 xxtui 配置
        if notifier_type == 'xxtui':
            # 先从配置文件获取，如果不存在或为空，再检查环境变量
            api_key = self.get('notification.xxtui.api_key', '')
            if not api_key or api_key.strip() == '':
                api_key = os.getenv('XXTUI_KEY', '')
            
            if not api_key or api_key.strip() == '':
                print("[ERROR] 配置错误: 选择了 xxtui 通知器但未提供 API 密钥")
                print("       方式 1: 在配置文件中设置 notification.xxtui.api_key")
                print("       方式 2: 设置环境变量 export XXTUI_KEY='your-api-key'")
                return False
        
        return True


def load_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    便捷函数：加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    loader = ConfigLoader(config_path)
    config = loader.load()
    
    if not loader.validate():
        raise ValueError("配置文件验证失败，请检查必需项")
    
    return config


# ----------------------------
# 日志类
# ----------------------------
class Logger:
    """负责打印与保存日志"""

    def __init__(self, enable_console: bool = True):
        self.enable_console = enable_console
        self.logs = []

    def info(self, msg: str):
        text = f"[INFO] {msg}"
        if self.enable_console:
            print(text)
        self.logs.append(text + "\n")

    def warn(self, msg: str):
        text = f"[WARN] {msg}"
        if self.enable_console:
            print(text)
        self.logs.append(text + "\n")

    def write_child(self, line: str):
        """实时打印子进程输出"""
        text = "    " + line
        if self.enable_console:
            sys.stdout.write(text)
            sys.stdout.flush()
        self.logs.append(line)

    def save(self, log_target: str, process_info: dict):
        """保存日志到文件或目录"""
        log_path = Path(log_target)
        if log_path.suffix:  # 明确是文件
            log_path.parent.mkdir(parents=True, exist_ok=True)
        else:  # 是目录
            log_path.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            log_path = log_path / f"train_{timestamp}.log"

        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(self.logs)
            f.write("\n===== 子进程执行信息 =====\n")
            for k, v in process_info.items():
                f.write(f"{k:12s}: {v}\n")
            f.write("==========================\n")

        if self.enable_console:
            print(f"\n[INFO] 日志已保存至: {log_path}")
