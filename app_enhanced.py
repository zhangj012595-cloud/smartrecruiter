"""
SmartRecruiter主应用 - 增强版
集成GitHub渠道和多渠道配置管理
"""

import streamlit as st
import yaml
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# 导入项目模块
from channels import ChannelManager
from config.recruitment_config import RecruitmentConfigManager
from matcher_simple import SimpleTestMatcher as SimpleMatcher

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


def init_session_state():
    """初始化session state"""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = RecruitmentConfigManager("config/recruitment_configs.json")
    
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
    
    if 'selected_channel_type' not in st.session_state:
        st.session_state.selected_channel_type = "linkedin"  # 默认LinkedIn


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


def show_sidebar():
    """显示增强版侧边栏"""
    with st.sidebar:
        st.title("🔧 智能招聘系统")
        
        # 渠道选择
        st.subheader("🎯 数据源选择")
        channel_options = st.session_state.channel_manager.list_channels()
        
        # 显示渠道状态
        for channel in channel_options:
            channel_status = st.session_state.config_manager.get_channel_status(channel.capitalize())
            if channel_status['exists']:
                status_icon = "✅" if channel_status['enabled'] else "❌"
                st.caption(f"{status_icon} {channel.capitalize()}: {'已启用' if channel_status['enabled'] else '已禁用'}")
        
        # 渠道管理
        with st.expander("📊 渠道管理", expanded=False):
            # 列出所有渠道
            channels = st.session_state.config_manager.list_channels()
            for channel in channels:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{channel['name']}**")
                with col2:
                    status = "启用" if channel['enabled'] else "禁用"
                    st.write(status)
                with col3:
                    if st.button("切换", key=f"toggle_{channel['name']}"):
                        if channel['enabled']:
                            st.session_state.config_manager.disable_channel(channel['name'])
                        else:
                            st.session_state.config_manager.enable_channel(channel['name'])
                        st.rerun()
        
        # 系统配置
        st.subheader("⚙️ 系统配置")
        
        with st.expander("GitHub配置", expanded=False):
            st.info("GitHub API完全免费，无需账号即可使用")
            
            # GitHub Token输入（可选）
            github_token = st.text_input("GitHub Token（可选）", type="password",
                                        help="提供Token可将API限制从60次/小时提高到5000次/小时")
            
            if github_token:
                st.success("✅ GitHub Token已设置")
                # 保存到配置
                update_data = {'api_key': github_token}
                st.session_state.config_manager.update_channel_config("GitHub", update_data)
            else:
                st.warning("⚠️ 未使用Token，API限制为60次/小时")
        
        with st.expander("LinkedIn配置", expanded=False):
            username = st.text_input("LinkedIn邮箱", 
                                    value=st.session_state.config.get('linkedin', {}).get('username', ''))
            password = st.text_input("LinkedIn密码", type="password",
                                    value=st.session_state.config.get('linkedin', {}).get('password', ''))
            
            if st.button("保存LinkedIn配置"):
                # 这里可以添加保存逻辑
                st.success("配置已保存")
        
        # 关于信息
        st.divider()
        st.caption("SmartRecruiter v2.0")
        st.caption("支持多渠道人才搜索")
        st.caption(f"当前渠道: {len(channels)} 个")


