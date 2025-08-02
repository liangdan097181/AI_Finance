#!/bin/bash

# 启动测试服务器脚本

echo "🚀 启动测试服务器"
echo "=================="

# 1. 清理现有进程
echo "🧹 清理现有进程..."
pkill -f "python app_with_deepseek.py" 2>/dev/null || true
sleep 2

# 2. 设置环境变量
export DEEPSEEK_API_KEY="sk-2d0a6b616f994c5991a36b7af9fd048b"
echo "✅ 环境变量已设置"

# 3. 启动后端服务器
echo "🔧 启动后端服务器..."
nohup python app_with_deepseek.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 4. 等待后端启动
echo "⏳ 等待后端启动..."
sleep 5

# 5. 测试后端 API
echo "🧪 测试后端 API..."
response=$(curl -s http://localhost:5001/api/market-indices)
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 后端 API 正常"
else
    echo "❌ 后端 API 异常"
    echo "响应: $response"
    exit 1
fi

# 6. 测试组合仓位占比功能
echo "📊 测试组合仓位占比功能..."
python test_portfolio_allocation.py

echo ""
echo "🎉 测试服务器启动完成！"
echo "========================"
echo "📊 后端服务: http://localhost:5001"
echo "🧪 测试完成，可以启动前端进行完整测试"
echo ""
echo "启动前端命令: npm start"
echo "停止后端命令: kill $BACKEND_PID"