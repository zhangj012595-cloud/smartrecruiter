#!/usr/bin/env python3
"""
招聘网站配置Web界面
Flask应用，用于管理多种招聘网站配置
集成到SmartRecruiter项目工具集中
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from flask import Flask, render_template_string, request, jsonify, redirect, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask未安装，请运行: pip install flask")
    print("备用方案: 使用Streamlit配置界面 (app_enhanced.py)")


class RecruitmentConfigWebUI:
    """招聘网站配置Web界面"""
    
    def __init__(self, config_file: str = "config/recruitment_configs.json"):
        self.config_file = config_file
        self.app = None
        
        # 确保配置目录存在
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    def load_configs(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_configs(self, configs: Dict[str, Any]):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)
    
    def get_default_configs(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "channels": {
                "GitHub": {
                    "name": "GitHub",
                    "enabled": True,
                    "auth_type": "api_key",
                    "base_url": "https://api.github.com",
                    "rate_limit": 60,
                    "is_paid": False,
                    "endpoints": {
                        "user_search": "/search/users",
                        "rate_limit": "/rate_limit",
                        "user_details": "/users/{username}"
                    },
                    "description": "GitHub开发者搜索，完全免费",
                    "last_updated": "2026-04-16T03:00:00"
                },
                "LinkedIn": {
                    "name": "LinkedIn",
                    "enabled": True,
                    "auth_type": "cookie",
                    "base_url": "https://www.linkedin.com",
                    "rate_limit": 100,
                    "is_paid": True,
                    "endpoints": {
                        "search": "/search/results/people",
                        "profile": "/in/{username}"
                    },
                    "description": "LinkedIn职场人士搜索，需要账号认证",
                    "last_updated": "2026-04-16T03:00:00"
                },
                "BOSS直聘": {
                    "name": "BOSS直聘",
                    "enabled": False,
                    "auth_type": "api_key",
                    "base_url": "https://www.zhipin.com",
                    "rate_limit": 100,
                    "is_paid": True,
                    "endpoints": {},
                    "description": "BOSS直聘招聘网站，需要API申请",
                    "last_updated": "2026-04-16T03:00:00"
                },
                "智联招聘": {
                    "name": "智联招聘",
                    "enabled": False,
                    "auth_type": "api_key",
                    "base_url": "https://www.zhaopin.com",
                    "rate_limit": 100,
                    "is_paid": True,
                    "endpoints": {},
                    "description": "智联招聘网站，需要API申请",
                    "last_updated": "2026-04-16T03:00:00"
                },
                "脉脉": {
                    "name": "脉脉",
                    "enabled": False,
                    "auth_type": "oauth",
                    "base_url": "https://maimai.cn",
                    "rate_limit": 50,
                    "is_paid": True,
                    "endpoints": {},
                    "description": "脉脉职场社交，需要企业认证",
                    "last_updated": "2026-04-16T03:00:00",
                    "note": "已准备API申请材料"
                }
            },
            "system": {
                "version": "2.0",
                "last_updated": "2026-04-16T03:00:00",
                "total_channels": 5,
                "enabled_channels": 2
            }
        }
    
    def create_app(self):
        """创建Flask应用"""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask未安装，请运行: pip install flask")
        
        self.app = Flask(__name__, static_folder='static')
        
        # HTML模板
        index_template = '''
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SmartRecruiter - 招聘网站配置系统</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css">
            <style>
                :root {
                    --primary-color: #4361ee;
                    --secondary-color: #3a0ca3;
                    --success-color: #4cc9f0;
                    --danger-color: #f72585;
                    --warning-color: #f8961e;
                    --light-bg: #f8f9fa;
                    --dark-text: #212529;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                }
                
                .navbar-brand {
                    font-weight: 600;
                    color: var(--primary-color);
                }
                
                .card {
                    border: none;
                    border-radius: 15px;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    margin-bottom: 20px;
                }
                
                .card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 30px rgba(0,0,0,0.15);
                }
                
                .card-header {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    border-radius: 15px 15px 0 0 !important;
                    padding: 15px 20px;
                }
                
                .status-badge {
                    display: inline-block;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                }
                
                .status-enabled {
                    background-color: #d4edda;
                    color: #155724;
                }
                
                .status-disabled {
                    background-color: #f8d7da;
                    color: #721c24;
                }
                
                .channel-icon {
                    width: 40px;
                    height: 40px;
                    background: var(--primary-color);
                    color: white;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 15px;
                }
                
                .stats-card {
                    text-align: center;
                    padding: 20px;
                    border-radius: 15px;
                    color: white;
                    margin-bottom: 20px;
                }
                
                .stats-total {
                    background: linear-gradient(135deg, #4cc9f0, #4361ee);
                }
                
                .stats-enabled {
                    background: linear-gradient(135deg, #4ade80, #22c55e);
                }
                
                .stats-free {
                    background: linear-gradient(135deg, #f59e0b, #d97706);
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    border: none;
                    border-radius: 25px;
                    padding: 10px 25px;
                    font-weight: 600;
                }
                
                .btn-primary:hover {
                    background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
                }
                
                .modal-content {
                    border-radius: 15px;
                    border: none;
                }
                
                .modal-header {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    border-radius: 15px 15px 0 0;
                }
                
                .form-control:focus {
                    border-color: var(--primary-color);
                    box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.25);
                }
                
                .badge-free {
                    background-color: var(--success-color);
                }
                
                .badge-paid {
                    background-color: var(--warning-color);
                }
                
                .search-box {
                    background: white;
                    border-radius: 25px;
                    padding: 10px 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                
                .footer {
                    text-align: center;
                    padding: 20px;
                    color: #6c757d;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <!-- 导航栏 -->
            <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
                <div class="container">
                    <a class="navbar-brand" href="#">
                        <i class="bi bi-person-badge me-2"></i>
                        SmartRecruiter v2.0
                    </a>
                    <div class="navbar-nav ms-auto">
                        <span class="nav-item me-3">
                            <small class="text-muted">招聘配置系统</small>
                        </span>
                        <a href="/smartrecruiter" class="btn btn-sm btn-outline-primary" target="_blank">
                            <i class="bi bi-arrow-right-circle me-1"></i> 返回主应用
                        </a>
                    </div>
                </div>
            </nav>
            
            <!-- 主要内容 -->
            <div class="container py-4">
                <!-- 头部信息 -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-body">
                                <div class="row align-items-center">
                                    <div class="col-md-8">
                                        <h1 class="h3 mb-2">招聘网站配置管理系统</h1>
                                        <p class="text-muted mb-0">
                                            管理多种招聘渠道配置，支持GitHub、LinkedIn、BOSS直聘、智联招聘、脉脉等
                                        </p>
                                    </div>
                                    <div class="col-md-4 text-end">
                                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addChannelModal">
                                            <i class="bi bi-plus-circle me-1"></i> 添加新渠道
                                        </button>
                                        <a href="/export" class="btn btn-outline-primary ms-2">
                                            <i class="bi bi-download me-1"></i> 导出配置
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 统计卡片 -->
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stats-card stats-total">
                            <i class="bi bi-grid-3x3-gap" style="font-size: 2rem;"></i>
                            <h3 class="mt-2 mb-0">{{ stats.total_channels }}</h3>
                            <p class="mb-0">总渠道数</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stats-card stats-enabled">
                            <i class="bi bi-check-circle" style="font-size: 2rem;"></i>
                            <h3 class="mt-2 mb-0">{{ stats.enabled_channels }}</h3>
                            <p class="mb-0">已启用渠道</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stats-card stats-free">
                            <i class="bi bi-coin" style="font-size: 2rem;"></i>
                            <h3 class="mt-2 mb-0">{{ stats.free_channels }}</h3>
                            <p class="mb-0">免费渠道</p>
                        </div>
                    </div>
                </div>
                
                <!-- 搜索框 -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="search-box">
                            <div class="input-group">
                                <span class="input-group-text bg-transparent border-0">
                                    <i class="bi bi-search"></i>
                                </span>
                                <input type="text" class="form-control border-0" id="searchInput" 
                                       placeholder="搜索渠道名称或描述..." 
                                       onkeyup="filterChannels()">
                                <button class="btn btn-link text-muted" onclick="clearSearch()">
                                    <i class="bi bi-x-circle"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 渠道列表 -->
                <div id="channelsList">
                    {% for channel in channels %}
                    <div class="channel-card" data-channel-name="{{ channel.name|lower }}" 
                         data-channel-desc="{{ channel.description|lower }}">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <div class="d-flex align-items-center">
                                    <div class="channel-icon">
                                        <i class="bi bi-{% if channel.name == 'GitHub' %}github{% elif channel.name == 'LinkedIn' %}linkedin{% else %}globe{% endif %}"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0">{{ channel.name }}</h5>
                                        <small class="text-white-50">{{ channel.description }}</small>
                                    </div>
                                </div>
                                <div>
                                    <span class="status-badge {% if channel.enabled %}status-enabled{% else %}status-disabled{% endif %} me-2">
                                        {% if channel.enabled %}已启用{% else %}已禁用{% endif %}
                                    </span>
                                    <span class="badge {% if channel.is_paid %}badge-paid{% else %}badge-free{% endif %}">
                                        {% if channel.is_paid %}付费{% else %}免费{% endif %}
                                    </span>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <p class="mb-2">
                                            <i class="bi bi-link-45deg me-2"></i>
                                            <strong>基础URL:</strong> {{ channel.base_url }}
                                        </p>
                                        <p class="mb-2">
                                            <i class="bi bi-shield-lock me-2"></i>
                                            <strong>认证类型:</strong> {{ channel.auth_type }}
                                        </p>
                                        <p class="mb-2">
                                            <i class="bi bi-speedometer2 me-2"></i>
                                            <strong>API限制:</strong> {{ channel.rate_limit }} 次/小时
                                        </p>
                                    </div>
                                    <div class="col-md-6">
                                        <p class="mb-2">
                                            <i class="bi bi-calendar-event me-2"></i>
                                            <strong>最后更新:</strong> {{ channel.last_updated }}
                                        </p>
                                        {% if channel.note %}
                                        <p class="mb-2">
                                            <i class="bi bi-info-circle me-2"></i>
                                            <strong>备注:</strong> {{ channel.note }}
                                        </p>
                                        {% endif %}
                                        <div class="mt-3">
                                            <button class="btn btn-sm btn-outline-primary me-2" 
                                                    onclick="toggleChannel('{{ channel.name }}', {{ channel.enabled|lower }})">
                                                <i class="bi bi-power me-1"></i>
                                                {% if channel.enabled %}禁用{% else %}启用{% endif %}
                                            </button>
                                            <button class="btn btn-sm btn-outline-secondary me-2" 
                                                    data-bs-toggle="modal" 
                                                    data-bs-target="#editChannelModal"
                                                    onclick="editChannel('{{ channel.name }}')">
                                                <i class="bi bi-pencil me-1"></i> 编辑
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" 
                                                    onclick="deleteChannel('{{ channel.name }}')">
                                                <i class="bi bi-trash me-1"></i> 删除
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                <!-- 空状态 -->
                <div id="noResults" class="text-center py-5" style="display: none;">
                    <i class="bi bi-search" style="font-size: 3rem; color: #6c757d;"></i>
                    <h4 class="mt-3">未找到匹配的渠道</h4>
                    <p class="text-muted">尝试使用不同的关键词搜索</p>
                </div>
                
                <!-- 系统信息 -->
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6 class="mb-3"><i class="bi bi-info-circle me-2"></i> 系统信息</h6>
                                        <p class="mb-2"><strong>版本:</strong> {{ system.version }}</p>
                                        <p class="mb-2"><strong>最后更新:</strong> {{ system.last_updated }}</p>
                                        <p class="mb-2"><strong>配置文件:</strong> {{ config_file }}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="mb-3"><i class="bi bi-lightbulb me-2"></i> 使用提示</h6>
                                        <ul class="mb-0">
                                            <li>GitHub渠道完全免费，立即可用</li>
                                            <li>LinkedIn需要账号认证才能使用</li>
                                            <li>其他渠道需要申请API密钥</li>
                                            <li>配置会自动保存到项目文件中</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 页脚 -->
            <div class="footer">
                <p class="mb-0">
                    <i class="bi bi-code-slash me-1"></i>
                    SmartRecruiter v2.0 - 招聘网站配置系统
                    <br>
                    <small>最后更新: 2026-04-16 | 项目地址: github.com/zhangj012595-cloud/smartrecruiter</small>
                </p>
            </div>
            
            <!-- 添加渠道模态框 -->
            <div class="modal fade" id="addChannelModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"><i class="bi bi-plus-circle me-2"></i>添加新渠道</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addChannelForm">
                                <div class="mb-3">
                                    <label class="form-label">渠道名称</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">基础URL</label>
                                    <input type="url" class="form-control" name="base_url" required>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">认证类型</label>
                                        <select class="form-select" name="auth_type">
                                            <option value="api_key">API密钥</option>
                                            <option value="oauth">OAuth认证</option>
                                            <option value="cookie">Cookie认证</option>
                                            <option value="none">无需认证</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">API限制 (次/小时)</label>
                                        <input type="number" class="form-control" name="rate_limit" value="60" min="1">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">描述</label>
                                    <textarea class="form-control" name="description" rows="2"></textarea>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" name="enabled" id="enabledCheck" checked>
                                    <label class="form-check-label" for="enabledCheck">启用渠道</label>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" name="is_paid" id="paidCheck">
                                    <label class="form-check-label" for="paidCheck">付费服务</label>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="saveNewChannel()">保存</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 编辑渠道模态框 -->
            <div class="modal fade" id="editChannelModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"><i class="bi bi-pencil me-2"></i>编辑渠道</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="editChannelForm">
                                <input type="hidden" name="original_name">
                                <div class="mb-3">
                                    <label class="form-label">渠道名称</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">基础URL</label>
                                    <input type="url" class="form-control" name="base_url" required>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">API限制 (次/小时)</label>
                                        <input type="number" class="form-control" name="rate_limit" min="1">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">最后更新</label>
                                        <input type="text" class="form-control" name="last_updated" readonly>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">描述</label>
                                    <textarea class="form-control" name="description" rows="2"></textarea>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" name="enabled" id="editEnabledCheck">
                                    <label class="form-check-label" for="editEnabledCheck">启用渠道</label>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="updateChannel()">更新</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- JavaScript -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // 搜索过滤
                function filterChannels() {
                    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                    const channelCards = document.querySelectorAll('.channel-card');
                    let visibleCount = 0;
                    
                    channelCards.forEach(card => {
                        const channelName = card.dataset.channelName;
                        const channelDesc = card.dataset.channelDesc;
                        
                        if (channelName.includes(searchTerm) || channelDesc.includes(searchTerm)) {
                            card.style.display = 'block';
                            visibleCount++;
                        } else {
                            card.style.display = 'none';
                        }
                    });
                    
                    // 显示/隐藏空状态
                    const noResults = document.getElementById('noResults');
                    if (visibleCount === 0 && searchTerm !== '') {
                        noResults.style.display = 'block';
                    } else {
                        noResults.style.display = 'none';
                    }
                }
                
                // 清空搜索
                function clearSearch() {
                    document.getElementById('searchInput').value = '';
                    filterChannels();
                }
                
                // 切换渠道状态
                function toggleChannel(channelName, currentStatus) {
                    if (confirm(`确定要${currentStatus ? '禁用' : '启用'} ${channelName} 渠道吗？`)) {
                        fetch(`/toggle/${channelName}`, {
                            method: 'POST'
                        }).then(response => {
                            if (response.ok) {
                                location.reload();
                            } else {
                                alert('操作失败');
                            }
                        });
                    }
                }
                
                // 编辑渠道
                function editChannel(channelName) {
                    fetch(`/channel/${channelName}`)
                        .then(response => response.json())
                        .then(channel => {
                            const form = document.getElementById('editChannelForm');
                            form.original_name.value = channel.name;
                            form.name.value = channel.name;
                            form.base_url.value = channel.base_url;
                            form.rate_limit.value = channel.rate_limit;
                            form.last_updated.value = new Date().toISOString().split('T')[0];
                            form.description.value = channel.description || '';
                            form.enabled.checked = channel.enabled;
                        });
                }
                
                // 更新渠道
                function updateChannel() {
                    const form = document.getElementById('editChannelForm');
                    const formData = new FormData(form);
                    const data = Object.fromEntries(formData);
                    
                    fetch(`/update/${data.original_name}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    }).then(response => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            alert('更新失败');
                        }
                    });
                }
                
                // 保存新渠道
                function saveNewChannel() {
                    const form = document.getElementById('addChannelForm');
                    const formData = new FormData(form);
                    const data = Object.fromEntries(formData);
                    data.last_updated = new Date().toISOString();
                    
                    fetch('/add', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    }).then(response => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            alert('添加失败');
                        }
                    });
                }
                
                // 删除渠道
                function deleteChannel(channelName) {
                    if (confirm(`确定要删除 ${channelName} 渠道吗？此操作不可撤销。`)) {
                        fetch(`/delete/${channelName}`, {
                            method: 'DELETE'
                        }).then(response => {
                            if (response.ok) {
                                location.reload();
                            } else {
                                alert('删除失败');
                            }
                        });
                    }
                }
                
                // 页面加载时过滤空渠道
                document.addEventListener('DOMContentLoaded', function() {
                    filterChannels();
                });
            </script>
        </body>
        </html>
        '''
        
        @self.app.route('/')
        def index():
            """主页"""
            configs = self.load_configs()
            
            # 如果配置文件为空，使用默认配置
            if not configs:
                configs = self.get_default_configs()
                self.save_configs(configs)
            
            channels = list(configs.get('channels', {}).values())
            
            # 计算统计信息
            total_channels = len(channels)
            enabled_channels = sum(1 for c in channels if c.get('enabled', False))
            free_channels = sum(1 for c in channels if not c.get('is_paid', False))
            
            stats = {
                'total_channels': total_channels,
                'enabled_channels': enabled_channels,
                'free_channels': free_channels
            }
            
            system_info = configs.get('system', {})
            
            return render_template_string(index_template,
                                         channels=channels,
                                         stats=stats,
                                         system=system_info,
                                         config_file=self.config_file)
        
        @self.app.route('/channel/<channel_name>')
        def get_channel(channel_name):
            """获取单个渠道信息"""
            configs = self.load_configs()
            channel = configs.get('channels', {}).get(channel_name)
            
            if channel:
                return jsonify(channel)
            else:
                return jsonify({'error': 'Channel not found'}), 404
        
        @self.app.route('/toggle/<channel_name>', methods=['POST'])
        def toggle_channel(channel_name):
            """切换渠道状态"""
            configs = self.load_configs()
            
            if channel_name in configs.get('channels', {}):
                channel = configs['channels'][channel_name]
                channel['enabled'] = not channel.get('enabled', False)
                channel['last_updated'] = "2026-04-16T03:00:00"  # 更新时间
                
                # 更新系统信息
                enabled_channels = sum(1 for c in configs['channels'].values() if c.get('enabled', False))
                configs['system']['enabled_channels'] = enabled_channels
                configs['system']['last_updated'] = "2026-04-16T03:00:00"
                
                self.save_configs(configs)
                return jsonify({'success': True, 'enabled': channel['enabled']})
            
            return jsonify({'error': 'Channel not found'}), 404
        
        @self.app.route('/add', methods=['POST'])
        def add_channel():
            """添加新渠道"""
            data = request.json
            configs = self.load_configs()
            
            channel_name = data.get('name')
            if not channel_name:
                return jsonify({'error': 'Channel name required'}), 400
            
            # 创建新渠道
            new_channel = {
                'name': channel_name,
                'enabled': data.get('enabled', True),
                'auth_type': data.get('auth_type', 'api_key'),
                'base_url': data.get('base_url', ''),
                'rate_limit': int(data.get('rate_limit', 60)),
                'is_paid': data.get('is_paid', False),
                'endpoints': {},
                'description': data.get('description', ''),
                'last_updated': data.get('last_updated', '2026-04-16T03:00:00')
            }
            
            configs['channels'][channel_name] = new_channel
            
            # 更新系统信息
            total_channels = len(configs['channels'])
            enabled_channels = sum(1 for c in configs['channels'].values() if c.get('enabled', False))
            
            configs['system']['total_channels'] = total_channels
            configs['system']['enabled_channels'] = enabled_channels
            configs['system']['last_updated'] = "2026-04-16T03:00:00"
            
            self.save_configs(configs)
            return jsonify({'success': True})
        
        @self.app.route('/update/<channel_name>', methods=['POST'])
        def update_channel(channel_name):
            """更新渠道"""
            data = request.json
            configs = self.load_configs()
            
            if channel_name in configs.get('channels', {}):
                channel = configs['channels'][channel_name]
                
                # 更新字段
                channel['name'] = data.get('name', channel['name'])
                channel['base_url'] = data.get('base_url', channel['base_url'])
                channel['rate_limit'] = int(data.get('rate_limit', channel['rate_limit']))
                channel['description'] = data.get('description', channel.get('description', ''))
                channel['enabled'] = data.get('enabled', channel['enabled'])
                channel['last_updated'] = "2026-04-16T03:00:00"
                
                # 如果名称改变，需要移动条目
                new_name = data.get('name')
                if new_name and new_name != channel_name:
                    configs['channels'][new_name] = channel
                    del configs['channels'][channel_name]
                
                self.save_configs(configs)
                return jsonify({'success': True})
            
            return jsonify({'error': 'Channel not found'}), 404
        
        @self.app.route('/delete/<channel_name>', methods=['DELETE'])
        def delete_channel(channel_name):
            """删除渠道"""
            configs = self.load_configs()
            
            if channel_name in configs.get('channels', {}):
                del configs['channels'][channel_name]
                
                # 更新系统信息
                total_channels = len(configs['channels'])
                enabled_channels = sum(1 for c in configs['channels'].values() if c.get('enabled', False))
                
                configs['system']['total_channels'] = total_channels
                configs['system']['enabled_channels'] = enabled_channels
                configs['system']['last_updated'] = "2026-04-16T03:00:00"
                
                self.save_configs(configs)
                return jsonify({'success': True})
            
            return jsonify({'error': 'Channel not found'}), 404
        
        @self.app.route('/export')
        def export_config():
            """导出配置"""
            configs = self.load_configs()
            return jsonify(configs)
        
        @self.app.route('/smartrecruiter')
        def redirect_to_smartrecruiter():
            """重定向到SmartRecruiter主应用"""
            return redirect('http://localhost:8501', code=302)
        
        return self.app
    
    def run(self, host='0.0.0.0', port=5000, debug=True):
        """运行Web应用"""
        if not FLASK_AVAILABLE:
            print("❌ Flask未安装，无法运行Web界面")
            print("请安装Flask: pip install flask")
            print("或使用Streamlit配置界面: streamlit run app_enhanced.py")
            return
        
        app = self.create_app()
        print(f"🚀 招聘配置Web界面启动中...")
        print(f"🌐 访问地址: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
        print(f"📁 配置文件: {self.config_file}")
        print(f"🔗 主应用: http://localhost:8501")
        print("📌 按 Ctrl+C 停止服务")
        
        app.run(host=host, port=port, debug=debug)


def main():
    """主函数"""
    ui = RecruitmentConfigWebUI()
    
    # 检查依赖
    if not FLASK_AVAILABLE:
        print("""
        ⚠️ 依赖缺失警告
        =============
        招聘配置Web界面需要Flask依赖。
        
        安装命令:
        pip install flask
        
        或者使用备用方案:
        1. 运行Streamlit配置界面: streamlit run app_enhanced.py
        2. 在【系统配置】标签页管理渠道
        
        立即安装Flask? (y/n): """)
        
        choice = input().strip().lower()
        if choice == 'y':
            import subprocess
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=True)
                print("✅ Flask安装成功，正在重新启动...")
                
                # 重新导入
                from flask import Flask, render_template_string, request, jsonify, redirect
                global FLASK_AVAILABLE
                FLASK_AVAILABLE = True
                
                # 重新运行
                ui.run()
            except Exception as e:
                print(f"❌ 安装失败: {e}")
                print("\n请手动安装: pip install flask")
        else:
            print("\n使用Streamlit配置界面:")
            print("streamlit run app_enhanced.py")
    else:
        ui.run()


if __name__ == "__main__":
    main()