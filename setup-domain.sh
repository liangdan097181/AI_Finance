#!/bin/bash

# 域名配置主脚本
echo "🚀 开始域名配置流程..."

# 给脚本添加执行权限
chmod +x configure-domain.sh
chmod +x setup-ssl.sh
chmod +x verify-deployment.sh

echo "📋 配置选项："
echo "1. 基础域名配置 (HTTP)"
echo "2. 完整配置 (HTTP + SSL)"
echo "3. 仅验证当前状态"

read -p "请选择配置选项 (1-3): " choice

case $choice in
    1)
        echo "🔧 执行基础域名配置..."
        ./configure-domain.sh
        echo "✅ 基础配置完成"
        ./verify-deployment.sh
        ;;
    2)
        echo "🔧 执行完整域名配置..."
        ./configure-domain.sh
        echo "⏳ 等待 DNS 解析生效 (建议等待 5-10 分钟)..."
        read -p "DNS 解析配置完成后按回车继续 SSL 配置..."
        ./setup-ssl.sh
        echo "✅ 完整配置完成"
        ./verify-deployment.sh
        ;;
    3)
        echo "🔍 验证当前部署状态..."
        ./verify-deployment.sh
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 域名配置流程完成！"
echo ""
echo "📋 重要提醒："
echo "1. 确保 DNS 解析已配置："
echo "   - A 记录: www -> 103.146.158.177"
echo "   - A 记录: @ -> 103.146.158.177"
echo ""
echo "2. 访问测试："
echo "   - HTTP: http://www.liangdan.online"
echo "   - HTTPS: https://www.liangdan.online (如果配置了 SSL)"
echo ""
echo "3. API 测试："
echo "   - curl http://www.liangdan.online/api/market-indices"