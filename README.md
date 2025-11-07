# 电子科技大学高性能计算平台使用指南

[![HPC](https://img.shields.io/badge/Platform-UESTC_HPC-blue.svg)](https://hpc.uestc.edu.cn/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 本仓库提供电子科技大学高性能计算中心（HPC）的完整使用指南，包括环境配置、工具脚本和训练任务监控系统。

---

## 📚 快速导航

### 🚀 新手入门
- **[完整配置流程](配置流程.md)** - 从零开始的详细指南
  - 准备工作（开户、VPN）
  - 登录节点配置（Conda、环境检测）
  - 计算节点使用（VSCode、GPU 检测）

### 🔧 工具箱

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| [hpc_env_check.sh](scripts/hpc_env_check.sh) | 登录节点环境检测 | 检查系统信息、Python、常用工具 |
| [gpu_env_check.sh](scripts/gpu_env_check.sh) | GPU 环境检测 | 检查 NVIDIA 驱动、CUDA、PyTorch 安装建议 |
| [install_conda.sh](scripts/install_conda.sh) | 自动安装 Miniconda | 一键配置 Python 虚拟环境 |
| [**hpc_run/**](hpc_run/) | **训练任务监控系统** | **自动监控训练进程，完成后推送通知（防止忘关机扣费）** ⭐ |

---

## 🎯 快速开始

### 第一步：克隆仓库
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

### 第三步：使用训练监控工具（推荐）
```bash
# 进入训练监控工具目录
cd hpc_run

# 查看详细使用说明
cat README.md

# 配置并运行你的训练任务（自动监控+通知）
python run.py
```

💡 **为什么要用训练监控工具？**
- ✅ 训练完成自动推送手机通知
- ✅ 避免忘记关闭计算节点导致持续扣费
- ✅ 无需修改训练代码，套壳运行即可
- ✅ 自动保存完整训练日志

详见：**[hpc_run 完整文档](hpc_run/README.md)** →

---

## 📖 详细文档

- **[配置流程完整指南](配置流程.md)** - 包含准备工作、登录节点、计算节点的详细步骤
- **[HPC Run 使用文档](hpc_run/README.md)** - 训练监控工具的配置和使用说明

---

## 🤝 贡献与反馈

遇到问题或有改进建议？

- 提交 [Issue](../../issues)
- 发起 [Pull Request](../../pulls)
- 联系维护者

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**⭐ 如果这个项目对你有帮助，欢迎 Star 支持！**

