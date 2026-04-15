"""
招聘渠道配置系统
管理多种招聘渠道的配置信息
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChannelConfig:
    """渠道配置"""
    name: str                    # 渠道名称
    enabled: bool               # 是否启用
    auth_type: str              # 认证类型: api_key, oauth, cookie, none
    api_key: Optional[str]      # API密钥
    api_secret: Optional[str]   # API密钥（可选）
    base_url: str               # API基础URL
    endpoints: Dict[str, str]   # API端点
    rate_limit: int             # 速率限制（次/小时）
    is_paid: bool               # 是否付费服务
    last_updated: str           # 最后更新时间


class RecruitmentConfigManager:
    """招聘配置管理器"""
    
    def __init__(self, config_file: str = "recruitment_configs.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.channels = {}
        self._load_configs()
    
    def _load_configs(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 转换为ChannelConfig对象
                for name, config_data in data.items():
                    self.channels[name] = ChannelConfig(**config_data)
                
                logger.info(f"加载了 {len(self.channels)} 个渠道配置")
            else:
                logger.info("配置文件不存在，初始化默认配置")
                self._init_default_configs()
                self.save_configs()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self._init_default_configs()
    
    def _init_default_configs(self):
        """初始化默认配置"""
        default_configs = {
            "LinkedIn": ChannelConfig(
                name="LinkedIn",
                enabled=False,  # Phase 2计划
                auth_type="oauth",
                api_key=None,
                api_secret=None,
                base_url="https://api.linkedin.com",
                endpoints={
                    "jobs_search": "/v2/jobSearch",
                    "company_search": "/v2/organizationSearch",
                    "profile_search": "/v2/people"
                },
                rate_limit=100,
                is_paid=True,
                last_updated=datetime.now().isoformat()
            ),
            "GitHub": ChannelConfig(
                name="GitHub",
                enabled=True,  # 立即可用
                auth_type="api_key",
                api_key=None,  # 可选，提高限制
                api_secret=None,
                base_url="https://api.github.com",
                endpoints={
                    "user_search": "/search/users",
                    "repo_search": "/search/repositories",
                    "user_info": "/users/{username}",
                    "user_repos": "/users/{username}/repos"
                },
                rate_limit=60,  # 未认证60次，认证后5000次
                is_paid=False,  # 完全免费
                last_updated=datetime.now().isoformat()
            ),
            "BOSS直聘": ChannelConfig(
                name="BOSS直聘",
                enabled=False,  # 需要申请API
                auth_type="api_key",
                api_key=None,
                api_secret=None,
                base_url="https://www.zhipin.com",
                endpoints={
                    "job_search": "/api/job/search",
                    "company_search": "/api/company/search"
                },
                rate_limit=100,
                is_paid=True,
                last_updated=datetime.now().isoformat()
            ),
            "智联招聘": ChannelConfig(
                name="智联招聘",
                enabled=False,  # 需要申请API
                auth_type="api_key",
                api_key=None,
                api_secret=None,
                base_url="https://www.zhaopin.com",
                endpoints={
                    "position_search": "/api/position/search",
                    "resume_search": "/api/resume/search"
                },
                rate_limit=100,
                is_paid=True,
                last_updated=datetime.now().isoformat()
            ),
            "脉脉": ChannelConfig(
                name="脉脉",
                enabled=False,  # 需要申请API
                auth_type="oauth",
                api_key=None,
                api_secret=None,
                base_url="https://open.maimai.cn",
                endpoints={
                    "user_search": "/api/user/search",
                    "contact_search": "/api/contact/search"
                },
                rate_limit=50,
                is_paid=True,
                last_updated=datetime.now().isoformat()
            )
        }
        
        self.channels = default_configs
    
    def save_configs(self):
        """保存配置到文件"""
        try:
            # 更新最后修改时间
            for channel in self.channels.values():
                channel.last_updated = datetime.now().isoformat()
            
            # 转换为字典
            data = {}
            for name, channel in self.channels.items():
                data[name] = asdict(channel)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"保存了 {len(self.channels)} 个渠道配置到 {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get_channel(self, name: str) -> Optional[ChannelConfig]:
        """获取渠道配置"""
        return self.channels.get(name)
    
    def get_enabled_channels(self) -> List[ChannelConfig]:
        """获取已启用的渠道"""
        return [c for c in self.channels.values() if c.enabled]
    
    def enable_channel(self, name: str) -> bool:
        """启用渠道"""
        if name in self.channels:
            self.channels[name].enabled = True
            self.save_configs()
            logger.info(f"已启用渠道: {name}")
            return True
        else:
            logger.error(f"渠道不存在: {name}")
            return False
    
    def disable_channel(self, name: str) -> bool:
        """禁用渠道"""
        if name in self.channels:
            self.channels[name].enabled = False
            self.save_configs()
            logger.info(f"已禁用渠道: {name}")
            return True
        else:
            logger.error(f"渠道不存在: {name}")
            return False
    
    def update_channel_config(self, name: str, config_data: Dict[str, Any]) -> bool:
        """更新渠道配置"""
        if name not in self.channels:
            logger.error(f"渠道不存在: {name}")
            return False
        
        try:
            channel = self.channels[name]
            
            # 更新配置字段
            for key, value in config_data.items():
                if hasattr(channel, key):
                    setattr(channel, key, value)
            
            channel.last_updated = datetime.now().isoformat()
            self.save_configs()
            
            logger.info(f"已更新渠道配置: {name}")
            return True
        except Exception as e:
            logger.error(f"更新配置失败 {name}: {e}")
            return False
    
    def add_channel(self, name: str, config_data: Dict[str, Any]) -> bool:
        """添加新渠道"""
        if name in self.channels:
            logger.error(f"渠道已存在: {name}")
            return False
        
        try:
            # 确保有必需字段
            required_fields = ['name', 'auth_type', 'base_url']
            for field in required_fields:
                if field not in config_data:
                    config_data[field] = ""
            
            # 设置默认值
            config_data.setdefault('enabled', False)
            config_data.setdefault('rate_limit', 60)
            config_data.setdefault('is_paid', False)
            config_data.setdefault('endpoints', {})
            config_data.setdefault('last_updated', datetime.now().isoformat())
            
            # 创建渠道配置
            channel = ChannelConfig(**config_data)
            self.channels[name] = channel
            self.save_configs()
            
            logger.info(f"已添加新渠道: {name}")
            return True
        except Exception as e:
            logger.error(f"添加渠道失败: {e}")
            return False
    
    def remove_channel(self, name: str) -> bool:
        """移除渠道"""
        if name not in self.channels:
            logger.error(f"渠道不存在: {name}")
            return False
        
        try:
            del self.channels[name]
            self.save_configs()
            logger.info(f"已移除渠道: {name}")
            return True
        except Exception as e:
            logger.error(f"移除渠道失败: {e}")
            return False
    
    def get_channel_status(self, name: str) -> Dict[str, Any]:
        """获取渠道状态"""
        if name not in self.channels:
            return {"exists": False, "error": f"渠道不存在: {name}"}
        
        channel = self.channels[name]
        
        status = {
            "exists": True,
            "name": channel.name,
            "enabled": channel.enabled,
            "auth_type": channel.auth_type,
            "base_url": channel.base_url,
            "rate_limit": channel.rate_limit,
            "is_paid": channel.is_paid,
            "last_updated": channel.last_updated,
            "requires_auth": channel.api_key is None and channel.auth_type != "none",
            "ready_for_use": channel.enabled and (channel.auth_type == "none" or channel.api_key is not None)
        }
        
        return status
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """列出所有渠道"""
        channels_list = []
        
        for name, channel in self.channels.items():
            channels_list.append({
                "name": name,
                "enabled": channel.enabled,
                "auth_type": channel.auth_type,
                "base_url": channel.base_url,
                "rate_limit": channel.rate_limit,
                "is_paid": channel.is_paid,
                "last_updated": channel.last_updated
            })
        
        return channels_list
    
    def export_config(self) -> str:
        """导出配置为JSON字符串"""
        data = {}
        for name, channel in self.channels.items():
            data[name] = asdict(channel)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def import_config(self, config_json: str) -> bool:
        """从JSON导入配置"""
        try:
            data = json.loads(config_json)
            
            # 验证数据格式
            for name, config_data in data.items():
                if not isinstance(config_data, dict):
                    raise ValueError(f"无效的配置格式: {name}")
            
            # 清空现有配置
            self.channels.clear()
            
            # 导入新配置
            for name, config_data in data.items():
                self.channels[name] = ChannelConfig(**config_data)
            
            self.save_configs()
            logger.info(f"从JSON导入了 {len(self.channels)} 个渠道配置")
            return True
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False


# 测试函数
def test_config_manager():
    """测试配置管理器"""
    print("=" * 60)
    print("招聘配置管理器测试")
    print("=" * 60)
    
    # 初始化管理器
    manager = RecruitmentConfigManager("test_configs.json")
    
    print("\n📋 当前渠道列表:")
    channels = manager.list_channels()
    for i, channel in enumerate(channels, 1):
        status = "✅ 启用" if channel['enabled'] else "❌ 禁用"
        print(f"{i}. {channel['name']} ({status})")
        print(f"   认证: {channel['auth_type']}")
        print(f"   URL: {channel['base_url']}")
        print(f"   限制: {channel['rate_limit']}次/小时")
        print(f"   付费: {'是' if channel['is_paid'] else '否'}")
    
    print("\n🎯 可立即使用的渠道:")
    enabled_channels = manager.get_enabled_channels()
    if enabled_channels:
        for channel in enabled_channels:
            print(f"• {channel.name} - {channel.base_url}")
    else:
        print("暂无启用的渠道")
    
    print("\n🔧 测试渠道操作...")
    
    # 测试GitHub渠道状态
    print("\nGitHub渠道状态:")
    status = manager.get_channel_status("GitHub")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 测试添加新渠道
    print("\n📝 测试添加新渠道...")
    new_channel_config = {
        'name': '测试渠道',
        'enabled': True,
        'auth_type': 'api_key',
        'api_key': 'test_key_123',
        'base_url': 'https://api.example.com',
        'endpoints': {'search': '/api/search'},
        'rate_limit': 100,
        'is_paid': False
    }
    
    if manager.add_channel("测试渠道", new_channel_config):
        print("✅ 添加新渠道成功")
    else:
        print("❌ 添加新渠道失败")
    
    # 测试更新配置
    print("\n🔄 测试更新配置...")
    update_data = {'rate_limit': 200, 'enabled': False}
    if manager.update_channel_config("测试渠道", update_data):
        print("✅ 更新配置成功")
    
    # 测试移除渠道
    print("\n🗑️  测试移除渠道...")
    if manager.remove_channel("测试渠道"):
        print("✅ 移除渠道成功")
    
    # 导出配置
    print("\n📤 导出配置...")
    exported = manager.export_config()
    print(f"配置已导出 ({len(exported)} 字符)")
    
    # 清理测试文件
    if os.path.exists("test_configs.json"):
        os.remove("test_configs.json")
        print("\n🧹 已清理测试文件")
    
    print("\n" + "=" * 60)
    print("配置管理器测试完成")
    print("=" * 60)
    
    print("\n💡 使用建议:")
    print("1. GitHub渠道已配置完成，可以立即使用")
    print("2. 其他渠道需要申请API密钥后启用")
    print("3. 可以使用Web界面管理配置")
    print("4. 配置会自动保存到JSON文件")


if __name__ == "__main__":
    test_config_manager()