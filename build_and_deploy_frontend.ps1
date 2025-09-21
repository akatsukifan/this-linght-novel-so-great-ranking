# 前端构建和部署脚本（PowerShell版本）

# 配置参数
$EC2_IP = "13.236.185.251"
$PEM_FILE = "G:\741520.pem"
$PROJECT_DIR = "d:\novel ranking demo"
$BUILD_DIR = "$PROJECT_DIR\dist"
$REMOTE_DIR = "/home/ec2-user/novel-ranking/dist"

# 1. 执行前端构建
Set-Location -Path $PROJECT_DIR
Write-Host "正在构建前端应用..."
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "前端构建失败！" -ForegroundColor Red
    exit 1
}

Write-Host "前端构建成功！" -ForegroundColor Green

# 2. 压缩构建结果
Write-Host "正在压缩构建文件..."
Set-Location -Path $BUILD_DIR
# 创建临时目录用于压缩
$TEMP_ZIP_DIR = "$env:TEMP\dist_zip"
if (Test-Path $TEMP_ZIP_DIR) {
    Remove-Item -Path $TEMP_ZIP_DIR -Recurse -Force
}
New-Item -Path $TEMP_ZIP_DIR -ItemType Directory | Out-Null

# 复制文件到临时目录
Get-ChildItem -Path . | Copy-Item -Destination $TEMP_ZIP_DIR -Recurse -Force

# 压缩文件
$ZIP_FILE = "$env:TEMP\dist.zip"
if (Test-Path $ZIP_FILE) {
    Remove-Item -Path $ZIP_FILE -Force
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($TEMP_ZIP_DIR, $ZIP_FILE)

# 3. 通过SSH上传到EC2实例
Write-Host "正在上传构建文件到EC2实例..."
scp -i "$PEM_FILE" "$ZIP_FILE" ec2-user@${EC2_IP}:/home/ec2-user/

if ($LASTEXITCODE -ne 0) {
    Write-Host "文件上传失败！" -ForegroundColor Red
    exit 1
}

# 4. 在EC2实例上解压并部署
Write-Host "正在EC2实例上解压并部署..."
ssh -i "$PEM_FILE" ec2-user@${EC2_IP} "mkdir -p $REMOTE_DIR && rm -rf $REMOTE_DIR/* && unzip -o /home/ec2-user/dist.zip -d $REMOTE_DIR && chmod -R 755 $REMOTE_DIR && rm -f /home/ec2-user/dist.zip"

if ($LASTEXITCODE -ne 0) {
    Write-Host "在EC2实例上部署失败！" -ForegroundColor Red
    exit 1
}

# 5. 清理本地临时文件
Remove-Item -Path $TEMP_ZIP_DIR -Recurse -Force
Remove-Item -Path $ZIP_FILE -Force

# 6. 验证部署结果
Write-Host "前端部署成功！" -ForegroundColor Green
Write-Host "请访问 http://${EC2_IP} 查看部署后的网站"