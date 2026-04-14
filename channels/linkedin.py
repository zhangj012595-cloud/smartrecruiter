"""
LinkedIn渠道 - 简化版本
专注Web应用，使用Selenium进行自动化
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Candidate:
    """候选人数据结构"""
    name: str
    title: str
    company: str
    location: str
    profile_url: str
    skills: List[str]
    experience_years: int
    experience_level: str
    avatar_url: Optional[str] = None
    summary: Optional[str] = None
    education: Optional[str] = None


class LinkedInChannel:
    """LinkedIn渠道实现（简化版）"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('linkedin', {})
        self.driver = None
        self.logged_in = False
        
        # 搜索配置
        self.search_config = config.get('search', {})
        self.locations = self.search_config.get('locations', [])
        self.experience_levels = self.search_config.get('experience_levels', [])
        
        logger.info("LinkedIn渠道初始化完成")
    
    def initialize(self) -> bool:
        """初始化浏览器驱动"""
        try:
            options = webdriver.ChromeOptions()
            
            # 配置选项
            if self.config.get('headless', False):
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 用户代理
            options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("浏览器驱动初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {e}")
            return False
    
    def login(self) -> bool:
        """登录LinkedIn"""
        if self.logged_in:
            return True
        
        try:
            # 检查是否有cookie文件
            cookie_path = self.config.get('cookie_path')
            if cookie_path:
                return self._login_with_cookies(cookie_path)
            
            # 使用用户名密码登录
            username = self.config.get('username')
            password = self.config.get('password')
            
            if not username or not password:
                logger.error("未提供登录凭据")
                return False
            
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # 输入用户名
            username_field = self.driver.find_element(By.ID, "username")
            username_field.send_keys(username)
            
            # 输入密码
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # 点击登录
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # 等待登录成功
            time.sleep(5)
            
            # 检查是否登录成功
            current_url = self.driver.current_url
            if "feed" in current_url or "linkedin.com" in current_url and "login" not in current_url:
                self.logged_in = True
                logger.info("LinkedIn登录成功")
                
                # 保存cookies供下次使用
                self._save_cookies()
                return True
            else:
                logger.error("LinkedIn登录失败")
                return False
                
        except Exception as e:
            logger.error(f"登录过程出错: {e}")
            return False
    
    def _login_with_cookies(self, cookie_path: str) -> bool:
        """使用cookies登录"""
        try:
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            with open(cookie_path, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            # 刷新页面应用cookies
            self.driver.refresh()
            time.sleep(3)
            
            # 检查是否登录成功
            if "feed" in self.driver.current_url or "linkedin.com" in self.driver.current_url:
                self.logged_in = True
                logger.info("使用cookies登录成功")
                return True
            else:
                logger.warning("cookies可能已过期，尝试重新登录")
                return self.login()
                
        except Exception as e:
            logger.error(f"使用cookies登录失败: {e}")
            return False
    
    def _save_cookies(self):
        """保存cookies到文件"""
        try:
            cookies = self.driver.get_cookies()
            cookie_path = self.config.get('cookie_path', 'linkedin_cookies.json')
            
            with open(cookie_path, 'w') as f:
                json.dump(cookies, f)
            
            logger.info(f"cookies已保存到: {cookie_path}")
        except Exception as e:
            logger.error(f"保存cookies失败: {e}")
    
    def search(self, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """搜索候选人"""
        if not self.driver:
            if not self.initialize():
                return []
        
        if not self.logged_in:
            if not self.login():
                return []
        
        try:
            # 构建搜索URL
            search_url = self._build_search_url(query)
            logger.info(f"搜索URL: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(3)
            
            # 等待搜索结果加载
            self._wait_for_results()
            
            # 提取搜索结果
            candidates = self._extract_candidates(limit)
            
            logger.info(f"找到 {len(candidates)} 个候选人")
            return candidates
            
        except Exception as e:
            logger.error(f"搜索过程出错: {e}")
            return []
    
    def _build_search_url(self, query: Dict[str, Any]) -> str:
        """构建LinkedIn搜索URL"""
        base_url = "https://www.linkedin.com/search/results/people/"
        
        # 关键词
        keywords = query.get('keywords', [])
        keyword_str = " ".join(keywords) if keywords else ""
        
        # 地点
        location = query.get('location', '')
        
        # 经验级别
        experience_level = query.get('experience_level', '')
        
        # 构建URL参数
        params = []
        
        if keyword_str:
            params.append(f"keywords={keyword_str.replace(' ', '%20')}")
        
        if location:
            params.append(f"location={location.replace(' ', '%20')}")
        
        if experience_level:
            # 将经验级别映射到LinkedIn参数
            level_mapping = {
                'Entry': '1',
                'Mid': '2',
                'Senior': '3',
                'Lead': '4',
                'Manager': '5',
                'Director': '6',
                'VP': '7',
                'C-Level': '8'
            }
            level_code = level_mapping.get(experience_level, '')
            if level_code:
                params.append(f"seniority={level_code}")
        
        # 添加其他参数
        params.append("origin=FACETED_SEARCH")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        else:
            return base_url
    
    def _wait_for_results(self, timeout: int = 30):
        """等待搜索结果加载"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
            )
            logger.info("搜索结果加载完成")
        except TimeoutException:
            logger.warning("等待搜索结果超时")
    
    def _extract_candidates(self, limit: int) -> List[Dict[str, Any]]:
        """从搜索结果页面提取候选人信息"""
        candidates = []
        
        try:
            # 找到所有候选人卡片
            result_items = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".search-results-container .reusable-search__result-container"
            )
            
            logger.info(f"找到 {len(result_items)} 个结果项")
            
            for i, item in enumerate(result_items[:limit]):
                try:
                    candidate = self._extract_candidate_from_item(item)
                    if candidate:
                        candidates.append(candidate)
                except Exception as e:
                    logger.warning(f"提取第 {i+1} 个候选人失败: {e}")
                    continue
                
                # 滚动以加载更多内容
                if i % 5 == 0:
                    self.driver.execute_script("arguments[0].scrollIntoView();", item)
                    time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"提取候选人信息失败: {e}")
        
        return candidates
    
    def _extract_candidate_from_item(self, item) -> Optional[Dict[str, Any]]:
        """从单个结果项提取候选人信息"""
        try:
            # 提取基本信息
            name_elem = item.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
            name = name_elem.text.strip()
            profile_url = name_elem.get_attribute('href')
            
            # 提取职位和公司
            title_elem = item.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
            title = title_elem.text.strip()
            
            # 提取地点
            location_elem = item.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
            location = location_elem.text.strip()
            
            # 尝试提取头像
            avatar_url = None
            try:
                avatar_elem = item.find_element(By.CSS_SELECTOR, ".entity-result__image img")
                avatar_url = avatar_elem.get_attribute('src')
            except:
                pass
            
            # 构建候选人对象
            candidate = {
                'name': name,
                'title': title,
                'company': self._extract_company_from_title(title),
                'location': location,
                'profile_url': profile_url,
                'avatar_url': avatar_url,
                'skills': self._extract_skills_from_title(title),
                'experience_years': self._estimate_experience_years(title),
                'experience_level': self._determine_experience_level(title),
                'summary': '',
                'education': ''
            }
            
            return candidate
            
        except Exception as e:
            logger.warning(f"提取候选人详细信息失败: {e}")
            return None
    
    def _extract_company_from_title(self, title: str) -> str:
        """从标题中提取公司名称"""
        # 简单的提取逻辑，实际需要更复杂的解析
        if ' at ' in title:
            return title.split(' at ')[-1].strip()
        elif ' @ ' in title:
            return title.split(' @ ')[-1].strip()
        elif '在' in title:
            return title.split('在')[-1].strip()
        else:
            # 尝试提取公司名称
            parts = title.split()
            if len(parts) > 1:
                return parts[-1]
            return title
    
    def _extract_skills_from_title(self, title: str) -> List[str]:
        """从标题中提取技能关键词"""
        skills = []
        common_skills = self.search_config.get('common_skills', [])
        
        title_lower = title.lower()
        for skill in common_skills:
            if skill.lower() in title_lower:
                skills.append(skill)
        
        return skills
    
    def _estimate_experience_years(self, title: str) -> int:
        """从标题估计工作经验年限"""
        # 简单的经验估计逻辑
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['senior', 'lead', 'principal', '资深', '高级']):
            return 5
        elif any(word in title_lower for word in ['mid', '中级', 'middle']):
            return 3
        elif any(word in title_lower for word in ['junior', 'entry', '初级', '助理']):
            return 1
        else:
            return 2  # 默认值
    
    def _determine_experience_level(self, title: str) -> str:
        """确定经验级别"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['vp', 'vice president', '副总裁', '副总经理']):
            return 'VP'
        elif any(word in title_lower for word in ['director', '总监', '主任']):
            return 'Director'
        elif any(word in title_lower for word in ['manager', '经理', '主管']):
            return 'Manager'
        elif any(word in title_lower for word in ['lead', '组长', '负责人']):
            return 'Lead'
        elif any(word in title_lower for word in ['senior', '资深', '高级']):
            return 'Senior'
        elif any(word in title_lower for word in ['mid', '中级']):
            return 'Mid'
        else:
            return 'Entry'
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            if not self.driver:
                if not self.initialize():
                    return False
            
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            # 检查是否能访问LinkedIn
            if "linkedin.com" in self.driver.current_url:
                logger.info("LinkedIn连接测试成功")
                return True
            else:
                logger.warning("LinkedIn连接测试失败")
                return False
                
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logged_in = False
            logger.info("浏览器已关闭")


def get_channel(config: Dict[str, Any]) -> LinkedInChannel:
    """获取LinkedIn渠道实例"""
    return LinkedInChannel(config)