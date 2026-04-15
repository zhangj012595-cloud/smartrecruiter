#!/bin/bash

# 简单的项目上下文检查脚本
# 用于快速验证工作目录是否正确

echo "="===============================================
echo "🔍 项目上下文快速检查"
echo "="===============================================

# 1. 检查当前目录
echo ""
echo "📍 当前工作目录:"
pwd
echo "  相对路径: $(pwd | sed "s|$HOME|~|")"

# 2. 检查是否在smartrecruiter项目中
if [[ $(basename "$PWD") == "smartrecruiter-mvp" ]]; then
    echo "✅ 正确: 在smartrecruiter-mvp项目中"
    
    # 检查项目文件
    echo ""
    echo "📁 项目文件检查:"
    if [ -f "app.py" ]; then
        echo "   ✅ app.py (主应用)"
    fi
    if [ -f "app_enhanced.py" ]; then
        echo "   ✅ app_enhanced.py (增强版应用)"
    fi
    if [ -d "channels" ]; then
        echo "   ✅ channels/ (招聘渠道模块)"
    fi
    if [ -d "config" ]; then
        echo "   ✅ config/ (配置管理)"
    fi
    if [ -f "requirements.txt" ]; then
        echo "   ✅ requirements.txt (依赖文件)"
    fi
    if [ -f "README.md" ]; then
        echo "   ✅ README.md (项目文档)"
    fi
    
    # 检查Git状态
    echo ""
    echo "📦 Git状态:"
    if [ -d ".git" ]; then
        echo "   ✅ Git仓库已初始化"
        git remote -v 2>/dev/null | head -2 | while read line; do
            echo "      $line"
        done
    else
        echo "   ❌ 不是Git仓库"
    fi
    
    # 文件统计
    echo ""
    echo "📊 项目统计:"
    echo "   文件总数: $(find . -type f -name "*.py" -o -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.sh" | wc -l)"
    echo "   Python文件: $(find . -name "*.py" | wc -l)"
    echo "   文档文件: $(find . -name "*.md" | wc -l)"
    
else
    echo "⚠️  警告: 不在smartrecruiter-mvp项目中"
    echo ""
    echo "建议操作:"
    echo "1. 切换到正确目录: cd smartrecruiter-mvp/"
    echo "2. 或者确认是否要在其他项目中工作"
    echo ""
    echo "可用项目:"
    ls -d */ 2>/dev/null | grep -E "smartrecruiter|project" || echo "   未发现明显的项目目录"
fi

# 3. 检查整合状态
echo ""
echo "="===============================================
echo "🔄 整合状态检查"
echo "="===============================================

# 检查关键整合文件
integrated_files=(
    "channels/github.py"
    "config/recruitment_config.py" 
    "app_enhanced.py"
    "utils/github_talent_advanced.py"
    "tools/recruitment_config_web.py"
)

echo "整合的关键文件:"
for file in "${integrated_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
    fi
done

# 4. 建议
echo ""
echo "="===============================================
echo "💡 建议"
echo "="===============================================

if [[ $(basename "$PWD") == "smartrecruiter-mvp" ]]; then
    echo "1. 运行增强版应用: streamlit run app_enhanced.py"
    echo "2. 查看整合报告: cat INTEGRATION_SUMMARY.md"
    echo "3. 运行快速测试: python3 test_enhanced_app.py"
    echo "4. 查看TODO清单: cat TODO_LOBSTER_3.md"
else
    echo "1. 切换到项目: cd smartrecruiter-mvp"
    echo "2. 或者创建新项目目录"
    echo "3. 避免在工作空间根目录直接开发"
fi

echo ""
echo "📝 记住: 总是在正确的项目目录中工作！"
echo "="===============================================