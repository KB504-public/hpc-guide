# 电子科技大学高性能计算平台使用指南

[![HPC](https://img.shields.io/badge/Platform-UESTC_HPC-blue.svg)](https://hpc.uestc.edu.cn/)

本仓库提供电子科技大学高性能计算中心（HPC）的完整使用指南，涵盖账号配置、环境搭建、工具脚本与训练任务监控等内容。  

**核心内容速览**  

- **[配置流程](SETUP_GUIDE.md)**：开户、登录节点配置、计算节点使用
- **常用脚本**：  
  - [`hpc_env_check.sh`](scripts/hpc_env_check.sh)：登录节点检测  
  - [`gpu_env_check.sh`](scripts/gpu_env_check.sh)：GPU/CUDA 检测  
  - [`install_conda.sh`](scripts/install_conda.sh)：自动安装 Miniconda  
  - [`hpc_run/`](hpc_run/)：训练任务监控系统 ⭐ 自动提醒防止忘关机扣费  

## 🎯 快速开始

## 第一步：克隆仓库

```bash
# 在登录节点的 terminal 中执行
git clone https://github.com/Y006/hpc-guide.git
cd hpc-guide
```

### 第二步：环境检测与配置
```bash
# 1. 检测登录节点环境
bash scripts/hpc_env_check.sh

# 2. 安装 Conda（如果未安装）
bash scripts/install_conda.sh

# 3. 在计算节点检测 GPU 环境
bash scripts/gpu_env_check.sh
```

### 第三步：使用训练监控工具

HPC 平台采用双脚本架构，将训练和监控分离到不同节点：

```bash
# 1. 编辑配置文件
cd hpc_run
vim config/config.yaml  # 配置训练命令、工作目录、通知方式

# 2. 在登录节点（免费）启动监控程序
python train_monitor.py   # 持续运行，等待训练完成

# 3. 在计算节点（计费）运行训练
python train_wrapper.py   # 执行训练，完成后通知监控器
```

💡 **为什么要分离？**
- ✅ 监控程序在免费的登录节点运行，不产生费用
- ✅ 计算节点仅运行训练，完成即可关闭
- ✅ 训练完成自动推送通知，避免忘记关机扣费
- ✅ 无需修改训练代码，套壳运行即可

详见：**[HPC 使用文档](hpc_run/HPC_USAGE.md)** →

## 📖 详细文档

- **[配置流程完整指南](SETUP_GUIDE.md)** - 包含准备工作、登录节点、计算节点的详细步骤
- **[HPC 训练监控使用文档](hpc_run/HPC_USAGE.md)** - 双脚本架构详细说明和配置指南

## 🤝 贡献与反馈

遇到问题或有改进建议？

- 提交 [Issue](../../issues)
- 发起 [Pull Request](../../pulls)
- 联系维护者

**⭐ 如果这个项目对你有帮助，欢迎 Star 支持！**

