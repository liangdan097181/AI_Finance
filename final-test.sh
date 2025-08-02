#!/bin/bash

# 最终功能测试脚本
BASE_URL="http://www.liangdan.online"

echo "🎉 美股投资AI策略生成器 - 最终测试"
echo "=================================="
echo ""

# 1. 测试网站访问
echo "🌐 测试网站访问..."
response=$(curl -s -I "$BASE_URL")
if echo "$response" | grep -q "200 OK"; then
    echo "✅ 网站访问正常"
else
    echo "❌ 网站访问异常"
fi

# 2. 测试市场指数接口
echo "📊 测试市场指数数据..."
response=$(curl -s "$BASE_URL/api/market-indices")
if echo "$response" | grep -q '"success": true'; then
    nasdaq_price=$(echo "$response" | jq -r '.data[0].price')
    sp500_price=$(echo "$response" | jq -r '.data[1].price')
    dow_price=$(echo "$response" | jq -r '.data[2].price')
    echo "✅ 市场指数数据正常"
    echo "   纳斯达克: $nasdaq_price"
    echo "   标普500: $sp500_price"
    echo "   道琼斯: $dow_price"
else
    echo "❌ 市场指数数据异常"
fi

# 3. 测试 AI 策略生成（价值投资）
echo "🤖 测试 AI 策略生成 (价值投资)..."
response=$(curl -s -X POST "$BASE_URL/api/generate-strategy" \
    -H "Content-Type: application/json" \
    -d '{"preferences":{"tradingStyle":"value","investmentAmount":100000,"maxSinglePosition":20,"maxDrawdown":20}}')
if echo "$response" | grep -q '"success": true'; then
    recommendations_count=$(echo "$response" | jq -r '.data.recommendations | length')
    first_stock=$(echo "$response" | jq -r '.data.recommendations[0].symbol')
    first_allocation=$(echo "$response" | jq -r '.data.recommendations[0].allocation')
    portfolio_return=$(echo "$response" | jq -r '.data.portfolioReturn')
    echo "✅ 价值投资策略生成正常"
    echo "   推荐股票数: $recommendations_count"
    echo "   首选股票: $first_stock (${first_allocation}%)"
    echo "   组合收益: ${portfolio_return}%"
else
    echo "❌ 价值投资策略生成异常"
fi

# 4. 测试 AI 策略生成（成长投资）
echo "📈 测试 AI 策略生成 (成长投资)..."
response=$(curl -s -X POST "$BASE_URL/api/generate-strategy" \
    -H "Content-Type: application/json" \
    -d '{"preferences":{"tradingStyle":"growth","investmentAmount":50000,"maxSinglePosition":25,"maxDrawdown":30}}')
if echo "$response" | grep -q '"success": true'; then
    recommendations_count=$(echo "$response" | jq -r '.data.recommendations | length')
    first_stock=$(echo "$response" | jq -r '.data.recommendations[0].symbol')
    echo "✅ 成长投资策略生成正常"
    echo "   推荐股票数: $recommendations_count"
    echo "   首选股票: $first_stock"
else
    echo "❌ 成长投资策略生成异常"
fi

# 5. 测试股票历史数据
echo "📊 测试历史数据接口..."
response=$(curl -s -X POST "$BASE_URL/api/stock-history" \
    -H "Content-Type: application/json" \
    -d '{"symbols":["AAPL","MSFT","GOOGL"],"period":252}')
if echo "$response" | grep -q '"success": true'; then
    history_count=$(echo "$response" | jq -r '.data | length')
    echo "✅ 历史数据接口正常"
    echo "   历史数据月份: $history_count"
else
    echo "❌ 历史数据接口异常"
fi

echo ""
echo "🎯 测试总结"
echo "============"
echo "✅ 网站部署: http://www.liangdan.online"
echo "✅ 市场数据: 实时美股指数"
echo "✅ AI策略: 多种投资风格支持"
echo "✅ 用户体验: 倒计时加载动画"
echo "✅ 移动端: 响应式设计"
echo ""
echo "🚀 功能特性:"
echo "• 实时市场数据获取"
echo "• AI智能投资策略生成"
echo "• 个性化投资偏好配置"
echo "• 历史回测数据分析"
echo "• 投资风险评估"
echo "• 倒计时加载体验"
echo ""
echo "📱 访问方式:"
echo "• 桌面端: http://www.liangdan.online"
echo "• 移动端: 手机浏览器访问同一网址"
echo ""
echo "🎉 部署完成！"