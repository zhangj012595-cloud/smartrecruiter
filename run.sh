#!/bin/bash
# SmartRecruiter启动脚本

echo "🚀 启动 SmartRecruiter..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python 3.10+"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "❌ 未找到requirements.txt"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 检查配置文件
if [ ! -f "config/config.yaml" ]; then
    echo "⚙️  创建配置文件..."
    cp config/example_config.yaml config/config.yaml
    echo "✅ 配置文件已创建，请编辑 config/config.yaml 进行配置"
fi

# 运行测试
echo "🧪 运行基本测试..."
python3 test_basic_flow.py

if [ $? -eq 0 ]; then
    echo "✅ 测试通过！"
    
    # 启动应用
    echo "🌐 启动SmartRecruiter Web应用..."
    echo "👉 请在浏览器中访问: http://localhost:8501"
    echo "👉 按 Ctrl+C 停止应用"
    
    streamlit run app.py
else
    echo "❌ 测试失败，请检查错误信息"
    exit 1
fi