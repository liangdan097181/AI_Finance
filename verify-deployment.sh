#!/bin/bash

# 部署验证脚本
echo "🔍 开始验证部署状态..."

# 1. 检查 Nginx 状态
echo "📊 检查 Nginx 状态:"
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 服务运行正常"
else
    echo "❌ Nginx 服务未运行"
fi

# 2. 检查 Nginx 配置
echo "📋 检查 Nginx 配置:"
if nginx -t 2>/dev/null; then
    echo "✅ Nginx 配置正确"
else
    echo "❌ Nginx 配置有误"
fi

# 3. 检查后端服务
echo "🔧 检查后端服务:"
if ps aux | grep -q "[p]ython.*app.py"; then
    echo "✅ 后端服务运行正常"
    echo "   进程信息: $(ps aux | grep '[p]ython.*app.py' | awk '{print $2, $11, $12}')"
else
    echo "❌ 后端服务未运行"
fi

# 4. 检查前端文件
echo "📁 检查前端文件:"
if [ -d "/var/www/finance-app/build" ] && [ "$(ls -A /var/www/finance-app/build)" ]; then
    echo "✅ 前端构建文件存在"
    echo "   文件数量: $(find /var/www/finance-app/build -type f | wc -l) 个文件"
else
    echo "❌ 前端构建文件不存在"
fi

# 5. 测试网站访问
echo "🌐 测试网站访问:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    echo "✅ 本地访问正常 (HTTP 200)"
else
    echo "⚠️  本地访问异常"
fi

# 6. 测试 API 接口
echo "🔌 测试 API 接口:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/market-indices | grep -q "200"; then
    echo "✅ API 接口正常 (HTTP 200)"
else
    echo "⚠️  API 接口异常"
fi

# 7. 检查端口占用
echo "🔌 检查端口占用:"
echo "   端口 80 (HTTP): $(netstat -tlnp | grep ':80 ' | awk '{print $7}' | cut -d'/' -f2)"
echo "   端口 5001 (后端): $(netstat -tlnp | grep ':5001 ' | awk '{print $7}' | cut -d'/' -f2)"

# 8. 检查日志
echo "📝 最近的错误日志:"
if [ -f "/var/log/nginx/error.log" ]; then
    echo "   Nginx 错误日志 (最近 5 行):"
    tail -5 /var/log/nginx/error.log 2>/dev/null || echo "   无错误日志"
fi

if [ -f "/var/www/finance-app/backend.log" ]; then
    echo "   后端日志 (最近 5 行):"
    tail -5 /var/www/finance-app/backend.log 2>/dev/null || echo "   无后端日志"
fi

echo ""
echo "🎯 验证完成！"
echo ""
echo "📋 手动验证步骤："
echo "1. 浏览器访问: http://www.liangdan.online"
echo "2. API 测试: curl http://www.liangdan.online/api/market-indices"
echo "3. 响应头检查: curl -I http://www.liangdan.online"