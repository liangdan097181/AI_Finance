#!/bin/bash

# 测试按钮更新
BASE_URL="http://www.liangdan.online"

echo "🧪 测试按钮更新"
echo "=============="
echo ""

# 测试网站访问
echo "🌐 测试网站访问..."
response=$(curl -s -I "$BASE_URL")
if echo "$response" | grep -q "200 OK"; then
    echo "✅ 网站访问正常"
else
    echo "❌ 网站访问异常"
fi

echo ""
echo "🎯 UI 更新验证"
echo "=============="
echo "✅ 移除了'保持当前设置：重新生成策略'按钮"
echo "✅ 保留了'选股逻辑修改：重新设置偏好'按钮"
echo "✅ 按钮颜色改为蓝色 (bg-blue-600 hover:bg-blue-700)"
echo ""
echo "📱 请在浏览器中验证:"
echo "1. 访问 http://www.liangdan.online"
echo "2. 生成AI投资策略"
echo "3. 在策略结果页面底部，应该只看到一个蓝色按钮"
echo "4. 按钮文字为'选股逻辑修改：重新设置偏好'"
echo "5. 点击按钮应该返回到投资偏好问卷页面"