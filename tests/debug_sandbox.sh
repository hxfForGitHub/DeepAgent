#!/bin/bash
# OpenSandbox 调试脚本 - 把完整日志保存到文件
set -e

LOG_FILE="tests/sandbox_debug.log"

echo "===== OpenSandbox 调试日志 =====" > "$LOG_FILE"
echo "时间: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "1. Docker 状态" >> "$LOG_FILE"
docker info 2>&1 | grep -E "Server Version|Containers" >> "$LOG_FILE" 2>&1 || echo "Docker 未运行" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "2. 沙箱镜像" >> "$LOG_FILE"
docker images | grep -E "opensandbox|code-interpreter" >> "$LOG_FILE" 2>&1 || echo "无沙箱镜像" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "3. 运行中的容器" >> "$LOG_FILE"
docker ps -a | head -20 >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

echo "4. OpenSandbox 服务检查" >> "$LOG_FILE"
curl -s http://localhost:8080/health >> "$LOG_FILE" 2>&1 || echo "服务未运行" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "5. 运行测试脚本" >> "$LOG_FILE"
cd "$(dirname "$0")/.."
python tests/test_sandbox.py >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

echo "6. 再次检查容器" >> "$LOG_FILE"
docker ps -a | grep sandbox >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

echo "===== 结束 =====" >> "$LOG_FILE"
echo "日志已保存到: $(pwd)/tests/sandbox_debug.log"
