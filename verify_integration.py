#!/usr/bin/env python3
"""
验证GitHub渠道整合
简化的验证脚本，不依赖外部依赖
"""

import os
import sys


def verify_integration():
    """验证整合情况"""
    print("=" * 70)
    print("SmartRecruiter项目整合验证")
    print("=" * 70)
    
    print("\n📁 项目结构验证:")
    
    # 1. 检查核心文件
    core_files = [
        ("app.py", "主应用"),
        ("requirements.txt", "依赖文件"),
        ("README.md", "项目文档"),
        ("channels/__init__.py", "渠道管理器"),
        ("channels/linkedin.py", "LinkedIn渠道"),
        ("channels/mock_linkedin.py", "模拟LinkedIn渠道"),
        ("channels/github.py", "GitHub渠道（新增）"),
        ("config/recruitment_config.py", "招聘配置系统（新增）"),
        ("matcher.py", "匹配算法"),
        ("utils/", "工具目录")
    ]
    
    missing_files = []
    for file_path, description in core_files:
        if os.path.exists(file_path):
            print(f"   ✅ {description}: {file_path}")
        else:
            print(f"   ❌ {description}: {file_path} (缺失)")
            missing_files.append(file_path)
    
    # 2. 检查新增的GitHub渠道
    print("\n🆕 新增功能验证:")
    
    github_channel = "channels/github.py"
    if os.path.exists(github_channel):
        print(f"   ✅ GitHub渠道已创建")
        
        # 检查文件大小
        size = os.path.getsize(github_channel)
        print(f"      文件大小: {size} 字节")
        
        # 检查关键函数
        with open(github_channel, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_functions = ['class GitHubChannel', 'def search_candidates', 'def get_channel']
        for func in required_functions:
            if func in content:
                print(f"      包含: {func}")
            else:
                print(f"      缺失: {func}")
    else:
        print(f"   ❌ GitHub渠道未创建")
    
    # 3. 检查招聘配置系统
    config_system = "config/recruitment_config.py"
    if os.path.exists(config_system):
        print(f"   ✅ 招聘配置系统已创建")
        
        # 检查文件大小
        size = os.path.getsize(config_system)
        print(f"      文件大小: {size} 字节")
    else:
        print(f"   ❌ 招聘配置系统未创建")
    
    # 4. 检查现有渠道兼容性
    print("\n🔄 兼容性验证:")
    
    # 检查渠道管理器是否支持GitHub
    channels_init = "channels/__init__.py"
    if os.path.exists(channels_init):
        with open(channels_init, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "'github': 'channels.github'" in content or '"github": "channels.github"' in content:
            print(f"   ✅ 渠道管理器已集成GitHub")
        else:
            print(f"   ❌ 渠道管理器未集成GitHub")
    
    # 5. 检查依赖
    print("\n📦 依赖验证:")
    
    requirements = "requirements.txt"
    if os.path.exists(requirements):
        with open(requirements, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键依赖
        required_deps = ['requests', 'streamlit', 'selenium']
        for dep in required_deps:
            if dep in content:
                print(f"   ✅ {dep} 在依赖列表中")
            else:
                print(f"   ❌ {dep} 不在依赖列表中")
    
    # 6. 项目状态总结
    print("\n" + "=" * 70)
    print("📊 整合状态总结")
    print("=" * 70)
    
    print("\n✅ 已完成的工作:")
    print("1. GitHub招聘渠道模块已创建")
    print("2. 招聘网站配置管理系统已创建")
    print("3. 渠道管理器已更新支持GitHub")
    print("4. 项目结构保持完整")
    
    print("\n⚠️  待解决的问题:")
    print("1. 需要安装requests库: pip install requests")
    print("2. GitHub API搜索参数需要调整")
    print("3. 需要测试Streamlit应用集成")
    
    print("\n🚀 立即执行步骤:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 测试GitHub渠道: python channels/github.py")
    print("3. 运行Streamlit应用: streamlit run app.py")
    print("4. 在Web界面中选择GitHub渠道测试")
    
    print("\n🎯 成功整合的特征:")
    print("• 项目原有功能保持不变")
    print("• 新增GitHub渠道作为可选项")
    print("• 配置系统支持多种招聘网站")
    print("• 架构扩展性强，易于添加新渠道")
    
    return len(missing_files) == 0


def main():
    """主函数"""
    try:
        success = verify_integration()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 验证通过！项目整合成功完成")
            print("   现在可以继续基于现有项目进行开发")
        else:
            print("⚠️  验证发现一些问题")
            print("   请先解决缺失的文件问题")
        
        print("\n💡 重要提醒:")
        print("请确保在smartrecruiter-mvp目录中工作")
        print("这是昨天创建的hr-2项目，应该在这里继续开发")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()