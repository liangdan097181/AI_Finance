#!/bin/bash

# SSL 证书配置脚本
set -e

echo "🔒 开始配置 SSL 证书..."

# 1. 更新系统包
echo "📦 更新系统包..."
apt update

# 2. 安装 Certbot
echo "📥 安装 Certbot..."
apt install -y certbot python3-certbot-nginx

# 3. 获取 SSL 证书
echo "🔐 获取 SSL 证书..."
certbot --nginx -d www.liangdan.online -d liangdan.online --non-interactive --agree-tos --email admin@liangdan.online

# 4. 设置自动续期
echo "⏰ 设置证书自动续期..."
systemctl enable certbot.timer
systemctl start certbot.timer

# 5. 测试自动续期
echo "🧪 测试自动续期..."
certbot renew --dry-run

echo "✅ SSL 证书配置完成！"
echo "🌐 现在可以通过 https://www.liangdan.online 访问网站"