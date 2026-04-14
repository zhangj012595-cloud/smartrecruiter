"""
模拟LinkedIn渠道 - 用于测试基本流程
不依赖真实的LinkedIn账号
"""

import random
import time
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MockLinkedInChannel:
    """模拟LinkedIn渠道，返回测试数据"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('linkedin', {})
        self.search_config = config.get('search', {})
        logger.info("模拟LinkedIn渠道初始化完成")
    
    def initialize(self) -> bool:
        """初始化（总是成功）"""
        logger.info("模拟LinkedIn渠道初始化成功")
        return True
    
    def login(self) -> bool:
        """模拟登录（总是成功）"""
        logger.info("模拟LinkedIn登录成功")
        return True
    
    def search(self, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """模拟搜索，返回测试候选人数据"""
        logger.info(f"模拟搜索: {query}, 限制: {limit}")
        
        # 模拟网络延迟
        time.sleep(0.5)
        
        # 生成测试候选人
        candidates = []
        keywords = query.get('keywords', [])
        location = query.get('location', '')
        experience_level = query.get('experience_level', '')
        
        # 候选人姓名池
        first_names = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴',
                      '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
        last_names = ['明', '伟', '芳', '秀英', '娜', '敏', '静', '丽', '强', '磊',
                     '军', '洋', '勇', '艳', '杰', '娟', '涛', '超', '婷', '鹏']
        
        # 职位池
        positions = [
            'Python开发工程师', 'Java开发工程师', '前端开发工程师', '后端开发工程师',
            '全栈开发工程师', '数据科学家', '机器学习工程师', 'DevOps工程师',
            '测试工程师', '产品经理', 'UI设计师', '运营专员', '市场经理'
        ]
        
        # 公司池
        companies = [
            '阿里巴巴', '腾讯', '百度', '字节跳动', '美团', '京东', '拼多多',
            '华为', '小米', 'OPPO', 'vivo', '滴滴', '快手', '网易', '搜狐',
            '新浪', '携程', '贝壳找房', '蔚来', '理想汽车', '小鹏汽车'
        ]
        
        # 地点池
        locations = ['北京', '上海', '深圳', '广州', '杭州', '南京', '成都', '武汉']
        
        # 技能池（基于关键词）
        all_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Django', 'Flask', 'FastAPI', 'Spring',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', '机器学习', '深度学习', '数据分析'
        ]
        
        # 生成候选人
        for i in range(min(limit, 30)):  # 最多生成30个测试候选人
            # 随机选择姓名
            name = f"{random.choice(first_names)}{random.choice(last_names)}"
            
            # 基于关键词调整技能
            candidate_skills = []
            if keywords:
                # 包含部分关键词技能
                for skill in keywords:
                    if random.random() < 0.7:  # 70%概率包含关键词技能
                        candidate_skills.append(skill)
            
            # 添加一些随机技能
            additional_skills = random.sample(all_skills, random.randint(2, 5))
            candidate_skills.extend(additional_skills)
            candidate_skills = list(set(candidate_skills))  # 去重
            
            # 基于经验级别调整经验年限
            if experience_level == 'Entry':
                exp_years = random.randint(1, 2)
                exp_level = 'Entry'
            elif experience_level == 'Mid':
                exp_years = random.randint(3, 5)
                exp_level = 'Mid'
            elif experience_level == 'Senior':
                exp_years = random.randint(6, 10)
                exp_level = 'Senior'
            else:
                exp_years = random.randint(1, 10)
                exp_level = random.choice(['Entry', 'Mid', 'Senior'])
            
            # 基于地点调整位置
            if location and location in locations:
                candidate_location = location
            else:
                candidate_location = random.choice(locations)
            
            candidate = {
                'name': name,
                'title': random.choice(positions),
                'company': random.choice(companies),
                'location': candidate_location,
                'profile_url': f'https://www.linkedin.com/in/mock-{i}',
                'skills': candidate_skills,
                'experience_years': exp_years,
                'experience_level': exp_level,
                'avatar_url': None,
                'summary': f'拥有{exp_years}年经验的{random.choice(positions)}，擅长{candidate_skills[0] if candidate_skills else "技术开发"}',
                'education': random.choice(['本科', '硕士', '博士'])
            }
            
            candidates.append(candidate)
        
        logger.info(f"生成 {len(candidates)} 个模拟候选人")
        return candidates
    
    def test_connection(self) -> bool:
        """测试连接（总是成功）"""
        logger.info("模拟LinkedIn连接测试成功")
        return True
    
    def close(self):
        """关闭（无操作）"""
        logger.info("模拟LinkedIn渠道已关闭")


def get_channel(config: Dict[str, Any]) -> MockLinkedInChannel:
    """获取模拟LinkedIn渠道实例"""
    return MockLinkedInChannel(config)