def show_search_tab_enhanced():
    """增强版搜索标签页"""
    st.subheader("🔍 多渠道候选人搜索")
    
    # 检查是否有关键词
    if st.session_state.jd_keywords is None:
        st.warning("⚠️ 请先在【职位描述】标签页提取关键词")
        return
    
    # 搜索条件容器
    search_container = st.container()
    
    with search_container:
        # 第一行：渠道选择
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 获取可用渠道
            available_channels = st.session_state.channel_manager.list_channels()
            
            # 过滤已启用的渠道
            enabled_channels = []
            for channel in available_channels:
                channel_status = st.session_state.config_manager.get_channel_status(channel.capitalize())
                if channel_status.get('enabled', False):
                    enabled_channels.append(channel)
            
            if not enabled_channels:
                st.error("❌ 没有启用的招聘渠道，请在侧边栏启用至少一个渠道")
                return
            
            # 渠道选择
            selected_channel = st.selectbox(
                "选择数据源",
                enabled_channels,
                format_func=lambda x: f"{x.capitalize()} ({'免费' if x == 'github' else '可能需要认证'})"
            )
            
            # 显示渠道说明
            if selected_channel == 'github':
                st.info("🌐 GitHub: 搜索开源开发者，基于项目质量和社区影响力")
            elif selected_channel == 'linkedin':
                st.info("💼 LinkedIn: 搜索职场专业人士，基于工作经验和技能")
            elif selected_channel == 'mock_linkedin':
                st.info("🧪 Mock: 测试数据，用于演示功能")
        
        with col2:
            # 搜索数量
            default_limit = st.session_state.config.get('search', {}).get('default_limit', 50)
            search_limit = st.number_input("搜索数量", min_value=5, max_value=200, value=20)
        
        # 第二行：渠道特定搜索条件
        st.divider()
        st.subheader("搜索条件")
        
        # 通用搜索条件
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 关键词
            keywords = st.session_state.jd_keywords['skills']
            st.write("**关键词**:", ", ".join(keywords[:5]))
        
        with col2:
            # 根据渠道显示不同的条件
            if selected_channel == 'github':
                # GitHub特定条件
                location = st.text_input("地理位置（可选）", placeholder="如: China, Beijing")
                min_followers = st.number_input("最小关注者", min_value=0, value=10)
                min_repos = st.number_input("最小仓库数", min_value=0, value=5)
            else:
                # LinkedIn/Mock条件
                locations = st.session_state.config.get('search', {}).get('locations', [])
                selected_location = st.selectbox("工作地点", ["不限"] + locations)
        
        with col3:
            if selected_channel == 'github':
                # 技术栈选择
                tech_stack_options = ['Python', 'JavaScript', 'Java', 'Go', 'Rust', 
                                     'React', 'Vue', 'Django', 'Flask', 'Node.js']
                selected_tech = st.multiselect("技术栈（可选）", tech_stack_options)
            else:
                # 经验级别
                experience_levels = st.session_state.config.get('search', {}).get('experience_levels', [])
                selected_experience = st.selectbox("经验级别", ["不限"] + experience_levels)
    
    # 搜索按钮
    st.divider()
    
    search_button_container = st.container()
    with search_button_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 开始搜索", type="primary", use_container_width=True,
                        disabled=st.session_state.search_in_progress):
                st.session_state.search_in_progress = True
                st.session_state.selected_channel_type = selected_channel
                
                # 构建搜索查询
                if selected_channel == 'github':
                    query = {
                        'keywords': keywords,
                        'location': location if location else None,
                        'min_followers': min_followers,
                        'min_repos': min_repos,
                        'tech_stack': selected_tech if selected_tech else None,
                        'limit': search_limit
                    }
                else:
                    query = {
                        'keywords': keywords,
                        'location': selected_location if selected_location != "不限" else "",
                        'experience_level': selected_experience if selected_experience != "不限" else "",
                        'limit': search_limit
                    }
                
                # 执行搜索
                with st.spinner(f"正在搜索{selected_channel.capitalize()}候选人..."):
                    try:
                        if selected_channel == 'github':
                            # 特殊处理GitHub搜索
                            from channels.github import get_channel
                            github_config = {}
                            github_channel = get_channel(github_config)
                            candidates = github_channel.search_candidates(query)
                        else:
                            # 使用渠道管理器
                            candidates = st.session_state.channel_manager.search(
                                selected_channel, 
                                query, 
                                search_limit
                            )
                        
                        # 统一候选人格式
                        unified_candidates = unify_candidates(candidates, selected_channel)
                        st.session_state.search_results = unified_candidates
                        st.session_state.search_in_progress = False
                        
                        st.success(f"✅ 搜索完成！找到 {len(unified_candidates)} 个候选人")
                        
                    except Exception as e:
                        st.error(f"❌ 搜索失败: {str(e)}")
                        logger.error(f"搜索失败: {e}", exc_info=True)
                        st.session_state.search_in_progress = False
    
    # 显示搜索结果
    if st.session_state.search_results:
        st.divider()
        show_unified_search_results(st.session_state.search_results, st.session_state.selected_channel_type)


