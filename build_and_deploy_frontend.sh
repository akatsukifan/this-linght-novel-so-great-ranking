#!/bin/bash

# 前端构建和部署脚本

# 配置参数
EC2_IP="13.236.185.251"
PEM_FILE="G:\741520.pem"
BUILD_DIR="d:\novel ranking demo\dist"
REMOTE_DIR="/home/ec2-user/novel-ranking/dist"

# 确保PEM文件路径正确（在Windows上使用双反斜杠）
PEM_FILE_WIN=$(echo "$PEM_FILE" | sed 's/\\/\\\\/g')

# 1. 执行前端构建
cd "d:\novel ranking demo"
echo "正在构建前端应用..."
npm run build

if [ $? -ne 0 ]; then
    echo "前端构建失败！"
exit 1
fi

echo "前端构建成功！"

# 2. 压缩构建结果
echo "正在压缩构建文件..."
cd "$BUILD_DIR"
zip -r dist.zip .

# 3. 通过SSH上传到EC2实例
echo "正在上传构建文件到EC2实例..."
scp -i "$PEM_FILE" dist.zip ec2-user@$EC2_IP:/home/ec2-user/

if [ $? -ne 0 ]; then
    echo "文件上传失败！"
exit 1
fi

# 4. 在EC2实例上解压并部署
echo "正在EC2实例上解压并部署..."
ssh -i "$PEM_FILE" ec2-user@$EC2_IP << EOF
    # 创建部署目录（如果不存在）
    mkdir -p "$REMOTE_DIR"
    
    # 删除旧文件
    rm -rf "$REMOTE_DIR"/*
    
    # 解压新文件
    unzip -o /home/ec2-user/dist.zip -d "$REMOTE_DIR"
    
    # 设置文件权限
    chmod -R 755 "$REMOTE_DIR"
    
    # 清理临时文件
    rm -f /home/ec2-user/dist.zip
    
    echo "前端部署成功！"
EOF

# 5. 清理本地临时文件
cd "$BUILD_DIR"
rm -f dist.zip

# 6. 验证部署结果
echo "正在验证部署结果..."
echo "请访问 http://$EC2_IP 查看部署后的网站"