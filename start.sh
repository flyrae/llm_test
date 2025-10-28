#!/bin/bash

echo "🚀 启动 LLM Test Tool..."
echo ""

# 检查Python
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python，请先安装 Python 3.8+"
    exit 1
fi
echo "✅ $(python3 --version)"

# 进入后端目录
cd backend

# 检查是否已安装依赖
echo ""
echo "检查依赖..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt -q

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  未找到 .env 文件，复制示例文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 启动应用
echo ""
echo "🎉 启动应用..."
echo "📡 访问地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python -m app.main
