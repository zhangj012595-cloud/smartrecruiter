"""
GitHub招聘渠道
基于GitHub API发现优秀技术人才
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GitHubCandidate:
    """GitHub候选人数据结构"""
    username: str
    name: Optional[str]
    location: Optional[str]
    company: Optional[str]
    bio: Optional[str]
    profile_url: str
    followers: int
    public_repos: int
    skills: Dict[str, int]  # 技能 -> 项目数量
    top_projects: List[Dict[str, Any]]
    score: float  # 综合评分（0-100）


class GitHubChannel:
    """GitHub招聘渠道"""
    
    def __init__(self, token: str = None):
        """
        初始化GitHub渠道
        
        Args:
            token: GitHub Personal Access Token（可选）
        """
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'SmartRecruiter-GitHub-Channel'
        })
        
        if token:
            self.session.headers['Authorization'] = f'token {token}'
            self.authenticated = True
            logger.info("使用GitHub Token认证（5000次/小时）")
        else:
            self.authenticated = False
            logger.warning("未使用Token（60次/小时限制）")
    
    def search_candidates(self, 
                         search_params: Dict[str, Any]) -> List[GitHubCandidate]:
        """
        搜索GitHub候选人
        
        Args:
            search_params: 搜索参数
                - keywords: List[str] - 关键词列表
                - location: str - 地理位置
                - min_followers: int - 最小关注者数
                - min_repos: int - 最小仓库数
                - tech_stack: List[str] - 技术栈
                - limit: int - 返回数量限制
        
        Returns:
            GitHub候选人列表
        """
        logger.info(f"搜索GitHub候选人: {search_params}")
        
        # 提取参数
        keywords = search_params.get('keywords', [])
        location = search_params.get('location')
        min_followers = search_params.get('min_followers', 10)
        min_repos = search_params.get('min_repos', 5)
        tech_stack = search_params.get('tech_stack', [])
        limit = search_params.get('limit', 10)
        
        # 构建搜索查询
        query_parts = ['type:user']
        
        # 关键词
        if keywords:
            query_parts.extend(keywords)
        
        # 地理位置
        if location:
            query_parts.append(f'location:{location}')
        
        # 关注者筛选
        query_parts.append(f'followers:>={min_followers}')
        
        # 仓库数筛选
        query_parts.append(f'repos:>={min_repos}')
        
        query = '+'.join(query_parts)
        url = f"{self.base_url}/search/users"
        params = {
            'q': query,
            'sort': 'followers',
            'order': 'desc',
            'per_page': limit
        }
        
        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                candidates = []
                
                for user in data['items'][:limit]:
                    candidate = self._get_candidate_details(user['login'], tech_stack)
                    if candidate:
                        candidates.append(candidate)
                
                # 按评分排序
                candidates.sort(key=lambda x: x.score, reverse=True)
                logger.info(f"找到 {len(candidates)} 位候选人")
                return candidates
            else:
                logger.error(f"搜索失败: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"搜索异常: {e}")
            return []
    
    def _get_candidate_details(self, username: str, 
                             tech_stack: List[str] = None) -> Optional[GitHubCandidate]:
        """获取候选人详细信息"""
        try:
            # 获取用户基本信息
            user_info = self._get_user_info(username)
            if not user_info:
                return None
            
            # 获取用户仓库
            repos = self._get_user_repos(username, limit=20)
            
            # 分析技能
            skills = self._analyze_skills(repos)
            
            # 获取顶级项目
            top_projects = self._get_top_projects(repos, tech_stack)
            
            # 计算评分
            score = self._calculate_score(user_info, repos, skills)
            
            return GitHubCandidate(
                username=username,
                name=user_info.get('name'),
                location=user_info.get('location'),
                company=user_info.get('company'),
                bio=user_info.get('bio'),
                profile_url=user_info['html_url'],
                followers=user_info['followers'],
                public_repos=user_info['public_repos'],
                skills=skills,
                top_projects=top_projects,
                score=score
            )
        except Exception as e:
            logger.error(f"获取候选人详情失败 {username}: {e}")
            return None
    
    def _get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"获取用户信息失败 {username}: {e}")
        return None
    
    def _get_user_repos(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户仓库"""
        try:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                'sort': 'updated',
                'direction': 'desc',
                'per_page': min(limit, 100)
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"获取用户仓库失败 {username}: {e}")
        return []
    
    def _analyze_skills(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析技能"""
        skills = {}
        
        for repo in repos:
            language = repo.get('language')
            if language:
                skills[language] = skills.get(language, 0) + 1
            
            # 从topics中提取技能
            topics = repo.get('topics', [])
            for topic in topics:
                # 常见技术关键词
                tech_keywords = ['python', 'javascript', 'java', 'go', 'rust',
                               'react', 'vue', 'angular', 'django', 'flask',
                               'docker', 'kubernetes', 'aws', 'azure', 'gcp',
                               'machine-learning', 'ai', 'deep-learning']
                
                for keyword in tech_keywords:
                    if keyword in topic.lower():
                        skills[keyword] = skills.get(keyword, 0) + 1
        
        return skills
    
    def _get_top_projects(self, repos: List[Dict[str, Any]], 
                         tech_stack: List[str] = None) -> List[Dict[str, Any]]:
        """获取顶级项目"""
        if not repos:
            return []
        
        # 过滤技术栈
        filtered_repos = repos
        if tech_stack:
            filtered_repos = [r for r in repos 
                            if r.get('language') and 
                            r['language'].lower() in [t.lower() for t in tech_stack]]
        
        # 按星标数排序
        sorted_repos = sorted(filtered_repos, 
                            key=lambda x: x['stargazers_count'], 
                            reverse=True)
        
        top_projects = []
        for repo in sorted_repos[:5]:  # 取前5个
            project = {
                'name': repo['name'],
                'description': repo.get('description'),
                'language': repo.get('language'),
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'url': repo['html_url'],
                'updated_at': repo['updated_at'][:10]
            }
            top_projects.append(project)
        
        return top_projects
    
    def _calculate_score(self, user: Dict[str, Any], 
                        repos: List[Dict[str, Any]], 
                        skills: Dict[str, Any]) -> float:
        """计算候选人评分"""
        score = 0.0
        
        # 1. 关注者评分（0-30分）
        followers_score = min(user['followers'] / 100 * 30, 30)
        score += followers_score
        
        # 2. 仓库数评分（0-25分）
        repos_score = min(user['public_repos'] / 30 * 25, 25)
        score += repos_score
        
        # 3. 项目质量评分（0-45分）
        if repos:
            repo_scores = []
            for repo in repos[:10]:  # 只看前10个仓库
                # 星标评分
                stars_score = min(repo['stargazers_count'] / 200 * 30, 30)
                # Fork评分
                forks_score = min(repo['forks_count'] / 100 * 15, 15)
                repo_scores.append(stars_score + forks_score)
            
            if repo_scores:
                avg_repo_score = sum(repo_scores) / len(repo_scores)
                score += min(avg_repo_score, 45)
        
        return round(score, 1)
    
    def generate_candidate_report(self, candidate: GitHubCandidate) -> str:
        """生成候选人报告"""
        report = f"""
{'='*60}
GitHub候选人报告
{'='*60}

👤 基本信息
{'─'*30}
用户名: {candidate.username}
姓名: {candidate.name or '未提供'}
位置: {candidate.location or '未提供'}
公司: {candidate.company or '未提供'}
简介: {candidate.bio or '未提供'}

📊 GitHub数据
{'─'*30}
关注者: {candidate.followers}
公开仓库: {candidate.public_repos}
综合评分: {candidate.score}/100

🛠️  技术栈
{'─'*30}
"""
        
        if candidate.skills:
            sorted_skills = sorted(candidate.skills.items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)
            for skill, count in sorted_skills[:10]:  # 显示前10个技能
                report += f"{skill}: {count} 个项目\n"
        else:
            report += "暂无技能数据\n"
        
        report += f"""
⭐ 顶级项目
{'─'*30}
"""
        
        for project in candidate.top_projects[:3]:  # 显示前3个项目
            report += f"• {project['name']}\n"
            if project['description']:
                report += f"  描述: {project['description']}\n"
            report += f"  语言: {project['language'] or '未指定'}\n"
            report += f"  ⭐ {project['stars']} | 🔀 {project['forks']}\n"
            report += f"  更新: {project['updated_at']}\n"
            report += f"  地址: {project['url']}\n\n"
        
        report += f"""
🔗 链接信息
{'─'*30}
GitHub主页: {candidate.profile_url}
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        return report
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            url = f"{self.base_url}/"
            response = self.session.get(url)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'rate_limit': self._get_rate_limit(),
                'authenticated': self.authenticated
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_rate_limit(self) -> Dict[str, Any]:
        """获取API限制信息"""
        try:
            url = f"{self.base_url}/rate_limit"
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'limit': data['rate']['limit'],
                    'remaining': data['rate']['remaining'],
                    'reset_time': data['rate']['reset']
                }
        except:
            pass
        return {'limit': 60, 'remaining': 60, 'reset_time': 0}


