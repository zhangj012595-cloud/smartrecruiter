#!/usr/bin/env python3
"""
测试SmartRecruiter基本流程
不依赖LinkedIn，使用模拟数据进行测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from channels import ChannelManager
from matcher_simple import SimpleTestMatcher
import yaml


def test_channel_manager():
    """测试渠道管理器"""
    print("🧪 测试渠道管理器...")
    
    # 创建配置
    config = {
        'linkedin': {'username': 'test', 'password': 'test'},
        'search': {
            'locations': ['北京', '上海', '深圳'],
            'experience_levels': ['Entry', 'Mid', 'Senior']
        }
    }
    
    # 创建渠道管理器
    cm = ChannelManager(config)
    
    # 列出可用渠道
    channels = cm.list_channels()
    print(f"  可用渠道: {channels}")
    
    # 测试模拟渠道
    if 'mock_linkedin' in channels:
        print("  ✅ 找到模拟LinkedIn渠道")
        
        # 获取渠道实例
        channel = cm.get_channel('mock_linkedin')
        
        # 测试连接
        if channel.test_connection():
            print("  ✅ 模拟渠道连接测试成功")
        else:
            print("  ❌ 模拟渠道连接测试失败")
            return False
        
        # 测试搜索
        query = {
            'keywords': ['Python', 'Django'],
            'location': '北京',
            'experience_level': 'Senior'
        }
        
        candidates = channel.search(query, limit=5)
        print(f"  ✅ 模拟搜索成功，找到 {len(candidates)} 个候选人")
        
        if candidates:
            print(f"    第一个候选人: {candidates[0]['name']} - {candidates[0]['title']}")
            return True
        else:
            print("  ❌ 模拟搜索未返回候选人")
            return False
    else:
        print("  ❌ 未找到模拟LinkedIn渠道")
        return False


def test_matcher():
    """测试匹配器"""
    print("\n🧪 测试匹配器...")
    
    # 创建匹配器
    matcher = SimpleTestMatcher()
    
    # 测试关键词提取
    jd_text = "招聘Python高级开发工程师，要求5年以上经验，熟悉Django/Flask，工作地点北京"
    jd_keywords = matcher.extract_keywords_from_jd(jd_text)
    
    print(f"  ✅ 关键词提取成功")
    print(f"    技能: {jd_keywords['skills']}")
    print(f"    经验: {jd_keywords['experience_years']}年")
    print(f"    地点: {jd_keywords['locations']}")
    
    # 创建测试候选人
    test_candidate = {
        'name': '张三',
        'title': 'Python开发工程师',
        'company': '测试公司',
        'location': '北京',
        'skills': ['Python', 'Django', 'Flask', 'MySQL'],
        'experience_years': 6,
        'experience_level': 'Senior'
    }
    
    # 测试匹配
    match_result = matcher.match_candidate(jd_keywords, test_candidate)
    print(f"  ✅ 候选人匹配成功")
    print(f"    总分: {match_result['total_score']}%")
    print(f"    匹配技能: {match_result['matched_skills']}")
    
    return True


def test_full_workflow():
    """测试完整工作流程"""
    print("\n🧪 测试完整工作流程...")
    
    # 创建配置
    config = {
        'linkedin': {'username': 'test', 'password': 'test'},
        'search': {
            'locations': ['北京', '上海', '深圳'],
            'experience_levels': ['Entry', 'Mid', 'Senior'],
            'default_limit': 10
        }
    }
    
    # 初始化组件
    cm = ChannelManager(config)
    matcher = SimpleTestMatcher(config)
    
    # 1. 提取职位描述关键词
    jd_text = """
    招聘全栈开发工程师：
    - 3年以上Python/JavaScript开发经验
    - 熟悉React/Vue前端框架
    - 掌握Django/Flask后端框架
    - 了解Docker/Kubernetes
    - 工作地点：上海、杭州
    - 本科及以上学历
    """
    
    jd_keywords = matcher.extract_keywords_from_jd(jd_text)
    print(f"  1. ✅ 职位描述关键词提取完成")
    
    # 2. 搜索候选人
    query = {
        'keywords': jd_keywords['skills'],
        'location': '上海',
        'experience_level': 'Mid'
    }
    
    candidates = cm.search('mock_linkedin', query, limit=8)
    print(f"  2. ✅ 候选人搜索完成，找到 {len(candidates)} 个候选人")
    
    # 3. 匹配候选人
    ranked_candidates = matcher.rank_candidates(jd_keywords, candidates)
    print(f"  3. ✅ 候选人匹配完成，排名前3:")
    
    for i, candidate in enumerate(ranked_candidates[:3]):
        print(f"     {i+1}. {candidate['candidate']['name']} - {candidate['total_score']}%")
    
    # 4. 生成报告
    match_report = matcher.generate_match_report(jd_keywords, ranked_candidates)
    print(f"  4. ✅ 匹配报告生成完成")
    print(f"     总结: {match_report['summary']}")
    
    return True


def test_config_file():
    """测试配置文件"""
    print("\n🧪 测试配置文件...")
    
    config_path = "config/example_config.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("  ✅ 配置文件加载成功")
        print(f"    搜索地点: {config.get('search', {}).get('locations', [])[:3]}...")
        print(f"    经验级别: {config.get('search', {}).get('experience_levels', [])}")
        return True
    else:
        print(f"  ❌ 配置文件不存在: {config_path}")
        return False


def main():
    """主测试函数"""
    print("🚀 SmartRecruiter基本流程测试")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 4
    
    try:
        # 测试1: 渠道管理器
        if test_channel_manager():
            tests_passed += 1
        
        # 测试2: 匹配器
        if test_matcher():
            tests_passed += 1
        
        # 测试3: 完整工作流程
        if test_full_workflow():
            tests_passed += 1
        
        # 测试4: 配置文件
        if test_config_file():
            tests_passed += 1
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试结果
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {tests_passed}/{tests_total} 通过")
    
    if tests_passed == tests_total:
        print("🎉 所有测试通过！基本流程正常。")
        print("\n✅ 下一步:")
        print("   1. 运行 'streamlit run app.py' 启动Web应用")
        print("   2. 在浏览器中访问 http://localhost:8501")
        print("   3. 使用模拟数据进行测试")
        return 0
    else:
        print(f"⚠️  有 {tests_total - tests_passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())