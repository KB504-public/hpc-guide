# HPC 平台使用指南

本文档介绍如何在 HPC 计算平台上使用训练监控系统。HPC 平台的特点是：
- **计算节点**: 计费资源，仅用于运行训练任务
- **登录节点**: 免费资源，长期可用，用于监控和管理

为避免忘记关闭计费的计算节点，我们将系统拆分为两个脚本：
- `train_wrapper.py`: 在**计算节点**上运行，包装训练任务
- `train_monitor.py`: 在**登录节点**上运行，监控训练完成并发送通知

## 工作流程

```
计算节点 (billable)          登录节点 (free, always on)
┌──────────────────┐         ┌──────────────────┐
│ train_wrapper.py │         │train_monitor.py  │
│                  │         │                  │
│ 1. 执行训练      │         │ 1. 轮询标记文件  │
│ 2. 捕获日志      │────────>│ 2. 发现完成      │
│ 3. 写入标记文件  │  共享存储│ 3. 发送通知      │
└──────────────────┘         └──────────────────┘
```

## 使用步骤

### 1. 配置通知服务

创建 API 密钥文件（如果还没有）：
```bash
cd hpc_run/config
cp api_keys.yaml.example api_keys.yaml
# 编辑 api_keys.yaml，填入真实的 xxtui API 密钥
```

### 2. 在计算节点上启动训练

在你的训练项目目录中运行：

```bash
# 基本用法
python /path/to/hpc_run/train_wrapper.py \
    --work-dir /path/to/your/project \
    --command "python train.py"

# 带参数的训练命令
python /path/to/hpc_run/train_wrapper.py \
    --work-dir /path/to/your/project \
    --command "python train.py --epochs 100 --batch-size 32"

# 自定义日志目录
python /path/to/hpc_run/train_wrapper.py \
    --work-dir /path/to/your/project \
    --command "python train.py" \
    --log-dir ./custom_logs
```

**参数说明**:
- `--work-dir`: 训练项目的工作目录（必需）
- `--command`: 训练命令（必需）
- `--log-dir`: 日志保存目录（可选，默认为 `logs`）

### 3. 在登录节点上启动监控

在另一个终端（登录节点）运行：

```bash
# 持续监控模式（推荐）
python /path/to/hpc_run/train_monitor.py \
    --work-dir /path/to/your/project \
    --interval 60

# 单次检查模式
python /path/to/hpc_run/train_monitor.py \
    --work-dir /path/to/your/project \
    --once
```

**参数说明**:
- `--work-dir`: 训练项目的工作目录（必需，与 wrapper 保持一致）
- `--interval`: 检查间隔秒数（可选，默认 60 秒）
- `--once`: 仅检查一次，不持续轮询（可选）

### 4. 完成后处理

监控程序会：
1. 检测到训练完成标记文件
2. 生成训练报告
3. 发送通知到你的设备
4. 清理标记文件

此时你可以**安全关闭计算节点**，不会错过训练结果！

## 文件说明

训练期间会在工作目录下生成：

```
your_project/
├── logs/                      # 日志目录
│   └── train_YYYYMMDD_HHMMSS.log
└── .train_complete.json       # 完成标记（监控后自动删除）
```

`.train_complete.json` 格式示例：
```json
{
    "timestamp": "2024-01-01 12:34:56",
    "status": "success",
    "exit_code": 0,
    "log_file": "logs/train_20240101_123456.log"
}
```

## 配置文件

确保 `config/config.yaml` 配置正确：

```yaml
# 通知设置
notification:
  type: "xxtui"           # 通知服务类型
  api_keys_file: "config/api_keys.yaml"  # API 密钥文件路径
  
  # xxtui 推送配置
  xxtui:
    url: "https://xxtui.com/push"
    headers:
      Content-Type: "application/json"
    body:
      title: "训练完成通知"
      content: "训练任务已完成"

# 报告设置（可选）
report:
  include_last_n_lines: 50  # 报告中包含最后 N 行日志
```

## 注意事项

1. **共享存储**: 确保计算节点和登录节点都能访问 `--work-dir` 指定的目录
2. **Python 环境**: 
   - 计算节点需要有训练代码所需的 Python 环境
   - 登录节点需要安装 `requests` 等依赖包
3. **网络访问**: 登录节点需要能访问通知服务 API
4. **进程管理**: 可以使用 `nohup` 或 `screen` 让监控脚本后台运行

## 示例：使用 screen 后台运行

```bash
# 在登录节点启动 screen 会话
screen -S train_monitor

# 在 screen 中运行监控
python /path/to/hpc_run/train_monitor.py \
    --work-dir /path/to/your/project \
    --interval 60

# 按 Ctrl+A 然后 D 分离会话
# 训练完成后，可以用 screen -r train_monitor 恢复查看
```

## 对比：实验室服务器使用方式

如果你在**实验室服务器**（可以长期运行监控的环境）使用，请切换到 `lab-server` 分支：

```bash
git checkout lab-server
```

在该分支中，使用原来的 `run.py` 脚本，它会在同一台机器上执行训练并监控：

```bash
python hpc_run/run.py --config hpc_run/config/config.yaml
```

## 故障排查

### 监控程序没有发送通知
- 检查 `api_keys.yaml` 是否配置正确
- 检查登录节点是否能访问通知服务 URL
- 查看监控程序的控制台输出

### 找不到完成标记文件
- 确认 wrapper 和 monitor 使用相同的 `--work-dir`
- 检查计算节点是否正常运行
- 查看计算节点的输出日志

### 训练日志为空
- 确保训练脚本有输出（print 语句）
- 检查 Python buffering 设置，可能需要 `python -u` 强制无缓冲输出