def get_channel(config: Dict[str, Any] = None) -> 'GitHubChannel':
    """
    获取GitHub渠道实例（兼容现有架构）
    
    Args:
        config: 配置信息
    
    Returns:
        GitHubChannel实例
    """
    # 从配置中获取GitHub Token
    token = None
    if config and 'channels' in config and 'github' in config['channels']:
        token = config['channels']['github'].get('api_key')
    
    return GitHubChannel(token)


# 测试函数
def test_github_channel():
    """测试GitHub渠道"""
    print("=" * 60)
    print("GitHub招聘渠道测试")
    print("=" * 60)
    
    # 初始化渠道
    channel = GitHubChannel()
    
    # 测试连接
    print("\n🔗 测试API连接...")
    connection = channel.test_connection()
    print(f"连接状态: {'成功' if connection['success'] else '失败'}")
    print(f"认证状态: {'是' if connection.get('authenticated') else '否'}")
    
    if connection.get('rate_limit'):
        rate = connection['rate_limit']
        print(f"API限制: {rate['remaining']}/{rate['limit']}")
    
    # 测试搜索
    print("\n🔍 测试候选人搜索...")
    search_params = {
        'keywords': ['python', 'backend'],
        'location': 'China',
        'min_followers': 20,
        'min_repos': 8,
        'limit': 3
    }
    
    candidates = channel.search_candidates(search_params)
    
    if candidates:
        print(f"✅ 找到 {len(candidates)} 位候选人")
        
        # 显示候选人信息
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{i}. {candidate.username} ({candidate.score}/100)")
            print(f"   姓名: {candidate.name or '未知'}")
            print(f"   位置: {candidate.location or '未知'}")
            print(f"   公司: {candidate.company or '未知'}")
            print(f"   关注者: {candidate.followers}")
            print(f"   仓库数: {candidate.public_repos}")
            
            if candidate.top_projects:
                best_project = max(candidate.top_projects, 
                                 key=lambda x: x['stars'])
                print(f"   最佳项目: {best_project['name']} (⭐{best_project['stars']})")
        
        # 生成详细报告
        print("\n📋 生成详细报告...")
        report = channel.generate_candidate_report(candidates[0])
        print(report)
        
        # 保存报告
        with open(f"github_candidate_report_{candidates[0].username}.txt", "w") as f:
            f.write(report)
        print(f"✅ 报告已保存")
    else:
        print("❌ 未找到候选人")
        print("\n💡 建议：")
        print("  1. 获取GitHub Token提高搜索效率")
        print("  2. 放宽搜索条件（减少关注者要求）")
        print("  3. 移除地理位置限制")
    
    print("\n" + "=" * 60)
    print("GitHub渠道测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_github_channel()