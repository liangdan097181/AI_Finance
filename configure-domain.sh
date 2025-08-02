#!/bin/bash

# 域名配置脚本 - www.liangdan.online
# 服务器: 103.146.158.177

set -e

echo "🌐 开始配置域名 www.liangdan.online..."

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

# 3. 测试 Nginx 配置
echo "🧪 测试 Nginx 配置..."
if nginx -t; then
    echo "✅ Nginx 配置测试通过"
else
    echo "❌ Nginx 配置测试失败"
    exit 1
fi

# 4. 重新加载 Nginx
echo "🔄 重新加载 Nginx..."
systemctl reload nginx
echo "✅ Nginx 重新加载完成"

# 5. 检查后端服务状态
echo "🔍 检查后端服务状态..."
if ps aux | grep -q "[p]ython.*app.py"; then
    echo "✅ 后端服务正在运行"
else
    echo "⚠️  后端服务未运行，正在启动..."
    cd /var/www/finance-app/backend
    if [ -d "venv" ]; then
        source venv/bin/activate
        nohup python app.py > ../backend.log 2>&1 &
        echo "✅ 后端服务已启动"
    else
        echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    fi
fi

# 6. 检查前端构建
echo "🔍 检查前端构建..."
if [ -d "/var/www/finance-app/build" ] && [ "$(ls -A /var/www/finance-app/build)" ]; then
    echo "✅ 前端构建文件存在"
else
    echo "⚠️  前端构建文件不存在，正在构建..."
    cd /var/www/finance-app
    if [ -f "package.json" ]; then
        npm run build
        echo "✅ 前端构建完成"
    else
        echo "❌ package.json 不存在，请检查前端项目"
    fi
fi

# 7. 验证配置
echo "🔍 验证配置..."
echo "检查 Nginx 状态:"
systemctl status nginx --no-pager -l

echo ""
echo "🎉 域名配置完成！"
echo ""
echo "📋 DNS 解析配置提醒："
echo "请在域名服务商配置以下 DNS 记录："
echo "| 类型 | 主机记录 | 记录值          |"
echo "|------|----------|----------------|"
echo "| A    | www      | 103.146.158.177|"
echo "| A    | @        | 103.146.158.177|"
echo ""
echo "🔍 验证方式："
echo "1. 访问网站: http://www.liangdan.online"
echo "2. 测试 API: http://www.liangdan.online/api/market-indices"
echo "3. 检查响应: curl -I http://www.liangdan.online"
echo ""
echo "🔒 SSL 证书配置（可选）："
echo "apt install -y certbot python3-certbot-nginx"
echo "certbot --nginx -d www.liangdan.online -d liangdan.online"