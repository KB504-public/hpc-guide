# HPC Run

高性能计算平台训练监控工具 - 避免忘记关闭 HPC 导致持续计费

## 功能

- 套壳运行任意训练命令，无需修改训练代码
- 实时捕获并显示训练输出
- 自动保存训练日志
- 训练完成后自动发送通知（支持手机推送）

## 快速开始

1. 配置任务

    编辑 `config/config.yaml`：

    1. 添加你的训练脚本所在的文件夹和训练使用的命令；

       在 `config/examples/` 目录下提供了多种场景的配置示例，例如参考 `example3_conda.yaml` 来使用 Conda 环境。
    2. 选择推送方法并填写你的 API；

    ```yaml
    train:
      work_dir: "tests"
      command: "python train_dummy.py --steps 20 --sleep 0.2"
      log:
        dir: "logs"
        save: true
    
    notification:
      type: "xxtui"
      xxtui:
        api_key: ""
        timeout: 8
    ```

2. 运行

    ```bash
    python run.py
    ```

## 项目结构

```
hpc-run/
├── run.py                  # 主程序
├── config/
│   ├── config.yaml         # 配置文件
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
