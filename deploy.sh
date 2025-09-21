#!/bin/bash

# 小说排名网站快速部署脚本（AWS版）
# 使用方法：在AWS EC2实例上运行 chmod +x deploy.sh && ./deploy.sh

# 配置变量
PROJECT_PATH="$(pwd)"
VENV_PATH="$PROJECT_PATH/venv"

# 安装系统依赖
echo "正在安装系统依赖..."
sudo dnf update
sudo dnf install -y python3 python3-pip python3-venv nginx git

# 创建虚拟环境
if [ ! -d "$VENV_PATH" ]; then
    echo "正在创建Python虚拟环境..."
    python3 -m venv $VENV_PATH
fi

# 激活虚拟环境
source $VENV_PATH/bin/activate

# 安装项目依赖
echo "正在安装项目依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 收集静态文件
echo "正在收集静态文件..."
python manage.py collectstatic --noinput

# 运行数据库迁移（如果需要）
echo "正在运行数据库迁移..."
python manage.py migrate

# 配置Gunicorn服务
echo "正在配置Gunicorn服务..."
SERVICE_FILE="/etc/systemd/system/novel-ranking.service"

sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Gunicorn daemon for Novel Ranking website
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=$PROJECT_PATH
ExecStart=$VENV_PATH/bin/gunicorn --config gunicorn_config.py backend.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 启动并启用Gunicorn服务
echo "正在启动Gunicorn服务..."
sudo systemctl daemon-reload
sudo systemctl start novel-ranking
sudo systemctl enable novel-ranking

# 配置Nginx（Amazon Linux 2023使用conf.d目录）
NGINX_CONF="/etc/nginx/conf.d/novel-ranking.conf"

echo "正在配置Nginx..."
sudo bash -c "cat > $NGINX_CONF" << 'EOF'
# Nginx 配置 - 小说排名网站

server {
    listen 80;
    server_name _;
    server_name 13.236.185.251;

    # 静态文件配置
    location /static/ {
        alias /home/ec2-user/novel-ranking/staticfiles/;
        expires 30d;
    }

    # 前端Vue项目配置
    location / {
        root /home/ec2-user/novel-ranking/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API配置
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 管理后台配置
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 错误页面
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

# 检查Nginx配置并重启
sudo nginx -t
sudo systemctl restart nginx

# 配置防火墙（Amazon Linux 2023安全组已处理主要防火墙规则）
echo "正在配置防火墙..."
# 检查并安装firewalld（如需要）
if ! command -v firewall-cmd &> /dev/null; then
    echo "firewalld未安装，正在安装..."
    sudo dnf install -y firewalld
    sudo systemctl start firewalld
    sudo systemctl enable firewalld
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --reload
    echo "firewalld配置完成！"
else
    echo "firewalld已安装，配置防火墙规则..."
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --reload
    echo "防火墙规则配置完成！"
fi

# 输出AWS安全组提醒
echo "请注意：AWS EC2的主要防火墙规则由安全组控制，请确保您的安全组已开放80、443和22端口！"

# 输出部署结果
echo "\n部署完成！\n"
echo "项目路径: $PROJECT_PATH"
echo "\n请完成以下步骤："
echo "1. 查看您的AWS EC2实例公网IP地址"
echo "2. 将您的域名解析到AWS EC2实例的公网IP"
echo "3. 在AWS EC2安全组中确保已开放80、443、22端口"
echo "4. 访问 http://您的域名 或 http://您的AWS EC2实例IP查看网站"
echo "\n查看服务状态命令："
echo "- Gunicorn: systemctl status novel-ranking"
echo "- Nginx: systemctl status nginx"
echo "\n如有问题，请参考DEPLOYMENT_GUIDE.md文档"