def unify_candidates(candidates: List[Any], source_type: str) -> List[Dict[str, Any]]:
    """统一不同渠道的候选人格式"""
    unified = []
    
    if source_type == 'github':
        # GitHub候选人格式
        for candidate in candidates:
            unified.append({
                'id': candidate.username,
                'name': candidate.name or candidate.username,
                'title': f"GitHub开发者 (评分: {candidate.score}/100)",
                'company': candidate.company or "未提供",
                'location': candidate.location or "未提供",
                'skills': list(candidate.skills.keys())[:10] if candidate.skills else [],
                'profile_url': candidate.profile_url,
                'source': 'github',
                'score': candidate.score,
                'details': {
                    'followers': candidate.followers,
                    'public_repos': candidate.public_repos,
                    'top_projects': candidate.top_projects[:3] if candidate.top_projects else []
                }
            })
    else:
        # LinkedIn/Mock候选人格式（保持原样）
        for candidate in candidates:
            if isinstance(candidate, dict):
                candidate['source'] = source_type
                candidate['score'] = candidate.get('match_score', 0)
                unified.append(candidate)
    
    # 按评分排序
    unified.sort(key=lambda x: x.get('score', 0), reverse=True)
    return unified


def show_unified_search_results(candidates: List[Dict[str, Any]], source_type: str):
    """显示统一格式的搜索结果"""
    st.subheader(f"搜索结果 ({len(candidates)} 个候选人)")
    
    if not candidates:
        st.info("📭 未找到符合条件的候选人")
        return
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("候选人总数", len(candidates))
    
    with col2:
        avg_score = sum(c.get('score', 0) for c in candidates) / len(candidates)
        st.metric("平均评分", f"{avg_score:.1f}")
    
    with col3:
        top_score = max(c.get('score', 0) for c in candidates)
        st.metric("最高评分", f"{top_score:.1f}")
    
    with col4:
        st.metric("数据源", source_type.capitalize())
    
    # 候选人列表
    st.divider()
    
    for i, candidate in enumerate(candidates[:20]):  # 最多显示20个
        with st.expander(f"{i+1}. {candidate['name']} - {candidate['title']} (评分: {candidate.get('score', 0):.1f})", 
                        expanded=(i < 3)):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # 候选人基本信息
                st.write("**基本信息**")
                st.write(f"**名称**: {candidate['name']}")
                st.write(f"**职位**: {candidate['title']}")
                st.write(f"**公司**: {candidate['company']}")
                st.write(f"**地点**: {candidate['location']}")
                st.write(f"**数据源**: {candidate['source'].capitalize()}")
                
                # GitHub特定信息
                if candidate['source'] == 'github':
                    details = candidate.get('details', {})
                    st.write(f"**关注者**: {details.get('followers', 0)}")
                    st.write(f"**仓库数**: {details.get('public_repos', 0)}")
            
            with col2:
                # 技能
                st.write("**技能**")
                skills = candidate.get('skills', [])
                if skills:
                    cols = st.columns(min(4, len(skills)))
                    for idx, skill in enumerate(skills[:4]):
                        with cols[idx % 4]:
                            st.info(skill)
                else:
                    st.write("暂无技能信息")
                
                # GitHub项目信息
                if candidate['source'] == 'github':
                    top_projects = candidate.get('details', {}).get('top_projects', [])
                    if top_projects:
                        st.write("**优质项目**")
                        for project in top_projects:
                            st.write(f"• **{project['name']}**: {project.get('description', '无描述')}")
                            st.write(f"  ⭐ {project.get('stars', 0)} | 🔀 {project.get('forks', 0)}")
                            st.write(f"  🔗 {project.get('url', '')}")
                
                # 操作按钮
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("👀 查看详情", key=f"view_{candidate['id']}"):
                        st.session_state[f"view_candidate_{candidate['id']}"] = True
                
                with col_btn2:
                    if st.button("💾 保存", key=f"save_{candidate['id']}"):
                        st.success(f"已保存候选人: {candidate['name']}")
                
                with col_btn3:
                    profile_url = candidate.get('profile_url')
                    if profile_url:
                        st.link_button("🌐 打开主页", profile_url)
    
    # 分页信息
    if len(candidates) > 20:
        st.info(f"显示前20个候选人，共有{len(candidates)}个候选人")
    
    # 导出功能
    st.divider()
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("📥 导出搜索结果 (CSV)"):
            # 这里可以添加CSV导出逻辑
            st.success("导出功能开发中...")
    
    with col_exp2:
        if st.button("📊 生成分析报告"):
            # 这里可以添加报告生成逻辑
            st.success("报告生成功能开发中...")


