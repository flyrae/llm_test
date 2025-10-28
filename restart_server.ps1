# 重启LLM测试工具服务器
# 使用方法: 在PowerShell中运行 .\restart_server.ps1

Write-Host "🔄 正在重启LLM测试工具服务器..." -ForegroundColor Cyan

# 切换到backend目录
Set-Location D:\develop\llm_test\backend

Write-Host "📍 当前目录: $(Get-Location)" -ForegroundColor Gray

# 启动服务器
Write-Host "🚀 启动服务器..." -ForegroundColor Green
D:\mambaforge\envs\modelscope\python.exe app/main.py
