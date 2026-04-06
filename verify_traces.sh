#!/bin/bash

set -e

echo "=========================================="
echo "Phoenix Trace 数据验证"
echo "=========================================="

# 1. 检查 Phoenix 是否运行
echo ""
echo "1. 检查 Phoenix 状态..."
if curl -s http://localhost:6006/healthz > /dev/null 2>&1; then
    echo "✓ Phoenix 正在运行"
else
    echo "✗ Phoenix 未运行，请先启动: make start"
    exit 1
fi

# 2. 检查端口映射
echo ""
echo "2. 检查端口映射..."
if docker ps | grep -q "4317->4317"; then
    echo "✓ OTLP gRPC 端口 (4317) 已映射"
else
    echo "✗ OTLP gRPC 端口 (4317) 未映射"
    echo "请重启 Phoenix: make stop && make start"
    exit 1
fi

if docker ps | grep -q "6006->6006"; then
    echo "✓ Phoenix UI 端口 (6006) 已映射"
else
    echo "✗ Phoenix UI 端口 (6006) 未映射"
    exit 1
fi

# 3. 创建测试 trace
echo ""
echo "3. 创建测试 trace..."
source .venv/bin/activate
python test_trace.py

# 4. 等待数据同步
echo ""
echo "4. 等待数据同步到 Phoenix..."
sleep 3

# 5. 检查 Phoenix UI
echo ""
echo "5. 验证结果:"
echo "   - 打开 Phoenix UI: http://localhost:6006"
echo "   - 点击左侧 'Traces' 菜单"
echo "   - 应该能看到刚才创建的 trace"
echo ""
echo "✓ 验证完成！"
echo ""
echo "如果看不到数据，请检查:"
echo "  1. Phoenix 日志: docker logs cinder-phoenix"
echo "  2. Cinder 日志: tail -f ~/.cinder/cinder.log"
echo "  3. 网络连接: curl http://localhost:6006/healthz"
