#!/bin/bash

# Cinder Web Dashboard 启动脚本
# 同时启动后端 API 和前端开发服务器

set -e

# 颜色定义（白色背景适用的明亮颜色）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
BRIGHT_BLUE='\033[1;34m'
BRIGHT_GREEN='\033[1;32m'
BRIGHT_CYAN='\033[1;36m'
BRIGHT_YELLOW='\033[1;33m'
BRIGHT_MAGENTA='\033[1;35m'
NC='\033[0m'

# 默认配置
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
OPEN_BROWSER=${OPEN_BROWSER:-false}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --open)
            OPEN_BROWSER=true
            shift
            ;;
        --help)
            echo "用法: ./start-web.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --backend-port PORT    后端端口 (默认: 8000)"
            echo "  --frontend-port PORT   前端端口 (默认: 3000)"
            echo "  --open                 自动打开浏览器"
            echo "  --help                 显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}🚀 启动 Cinder Web Dashboard${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/cinder_cli/web/frontend"
LOG_DIR="$PROJECT_DIR/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志文件
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# 清空日志文件
> "$BACKEND_LOG"
> "$FRONTEND_LOG"

# 检查前端依赖
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}📦 安装前端依赖...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    cd "$PROJECT_DIR"
fi

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 停止服务...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$TAIL_PID" ]; then
        kill $TAIL_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ 服务已停止${NC}"
    echo ""
    echo -e "${BLUE}📋 日志文件位置:${NC}"
    echo -e "  后端日志: $BACKEND_LOG"
    echo -e "  前端日志: $FRONTEND_LOG"
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

# 启动后端
echo -e "${GREEN}▶ 启动后端 API (端口: $BACKEND_PORT)${NC}"
source .venv/bin/activate
uvicorn cinder_cli.web.server:create_app --factory --host localhost --port $BACKEND_PORT >> "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}✗ 后端启动失败${NC}"
    echo -e "${YELLOW}后端日志:${NC}"
    cat "$BACKEND_LOG"
    exit 1
fi

# 启动前端（设置 API 地址环境变量）
echo -e "${GREEN}▶ 启动前端开发服务器 (端口: $FRONTEND_PORT)${NC}"
cd "$FRONTEND_DIR"
NEXT_PUBLIC_API_URL="http://localhost:$BACKEND_PORT" PORT=$FRONTEND_PORT npm run dev >> "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_DIR"

# 等待前端启动
sleep 3

# 检查前端是否启动成功
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}✗ 前端启动失败${NC}"
    echo -e "${YELLOW}前端日志:${NC}"
    cat "$FRONTEND_LOG"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}✓ 服务启动成功！${NC}"
echo ""
echo -e "  ${GREEN}后端 API:${NC}  http://localhost:$BACKEND_PORT"
echo -e "  ${GREEN}API 文档:${NC}   http://localhost:$BACKEND_PORT/docs"
echo -e "  ${GREEN}前端界面:${NC}   http://localhost:$FRONTEND_PORT"
echo ""
echo -e "${BLUE}📋 日志文件:${NC}"
echo -e "  后端: $BACKEND_LOG"
echo -e "  前端: $FRONTEND_LOG"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 自动打开浏览器
if [ "$OPEN_BROWSER" = true ]; then
    sleep 2
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:$FRONTEND_PORT"
    elif command -v open &> /dev/null; then
        open "http://localhost:$FRONTEND_PORT"
    fi
fi

# 实时显示日志（带颜色和前缀）
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                           实时日志${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 使用 awk 为日志添加颜色和前缀
tail -f "$BACKEND_LOG" "$FRONTEND_LOG" 2>/dev/null | awk -v BRIGHT_CYAN="$BRIGHT_CYAN" -v BRIGHT_GREEN="$BRIGHT_GREEN" -v NC="$NC" '
{
    if (filename != FILENAME) {
        filename = FILENAME
    }
    
    # 后端日志 - 明亮青色
    if (index(FILENAME, "backend") > 0) {
        print BRIGHT_CYAN "[BACKEND]  " $0 NC
    }
    # 前端日志 - 明亮绿色
    else if (index(FILENAME, "frontend") > 0) {
        print BRIGHT_GREEN "[FRONTEND] " $0 NC
    }
    else {
        print $0
    }
    fflush()
}' &

TAIL_PID=$!

# 等待进程
wait $BACKEND_PID $FRONTEND_PID
