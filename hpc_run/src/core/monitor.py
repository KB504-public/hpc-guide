#!/usr/bin/env python3
"""
系统监控模块
负责监控进程的 CPU、内存和 GPU 使用情况
"""
import psutil
import shutil
import subprocess
from typing import Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ResourceMetrics:
    """资源使用指标"""
    cpu_samples: list = field(default_factory=list)
    gpu_samples: list = field(default_factory=list)
    max_memory: float = 0.0  # MB
    
    def add_cpu(self, value: float):
        """添加 CPU 采样值"""
        self.cpu_samples.append(value)
    
    def add_gpu(self, value: float):
        """添加 GPU 采样值"""
        self.gpu_samples.append(value)
    
    def update_memory(self, value: float):
        """更新最大内存值"""
        self.max_memory = max(self.max_memory, value)
    
    def get_avg_cpu(self) -> float:
        """获取平均 CPU 使用率"""
        return sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0
    
    def get_avg_gpu(self) -> Optional[float]:
        """获取平均 GPU 使用率"""
        return sum(self.gpu_samples) / len(self.gpu_samples) if self.gpu_samples else None
    
    def get_max_memory(self) -> float:
        """获取最大内存使用量（MB）"""
        return self.max_memory


class SystemMonitor:
    """系统资源监控器"""
    
    def __init__(self, pid: int):
        """
        初始化监控器
        
        Args:
            pid: 要监控的进程 ID
        """
        self.pid = pid
        try:
            self.process = psutil.Process(pid)
            # 初始化 CPU 采样
            self.process.cpu_percent(interval=None)
        except psutil.NoSuchProcess:
            raise ValueError(f"进程不存在: PID={pid}")
        
        self.metrics = ResourceMetrics()
        self._nvidia_smi_path = self._find_nvidia_smi()
    
    def _find_nvidia_smi(self) -> Optional[str]:
        """查找 nvidia-smi 路径"""
        return shutil.which('nvidia-smi')
    
    def sample_cpu(self) -> float:
        """
        采样 CPU 使用率
        
        Returns:
            CPU 使用率百分比
        """
        try:
            cpu_percent = self.process.cpu_percent(interval=None)
            self.metrics.add_cpu(cpu_percent)
            return cpu_percent
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0
    
    def sample_memory(self) -> float:
        """
        采样内存使用量
        
        Returns:
            内存使用量（MB）
        """
        try:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            self.metrics.update_memory(memory_mb)
            return memory_mb
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0
    
    def sample_gpu(self) -> Optional[float]:
        """
        采样 GPU 使用率（所有 GPU 的平均值）
        
        Returns:
            GPU 使用率百分比，如果无 GPU 或采样失败则返回 None
        """
        if not self._nvidia_smi_path:
            return None
        
        try:
            output = subprocess.check_output(
                [self._nvidia_smi_path, '--query-gpu=utilization.gpu', 
                 '--format=csv,noheader,nounits'],
                timeout=2
            )
            values = [float(x) for x in output.decode().strip().splitlines() if x.strip()]
            
            if values:
                avg_gpu = sum(values) / len(values)
                self.metrics.add_gpu(avg_gpu)
                return avg_gpu
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
            pass
        
        return None
    
    def sample_all(self) -> Tuple[float, float, Optional[float]]:
        """
        采样所有资源指标
        
        Returns:
            (CPU%, 内存MB, GPU%)
        """
        cpu = self.sample_cpu()
        mem = self.sample_memory()
        gpu = self.sample_gpu()
        return cpu, mem, gpu
    
    def get_metrics(self) -> ResourceMetrics:
        """
        获取累积的资源指标
        
        Returns:
            资源使用指标对象
        """
        return self.metrics
