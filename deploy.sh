#!/bin/bash

# 部署脚本 - 在服务器上运行

echo "开始部署 Finance App..."

# 设置项目目录
PROJECT_DIR="/var/www/finance-app"
cd $PROJECT_DIR

# 1. 安装前端依赖并构建
echo "安装前端依赖..."
npm install

echo "构建前端项目..."
npm run build

# 2. 设置后端环境
echo "设置后端 Python 环境..."
cd backend
python3 -m venv venv
source venv/bin/activate

# 安装后端依赖
pip install flask flask-cors akshare pandas numpy

# 3. 创建 PM2 配置文件
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
    max_memory_restart: '1G'
  }]
};
EOF

# 4. 启动后端服务
echo "启动后端服务..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# 5. 配置 Nginx
echo "配置 Nginx..."
cat > /etc/nginx/sites-available/finance-app << 'EOF'
server {
    listen 80;
    server_name 103.146.158.177;
    
    # 前端静态文件
    location / {
        root /var/www/finance-app/build;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
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
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/finance-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试并重启 Nginx
nginx -t && systemctl restart nginx

# 6. 设置防火墙
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

echo "部署完成！"
echo "前端访问地址: http://103.146.158.177"
echo "后端 API 地址: http://103.146.158.177/api/"

# 显示服务状态
echo "=== 服务状态 ==="
pm2 status
systemctl status nginx