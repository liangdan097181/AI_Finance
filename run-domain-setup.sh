#!/bin/bash

# 域名配置执行脚本
SERVER="103.146.158.177"
USER="root"

echo "🚀 开始域名配置流程..."

# 1. 上传配置脚本到服务器
echo "📤 上传配置脚本到服务器..."
scp deploy-domain.sh verify-deployment.sh ${USER}@${SERVER}:/root/

# 2. 连接服务器并执行配置
echo "🔧 连接服务器执行配置..."
ssh ${USER}@${SERVER} << 'EOF'
# 给脚本添加执行权限
chmod +x deploy-domain.sh verify-deployment.sh

echo "🌐 执行域名配置..."
./deploy-domain.sh

echo ""
echo "🔍 执行验证检查..."
./verify-deployment.sh

echo ""
echo "✅ 域名配置完成！"
echo "🌐 请访问: http://www.liangdan.online"
EOF

echo ""
echo "🎉 配置流程完成！"
echo ""
echo "📋 验证步骤："
echo "1. 浏览器访问: http://www.liangdan.online"
echo "2. API 测试: curl http://www.liangdan.online/api/market-indices"