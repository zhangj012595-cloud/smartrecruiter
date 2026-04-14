"""
渠道系统管理器
简化版本，专注Web应用
"""

import importlib
import os
from typing import Dict, Any, List, Optional


class ChannelManager:
    """简化渠道管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.channels = {}
        self.available_channels = self._discover_channels()
    
    def _discover_channels(self) -> Dict[str, str]:
        """发现可用的渠道"""
        channels = {}
        channel_dir = os.path.dirname(__file__)
        
        # 默认包含模拟渠道
        channels['mock_linkedin'] = "channels.mock_linkedin"
        
        # 发现其他渠道
        for file in os.listdir(channel_dir):
            if file.endswith('.py') and not file.startswith('_'):
                channel_name = file[:-3]  # 移除.py
                if channel_name not in ['base', '__init__', 'mock_linkedin']:
                    channels[channel_name] = f"channels.{channel_name}"
        
        return channels
    
    def load_channel(self, channel_name: str) -> Any:
        """动态加载渠道"""
        if channel_name not in self.available_channels:
            raise ValueError(f"未知的渠道: {channel_name}")
        
        try:
            module_path = self.available_channels[channel_name]
            module = importlib.import_module(module_path)
            
            # 假设每个渠道模块都有一个get_channel函数
            if hasattr(module, 'get_channel'):
                channel = module.get_channel(self.config)
                self.channels[channel_name] = channel
                return channel
            else:
                raise AttributeError(f"渠道 {channel_name} 没有get_channel函数")
                
        except ImportError as e:
            raise ImportError(f"无法加载渠道 {channel_name}: {e}")
    
    def get_channel(self, channel_name: str) -> Any:
        """获取渠道实例"""
        if channel_name in self.channels:
            return self.channels[channel_name]
        
        return self.load_channel(channel_name)
    
    def list_channels(self) -> List[str]:
        """列出所有可用渠道"""
        return list(self.available_channels.keys())
    
    def search(self, channel_name: str, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """通过指定渠道搜索候选人"""
        channel = self.get_channel(channel_name)
        return channel.search(query, limit)
    
    def test_connection(self, channel_name: str) -> bool:
        """测试渠道连接"""
        try:
            channel = self.get_channel(channel_name)
            return channel.test_connection()
        except Exception as e:
            print(f"测试连接失败: {e}")
            return False