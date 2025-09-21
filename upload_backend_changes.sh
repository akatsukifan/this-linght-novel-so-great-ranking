#!/bin/bash
# 后端代码上传脚本(Linux/Mac版)
# 此脚本用于将修改后的后端代码上传到AWS EC2实例

# 配置参数
EC2_IP="13.236.185.251"  # EC2实例的IP地址
PEM_FILE="G:\741520.pem"  # PEM密钥文件路径（Windows路径格式）
LOCAL_PROJECT_DIR="d:\novel ranking demo"  # Windows本地项目路径
REMOTE_PROJECT_DIR="/home/ec2-user/novel-ranking"

# 检查操作系统并调整路径格式
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux或Mac系统
    # 转换Windows路径到Linux/Mac格式
    # 用户需要根据实际情况修改这些路径
    echo "检测到Linux/Mac系统，请注意路径可能需要手动调整！"
    echo "建议修改脚本中的本地路径和PEM文件路径为Linux/Mac格式"
    # 提示用户手动修改
fi

# 确保PEM文件存在
if [ ! -f "$PEM_FILE" ]; then
    echo "错误：找不到PEM密钥文件 $PEM_FILE" >&2
    echo "请确保PEM密钥文件路径正确" >&2
    exit 1
fi

# 上传修改的后端文件
echo "正在上传修改的后端文件到EC2实例..."

# 上传views.py文件
echo "上传 cart/views.py..."
scp -i "$PEM_FILE" "$LOCAL_PROJECT_DIR/cart/views.py" ec2-user@${EC2_IP}:${REMOTE_PROJECT_DIR}/cart/views.py

if [ $? -ne 0 ]; then
    echo "上传views.py失败" >&2
    exit 1
fi

echo "文件上传成功！"
    
    # 提示用户登录EC2实例并重启服务
    echo "\n请执行以下步骤完成部署："
    echo "1. 通过SSH登录到EC2实例："
    echo "   ssh -i \"$PEM_FILE\" ec2-user@$EC2_IP"
    echo "2. 在EC2实例上执行以下命令重启Gunicorn服务："
    echo "   sudo systemctl restart novel-ranking"
    echo "3. 验证服务状态："
    echo "   sudo systemctl status novel-ranking"
    echo "\n如果需要查看应用日志，可以执行："
    echo "   sudo journalctl -u novel-ranking"