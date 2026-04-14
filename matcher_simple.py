"""
简化匹配算法 - 用于测试基本流程
Phase 1: 仅测试界面流程，实际匹配算法在Phase 2实现
"""

import random
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class SimpleTestMatcher:
    """简化测试匹配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        logger.info("简化测试匹配器初始化完成")
    
    def extract_keywords_from_jd(self, job_description: str) -> Dict[str, Any]:
        """从职位描述中提取关键词（简化版）"""
        logger.info("从职位描述提取关键词（测试版）")
        
        # 简单的关键词提取
        common_skills = ['Python', 'Java', 'JavaScript', 'React', 'Vue', 'Django', 'Flask']
        
        # 随机选择一些技能
        skills_found = random.sample(common_skills, random.randint(2, 4))
        
        # 随机经验年限
        experience_years = random.choice([1, 2, 3, 5, 7, 10])
        
        # 随机地点
        common_locations = ['北京', '上海', '深圳', '广州', '杭州']
        locations_found = random.sample(common_locations, random.randint(1, 3))
        
        # 随机学历
        education = random.choice(['本科', '硕士', '博士', '不限'])
        
        return {
            'skills': skills_found,
            'experience_years': experience_years,
            'locations': locations_found,
            'education': education,
            'text': job_description
        }
    
    def match_candidate(self, jd_keywords: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        """匹配单个候选人（简化测试版）"""
        # 生成随机匹配度
        skill_score = random.uniform(0.5, 1.0)
        experience_score = random.uniform(0.6, 1.0)
        location_score = random.uniform(0.7, 1.0)
        
        # 加权总分
        total_score = (skill_score * 0.5 + experience_score * 0.3 + location_score * 0.2) * 100
        
        # 匹配的技能（随机）
        matched_skills = []
        if jd_keywords['skills'] and candidate.get('skills'):
            # 随机选择一些匹配的技能
            possible_matches = set(jd_keywords['skills']) & set(candidate.get('skills', []))
            if possible_matches:
                matched_skills = random.sample(list(possible_matches), min(len(possible_matches), 3))
            else:
                # 如果没有共同技能，随机选择一些
                matched_skills = random.sample(jd_keywords['skills'], min(len(jd_keywords['skills']), 2))
        
        # 缺失的技能
        missing_skills = []
        if jd_keywords['skills']:
            missing_skills = [skill for skill in jd_keywords['skills'] if skill not in matched_skills]
        
        return {
            'total_score': round(total_score, 2),
            'skill_score': round(skill_score * 100, 2),
            'experience_score': round(experience_score * 100, 2),
            'location_score': round(location_score * 100, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills[:3],  # 只显示前3个
            'skill_match_percentage': round(len(matched_skills) / len(jd_keywords['skills']) * 100, 2) if jd_keywords['skills'] else 100,
            'candidate': candidate
        }
    
    def rank_candidates(self, jd_keywords: Dict[str, Any], candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对候选人进行排名（简化测试版）"""
        logger.info(f"开始对 {len(candidates)} 个候选人进行排名（测试版）")
        
        scored_candidates = []
        
        for candidate in candidates:
            match_result = self.match_candidate(jd_keywords, candidate)
            scored_candidates.append(match_result)
        
        # 按总分降序排序
        scored_candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 添加排名
        for i, candidate in enumerate(scored_candidates):
            candidate['rank'] = i + 1
        
        logger.info(f"候选人排名完成（测试版）")
        return scored_candidates
    
    def generate_match_report(self, jd_keywords: Dict[str, Any], ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成匹配报告（简化测试版）"""
        logger.info("生成匹配报告（测试版）")
        
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
        top_skills = skill_counter.most_common(5)
        
        # 平均匹配度
        avg_score = sum(c['total_score'] for c in ranked_candidates) / total_candidates
        
        return {
            'summary': f'找到 {total_candidates} 个候选人，其中 {high_match} 个高度匹配（测试数据）',
            'statistics': {
                'total_candidates': total_candidates,
                'high_match_count': high_match,
                'medium_match_count': medium_match,
                'low_match_count': low_match,
                'average_score': round(avg_score, 2),
                'top_matched_skills': top_skills
            },
            'top_candidates': ranked_candidates[:5],  # 只返回前5个
            'jd_requirements': {
                'required_skills': jd_keywords['skills'],
                'experience_years': jd_keywords['experience_years'],
                'locations': jd_keywords['locations'],
                'education': jd_keywords['education']
            },
            'note': '⚠️ 这是测试数据，实际匹配算法将在Phase 2实现'
        }