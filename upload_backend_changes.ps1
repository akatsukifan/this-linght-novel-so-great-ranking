# 后端代码上传脚本
# 此脚本用于将修改后的后端代码上传到AWS EC2实例

# 配置参数
$EC2_IP = "13.236.185.251"  # EC2实例的IP地址
$PEM_FILE = "G:\741520.pem"  # PEM密钥文件路径
$LOCAL_PROJECT_DIR = "d:\novel ranking demo"
$REMOTE_PROJECT_DIR = "/home/ec2-user/novel-ranking"

# 确保PEM文件存在
if (-not (Test-Path $PEM_FILE)) {
    Write-Host "错误：找不到PEM密钥文件 $PEM_FILE" -ForegroundColor Red
    Write-Host "请确保PEM密钥文件路径正确" -ForegroundColor Yellow
    exit 1
}

# 上传修改的后端文件
Write-Host "正在上传修改的后端文件到EC2实例..." -ForegroundColor Green

try {
    # 上传views.py文件
    Write-Host "上传 cart/views.py..."
    scp -i "$PEM_FILE" "$LOCAL_PROJECT_DIR\cart\views.py" ec2-user@${EC2_IP}:${REMOTE_PROJECT_DIR}/cart/views.py
    
    if ($LASTEXITCODE -ne 0) {
        throw "上传views.py失败"
    }
    
    Write-Host "文件上传成功！" -ForegroundColor Green
    
    # 提示用户登录EC2实例并重启服务
    Write-Host "\n请执行以下步骤完成部署：" -ForegroundColor Cyan
    Write-Host "1. 通过SSH登录到EC2实例："
    Write-Host "   ssh -i \"$PEM_FILE\" ec2-user@$EC2_IP" -ForegroundColor Yellow
    Write-Host "2. 在EC2实例上执行以下命令重启Gunicorn服务："
    Write-Host "   sudo systemctl restart novel-ranking" -ForegroundColor Yellow
    Write-Host "3. 验证服务状态："
    Write-Host "   sudo systemctl status novel-ranking" -ForegroundColor Yellow
    Write-Host "\n如果需要查看应用日志，可以执行："
    Write-Host "   sudo journalctl -u novel-ranking" -ForegroundColor Yellow
    
} catch {
    Write-Host "上传过程中出现错误：$_" -ForegroundColor Red
    Write-Host "请检查EC2实例连接设置和网络连接" -ForegroundColor Yellow
    exit 1
}