#!/usr/bin/env python3
"""
PyTorch 训练测试脚本
用于验证 GPU 运行环境与日志输出
"""
import os
import time
import random
import argparse
import statistics
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim


# ------------------------
# 参数解析
# ------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--steps", type=int, default=50)
parser.add_argument("--sleep", type=float, default=0.0)
parser.add_argument("--batch-size", type=int, default=64)
parser.add_argument("--hidden", type=int, default=128)
parser.add_argument("--input-dim", type=int, default=100)
parser.add_argument("--log", type=str, default=None)
parser.add_argument("--log-dir", type=str, default=None)
args = parser.parse_args()


# ------------------------
# 确定日志路径
# ------------------------
if args.log:
    log_path = args.log
elif args.log_dir:
    os.makedirs(args.log_dir, exist_ok=True)
    log_path = os.path.join(args.log_dir, "train.log")
else:
    script_dir = Path(__file__).parent
    log_dir = script_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = str(log_dir / "train.log")

print(f"[INFO] Log file: {log_path}")

# ------------------------
# 初始化环境
# ------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] 使用设备: {device}")

# 设置随机种子以便复现
torch.manual_seed(42)
random.seed(42)

# ------------------------
# 构建简单模型
# ------------------------
class SimpleMLP(nn.Module):
    def __init__(self, input_dim=100, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x):
        return self.net(x)


model = SimpleMLP(args.input_dim, args.hidden).to(device)
optimizer = optim.SGD(model.parameters(), lr=0.01)
criterion = nn.MSELoss()

print(f"[INFO] 模型参数量: {sum(p.numel() for p in model.parameters()):,}")

# ------------------------
# 模拟训练数据
# ------------------------
x = torch.randn(args.batch_size, args.input_dim, device=device)
y_true = torch.randn(args.batch_size, 1, device=device)

# ------------------------
# 训练循环
# ------------------------
losses = []
start_time = time.time()

for step in range(1, args.steps + 1):
    optimizer.zero_grad()
    pred = model(x)
    loss = criterion(pred, y_true)
    loss.backward()
    optimizer.step()

    loss_value = loss.item()
    losses.append(loss_value)

    print(f"[train] step={step:03d} | loss={loss_value:.6f}")
    if args.sleep > 0:
        time.sleep(args.sleep)

# ------------------------
# 统计与日志写入
# ------------------------
avg_loss = statistics.mean(losses)
min_loss = min(losses)
max_loss = max(losses)
elapsed = time.time() - start_time

with open(log_path, "w") as f:
    f.write("[train] done.\n")
    f.write(f"steps={args.steps}\n")
    f.write(f"avg_loss={avg_loss:.6f}, min_loss={min_loss:.6f}, max_loss={max_loss:.6f}\n")
    f.write(f"device={device}\n")
    f.write(f"elapsed={elapsed:.2f}s\n")

print("[train] done.")
print(f"[train] summary: avg_loss={avg_loss:.6f}, min_loss={min_loss:.6f}, time={elapsed:.2f}s")