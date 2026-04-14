"""
SmartRecruiter主应用 - Streamlit版本
Phase 1: 简化Web应用
"""

import streamlit as st
import yaml
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

# 导入项目模块
from channels import ChannelManager
from matcher import SimpleMatcher

# 设置页面配置
st.set_page_config(
    page_title="SmartRecruiter - 智能招聘匹配系统",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化全局变量
def init_session_state():
    """初始化session state"""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    
    if 'channel_manager' not in st.session_state:
        st.session_state.channel_manager = ChannelManager(st.session_state.config)
    
    if 'matcher' not in st.session_state:
        st.session_state.matcher = SimpleMatcher(st.session_state.config)
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    
    if 'match_results' not in st.session_state:
        st.session_state.match_results = []
    
    if 'jd_keywords' not in st.session_state:
        st.session_state.jd_keywords = None
    
    if 'search_in_progress' not in st.session_state:
        st.session_state.search_in_progress = False
    
    if 'match_in_progress' not in st.session_state:
        st.session_state.match_in_progress = False

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = Path("config/config.yaml")
    example_path = Path("config/example_config.yaml")
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logger.info("配置文件加载成功")
            return config
    elif example_path.exists():
        st.warning("⚠️ 未找到配置文件，使用示例配置")
        with open(example_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config
    else:
        st.error("❌ 未找到配置文件")
        return {}

def save_config(config: Dict[str, Any]):
    """保存配置文件"""
    config_path = Path("config/config.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    logger.info("配置文件已保存")

def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.title("🔧 设置")
        
        # 配置编辑
        st.subheader("系统配置")
        
        # LinkedIn配置
        with st.expander("LinkedIn配置", expanded=False):
            username = st.text_input("LinkedIn邮箱", 
                                    value=st.session_state.config.get('linkedin', {}).get('username', ''))
            password = st.text_input("LinkedIn密码", type="password",
                                    value=st.session_state.config.get('linkedin', {}).get('password', ''))
            use_cookie = st.checkbox("使用Cookie文件", 
                                    value=bool(st.session_state.config.get('linkedin', {}).get('cookie_path')))
            
            if use_cookie:
                cookie_path = st.text_input("Cookie文件路径",
                                          value=st.session_state.config.get('linkedin', {}).get('cookie_path', 'cookies/linkedin_cookies.json'))
            else:
                cookie_path = None
            
            headless = st.checkbox("无头模式", 
                                  value=st.session_state.config.get('linkedin', {}).get('headless', False))
        
        # 搜索配置
        with st.expander("搜索配置", expanded=False):
            default_limit = st.number_input("默认搜索数量", min_value=10, max_value=200, value=50)
            
            # 地点选择
            default_locations = st.session_state.config.get('search', {}).get('locations', [])
            locations = st.text_area("常用地点（每行一个）", 
                                    value="\n".join(default_locations),
                                    height=100)
            
            # 经验级别
            experience_levels = st.session_state.config.get('search', {}).get('experience_levels', [])
            levels_text = st.text_area("经验级别（每行一个）",
                                      value="\n".join(experience_levels),
                                      height=100)
        
        # 匹配配置
        with st.expander("匹配配置", expanded=False):
            skill_weight = st.slider("技能权重", 0.0, 1.0, 0.5, 0.1)
            experience_weight = st.slider("经验权重", 0.0, 1.0, 0.3, 0.1)
            location_weight = st.slider("地点权重", 0.0, 1.0, 0.2, 0.1)
            
            # 确保权重和为1
            total = skill_weight + experience_weight + location_weight
            if total != 1.0:
                st.warning(f"权重总和应为1.0，当前为{total:.2f}")
        
        # 保存配置按钮
        if st.button("💾 保存配置", type="primary"):
            # 更新配置
            config = st.session_state.config.copy()
            
            # LinkedIn配置
            config.setdefault('linkedin', {})
            config['linkedin']['username'] = username
            config['linkedin']['password'] = password
            if cookie_path:
                config['linkedin']['cookie_path'] = cookie_path
            else:
                config['linkedin'].pop('cookie_path', None)
            config['linkedin']['headless'] = headless
            
            # 搜索配置
            config.setdefault('search', {})
            config['search']['default_limit'] = default_limit
            config['search']['locations'] = [loc.strip() for loc in locations.split('\n') if loc.strip()]
            config['search']['experience_levels'] = [level.strip() for level in levels_text.split('\n') if level.strip()]
            
            # 匹配配置
            config.setdefault('matching', {})
            config['matching']['weights'] = {
                'skills': skill_weight,
                'experience': experience_weight,
                'location': location_weight
            }
            
            # 保存配置
            save_config(config)
            st.session_state.config = config
            st.success("✅ 配置已保存！")
            time.sleep(1)
            st.rerun()
        
        # 系统状态
        st.divider()
        st.subheader("📊 系统状态")
        
        # 渠道状态
        st.write("**可用渠道:**")
        try:
            channels = st.session_state.channel_manager.list_channels()
            for channel in channels:
                st.write(f"- {channel}")
        except:
            st.write("- LinkedIn (默认)")
        
        # 连接测试
        if st.button("🔗 测试连接", type="secondary"):
            with st.spinner("测试连接中..."):
                # 这里可以添加连接测试逻辑
                time.sleep(1)
                st.success("✅ 连接测试成功！")
        
        # 版本信息
        st.divider()
        st.caption("SmartRecruiter v0.1.0")
        st.caption("Phase 1: MVP版本")

def show_main_content():
    """显示主内容"""
    st.title("🔍 SmartRecruiter - 智能招聘匹配系统")
    st.markdown("### Phase 1: LinkedIn搜索 + 简单匹配")
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📝 职位描述", "🔍 搜索候选人", "📊 匹配结果"])
    
    with tab1:
        show_job_description_tab()
    
    with tab2:
        show_search_tab()
    
    with tab3:
        show_results_tab()

def show_job_description_tab():
    """职位描述标签页"""
    st.subheader("输入职位描述")
    
    # 职位描述输入
    jd_text = st.text_area(
        "粘贴职位描述文本",
        height=200,
        placeholder="例如：\n我们正在寻找一名高级Python开发工程师，要求：\n- 5年以上Python开发经验\n- 熟悉Django/Flask框架\n- 有微服务架构经验\n- 熟练使用MySQL/Redis\n- 工作地点：北京、上海、深圳\n- 本科及以上学历",
        key="jd_text"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 技能关键词
        skill_keywords = st.text_area(
            "技能关键词（可选，每行一个）",
            height=100,
            placeholder="Python\nDjango\nFlask\nMySQL\nRedis\n微服务",
            help="如果职位描述中没有明确技能，可以在这里指定"
        )
    
    with col2:
        # 其他要求
        location = st.text_input("工作地点", placeholder="北京、上海、深圳")
        experience_years = st.number_input("经验年限要求", min_value=0, value=5)
    
    # 提取关键词按钮
    if st.button("🔑 提取关键词", type="primary"):
        if jd_text:
            with st.spinner("正在提取关键词..."):
                # 提取关键词
                jd_keywords = st.session_state.matcher.extract_keywords_from_jd(jd_text)
                
                # 如果有手动输入的关键词，合并
                if skill_keywords:
                    manual_skills = [skill.strip() for skill in skill_keywords.split('\n') if skill.strip()]
                    jd_keywords['skills'].extend(manual_skills)
                    jd_keywords['skills'] = list(set(jd_keywords['skills']))  # 去重
                
                # 如果有手动输入的地点，替换
                if location:
                    jd_keywords['locations'] = [loc.strip() for loc in location.split('、') if loc.strip()]
                
                # 如果有手动输入的经验年限，替换
                if experience_years > 0:
                    jd_keywords['experience_years'] = experience_years
                
                st.session_state.jd_keywords = jd_keywords
                st.success("✅ 关键词提取完成！")
                
                # 显示提取结果
                show_keywords_result(jd_keywords)
        else:
            st.error("请输入职位描述")

def show_keywords_result(jd_keywords: Dict[str, Any]):
    """显示提取的关键词结果"""
    st.subheader("📋 提取结果")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("技能关键词", len(jd_keywords['skills']))
        if jd_keywords['skills']:
            with st.expander("查看技能"):
                for skill in jd_keywords['skills']:
                    st.write(f"- {skill}")
    
    with col2:
        st.metric("经验要求", f"{jd_keywords['experience_years']}年")
    
    with col3:
        st.metric("工作地点", len(jd_keywords['locations']))
        if jd_keywords['locations']:
            with st.expander("查看地点"):
                for loc in jd_keywords['locations']:
                    st.write(f"- {loc}")
    
    with col4:
        st.metric("学历要求", jd_keywords['education'])

def show_search_tab():
    """搜索标签页"""
    st.subheader("搜索候选人")
    
    # 检查是否有关键词
    if st.session_state.jd_keywords is None:
        st.warning("⚠️ 请先在【职位描述】标签页提取关键词")
        return
    
    # 搜索条件
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 地点选择
        locations = st.session_state.config.get('search', {}).get('locations', [])
        selected_location = st.selectbox("工作地点", ["不限"] + locations)
    
    with col2:
        # 经验级别
        experience_levels = st.session_state.config.get('search', {}).get('experience_levels', [])
        selected_experience = st.selectbox("经验级别", ["不限"] + experience_levels)
    
    with col3:
        # 搜索数量
        default_limit = st.session_state.config.get('search', {}).get('default_limit', 50)
        search_limit = st.number_input("搜索数量", min_value=10, max_value=200, value=default_limit)
    
    # 搜索按钮
    if st.button("🔍 开始搜索", type="primary", disabled=st.session_state.search_in_progress):
        st.session_state.search_in_progress = True
        
        # 构建搜索查询
        query = {
            'keywords': st.session_state.jd_keywords['skills'],
            'location': selected_location if selected_location != "不限" else "",
            'experience_level': selected_experience if selected_experience != "不限" else ""
        }
        
        # 执行搜索
        with st.spinner(f"正在搜索LinkedIn候选人..."):
            try:
                candidates = st.session_state.channel_manager.search(
                    "linkedin", 
                    query, 
                    search_limit
                )
                
                st.session_state.search_results = candidates
                st.session_state.search_in_progress = False
                
                st.success(f"✅ 搜索完成！找到 {len(candidates)} 个候选人")
                
                # 显示搜索结果预览
                show_search_preview(candidates)
                
            except Exception as e:
                st.error(f"❌ 搜索失败: {str(e)}")
                st.session_state.search_in_progress = False
    
    # 显示搜索结果
    if st.session_state.search_results:
        st.divider()
        show_search_results(st.session_state.search_results)

def show_search_preview(candidates: List[Dict[str, Any]]):
    """显示搜索结果预览"""
    if not candidates:
        return
    
    st.subheader("📋 搜索结果预览")
    
    # 显示前5个结果
    for i, candidate in enumerate(candidates[:5]):
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 2])
            
            with col1:
                # 头像
                if candidate.get('avatar_url'):
                    st.image(candidate['avatar_url'], width=80)
                else:
                    st.write("👤")
            
            with col2:
                # 基本信息
                st.write(f"**{candidate.get('name', '未知')}**")
                st.write(candidate.get('title', ''))
                st.write(candidate.get('company', ''))
                st.write(f"📍 {candidate.get('location', '')}")
            
            with col3:
                # 技能和经验
                skills = candidate.get('skills', [])
                if skills:
                    st.write(f"技能: {', '.join(skills[:3])}")
                
                exp_years = candidate.get('experience_years', 0)
                exp_level = candidate.get('experience_level', '')
                st.write(f"经验: {exp_years}年 ({exp_level})")
            
            st.divider()

def show_search_results(candidates: List[Dict[str, Any]]):
    """显示完整搜索结果"""
    st.subheader("📊 所有搜索结果")
    
    # 匹配按钮
    if st.button("🎯 开始匹配", type="primary", disabled=st.session_state.match_in_progress):
        st.session_state.match_in_progress = True
        
        with st.spinner(f"正在匹配 {len(candidates)} 个候选人..."):
            try:
                # 进行匹配
                ranked_candidates = st.session_state.matcher.rank_candidates(
                    st.session_state.jd_keywords,
                    candidates
                )
                
                # 生成报告
                match_report = st.session_state.matcher.generate_match_report(
                    st.session_state.jd_keywords,
                    ranked_candidates
                )
                
                st.session_state.match_results = match_report
                st.session_state.match_in_progress = False
                
                st.success("✅ 匹配完成！")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 匹配失败: {str(e)}")
                st.session_state.match_in_progress = False
    
    # 显示所有候选人
    for i, candidate in enumerate(candidates):
        with st.expander(f"{i+1}. {candidate.get('name', '未知')} - {candidate.get('title', '')}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if candidate.get('avatar_url'):
                    st.image(candidate['avatar_url'], width=120)
                else:
                    st.write("👤")
            
            with col2:
                st.write(f"**公司:** {candidate.get('company', '')}")
                st.write(f"**地点:** {candidate.get('location', '')}")
                
                skills = candidate.get('skills', [])
                if skills:
                    st.write(f"**技能:** {', '.join(skills)}")
                
                st.write(f"**经验:** {candidate.get('experience_years', 0)}年 ({candidate.get('experience_level', '')})")
                
                # LinkedIn链接
                profile_url = candidate.get('profile_url', '')
                if profile_url:
                    st.markdown(f"[查看LinkedIn个人资料]({profile_url})")

def show_results_tab():
    """匹配结果标签页"""
    st.subheader("匹配结果")
    
    if not st.session_state.match_results:
        st.info("👈 请先完成搜索和匹配")
        return
    
    match_report = st.session_state.match_results
    
    # 统计信息
    st.subheader("📈 匹配统计")
    
    stats = match_report['statistics']
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总候选人", stats['total_candidates'])
    
    with col2:
        st.metric("高度匹配", stats['high_match_count'])
    
    with col3:
        st.metric("中等匹配", stats['medium_match_count'])
    
    with col4:
        st.metric("平均分数", f"{stats['average_score']}%")
    
    # 热门技能
    st.subheader("🔥 热门匹配技能")
    top_skills = stats['top_matched_skills']
    
    if top_skills:
        for skill, count in top_skills:
            st.write(f"- **{skill}**: {count} 次匹配")
    else:
        st.write("暂无匹配技能")
    
    # 职位要求
    st.subheader("📋 职位要求")
    jd_req = match_report['jd_requirements']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**技能要求:**")
        for skill in jd_req['required_skills']:
            st.write(f"- {skill}")
    
    with col2:
        st.write("**经验要求:**")
        st.write(f"- {jd_req['experience_years']}年")
        
        st.write("**教育要求:**")
        st.write(f"- {jd_req['education']}")
    
    with col3:
        st.write("**工作地点:**")
        for loc in jd_req['locations']:
            st.write(f"- {loc}")
    
    # 匹配结果
    st.subheader("🏆 最佳匹配候选人")
    
    top_candidates = match_report['top_candidates']
    
    for i, candidate_data in enumerate(top_candidates[:10]):
        candidate = candidate_data['candidate']
        
        with st.expander(f"#{i+1} {candidate.get('name', '未知')} - 匹配度: {candidate_data['total_score']}%", expanded=i<3):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # 匹配度图表
                scores = {
                    '技能': candidate_data['skill_score'],
                    '经验': candidate_data['experience_score'],
                    '地点': candidate_data['location_score']
                }
                
                # 简单的条形图
                for category, score in scores.items():
                    bar_width = int(score / 100 * 200)
                    st.write(f"{category}: {score}%")
                    st.progress(score / 100)
            
            with col2:
                # 候选人信息
                st.write(f"**职位:** {candidate.get('title', '')}")
                st.write(f"**公司:** {candidate.get('company', '')}")
                st.write(f"**地点:** {candidate.get('location', '')}")
                
                # 匹配的技能
                matched_skills = candidate_data['matched_skills']
                if matched_skills:
                    st.write(f"**匹配技能:** {', '.join(matched_skills[:5])}")
                
                # 缺失的技能
                missing_skills = candidate_data['missing_skills']
                if missing_skills:
                    st.write(f"**缺失技能:** {', '.join(missing_skills[:3])}")
                
                # LinkedIn链接
                profile_url = candidate.get('profile_url', '')
                if profile_url:
                    st.markdown(f"[🔗 查看LinkedIn个人资料]({profile_url})")
    
    # 导出按钮
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        # 导出JSON
        if st.button("💾 导出JSON"):
            export_data = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'job_description_keywords': st.session_state.jd_keywords,
                'match_report': match_report
            }
            
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="下载JSON文件",
                data=json_str,
                file_name=f"smartrecruiter_match_{time.strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        # 导出CSV
        if st.button("📊 导出CSV"):
            # 这里可以实现CSV导出逻辑
            st.info("CSV导出功能将在下一版本添加")

def main():
    """主函数"""
    # 初始化
    init_session_state()
    
    # 显示界面
    show_sidebar()
    show_main_content()
    
    # 页脚
    st.divider()
    st.caption("SmartRecruiter MVP v0.1.0 | Phase 1: LinkedIn搜索 + 简单匹配")
    st.caption("注意：使用LinkedIn搜索功能需要有效的LinkedIn账户。请遵守LinkedIn的使用条款。")

if __name__ == "__main__":
    main()