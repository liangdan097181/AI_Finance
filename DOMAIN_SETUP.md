# 域名配置指南

## 🎯 目标
配置域名 `www.liangdan.online` 指向服务器 `103.146.158.177`

## 📋 前置条件
1. 服务器已部署应用 (前端 + 后端)
2. Nginx 已安装并运行
3. 域名 DNS 解析已配置

## 🚀 快速开始

### 1. 上传脚本到服务器
```bash
# 将所有脚本文件上传到服务器
scp *.sh root@103.146.158.177:/root/
```

### 2. 连接服务器并执行
```bash
# SSH 连接服务器
ssh root@103.146.158.177

# 执行主配置脚本
./setup-domain.sh
```

## 📁 脚本说明

### `setup-domain.sh` - 主配置脚本
交互式配置脚本，提供三个选项：
- 基础域名配置 (仅 HTTP)
- 完整配置 (HTTP + SSL)
- 验证当前状态

### `configure-domain.sh` - 域名配置脚本
- 创建 Nginx 域名配置
- 启用配置并重载 Nginx
- 检查后端服务状态
- 验证前端构建文件

### `setup-ssl.sh` - SSL 证书配置脚本
- 安装 Certbot
- 获取 Let's Encrypt 证书
- 配置自动续期

### `verify-deployment.sh` - 验证脚本
- 检查各项服务状态
- 测试网站和 API 访问
- 显示错误日志

## 🌐 DNS 配置

在域名服务商配置以下 DNS 记录：

| 类型 | 主机记录 | 记录值 | TTL |
|------|----------|--------|-----|
| A | www | 103.146.158.177 | 600 |
| A | @ | 103.146.158.177 | 600 |

## ✅ 验证步骤

### 1. 检查 DNS 解析
```bash
# 检查域名解析
nslookup www.liangdan.online
dig www.liangdan.online
```

### 2. 测试网站访问
```bash
# 测试 HTTP 访问
curl -I http://www.liangdan.online

# 测试 API 接口
curl http://www.liangdan.online/api/market-indices
```

### 3. 浏览器访问
- 主页: http://www.liangdan.online
- API: http://www.liangdan.online/api/market-indices

## 🔧 故障排除

### Nginx 配置问题
```bash
# 检查 Nginx 配置
nginx -t

# 查看 Nginx 状态
systemctl status nginx

# 查看错误日志
tail -f /var/log/nginx/error.log
```

### 后端服务问题
```bash
# 检查后端进程
ps aux | grep python

# 查看后端日志
tail -f /var/www/finance-app/backend.log

# 重启后端服务
cd /var/www/finance-app/backend
source venv/bin/activate
nohup python app.py > ../backend.log 2>&1 &
```

### 前端构建问题
```bash
# 检查构建文件
ls -la /var/www/finance-app/build/

# 重新构建前端
cd /var/www/finance-app
npm run build
```

## 🔒 SSL 证书

### 手动配置 SSL
```bash
# 安装 Certbot
apt install -y certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d www.liangdan.online -d liangdan.online

# 测试自动续期
certbot renew --dry-run
```

### 证书续期
证书会自动续期，也可以手动续期：
```bash
certbot renew
```

## 📞 支持

如果遇到问题，请检查：
1. DNS 解析是否生效 (可能需要等待几分钟)
2. 服务器防火墙设置
3. Nginx 和后端服务状态
4. 域名是否正确配置