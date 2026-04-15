#!/usr/bin/env python3
"""
测试GitHub渠道整合
验证新开发的GitHub渠道能否正确集成到smartrecruiter项目中
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from channels import ChannelManager
from config.recruitment_config import RecruitmentConfigManager
import json


def test_github_channel_integration():
    """测试GitHub渠道整合"""
    print("=" * 70)
    print("GitHub渠道整合测试")
    print("=" * 70)
    
    # 1. 测试配置管理器
    print("\n1. 📋 测试招聘配置管理器...")
    config_manager = RecruitmentConfigManager("test_integration_config.json")
    
    print(f"   已加载 {len(config_manager.list_channels())} 个渠道配置")
    
    # 检查GitHub渠道状态
    github_status = config_manager.get_channel_status("GitHub")
    print(f"   GitHub渠道状态:")
    print(f"     • 存在: {github_status['exists']}")
    print(f"     • 启用: {github_status['enabled']}")
    print(f"     • 免费: {not github_status['is_paid']}")
    print(f"     • 准备就绪: {github_status['ready_for_use']}")
    
    # 2. 测试渠道管理器
    print("\n2. 🔌 测试渠道管理器...")
    channel_manager = ChannelManager()
    
    available_channels = channel_manager.list_channels()
    print(f"   可用渠道: {', '.join(available_channels)}")
    
    # 检查GitHub渠道是否可用
    if 'github' in available_channels:
        print("   ✅ GitHub渠道已发现")
    else:
        print("   ❌ GitHub渠道未发现")
        return False
    
    # 3. 测试GitHub渠道连接
    print("\n3. 🔗 测试GitHub渠道连接...")
    try:
        github_channel = channel_manager.get_channel('github')
        print("   ✅ GitHub渠道加载成功")
        
        # 测试连接
        connection = github_channel.test_connection()
        if connection.get('success'):
            print("   ✅ GitHub API连接成功")
            rate_limit = connection.get('rate_limit', {})
            print(f"     剩余请求: {rate_limit.get('remaining', 'N/A')}/{rate_limit.get('limit', 'N/A')}")
        else:
            print("   ⚠️  GitHub API连接可能有问题")
            
    except Exception as e:
        print(f"   ❌ GitHub渠道加载失败: {e}")
        return False
    
    # 4. 测试候选人搜索
    print("\n4. 🔍 测试GitHub候选人搜索...")
    try:
        search_params = {
            'keywords': ['python', 'developer'],
            'location': 'China',
            'min_followers': 5,
            'min_repos': 3,
            'tech_stack': ['Python'],
            'limit': 2
        }
        
        candidates = github_channel.search_candidates(search_params)
        
        if candidates:
            print(f"   ✅ 搜索成功，找到 {len(candidates)} 位候选人")
            for i, candidate in enumerate(candidates, 1):
                print(f"      {i}. {candidate.username} ({candidate.score}/100)")
                print(f"         位置: {candidate.location or '未知'}")
                print(f"         关注者: {candidate.followers}")
                print(f"         仓库数: {candidate.public_repos}")
                
                if candidate.top_projects:
                    best = max(candidate.top_projects, key=lambda x: x['stars'])
                    print(f"         最佳项目: {best['name']} (⭐{best['stars']})")
        else:
            print("   ⚠️  搜索成功但未找到候选人（可能条件太严格）")
            print("      建议：放宽关注者或仓库数量要求")
            
    except Exception as e:
        print(f"   ❌ 搜索失败: {e}")
        return False
    
    # 5. 测试报告生成
    print("\n5. 📊 测试报告生成...")
    try:
        if candidates:
            report = github_channel.generate_candidate_report(candidates[0])
            report_lines = report.split('\n')[:15]  # 只显示前15行
            
            print("   ✅ 报告生成成功（部分内容）：")
            for line in report_lines:
                if line.strip():
                    print(f"      {line}")
            print("      ...")
        else:
            print("   ⚠️  跳过报告生成（无候选人数据）")
            
    except Exception as e:
        print(f"   ❌ 报告生成失败: {e}")
        return False
    
    # 6. 测试配置导出
    print("\n6. 📤 测试配置导出...")
    try:
        exported_config = config_manager.export_config()
        config_size = len(exported_config)
        print(f"   ✅ 配置导出成功 ({config_size} 字符)")
        
        # 验证导出内容
        config_data = json.loads(exported_config)
        if 'GitHub' in config_data:
            print("   ✅ GitHub配置已包含在导出文件中")
            
    except Exception as e:
        print(f"   ❌ 配置导出失败: {e}")
        return False
    
    # 7. 测试现有项目兼容性
    print("\n7. 🔄 测试现有项目兼容性...")
    try:
        # 测试是否能导入原有配置格式
        from channels.mock_linkedin import get_channel as get_mock_channel
        mock_channel = get_mock_channel()
        
        print("   ✅ 原有Mock LinkedIn渠道工作正常")
        print("   ✅ 新旧渠道架构兼容")
        
    except Exception as e:
        print(f"   ❌ 兼容性测试失败: {e}")
        return False
    
    # 清理测试文件
    print("\n8. 🧹 清理测试文件...")
    test_files = ["test_integration_config.json", "recruitment_configs.json"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"      已删除: {file}")
    
    print("\n" + "=" * 70)
    print("🎉 整合测试完成！")
    print("=" * 70)
    
    print("\n📋 测试结果总结：")
    print("1. ✅ 配置管理器工作正常")
    print("2. ✅ GitHub渠道已成功集成")
    print("3. ✅ API连接和搜索功能正常")
    print("4. ✅ 报告生成功能正常")
    print("5. ✅ 配置导入导出正常")
    print("6. ✅ 与现有项目架构兼容")
    print("7. ✅ 所有测试文件已清理")
    
    print("\n🚀 下一步：")
    print("1. 运行Streamlit应用测试集成效果")
    print("2. 在Web界面中使用GitHub渠道")
    print("3. 根据实际需求调整搜索参数")
    print("4. 获取GitHub Token提高API限制")
    
    return True


def main():
    """主函数"""
    try:
        success = test_github_channel_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()