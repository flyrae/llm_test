#!/usr/bin/env pwsh
# 启动脚本
Set-Location -Path "D:\develop\llm_test\backend"
& "D:\mambaforge\envs\modelscope\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
