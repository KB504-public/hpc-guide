#!/bin/bash
# ===========================================================
# 🎓 学校高性能计算平台 - 登录节点环境快速检测脚本 (中英双语自适应)
# 作者: <qjy>
# ===========================================================

# ---------- 检查是否支持中文 ----------
SUPPORT_CHINESE=false
if locale -a 2>/dev/null | grep -qi "zh_CN.utf8"; then
  SUPPORT_CHINESE=true
fi

# 彩色输出
RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; BLUE="\033[34m"; BOLD="\033[1m"; NC="\033[0m"

print_line() { echo -e "${BOLD}-----------------------------------------------------------${NC}"; }

# ---------- 标题 ----------
echo -e "${BOLD}===========================================================${NC}"
if $SUPPORT_CHINESE; then
  echo -e "🎓 ${BLUE}学校高性能计算平台 - 登录节点环境检测${NC}"
else
  echo -e "🎓 ${BLUE}HPC Login Node Environment Check${NC}"
fi
echo -e "${BOLD}===========================================================${NC}"
echo

# ---------- 系统信息 ----------
if $SUPPORT_CHINESE; then echo -e "${BOLD}${BLUE}🖥️ 系统信息${NC}"; else echo -e "${BOLD}${BLUE}🖥️ System Information${NC}"; fi
print_line
echo "$( $SUPPORT_CHINESE && echo '主机名' || echo 'Hostname' ): $(hostname)"
echo "$( $SUPPORT_CHINESE && echo '操作系统' || echo 'Operating System' ): $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"')"
echo "$( $SUPPORT_CHINESE && echo '内核版本' || echo 'Kernel Version' ): $(uname -r)"
echo "$( $SUPPORT_CHINESE && echo '当前用户' || echo 'Current User' ): $(whoami)"
echo "$( $SUPPORT_CHINESE && echo '登录时间' || echo 'Login Time' ): $(date)"
echo

# ---------- 硬件资源 ----------
if $SUPPORT_CHINESE; then echo -e "${BOLD}${BLUE}⚙️ 硬件资源${NC}"; else echo -e "${BOLD}${BLUE}⚙️ Hardware Resources${NC}"; fi
print_line
echo "$( $SUPPORT_CHINESE && echo 'CPU 核心数' || echo 'CPU Cores' ): $(nproc)"
echo "$( $SUPPORT_CHINESE && echo 'CPU 型号' || echo 'CPU Model' ): $(lscpu | grep 'Model name' | sed 's/Model name:\s*//')"
echo "$( $SUPPORT_CHINESE && echo '内存总量' || echo 'Memory Total' ): $(free -h | awk '/Mem:/ {print $2}')"
echo
if $SUPPORT_CHINESE; then echo "GPU 状态:"; else echo "GPU Status:"; fi
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
    if $SUPPORT_CHINESE; then
        echo "未检测到 GPU（登录节点无 GPU 属正常情况）"
    else
        echo "No GPU detected (normal for login node)"
    fi
fi
echo

# ---------- Python 环境 ----------
if $SUPPORT_CHINESE; then echo -e "${BOLD}${BLUE}🐍 Python 环境${NC}"; else echo -e "${BOLD}${BLUE}🐍 Python Environment${NC}"; fi
print_line
if command -v python &> /dev/null; then
    echo -e "✔️ Python: ${GREEN}$(python --version 2>&1)${NC}"
else
    if $SUPPORT_CHINESE; then
        echo -e "❌ ${RED}未检测到 Python，请联系管理员或使用 Anaconda${NC}"
    else
        echo -e "❌ ${RED}Python not found. Please contact admin or use Anaconda.${NC}"
    fi
fi
echo

# ---------- 常用工具 ----------
if $SUPPORT_CHINESE; then echo -e "${BOLD}${BLUE}🔧 常用工具检测${NC}"; else echo -e "${BOLD}${BLUE}🔧 Common Toolchain Check${NC}"; fi
print_line
TOOLS=("git" "make" "conda" "wget" "curl" "tar" "vim")
missing_tools=()

for tool in "${TOOLS[@]}"; do
    if command -v $tool &> /dev/null; then
        ver=$($tool --version 2>&1 | head -n 1)
        echo -e "✔️ $tool: ${GREEN}${ver}${NC}"
    else
        if $SUPPORT_CHINESE; then
            echo -e "❌ ${RED}$tool: 未安装${NC}"
        else
            echo -e "❌ ${RED}$tool: Not installed${NC}"
        fi
        missing_tools+=("$tool")
    fi
done
echo

# ---------- 网络信息 ----------
if $SUPPORT_CHINESE; then echo -e "${BOLD}${BLUE}🌐 网络信息${NC}"; else echo -e "${BOLD}${BLUE}🌐 Network Information${NC}"; fi
print_line
echo "$( $SUPPORT_CHINESE && echo 'IP 地址' || echo 'IP Address' ): $(hostname -I 2>/dev/null | awk '{print $1}')"

gateway=$(ip route | grep default | awk '{print $3}')
if [ -n "$gateway" ]; then
    echo "$( $SUPPORT_CHINESE && echo '默认网关' || echo 'Default Gateway' ): $gateway"
else
    if $SUPPORT_CHINESE; then
        echo "未检测到默认网关（可能在隔离内网环境）"
    else
        echo "No default gateway detected (may be isolated network)"
    fi
fi

dns=$(grep "nameserver" /etc/resolv.conf | head -n1 | awk '{print $2}')
if [ -n "$dns" ]; then
    echo "$( $SUPPORT_CHINESE && echo 'DNS 服务器' || echo 'DNS Server' ): $dns"
else
    echo "$( $SUPPORT_CHINESE && echo '⚠️ 未配置 DNS' || echo '⚠️ No DNS configured')"
fi

echo -n "$( $SUPPORT_CHINESE && echo '外网连通性: ' || echo 'External Connectivity: ')"
ping -c 1 -W 1 www.baidu.com &>/dev/null && (
    $SUPPORT_CHINESE && echo "✅ 可访问百度" || echo "✅ Reachable (baidu.com)"
) || (
    ping -c 1 -W 1 www.google.com &>/dev/null && (
        $SUPPORT_CHINESE && echo "✅ 可访问 Google" || echo "✅ Reachable (google.com)"
    ) || (
        $SUPPORT_CHINESE && echo "❌ 无法访问外网" || echo "❌ No external network access"
    )
)
echo

# ---------- 结束信息 ----------
echo -e "${BOLD}===========================================================${NC}"
if $SUPPORT_CHINESE; then
  echo "✅ 环境检测完成 - 欢迎使用 HPC 平台！"
else
  echo "✅ Environment check completed - Welcome to the HPC platform!"
fi
echo -e "${BOLD}===========================================================${NC}"