#!/usr/bin/env bash

set -e

# ===============================
# 检查是否支持中文输出
# ===============================
SUPPORT_CHINESE=false
if locale -a 2>/dev/null | grep -q "zh_CN.utf8"; then
  SUPPORT_CHINESE=true
fi

# ===============================
# 定义提示函数
# ===============================
say() {
  if [ "$SUPPORT_CHINESE" = true ]; then
    echo -e "💬 $1"
  else
    echo -e "$2"
  fi
}

confirm() {
  if [ "$SUPPORT_CHINESE" = true ]; then
    read -rp "❓ 是否继续？(y/n): " yn
  else
    read -rp "❓ Continue? (y/n): " yn
  fi
  case $yn in
      [Yy]*) true ;;
      *) say "❌ 已取消安装。" "❌ Installation cancelled."; exit 1 ;;
  esac
}

# ===============================
# 检查是否已安装 conda
# ===============================
if command -v conda >/dev/null 2>&1; then
  say "✅ 已检测到 conda，跳过安装。" "✅ Conda detected, skipping installation."
  conda --version
  exit 0
else
  say "⚙️ 未检测到 conda，将开始安装 Miniconda。" "⚙️ Conda not found, installing Miniconda."
  confirm
fi

# ===============================
# 下载最新版 Miniconda 安装脚本
# ===============================
say "⬇️ 正在下载最新版 Miniconda 安装包..." "⬇️ Downloading latest Miniconda installer..."
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh

say "📦 准备安装 Miniconda 到 ~/miniconda3" "📦 Ready to install Miniconda to ~/miniconda3"
confirm

# ===============================
# 尝试安装最新版 Miniconda
# ===============================
INSTALL_LOG=$(mktemp)
if ! bash ~/miniconda.sh -b -p ~/miniconda3 >"$INSTALL_LOG" 2>&1; then
  if grep -q "GLIBC" "$INSTALL_LOG"; then
    say "⚠️ 检测到 GLIBC 版本过低，尝试安装兼容版本..." "⚠️ Detected old GLIBC, installing compatible version..."
    confirm
    wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.9.2-Linux-x86_64.sh -O ~/miniconda.sh
    if ! bash ~/miniconda.sh -b -p ~/miniconda3; then
      say "❌ 旧版 Miniconda 安装失败，请手动检查系统环境。" "❌ Failed to install old Miniconda. Please check your system."
      exit 1
    fi
  else
    say "❌ Miniconda 安装失败，错误如下：" "❌ Miniconda installation failed with error:"
    cat "$INSTALL_LOG"
    exit 1
  fi
else
  say "✅ Miniconda 安装成功！" "✅ Miniconda installed successfully!"
fi

# ===============================
# 添加环境变量
# ===============================
if ! grep -q "miniconda3/bin" ~/.bashrc; then
  say "🔧 将 conda 添加到 PATH（~/.bashrc）" "🔧 Adding conda to PATH (~/.bashrc)"
  echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
  say "✅ 请重新打开终端或执行：source ~/.bashrc" "✅ Please reopen terminal or run: source ~/.bashrc"
fi

# ===============================
# 验证安装
# ===============================
if [ -f "$HOME/miniconda3/bin/conda" ]; then
  "$HOME/miniconda3/bin/conda" --version
  say "🎉 安装完成！Conda 已可用。" "🎉 Installation complete! Conda is ready to use."
else
  say "⚠️ 安装似乎未成功，请检查日志。" "⚠️ Installation may have failed. Please check logs."
  exit 1
fi

# ===============================
# 使用建议 / 备注
# ===============================
echo ""
if [ "$SUPPORT_CHINESE" = true ]; then
  cat <<'EOF'
📘 使用建议（高性能计算平台特别说明）：
----------------------------------------------------
1️⃣  在 HPC 平台上，conda 下载速度可能较慢。

2️⃣  建议创建独立环境以隔离项目依赖：
        conda create -n myenv python=3.11
        conda activate myenv

3️⃣  若 conda 下载软件包过慢，可改用 pip：
        pip install fastapi uvicorn numpy pandas

✨ 小提示：第一次使用 conda 时执行：
        source ~/.bashrc
----------------------------------------------------
EOF
else
  cat <<'EOF'
📘 Usage tips (for HPC or server environments):
----------------------------------------------------
1️⃣  Conda downloads may be slow on HPC clusters.

2️⃣  Always create a separate environment to isolate dependencies:
        conda create -n myenv python=3.11
        conda activate myenv

3️⃣  If conda is too slow, you can install packages via pip:
        pip install fastapi uvicorn numpy pandas

✨ Tip: Run 'source ~/.bashrc' before using conda the first time.
----------------------------------------------------
EOF
fi