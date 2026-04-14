"""
简单匹配算法
Phase 1: 关键词匹配
"""

import re
from typing import Dict, List, Any, Set
import logging

logger = logging.getLogger(__name__)


class SimpleMatcher:
    """简化匹配算法"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.matching_config = config.get('matching', {}) if config else {}
        
        # 权重配置
        self.weights = self.matching_config.get('weights', {
            'skills': 0.5,
            'experience': 0.3,
            'location': 0.2
        })
        
        # 技能关键词库
        self.skill_keywords = self._load_skill_keywords()
        
        # 经验级别映射
        self.experience_levels = {
            'Entry': 1,      # 0-2年
            'Mid': 3,        # 3-5年
            'Senior': 5,     # 5+年
            'Lead': 7,       # 7+年
            'Manager': 10,   # 10+年
            'Director': 12,  # 12+年
            'VP': 15,        # 15+年
            'C-Level': 20    # 20+年
        }
        
        logger.info("简单匹配器初始化完成")
    
    def _load_skill_keywords(self) -> Set[str]:
        """加载技能关键词库"""
        common_skills = [
            # 编程语言
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB',
            
            # 前端框架
            'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt.js',
            
            # 后端框架
            'Spring', 'Django', 'Flask', 'FastAPI', 'Express', 'NestJS',
            'Laravel', 'Ruby on Rails', 'ASP.NET',
            
            # 数据库
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Oracle', 'SQL Server', 'SQLite', 'Cassandra',
            
            # 云平台
            'AWS', 'Azure', 'GCP', '阿里云', '腾讯云', '华为云',
            'EC2', 'S3', 'Lambda', 'RDS', 'DynamoDB',
            
            # DevOps
            'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions',
            'Terraform', 'Ansible', 'Prometheus', 'Grafana',
            
            # 大数据
            'Hadoop', 'Spark', 'Hive', 'Kafka', 'Flink', 'Storm',
            
            # AI/ML
            '机器学习', '深度学习', '人工智能', '神经网络', '自然语言处理',
            '计算机视觉', '数据挖掘', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            
            # 移动开发
            'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin',
            
            # 测试
            '单元测试', '集成测试', '自动化测试', 'Selenium', 'Jest',
            'Pytest', 'JUnit', 'TestNG',
            
            # 其他技术
            '微服务', 'REST API', 'GraphQL', '消息队列', 'WebSocket',
            '版本控制', 'Git', 'SVN', '敏捷开发', 'Scrum', 'DevOps',
            
            # 设计工具
            'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator',
            
            # 业务技能
            '产品管理', '项目管理', '数据分析', '商业分析', '运营',
            '市场营销', '销售', '客户服务', '财务管理', '人力资源管理'
        ]
        
        return set(common_skills)
    
    def extract_keywords_from_jd(self, job_description: str) -> Dict[str, Any]:
        """从职位描述中提取关键词"""
        logger.info("从职位描述提取关键词")
        
        jd_lower = job_description.lower()
        
        # 提取技能关键词
        skills_found = []
        for skill in self.skill_keywords:
            if skill.lower() in jd_lower:
                skills_found.append(skill)
        
        # 提取经验要求
        experience_years = self._extract_experience_years(job_description)
        
        # 提取地点
        locations = self._extract_locations(job_description)
        
        # 提取教育要求
        education = self._extract_education(job_description)
        
        return {
            'skills': skills_found,
            'experience_years': experience_years,
            'locations': locations,
            'education': education,
            'text': job_description
        }
    
    def _extract_experience_years(self, text: str) -> int:
        """从文本中提取经验年限要求"""
        patterns = [
            r'(\d+)\+?\s*年(?:以上)?经验',
            r'(\d+)\+?\s*years?(?:\s+experience)?',
            r'经验(\d+)\+?年',
            r'(\d+)\+?\s*年(?:以上)?工作经历',
            r'(\d+)\+?\s*yr'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    years = int(match.group(1))
                    logger.info(f"提取到经验要求: {years}年")
                    return years
                except ValueError:
                    continue
        
        # 如果没找到明确年限，根据文本内容推断
        text_lower = text.lower()
        if any(word in text_lower for word in ['senior', '资深', '高级', '主管', '经理']):
            return 5
        elif any(word in text_lower for word in ['mid', '中级', '3年', '五年']):
            return 3
        elif any(word in text_lower for word in ['junior', '初级', 'entry', '应届']):
            return 1
        else:
            return 2  # 默认值
    
    def _extract_locations(self, text: str) -> List[str]:
        """从文本中提取地点"""
        # 简单的地点提取，实际可以使用更复杂的NLP
        common_locations = [
            '北京', '上海', '深圳', '广州', '杭州', '南京', '成都', '武汉',
            '西安', '苏州', '天津', '重庆', '长沙', '合肥', '宁波', '厦门',
            '青岛', '大连', '沈阳', '长春', '哈尔滨', '郑州', '福州', '南昌',
            '昆明', '贵阳', '南宁', '海口', '石家庄', '太原', '呼和浩特',
            '兰州', '西宁', '银川', '乌鲁木齐', '拉萨', '台湾', '香港', '澳门'
        ]
        
        locations_found = []
        for location in common_locations:
            if location in text:
                locations_found.append(location)
        
        # 检查远程工作
        if any(word in text.lower() for word in ['远程', '在家办公', 'work from home', 'remote']):
            locations_found.append('远程')
        
        return locations_found
    
    def _extract_education(self, text: str) -> str:
        """从文本中提取教育要求"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['博士', 'phd', '博士后']):
            return '博士'
        elif any(word in text_lower for word in ['硕士', '研究生', 'master', 'mba']):
            return '硕士'
        elif any(word in text_lower for word in ['本科', '学士', 'bachelor', '大学']):
            return '本科'
        elif any(word in text_lower for word in ['大专', '专科', 'associate']):
            return '大专'
        else:
            return '不限'
    
    def match_candidate(self, jd_keywords: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        """匹配单个候选人"""
        logger.info(f"匹配候选人: {candidate.get('name', '未知')}")
        
        # 计算各项匹配度
        skill_score = self._calculate_skill_score(jd_keywords['skills'], candidate.get('skills', []))
        experience_score = self._calculate_experience_score(
            jd_keywords['experience_years'], 
            candidate.get('experience_years', 0)
        )
        location_score = self._calculate_location_score(
            jd_keywords['locations'], 
            candidate.get('location', '')
        )
        
        # 加权总分
        total_score = (
            skill_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            location_score * self.weights['location']
        )
        
        # 匹配的关键词
        matched_skills = set(jd_keywords['skills']) & set(candidate.get('skills', []))
        
        # 缺失的关键词
        missing_skills = set(jd_keywords['skills']) - set(candidate.get('skills', []))
        
        return {
            'total_score': round(total_score * 100, 2),  # 转换为百分比
            'skill_score': round(skill_score * 100, 2),
            'experience_score': round(experience_score * 100, 2),
            'location_score': round(location_score * 100, 2),
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'skill_match_percentage': round(len(matched_skills) / len(jd_keywords['skills']) * 100, 2) if jd_keywords['skills'] else 100,
            'candidate': candidate
        }
    
    def _calculate_skill_score(self, jd_skills: List[str], candidate_skills: List[str]) -> float:
        """计算技能匹配度"""
        if not jd_skills:
            return 1.0  # 没有技能要求则得满分
        
        jd_skills_set = set(jd_skills)
        candidate_skills_set = set(candidate_skills)
        
        # 匹配的技能数量
        matched_count = len(jd_skills_set & candidate_skills_set)
        
        # 基础匹配度
        base_score = matched_count / len(jd_skills_set)
        
        # 如果候选人技能多于职位要求，给予小幅奖励
        if candidate_skills_set and len(candidate_skills_set) > len(jd_skills_set):
            bonus = min(0.1, (len(candidate_skills_set) - len(jd_skills_set)) * 0.02)
            base_score = min(1.0, base_score + bonus)
        
        return min(1.0, base_score)
    
    def _calculate_experience_score(self, jd_years: int, candidate_years: int) -> float:
        """计算经验匹配度"""
        if jd_years <= 0:
            return 1.0  # 没有经验要求则得满分
        
        # 简单线性评分
        if candidate_years >= jd_years:
            return 1.0
        elif candidate_years >= jd_years * 0.8:
            return 0.9
        elif candidate_years >= jd_years * 0.6:
            return 0.7
        elif candidate_years >= jd_years * 0.4:
            return 0.5
        elif candidate_years >= jd_years * 0.2:
            return 0.3
        else:
            return 0.1
    
    def _calculate_location_score(self, jd_locations: List[str], candidate_location: str) -> float:
        """计算地点匹配度"""
        if not jd_locations:
            return 1.0  # 没有地点要求则得满分
        
        # 检查是否接受远程
        if '远程' in jd_locations:
            return 1.0
        
        # 检查地点匹配
        candidate_location_lower = candidate_location.lower()
        for jd_location in jd_locations:
            if jd_location.lower() in candidate_location_lower or jd_location in candidate_location:
                return 1.0
        
        # 部分匹配（如省份相同）
        for jd_location in jd_locations:
            # 简单检查：如果候选人地点包含职位地点的一部分
            if len(jd_location) > 2 and jd_location[:2] in candidate_location:
                return 0.7
        
        return 0.2  # 不匹配
    
    def rank_candidates(self, jd_keywords: Dict[str, Any], candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对候选人进行排名"""
        logger.info(f"开始对 {len(candidates)} 个候选人进行排名")
        
        scored_candidates = []
        
        for candidate in candidates:
            match_result = self.match_candidate(jd_keywords, candidate)
            scored_candidates.append(match_result)
        
        # 按总分降序排序
        scored_candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 添加排名
        for i, candidate in enumerate(scored_candidates):
            candidate['rank'] = i + 1
        
        logger.info(f"候选人排名完成")
        return scored_candidates
    
    def generate_match_report(self, jd_keywords: Dict[str, Any], ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成匹配报告"""
        logger.info("生成匹配报告")
        
        if not ranked_candidates:
            return {
                'summary': '未找到匹配的候选人',
                'statistics': {},
                'top_candidates': []
            }
        
        # 统计信息
        total_candidates = len(ranked_candidates)
        high_match = len([c for c in ranked_candidates if c['total_score'] >= 80])
        medium_match = len([c for c in ranked_candidates if 60 <= c['total_score'] < 80])
        low_match = len([c for c in ranked_candidates if c['total_score'] < 60])
        
        # 热门技能统计
        all_matched_skills = []
        for candidate in ranked_candidates:
            all_matched_skills.extend(candidate['matched_skills'])
        
        from collections import Counter
        skill_counter = Counter(all_matched_skills)
        top_skills = skill_counter.most_common(10)
        
        # 平均匹配度
        avg_score = sum(c['total_score'] for c in ranked_candidates) / total_candidates
        
        return {
            'summary': f'找到 {total_candidates} 个候选人，其中 {high_match} 个高度匹配',
            'statistics': {
                'total_candidates': total_candidates,
                'high_match_count': high_match,
                'medium_match_count': medium_match,
                'low_match_count': low_match,
                'average_score': round(avg_score, 2),
                'top_matched_skills': top_skills
            },
            'top_candidates': ranked_candidates[:10],  # 返回前10个
            'jd_requirements': {
                'required_skills': jd_keywords['skills'],
                'experience_years': jd_keywords['experience_years'],
                'locations': jd_keywords['locations'],
                'education': jd_keywords['education']
            }
        }