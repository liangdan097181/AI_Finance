#!/bin/bash

echo "🚀 更新服务器代码..."

# 服务器信息
SERVER="root@103.146.158.177"
PROJECT_PATH="/var/www/finance-app"

echo "📥 拉取最新代码..."
ssh $SERVER "cd $PROJECT_PATH && git pull origin main"

echo "🔄 重启后端服务..."
ssh $SERVER "cd $PROJECT_PATH && pkill -f 'python.*app_with_deepseek.py' || true"
ssh $SERVER "cd $PROJECT_PATH && nohup python3 app_with_deepseek.py > backend.log 2>&1 &"

echo "🔄 重新构建前端..."
ssh $SERVER "cd $PROJECT_PATH && npm run build"

echo "🔄 重启Nginx..."
ssh $SERVER "systemctl reload nginx"

echo "✅ 服务器更新完成！"

echo "🧪 测试服务状态..."
sleep 3

# 测试API
echo "测试API接口..."
curl -s -X POST http://103.146.158.177/api/generate-strategy \
  -H "Content-Type: application/json" \
  -d '{"preferences":{"investmentAmount":5900,"tradingStyle":"growth","allowShortSelling":false}}' \
  | python3 -m json.tool

echo "🎉 更新完成！"