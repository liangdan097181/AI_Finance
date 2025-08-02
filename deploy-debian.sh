#!/bin/bash

# Debian 11.2 部署脚本 - Finance App

echo "开始在 Debian 11.2 上部署 Finance App..."

# 设置项目目录
PROJECT_DIR="/var/www/finance-app"
cd $PROJECT_DIR

# 1. 系统更新
echo "更新系统包..."
apt update && apt upgrade -y

# 2. 安装基础依赖
echo "安装基础依赖..."
apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates

# 3. 安装 Python 3.9+ (Debian 11 需要升级)
echo "安装 Python 环境..."
apt install -y python3 python3-pip python3-venv python3-dev build-essential

# 安装 Python 3.10 (更好的兼容性)
echo "添加 Python 3.10 源..."
echo "deb http://deb.debian.org/debian bullseye-backports main" >> /etc/apt/sources.list
apt update
apt install -y -t bullseye-backports python3.10 python3.10-venv python3.10-dev || echo "使用系统默认 Python 3.9"

# 4. 安装 Node.js 18 LTS
echo "安装 Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 5. 安装 Nginx
echo "安装 Nginx..."
apt install -y nginx

# 6. 安装 PM2
echo "安装 PM2..."
npm install -g pm2

# 7. 安装前端依赖并构建
echo "安装前端依赖..."
npm install

echo "构建前端项目..."
npm run build

# 8. 设置后端 Python 环境
echo "设置后端 Python 环境..."
cd backend
# 优先使用 Python 3.10，如果没有则使用 3.9
if command -v python3.10 &> /dev/null; then
    python3.10 -m venv venv
else
    python3 -m venv venv
fi
source venv/bin/activate

# 9. 安装后端依赖
echo "安装后端依赖..."
pip install --upgrade pip setuptools wheel

# 安装核心依赖
pip install flask flask-cors pandas numpy requests

# 尝试安装 akshare (如果失败会继续)
echo "尝试安装 akshare..."
pip install akshare || echo "akshare 安装失败，将使用模拟数据"

# 10. 创建 PM2 配置文件
cd $PROJECT_DIR
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'finance-backend',
    script: 'backend/app.py',
    interpreter: 'backend/venv/bin/python',
    cwd: '/var/www/finance-app',
    env: {
      FLASK_ENV: 'production',
      PORT: 5001
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: '/var/log/finance-backend-error.log',
    out_file: '/var/log/finance-backend-out.log',
    log_file: '/var/log/finance-backend.log'
  }]
};
EOF

# 11. 启动后端服务
echo "启动后端服务..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd

# 12. 配置 Nginx
echo "配置 Nginx..."
cat > /etc/nginx/sites-available/finance-app << 'EOF'
server {
    listen 80;
    server_name _;
    
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
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/finance-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试并重启 Nginx
nginx -t && systemctl restart nginx
systemctl enable nginx

# 13. 设置防火墙 (如果安装了 ufw)
if command -v ufw &> /dev/null; then
    echo "配置防火墙..."
    ufw allow 22
    ufw allow 80
    ufw allow 443
    ufw --force enable
fi

# 14. 创建日志目录
mkdir -p /var/log
touch /var/log/finance-backend-error.log
touch /var/log/finance-backend-out.log
touch /var/log/finance-backend.log

# 15. 设置权限
chown -R www-data:www-data /var/www/finance-app/build
chmod -R 755 /var/www/finance-app/build

echo "部署完成！"
echo "前端访问地址: http://$(hostname -I | awk '{print $1}')"
echo "后端 API 地址: http://$(hostname -I | awk '{print $1}')/api/"

# 显示服务状态
echo "=== 服务状态 ==="
echo "PM2 进程:"
pm2 status
echo ""
echo "Nginx 状态:"
systemctl status nginx --no-pager -l
echo ""
echo "Python 版本:"
python3 --version
echo ""
echo "Node.js 版本:"
node --version
echo ""
echo "npm 版本:"
npm --version