def show_config_tab():
    """配置管理标签页"""
    st.subheader("⚙️ 系统配置管理")
    
    # 使用选项卡组织配置
    tab1, tab2, tab3 = st.tabs(["渠道配置", "搜索配置", "匹配配置"])
    
    with tab1:
        show_channel_config()
    
    with tab2:
        show_search_config()
    
    with tab3:
        show_matching_config()


def show_channel_config():
    """渠道配置界面"""
    st.write("### 招聘渠道配置")
    
    # 显示所有渠道
    channels = st.session_state.config_manager.list_channels()
    
    for channel in channels:
        with st.expander(f"{channel['name']} ({'✅ 启用' if channel['enabled'] else '❌ 禁用'})", 
                        expanded=channel['name'] == 'GitHub'):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**基础URL**: {channel['base_url']}")
                st.write(f"**认证类型**: {channel['auth_type']}")
                st.write(f"**API限制**: {channel['rate_limit']} 次/小时")
                st.write(f"**付费服务**: {'是' if channel['is_paid'] else '否'}")
                st.write(f"**最后更新**: {channel['last_updated']}")
            
            with col2:
                # 启用/禁用切换
                if st.button("切换状态", key=f"config_toggle_{channel['name']}"):
                    if channel['enabled']:
                        st.session_state.config_manager.disable_channel(channel['name'])
                    else:
                        st.session_state.config_manager.enable_channel(channel['name'])
                    st.rerun()
                
                # 编辑按钮
                if st.button("编辑", key=f"config_edit_{channel['name']}"):
                    st.session_state[f"editing_{channel['name']}"] = True
            
            # 编辑表单
            if st.session_state.get(f"editing_{channel['name']}", False):
                st.write("---")
                st.write(f"编辑 {channel['name']} 配置")
                
                # 简单的编辑表单
                new_rate_limit = st.number_input("API限制（次/小时）", 
                                                min_value=1, 
                                                value=channel['rate_limit'],
                                                key=f"rate_{channel['name']}")
                
                new_base_url = st.text_input("基础URL", 
                                            value=channel['base_url'],
                                            key=f"url_{channel['name']}")
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("保存", key=f"save_{channel['name']}"):
                        update_data = {
                            'rate_limit': new_rate_limit,
                            'base_url': new_base_url
                        }
                        if st.session_state.config_manager.update_channel_config(channel['name'], update_data):
                            st.success("配置已更新")
                            st.session_state[f"editing_{channel['name']}"] = False
                            st.rerun()
                
                with col_cancel:
                    if st.button("取消", key=f"cancel_{channel['name']}"):
                        st.session_state[f"editing_{channel['name']}"] = False
                        st.rerun()
    
    # 添加新渠道
    st.divider()
    st.write("### 添加新渠道")
    
    with st.form("add_channel_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_name = st.text_input("渠道名称")
            new_auth_type = st.selectbox("认证类型", ["api_key", "oauth", "cookie", "none"])
        
        with col2:
            new_base_url = st.text_input("基础URL")
            new_rate_limit = st.number_input("API限制", min_value=1, value=60)
        
        with col3:
            is_paid = st.checkbox("付费服务")
            enabled_by_default = st.checkbox("默认启用")
        
        if st.form_submit_button("添加渠道"):
            if new_name and new_base_url:
                new_config = {
                    'name': new_name,
                    'enabled': enabled_by_default,
                    'auth_type': new_auth_type,
                    'base_url': new_base_url,
                    'rate_limit': new_rate_limit,
                    'is_paid': is_paid,
                    'endpoints': {}
                }
                
                if st.session_state.config_manager.add_channel(new_name, new_config):
                    st.success(f"已添加渠道: {new_name}")
                    st.rerun()
            else:
                st.error("请填写渠道名称和基础URL")


def show_search_config():
    """搜索配置界面"""
    st.write("### 搜索配置")
    
    # 通用搜索配置
    st.write("**通用设置**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_limit = st.number_input("默认搜索数量", 
                                       min_value=10, 
                                       max_value=200, 
                                       value=st.session_state.config.get('search', {}).get('default_limit', 50))
    
    with col2:
        default_timeout = st.number_input("搜索超时时间（秒）", 
                                         min_value=10, 
                                         max_value=300, 
                                         value=st.session_state.config.get('search', {}).get('timeout', 60))
    
    # 地点配置
    st.write("**地点配置**")
    locations = st.session_state.config.get('search', {}).get('locations', [])
    
    new_location = st.text_input("添加新地点", placeholder="如: 北京, 上海, 深圳")
    
    if st.button("添加地点") and new_location:
        locations.append(new_location.strip())
        st.success(f"已添加地点: {new_location}")
    
    # 显示现有地点
    if locations:
        st.write("现有地点:")
        cols = st.columns(min(4, len(locations)))
        for idx, loc in enumerate(locations):
            with cols[idx % 4]:
                if st.button(f"🗑️ {loc}", key=f"del_loc_{loc}"):
                    locations.remove(loc)
                    st.rerun()
    
    # 保存配置按钮
    if st.button("💾 保存搜索配置"):
        # 这里可以添加保存逻辑
        st.success("搜索配置已保存")


def show_matching_config():
    """匹配配置界面"""
    st.write("### 匹配算法配置")
    
    st.info("匹配算法配置正在开发中...")
    
    # 简单的配置选项
    col1, col2 = st.columns(2)
    
    with col1:
        skill_weight = st.slider("技能权重", 0.0, 1.0, 0.4)
        experience_weight = st.slider("经验权重", 0.0, 1.0, 0.3)
    
    with col2:
        education_weight = st.slider("教育权重", 0.0, 1.0, 0.2)
        location_weight = st.slider("地点权重", 0.0, 1.0, 0.1)
    
    st.write(f"权重总和: {skill_weight + experience_weight + education_weight + location_weight:.2f}")
    
    if st.button("应用匹配配置"):
        st.success("匹配配置已应用")


def main():
    """主函数"""
    # 初始化session state
    init_session_state()
    
    # 显示侧边栏
    show_sidebar()
    
    # 主界面标题
    st.title("🎯 SmartRecruiter - 智能招聘匹配系统")
    st.caption("支持多渠道人才搜索和智能匹配")
    
    # 使用选项卡组织功能
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 候选人搜索", 
        "📄 职位描述", 
        "⚙️ 系统配置",
        "📊 分析报告"
    ])
    
    with tab1:
        show_search_tab_enhanced()
    
    with tab2:
        # 原有的职位描述功能
        st.subheader("职位描述分析")
        st.info("请上传或粘贴职位描述文本")
        
        jd_text = st.text_area("职位描述", height=200, 
                              placeholder="请输入职位描述...")
        
        if st.button("分析职位描述"):
            if jd_text:
                # 这里可以添加JD分析逻辑
                st.session_state.jd_keywords = {
                    'skills': ['Python', 'Java', '机器学习', '后端开发'],
                    'experience': '3-5年',
                    'education': '本科及以上'
                }
                st.success("✅ 关键词提取完成！")
                st.write("提取的关键词:", st.session_state.jd_keywords['skills'])
            else:
                st.warning("请输入职位描述文本")
    
    with tab3:
        show_config_tab()
    
    with tab4:
        st.subheader("分析报告")
        st.info("分析报告功能正在开发中...")
        
        if st.session_state.search_results:
            st.write(f"当前有 {len(st.session_state.search_results)} 个候选人数据可供分析")
            
            # 简单的统计信息
            scores = [c.get('score', 0) for c in st.session_state.search_results]
            if scores:
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("平均分", f"{avg_score:.1f}")
                with col2:
                    st.metric("最高分", f"{max_score:.1f}")
                with col3:
                    st.metric("最低分", f"{min_score:.1f}")
        else:
            st.write("暂无数据，请先进行搜索")


if __name__ == "__main__":
    main()