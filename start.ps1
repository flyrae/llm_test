# 启动 LLM Test Tool

Write-Host "🚀 启动 LLM Test Tool..." -ForegroundColor Cyan
Write-Host ""

# 检查Python
Write-Host "检查 Python 环境..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 未找到 Python，请先安装 Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# 进入后端目录
Set-Location -Path "backend"

# 检查是否已安装依赖
Write-Host ""
Write-Host "检查依赖..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt -q

# 检查环境变量文件
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "⚠️  未找到 .env 文件，复制示例文件..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ 已创建 .env 文件，请根据需要修改配置" -ForegroundColor Green
}

# 启动应用
Write-Host ""
Write-Host "🎉 启动应用..." -ForegroundColor Cyan
Write-Host "📡 访问地址: http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API文档: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

python -m app.main
