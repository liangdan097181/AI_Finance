#!/bin/bash

# API 功能测试脚本
BASE_URL="http://www.liangdan.online"

echo "🧪 开始测试 API 功能..."

# 1. 测试市场指数接口
echo "📊 测试市场指数接口..."
response=$(curl -s "$BASE_URL/api/market-indices")
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 市场指数接口正常"
    echo "   数据: $(echo "$response" | jq -r '.data[0].name'): $(echo "$response" | jq -r '.data[0].price')"
else
    echo "❌ 市场指数接口异常"
fi

# 2. 测试股票数据接口
echo "📈 测试股票数据接口..."
response=$(curl -s -X POST "$BASE_URL/api/stock-data" \
    -H "Content-Type: application/json" \
    -d '{"symbols":["AAPL","MSFT"]}')
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 股票数据接口正常"
    echo "   AAPL 价格: $(echo "$response" | jq -r '.data[0].currentPrice')"
else
    echo "❌ 股票数据接口异常"
fi

# 3. 测试 AI 策略生成接口
echo "🤖 测试 AI 策略生成接口..."
response=$(curl -s -X POST "$BASE_URL/api/generate-strategy" \
    -H "Content-Type: application/json" \
    -d '{"preferences":{"tradingStyle":"value","investmentAmount":100000,"maxSinglePosition":20,"maxDrawdown":20}}')
if echo "$response" | grep -q '"success": true'; then
    echo "✅ AI 策略生成接口正常"
    recommendations_count=$(echo "$response" | jq -r '.data.recommendations | length')
    echo "   生成了 $recommendations_count 个投资推荐"
    echo "   第一个推荐: $(echo "$response" | jq -r '.data.recommendations[0].symbol') - $(echo "$response" | jq -r '.data.recommendations[0].allocation')%"
else
    echo "❌ AI 策略生成接口异常"
    echo "   错误: $(echo "$response" | jq -r '.error')"
fi

# 4. 测试历史数据接口
echo "📊 测试历史数据接口..."
response=$(curl -s -X POST "$BASE_URL/api/stock-history" \
    -H "Content-Type: application/json" \
    -d '{"symbols":["AAPL","MSFT"],"period":252}')
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 历史数据接口正常"
    history_count=$(echo "$response" | jq -r '.data | length')
    echo "   获取了 $history_count 个月的历史数据"
else
    echo "❌ 历史数据接口异常"
fi

echo ""
echo "🎉 API 测试完成！"
echo ""
echo "🌐 网站访问: $BASE_URL"
echo "📱 移动端测试: 请在手机浏览器中访问上述网址"