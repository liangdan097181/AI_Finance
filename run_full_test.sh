#!/bin/bash

# 完整的 DeepSeek AI 集成测试脚本

echo "🚀 启动完整的 DeepSeek AI 测试环境"
echo "=================================="

# 1. 设置环境变量
export DEEPSEEK_API_KEY="sk-2d0a6b616f994c5991a36b7af9fd048b"
echo "✅ 环境变量已设置"

# 2. 清理现有进程
echo "🧹 清理现有进程..."
pkill -f "python app_with_deepseek.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
sleep 2

# 3. 启动后端服务器
echo "🔧 启动 DeepSeek AI 增强后端..."
nohup python app_with_deepseek.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 4. 等待后端启动
echo "⏳ 等待后端启动..."
sleep 5

# 5. 测试后端 API
echo "🧪 测试后端 API..."
response=$(curl -s -X POST http://localhost:5001/api/market-indices)
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 后端 API 正常"
else
    echo "❌ 后端 API 异常"
    exit 1
fi

# 6. 启动前端开发服务器
echo "🎨 启动前端开发服务器..."
npm start &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"

# 7. 等待前端启动
echo "⏳ 等待前端启动..."
sleep 10

# 8. 显示访问信息
echo ""
echo "🎉 测试环境启动完成！"
echo "=================================="
echo "📊 后端服务: http://localhost:5001"
echo "🎨 前端应用: http://localhost:3000"
echo "🤖 DeepSeek AI: 已集成"
echo ""
echo "📋 测试步骤:"
echo "1. 打开浏览器访问 http://localhost:3000"
echo "2. 填写投资偏好问卷"
echo "3. 点击 'AI生成投资策略'"
echo "4. 查看是否显示 AI 增强的策略分析"
echo ""
echo "🔍 监控日志:"
echo "- 后端日志: tail -f backend.log"
echo "- 前端控制台: 浏览器开发者工具"
echo ""
echo "⏹️  停止服务:"
echo "- 后端: kill $BACKEND_PID"
echo "- 前端: kill $FRONTEND_PID"
echo ""

# 9. 保持脚本运行
echo "按 Ctrl+C 停止所有服务..."
trap "echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 等待用户中断
while true; do
    sleep 1
done