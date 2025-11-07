# HPC Run

高性能计算平台训练监控工具 - 避免忘记关闭 HPC 导致持续计费

## 功能

- 套壳运行任意训练命令，无需修改训练代码
- 实时捕获并显示训练输出
- 自动保存训练日志
- 训练完成后自动发送通知（支持手机推送）

## 使用方式

本工具提供两种运行模式：

### 🖥️ HPC 计算平台模式（推荐用于计费环境）

适用于计算节点计费的 HPC 平台。将训练执行和监控分离到不同节点：
- **计算节点**（billable）: 仅运行训练
- **登录节点**（free）: 长期监控并发送通知

**详细使用说明请查看**: [HPC_USAGE.md](./HPC_USAGE.md)

### 💻 实验室服务器模式

适用于可以长期运行监控程序的实验室服务器。使用原版 `run.py` 在同一台机器上执行和监控：

```bash
# 切换到 lab-server 分支
git checkout lab-server

# 运行监控
python hpc_run/run.py --config hpc_run/config/config.yaml
```

## 快速开始（实验室服务器模式）

> **注意**: 如果你在 HPC 平台使用，请查看 [HPC_USAGE.md](./HPC_USAGE.md)

以下步骤适用于 `lab-server` 分支：

1. **配置 API 密钥（如使用推送通知）**

    ```bash
    # 复制 API 密钥示例文件
    cp config/api_keys.yaml.example config/api_keys.yaml
    
    # 编辑 api_keys.yaml，填写你的真实 API 密钥
    # 注意：api_keys.yaml 已被 .gitignore 忽略，不会被提交到 Git
    ```

2. **配置训练任务**

    编辑 `config/config.yaml`：

    1. 添加你的训练脚本所在的文件夹和训练使用的命令；

       在 `config/examples/` 目录下提供了多种场景的配置示例，例如参考 `example3_conda.yaml` 来使用 Conda 环境。
    2. 选择推送方法（console 或 xxtui）；

    ```yaml
    train:
      work_dir: "tests"
      command: "python train_dummy.py --steps 20 --sleep 0.2"
      log:
        dir: "logs"
        save: true
    
    notification:
      type: "xxtui"                      # 使用 xxtui 推送
      api_keys_file: "config/api_keys.yaml"  # API 密钥文件路径
      xxtui:
        timeout: 8
    ```

3. **运行**

    ```bash
    python run.py
    ```

## API 密钥安全说明

为了保护你的 API 密钥安全，本工具支持三种方式配置密钥（优先级从高到低）：

1. **API 密钥文件（推荐）** ✅
   - 将 `config/api_keys.yaml.example` 复制为 `config/api_keys.yaml`
   - 填写真实密钥
   - `api_keys.yaml` 已被 `.gitignore` 忽略，不会被提交到 Git

2. **环境变量**
   ```bash
   export XXTUI_KEY="your-api-key-here"
   ```

3. **直接写在 config.yaml**（不推荐）
   - 容易被误提交到 Git 造成泄露

## 项目结构

```
hpc-run/
├── run.py                  # 主程序
├── config/
│   ├── config.yaml         # 配置文件
│   ├── api_keys.yaml       # API 密钥文件（需手动创建，已被 .gitignore）
│   ├── api_keys.yaml.example  # API 密钥文件示例
│   └── examples/           # 配置示例
├── src/
│   ├── core/
│   │   ├── executor.py     # 核心执行器
│   │   ├── monitor.py      # 监控模块（保留）
│   │   └── reporter.py     # 报告生成器
│   ├── utils/
│   │   └── config_loader.py # 配置加载 + Logger
│   └── notifier/
│       ├── base.py         # 通知器基类
│       ├── console.py      # 将推送信息打印在终端
│       └── xxtui.py        # 使用 xxtui 推送
└── tests/
    └── train_dummy.py      # 测试使用的训练脚本
```
