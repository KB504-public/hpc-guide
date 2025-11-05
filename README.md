# 高性能计算平台使用指南 (HPC Guide)

此仓库包含针对电子科技大学高性能计算中心（HPC）登录节点与计算节点的使用说明与辅助脚本。

## 快速开始

1. 阅读 [配置流程](配置流程.md)。

2. 在登录节点的 terminal 中：

    ```bash
    git clone https://github.com/KB504-public/hpc-guide.git
    cd hpc-guide
    ```

## 脚本说明

- **`hpc_env_check.sh`** - 登录节点环境检测脚本，检查系统信息、已安装软件和 Conda 配置
- **`gpu_env_check.sh`** - 计算节点 GPU 环境检测脚本，检查 NVIDIA 驱动、CUDA 版本和 GPU 设备
- **`install_conda.sh`** - 自动化安装 Miniconda 脚本，用于配置 Python 虚拟环境

## 联系方式

遇到问题可以在仓库提交 Issue，或通过邮件/通知联系维护人。

