#!/bin/bash

# 域名部署脚本 - 仅 HTTP 配置
# 域名: www.liangdan.online
# 服务器: 103.146.158.177

set -e

echo "🌐 开始配置域名 www.liangdan.online (仅 HTTP)..."

# 1. 创建 Nginx 域名配置
echo "📝 创建 Nginx 配置文件..."
cat > /etc/nginx/sites-available/liangdan-online << 'EOF'
server {
    listen 80;
    server_name www.liangdan.online liangdan.online;
    
    # 前端静态文件
    location / {
        root /var/www/finance-app/build;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API 代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
EOF

echo "✅ Nginx 配置文件创建完成"

# 2. 启用新配置
echo "🔗 启用 Nginx 配置..."
ln -sf /etc/nginx/sites-available/liangdan-online /etc/nginx/sites-enabled/

# 3. 删除默认配置（如果存在）
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    echo "🗑️  删除默认配置..."
    rm -f /etc/nginx/sites-enabled/default
fi

# 4. 测试 Nginx 配置
echo "🧪 测试 Nginx 配置..."
if nginx -t; then
    echo "✅ Nginx 配置测试通过"
else
    echo "❌ Nginx 配置测试失败"
    exit 1
fi

# 5. 重新加载 Nginx
echo "🔄 重新加载 Nginx..."
systemctl reload nginx
echo "✅ Nginx 重新加载完成"

# 6. 检查后端服务状态
echo "🔍 检查后端服务状态..."
if ps aux | grep -q "[p]ython.*app.py"; then
    echo "✅ 后端服务正在运行"
    ps aux | grep "[p]ython.*app.py" | awk '{print "   进程 PID:", $2, "命令:", $11, $12}'
else
    echo "⚠️  后端服务未运行，正在启动..."
    cd /var/www/finance-app/backend
    if [ -d "venv" ]; then
        source venv/bin/activate
        nohup python app.py > ../backend.log 2>&1 &
        sleep 2
        if ps aux | grep -q "[p]ython.*app.py"; then
            echo "✅ 后端服务启动成功"
        else
            echo "❌ 后端服务启动失败，请检查日志"
        fi
    else
        echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    fi
fi

# 7. 检查前端构建
echo "🔍 检查前端构建..."
if [ -d "/var/www/finance-app/build" ] && [ "$(ls -A /var/www/finance-app/build)" ]; then
    echo "✅ 前端构建文件存在"
    echo "   文件数量: $(find /var/www/finance-app/build -type f | wc -l) 个文件"
else
    echo "⚠️  前端构建文件不存在，正在构建..."
    cd /var/www/finance-app
    if [ -f "package.json" ]; then
        npm run build
        if [ -d "build" ]; then
            echo "✅ 前端构建完成"
        else
            echo "❌ 前端构建失败"
        fi
    else
        echo "❌ package.json 不存在，请检查前端项目"
    fi
fi

# 8. 验证配置
echo "🔍 验证配置..."

# 检查 Nginx 状态
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 服务运行正常"
else
    echo "❌ Nginx 服务未运行"
fi

# 检查端口占用
echo "🔌 检查端口占用:"
nginx_process=$(netstat -tlnp 2>/dev/null | grep ':80 ' | awk '{print $7}' | cut -d'/' -f2)
backend_process=$(netstat -tlnp 2>/dev/null | grep ':5001 ' | awk '{print $7}' | cut -d'/' -f2)
echo "   端口 80 (HTTP): ${nginx_process:-未占用}"
echo "   端口 5001 (后端): ${backend_process:-未占用}"

# 测试本地访问
echo "🌐 测试本地访问:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    echo "✅ 本地访问正常 (HTTP 200)"
else
    echo "⚠️  本地访问异常"
fi

# 测试 API 接口
echo "🔌 测试 API 接口:"
api_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/market-indices)
if echo "$api_status" | grep -q "200"; then
    echo "✅ API 接口正常 (HTTP $api_status)"
else
    echo "⚠️  API 接口异常 (HTTP $api_status)"
fi

echo ""
echo "🎉 域名配置完成！"
echo ""
echo "🔍 验证方式："
echo "1. 浏览器访问: http://www.liangdan.online"
echo "2. API 测试: curl http://www.liangdan.online/api/market-indices"
echo "3. 响应头检查: curl -I http://www.liangdan.online"
echo ""
echo "📝 如果遇到问题，请检查："
echo "- DNS 解析是否生效"
echo "- 服务器防火墙设置"
echo "- 后端服务日志: tail -f /var/www/finance-app/backend.log"
echo "- Nginx 错误日志: tail -f /var/log/nginx/error.log"