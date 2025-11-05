#!/bin/bash
# ===========================================================
# ⚡ HPC 计算节点 GPU 检测与 PyTorch 安装建议脚本
# 作者: <你的名字>
# 功能: 检测 GPU、CUDA、Python 环境，并给出 PyTorch 安装命令（conda/pip）
# ===========================================================

RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; BLUE="\033[34m"; BOLD="\033[1m"; NC="\033[0m"

echo -e "${BOLD}===========================================================${NC}"
echo -e "⚡ ${BLUE}GPU 环境检测与 PyTorch 安装建议${NC}"
echo -e "${BOLD}===========================================================${NC}"
echo

# ---------- GPU 检测 ----------
echo -e "${BOLD}${BLUE}🎮 GPU 检测${NC}"
echo "-----------------------------------------------------------"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader
    GPU_COUNT=$(nvidia-smi -L | wc -l)
    echo "GPU 数量: ${GPU_COUNT}"
else
    echo -e "❌ ${RED}未检测到 nvidia-smi，请确认该节点是否有 GPU 或驱动是否安装${NC}"
    exit 1
fi
echo

# ---------- CUDA 环境 ----------
echo -e "${BOLD}${BLUE}🧩 CUDA 环境${NC}"
echo "-----------------------------------------------------------"
if command -v nvcc &> /dev/null; then
    CUDA_VER=$(nvcc --version | grep release | sed 's/.*release //' | sed 's/,.*//')
    echo -e "✔️ CUDA 编译器版本: ${GREEN}${CUDA_VER}${NC}"
else
    CUDA_VER=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}' | head -n1)
    if [ -n "$CUDA_VER" ]; then
        echo -e "✔️ CUDA 运行时版本: ${GREEN}${CUDA_VER}${NC}（未检测到 nvcc 编译器）"
    else
        echo -e "⚠️ 未检测到 CUDA 环境，请加载模块或联系管理员。"
        CUDA_VER="unknown"
    fi
fi
echo

# ---------- Python 环境 ----------
echo -e "${BOLD}${BLUE}🐍 Python 环境${NC}"
echo "-----------------------------------------------------------"
if command -v python &> /dev/null; then
    PY_VER=$(python --version 2>&1)
    echo -e "✔️ Python: ${GREEN}${PY_VER}${NC}"
else
    echo -e "⚠️ ${YELLOW}未检测到 Python，请先安装 Miniconda 或 Anaconda${NC}"
    echo
    echo "安装 Conda（推荐）:"
    echo -e "   ${YELLOW}wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh${NC}"
    echo -e "   ${YELLOW}bash Miniconda3-latest-Linux-x86_64.sh${NC}"
    echo
    exit 0
fi
echo

# ---------- 检查是否已安装 PyTorch ----------
echo -e "${BOLD}${BLUE}🔍 PyTorch 检测${NC}"
echo "-----------------------------------------------------------"
if python -c "import torch" &>/dev/null; then
    TORCH_VER=$(python -c "import torch; print(torch.__version__)")
    echo -e "✔️ 已安装 PyTorch: ${GREEN}${TORCH_VER}${NC}"
    python - <<'EOF'
import torch
if torch.cuda.is_available():
    print("CUDA 可用:", torch.version.cuda)
    print("当前 GPU:", torch.cuda.get_device_name(0))
else:
    print("⚠️ 检测到 PyTorch，但 CUDA 不可用，请检查 CUDA 对应版本。")
EOF
    echo
    exit 0
else
    echo -e "❌ ${RED}未检测到 PyTorch${NC}"
fi
echo

# ---------- 安装建议 ----------
echo -e "${BOLD}${BLUE}💡 PyTorch 安装建议${NC}"
echo "-----------------------------------------------------------"

# 提取 CUDA 主版本号（如 12.1 -> 12.1）
CUDA_MAJOR=$(echo "$CUDA_VER" | grep -Eo '[0-9]+\.[0-9]+' | head -n1)

if [[ -z "$CUDA_MAJOR" ]]; then
    echo "⚠️ 无法确定 CUDA 版本，建议使用 CPU 版 PyTorch 安装："
    echo -e "   ${YELLOW}conda install pytorch torchvision torchaudio cpuonly -c pytorch${NC}"
    echo -e "   ${YELLOW}pip install torch torchvision torchaudio${NC}"
elif (( $(echo "$CUDA_MAJOR >= 12.0" | bc -l) )); then
    echo "检测到 CUDA ${CUDA_MAJOR}，推荐安装 PyTorch CUDA 12.1 版本："
    echo
    echo "Conda 安装命令："
    echo -e "   ${YELLOW}conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia${NC}"
    echo
    echo "Pip 安装命令："
    echo -e "   ${YELLOW}pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121${NC}"
elif (( $(echo "$CUDA_MAJOR >= 11.8" | bc -l) )); then
    echo "检测到 CUDA ${CUDA_MAJOR}，推荐安装 PyTorch CUDA 11.8 版本："
    echo
    echo "Conda 安装命令："
    echo -e "   ${YELLOW}conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia${NC}"
    echo
    echo "Pip 安装命令："
    echo -e "   ${YELLOW}pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118${NC}"
else
    echo "⚠️ CUDA 版本 (${CUDA_MAJOR}) 较旧，推荐升级至 11.8 以上。"
    echo "临时方案（CPU 版 PyTorch）："
    echo -e "   ${YELLOW}conda install pytorch torchvision torchaudio cpuonly -c pytorch${NC}"
    echo -e "   ${YELLOW}pip install torch torchvision torchaudio${NC}"
fi
echo

echo -e "${BOLD}===========================================================${NC}"
echo "✅ GPU 环境检测完成，可根据建议安装 PyTorch。"
echo -e "${BOLD}===========================================================${NC}"