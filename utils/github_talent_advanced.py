"""
高级GitHub人才发现工具
整合今天开发的所有GitHub人才发现功能
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import math

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AdvancedGitHubCandidate:
    """高级GitHub候选人数据结构"""
    username: str
    name: Optional[str]
    email: Optional[str]
    company: Optional[str]
    location: Optional[str]
    blog: Optional[str]
    bio: Optional[str]
    profile_url: str
    avatar_url: str
    followers: int
    following: int
    public_repos: int
    public_gists: int
    created_at: str
    updated_at: str
    
    # 增强字段
    score: float  # 综合评分 (0-100)
    skills: Dict[str, int]  # 技能及使用频率
    top_projects: List[Dict[str, Any]]  # 优质项目
    contribution_metrics: Dict[str, Any]  # 贡献度指标
    community_impact: float  # 社区影响力 (0-100)
    technical_depth: float  # 技术深度 (0-100)
    professional_image: float  # 专业形象 (0-100)
    
    # 时间相关
    analysis_time: str
    last_active: str


class AdvancedGitHubTalentFinder:
    """高级GitHub人才发现器"""
    
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SmartRecruiter-GitHub-Talent-Finder"
        }
        
        if token:
            self.headers["Authorization"] = f"token {token}"
            logger.info("使用GitHub Token认证")
        else:
            logger.warning("未使用Token（60次/小时限制）")
        
        self.rate_limit_remaining = 60
        self.rate_limit_reset = None
    
    def check_rate_limit(self) -> Dict[str, Any]:
        """检查API限制"""
        try:
            response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers)
            response.raise_for_status()
            
            rate_data = response.json()
            resources = rate_data.get('resources', {})
            core = resources.get('core', {})
            
            self.rate_limit_remaining = core.get('remaining', 60)
            self.rate_limit_reset = core.get('reset', None)
            
            return {
                'remaining': self.rate_limit_remaining,
                'limit': core.get('limit', 60),
                'reset_time': datetime.fromtimestamp(self.rate_limit_reset).isoformat() if self.rate_limit_reset else None,
                'authenticated': 'Authorization' in self.headers
            }
        except Exception as e:
            logger.error(f"检查API限制失败: {e}")
            return {'remaining': 0, 'limit': 60, 'error': str(e)}
    
    def search_users(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """高级用户搜索"""
        try:
            # 构建搜索查询
            query_parts = []
            
            # 关键词搜索
            if query_params.get('keywords'):
                keywords = query_params['keywords']
                if isinstance(keywords, list):
                    query_parts.append(' '.join(keywords))
                else:
                    query_parts.append(keywords)
            
            # 地理位置
            if query_params.get('location'):
                query_parts.append(f"location:{query_params['location']}")
            
            # 语言偏好
            if query_params.get('language'):
                query_parts.append(f"language:{query_params['language']}")
            
            # 关注者范围
            if query_params.get('min_followers'):
                query_parts.append(f"followers:>={query_params['min_followers']}")
            
            # 仓库数量
            if query_params.get('min_repos'):
                query_parts.append(f"repos:>={query_params['min_repos']}")
            
            # 构建完整查询
            query = ' '.join(query_parts)
            
            # API参数
            params = {
                'q': query,
                'per_page': min(query_params.get('limit', 30), 100),  # GitHub限制每页最多100
                'page': query_params.get('page', 1),
                'sort': query_params.get('sort', 'followers'),  # followers, repositories, joined
                'order': query_params.get('order', 'desc')
            }
            
            logger.info(f"搜索GitHub用户: {query}")
            
            # 发送请求
            response = requests.get(
                f"{self.base_url}/search/users",
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # 更新API限制
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 60))
            
            data = response.json()
            return data.get('items', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"搜索失败: {e}")
            return []
        except Exception as e:
            logger.error(f"搜索过程中发生错误: {e}")
            return []
    
    def get_user_details(self, username: str) -> Optional[Dict[str, Any]]:
        """获取用户详细信息"""
        try:
            response = requests.get(
                f"{self.base_url}/users/{username}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 404:
                logger.warning(f"用户不存在: {username}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"获取用户详情失败 {username}: {e}")
            return None
    
    def get_user_repos(self, username: str, limit: int = 30) -> List[Dict[str, Any]]:
        """获取用户仓库"""
        try:
            params = {
                'per_page': min(limit, 100),
                'page': 1,
                'sort': 'updated',  # 按更新时间排序
                'direction': 'desc'
            }
            
            response = requests.get(
                f"{self.base_url}/users/{username}/repos",
                headers=self.headers,
                params=params,
                timeout=20
            )
            response.raise_for_status()
            
            repos = response.json()
            
            # 按星标数排序
            repos.sort(key=lambda x: x.get('stargazers_count', 0), reverse=True)
            return repos[:limit]
            
        except Exception as e:
            logger.error(f"获取用户仓库失败 {username}: {e}")
            return []
    
    def analyze_user_skills(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析用户技能"""
        skills = {}
        
        for repo in repos:
            language = repo.get('language')
            if language:
                skills[language] = skills.get(language, 0) + 1
            
            # 分析README中的技术关键词
            description = repo.get('description', '').lower()
            topics = repo.get('topics', [])
            
            # 常见技术栈关键词
            tech_keywords = {
                'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
                'javascript': ['javascript', 'node', 'react', 'vue', 'angular', 'typescript'],
                'java': ['java', 'spring', 'android'],
                'go': ['go', 'golang'],
                'rust': ['rust'],
                'cpp': ['c++', 'cpp'],
                'php': ['php', 'laravel', 'symfony'],
                'ruby': ['ruby', 'rails'],
                'swift': ['swift', 'ios'],
                'kotlin': ['kotlin', 'android'],
                'scala': ['scala'],
                'haskell': ['haskell'],
                'elixir': ['elixir', 'phoenix'],
                'clojure': ['clojure'],
                'erlang': ['erlang']
            }
            
            # 检查描述中的关键词
            for tech, keywords in tech_keywords.items():
                for keyword in keywords:
                    if keyword in description:
                        skills[tech] = skills.get(tech, 0) + 1
                        break
            
            # 检查主题标签
            for topic in topics:
                for tech, keywords in tech_keywords.items():
                    for keyword in keywords:
                        if keyword in topic.lower():
                            skills[tech] = skills.get(tech, 0) + 1
                            break
        
        return skills
    
    def calculate_candidate_score(self, user_data: Dict[str, Any], 
                                 repos: List[Dict[str, Any]],
                                 skills: Dict[str, int]) -> Dict[str, float]:
        """计算候选人综合评分"""
        scores = {
            'project_quality': 0.0,  # 项目质量 (45分)
            'community_impact': 0.0,  # 社区影响力 (30分)
            'activity_level': 0.0,  # 活跃度 (15分)
            'professional_image': 0.0  # 专业形象 (10分)
        }
        
        # 1. 项目质量评分 (45分)
        if repos:
            total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
            total_forks = sum(repo.get('forks_count', 0) for repo in repos)
            total_watchers = sum(repo.get('watchers_count', 0) for repo in repos)
            
            # 星标评分 (0-25分)
            star_score = min(25, total_stars / 10)  # 每10个星标得1分，最高25分
            
            # Fork评分 (0-10分)
            fork_score = min(10, total_forks / 5)  # 每5个fork得1分，最高10分
            
            # 项目数量评分 (0-10分)
            repo_count_score = min(10, len(repos) / 3)  # 每3个项目得1分，最高10分
            
            scores['project_quality'] = star_score + fork_score + repo_count_score
        
        # 2. 社区影响力评分 (30分)
        followers = user_data.get('followers', 0)
        following = user_data.get('following', 0)
        
        # 关注者评分 (0-20分)
        follower_score = min(20, followers / 5)  # 每5个关注者得1分，最高20分
        
        # 关注比评分 (0-10分)
        if following > 0:
            follow_ratio = followers / following
            follow_ratio_score = min(10, follow_ratio * 2)  # 关注比越高越好
        else:
            follow_ratio_score = 5  # 默认分
        
        scores['community_impact'] = follower_score + follow_ratio_score
        
        # 3. 活跃度评分 (15分)
        created_at = user_data.get('created_at')
        updated_at = user_data.get('updated_at')
        
        if created_at and updated_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                
                # 账户年龄 (0-5分)
                account_age_days = (datetime.now() - created_date).days
                account_age_score = min(5, account_age_days / 365)  # 每年得1分
                
                # 最近活跃 (0-10分)
                days_since_update = (datetime.now() - updated_date).days
                if days_since_update <= 7:
                    recent_activity_score = 10
                elif days_since_update <= 30:
                    recent_activity_score = 8
                elif days_since_update <= 90:
                    recent_activity_score = 6
                elif days_since_update <= 180:
                    recent_activity_score = 4
                elif days_since_update <= 365:
                    recent_activity_score = 2
                else:
                    recent_activity_score = 0
                
                scores['activity_level'] = account_age_score + recent_activity_score
            except:
                scores['activity_level'] = 7.5  # 默认分
        
        # 4. 专业形象评分 (10分)
        profile_completeness = 0
        
        # 检查资料完整性
        if user_data.get('name'): profile_completeness += 1
        if user_data.get('email'): profile_completeness += 1
        if user_data.get('company'): profile_completeness += 1
        if user_data.get('location'): profile_completeness += 1
        if user_data.get('blog'): profile_completeness += 1
        if user_data.get('bio'): profile_completeness += 2  # 个人简介更重要
        
        # 技能多样性 (0-4分)
        skill_diversity = min(4, len(skills))
        
        scores['professional_image'] = profile_completeness + skill_diversity
        
        return scores
    
    def find_talent(self, search_params: Dict[str, Any]) -> List[AdvancedGitHubCandidate]:
        """发现高级人才"""
        logger.info(f"开始高级人才发现: {search_params}")
        
        # 检查API限制
        rate_limit = self.check_rate_limit()
        if rate_limit.get('remaining', 0) < 10:
            logger.warning(f"API限制较低: {rate_limit.get('remaining')}次剩余")
        
        # 搜索用户
        users = self.search_users(search_params)
        
        if not users:
            logger.info("未找到符合条件的用户")
            return []
        
        logger.info(f"找到 {len(users)} 个潜在用户")
        
        candidates = []
        limit = search_params.get('limit', 10)
        
        for i, user in enumerate(users[:limit]):
            try:
                username = user.get('login')
                if not username:
                    continue
                
                logger.info(f"分析用户 {i+1}/{min(len(users), limit)}: {username}")
                
                # 获取详细信息
                user_details = self.get_user_details(username)
                if not user_details:
                    continue
                
                # 获取仓库
                repos = self.get_user_repos(username, limit=20)
                
                # 分析技能
                skills = self.analyze_user_skills(repos)
                
                # 计算评分
                score_components = self.calculate_candidate_score(user_details, repos, skills)
                total_score = sum(score_components.values())
                
                # 获取优质项目
                top_projects = []
                for repo in repos[:5]:  # 取前5个项目
                    if repo.get('stargazers_count', 0) > 0:  # 只包括有星标的项目
                        top_projects.append({
                            'name': repo.get('name'),
                            'description': repo.get('description'),
                            'url': repo.get('html_url'),
                            'stars': repo.get('stargazers_count', 0),
                            'forks': repo.get('forks_count', 0),
                            'language': repo.get('language'),
                            'updated_at': repo.get('updated_at')
                        })
                
                # 计算贡献度指标
                contribution_metrics = {
                    'total_contributions': len(repos),
                    'total_stars': sum(r.get('stargazers_count', 0) for r in repos),
                    'total_forks': sum(r.get('forks_count', 0) for r in repos),
                    'primary_languages': list(skills.keys())[:5],
                    'skill_diversity': len(skills)
                }
                
                # 创建候选人对象
                candidate = AdvancedGitHubCandidate(
                    username=username,
                    name=user_details.get('name'),
                    email=user_details.get('email'),
                    company=user_details.get('company'),
                    location=user_details.get('location'),
                    blog=user_details.get('blog'),
                    bio=user_details.get('bio'),
                    profile_url=user_details.get('html_url'),
                    avatar_url=user_details.get('avatar_url'),
                    followers=user_details.get('followers', 0),
                    following=user_details.get('following', 0),
                    public_repos=user_details.get('public_repos', 0),
                    public_gists=user_details.get('public_gists', 0),
                    created_at=user_details.get('created_at'),
                    updated_at=user_details.get('updated_at'),
                    score=total_score,
                    skills=skills,
                    top_projects=top_projects,
                    contribution_metrics=contribution_metrics,
                    community_impact=score_components['community_impact'],
                    technical_depth=score_components['project_quality'],
                    professional_image=score_components['professional_image'],
                    analysis_time=datetime.now().isoformat(),
                    last_active=user_details.get('updated_at', '')
                )
                
                candidates.append(candidate)
                
                # 避免API限制
                if i < len(users) - 1:
                    time.sleep(0.5)  # 避免请求过快
                    
            except Exception as e:
                logger.error(f"分析用户失败 {user.get('login')}: {e}")
                continue
        
        # 按评分排序
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"高级人才发现完成，找到 {len(candidates)} 个候选人")
        return candidates
    
    def generate_detailed_report(self, candidate: AdvancedGitHubCandidate) -> str:
        """生成详细报告"""
        report = []
        report.append("=" * 70)
        report.append(f"GitHub人才详细分析报告")
        report.append("=" * 70)
        report.append("")
        
        # 基本信息
        report.append("📋 **基本信息**")
        report.append(f"• 用户名: {candidate.username}")
        report.append(f"• 姓名: {candidate.name or '未提供'}")
        report.append(f"• 公司: {candidate.company or '未提供'}")
        report.append(f"• 地点: {candidate.location or '未提供'}")
        report.append(f"• 个人简介: {candidate.bio or '未提供'}")
        report.append(f"• 个人网站: {candidate.blog or '未提供'}")
        report.append(f"• GitHub主页: {candidate.profile_url}")
        report.append("")
        
        # 统计信息
        report.append("📊 **统计信息**")
        report.append(f"• 关注者: {candidate.followers}")
        report.append(f"• 关注中: {candidate.following}")
        report.append(f"• 公开仓库: {candidate.public_repos}")
        report.append(f"• 公开代码片段: {candidate.public_gists}")
        report.append(f"• 账户创建: {candidate.created_at}")
        report.append(f"• 最后活跃: {candidate.last_active}")
        report.append("")
        
        # 评分信息
        report.append("⭐ **综合评分**")
        report.append(f"• 总分: {candidate.score:.1f}/100")
        report.append(f"• 项目质量: {candidate.technical_depth:.1f}/45")
        report.append(f"• 社区影响力: {candidate.community_impact:.1f}/30")
        report.append(f"• 活跃度: {candidate.contribution_metrics.get('activity_score', 0):.1f}/15")
        report.append(f"• 专业形象: {candidate.professional_image:.1f}/10")
        report.append("")
        
        # 技能分析
        report.append("🛠️ **技能分析**")
        if candidate.skills:
            sorted_skills = sorted(candidate.skills.items(), key=lambda x: x[1], reverse=True)
            for skill, count in sorted_skills[:10]:
                report.append(f"• {skill}: {count}个项目")
        else:
            report.append("• 未检测到明确的技能信息")
        report.append("")
        
        # 优质项目
        report.append("🚀 **优质项目**")
        if candidate.top_projects:
            for i, project in enumerate(candidate.top_projects[:3], 1):
                report.append(f"{i}. **{project['name']}**")
                if project.get('description'):
                    report.append(f"   描述: {project['description']}")
                report.append(f"   星标: ⭐{project.get('stars', 0)}")
                report.append(f"   Fork: 🔀{project.get('forks', 0)}")
                if project.get('language'):
                    report.append(f"   语言: {project['language']}")
                report.append(f"   链接: {project.get('url')}")
                report.append("")
        else:
            report.append("• 未发现优质项目")
            report.append("")
        
        # 贡献度指标
        report.append("📈 **贡献度指标**")
        metrics = candidate.contribution_metrics
        report.append(f"• 总项目数: {metrics.get('total_contributions', 0)}")
        report.append(f"• 总星标数: {metrics.get('total_stars', 0)}")
        report.append(f"• 总Fork数: {metrics.get('total_forks', 0)}")
        report.append(f"• 技能多样性: {metrics.get('skill_diversity', 0)}种")
        report.append(f"• 主要语言: {', '.join(metrics.get('primary_languages', []))}")
        report.append("")
        
        # 评估建议
        report.append("💡 **评估建议**")
        if candidate.score >= 80:
            report.append("• ✅ **强烈推荐**: 综合评分优秀，技术深度和社区影响力都很突出")
        elif candidate.score >= 60:
            report.append("• 👍 **推荐**: 评分良好，具备较强的技术能力和社区参与度")
        elif candidate.score >= 40:
            report.append("• 🤔 **可考虑**: 评分中等，需要进一步考察具体技能匹配度")
        else:
            report.append("• ⚠️ **谨慎考虑**: 评分较低，可能需要更多成长时间")
        
        report.append("")
        report.append("=" * 70)
        report.append(f"报告生成时间: {candidate.analysis_time}")
        report.append("=" * 70)
        
        return '\n'.join(report)


def main():
    """测试函数"""
    finder = AdvancedGitHubTalentFinder()
    
    # 测试API连接
    rate_limit = finder.check_rate_limit()
    print(f"API限制: {rate_limit}")
    
    # 测试搜索
    search_params = {
        'keywords': ['python', 'developer'],
        'location': 'China',
        'min_followers': 10,
        'min_repos': 5,
        'limit': 3
    }
    
    candidates = finder.find_talent(search_params)
    
    if candidates:
        print(f"\n找到 {len(candidates)} 个候选人:")
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{i}. {candidate.username} (评分: {candidate.score:.1f})")
            print(f"   公司: {candidate.company or '未提供'}")
            print(f"   地点: {candidate.location or '未提供'}")
            print(f"   关注者: {candidate.followers}")
            print(f"   仓库数: {candidate.public_repos}")
            
            if candidate.skills:
                top_skills = sorted(candidate.skills.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   主要技能: {', '.join([s for s, _ in top_skills])}")
    else:
        print("未找到候选人")


if __name__ == "__main__":
    main()