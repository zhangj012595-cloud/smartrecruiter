# SmartRecruiter - 智能招聘匹配系统

## 🎯 项目简介
SmartRecruiter是一个基于Agent-Reach架构设计的智能招聘匹配系统，帮助公司快速找到合适的求职者。

## 🚀 Phase 1: MVP版本
- **目标**：快速可用的Web应用
- **核心功能**：LinkedIn搜索 + 简单关键词匹配
- **技术栈**：Streamlit + Python

## 📋 核心功能

### 1. **多渠道候选人搜索**（v2.0新增）
- **GitHub开发者搜索**：基于开源项目质量和社区影响力
- **LinkedIn职场人士搜索**：基于工作经验和技能匹配
- **统一搜索界面**：支持多种渠道的统一查询和展示

### 2. **智能渠道配置管理**（v2.0新增）
- 多招聘渠道集中管理（GitHub、LinkedIn、BOSS直聘、智联招聘、脉脉等）
- 渠道启用/禁用和配置编辑
- 支持API密钥管理和状态监控

### 3. 匹配算法
- 关键词匹配度计算
- 技能匹配度评分
- 多渠道候选人统一评分系统
- 经验匹配度评估

### 3. 结果展示
- 候选人列表显示
- 匹配度分数展示
- 详细信息查看

## 🧪 快速测试（无需LinkedIn账号）

### 基本流程测试
```bash
# 克隆仓库
git clone https://github.com/zhangj012595-cloud/smartrecruiter.git
cd smartrecruiter

# 运行自动测试
python3 test_basic_flow.py
```

测试将验证：
- ✅ 渠道管理器功能
- ✅ 关键词提取功能  
- ✅ 匹配算法流程
- ✅ 配置文件加载
- ✅ 完整工作流程

## 🔧 完整安装使用

### 环境要求
- Python 3.10+
- Chrome浏览器（用于真实LinkedIn搜索，测试阶段可选）

### 快速启动（推荐）
```bash
# 克隆仓库
git clone https://github.com/zhangj012595-cloud/smartrecruiter.git
cd smartrecruiter

# 使用启动脚本（自动创建虚拟环境、安装依赖、运行测试）
chmod +x run.sh
./run.sh
```

### 手动安装
```bash
# 克隆仓库
git clone https://github.com/zhangj012595-cloud/smartrecruiter.git
cd smartrecruiter

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 复制配置文件
cp config/example_config.yaml config/config.yaml

# 运行测试
python3 test_basic_flow.py

# 启动应用
streamlit run app.py
```

### 配置文件
复制 `config/example_config.yaml` 为 `config/config.yaml` 并填写：
```yaml
linkedin:
  username: "your_linkedin_email"
  password: "your_linkedin_password"
  # 或者使用cookie文件
  cookie_path: "path/to/cookies.json"

search:
  default_limit: 50
  locations: ["北京", "上海", "深圳", "杭州"]
  experience_levels: ["Entry", "Mid", "Senior"]
```

## 🎨 界面功能

### 主界面
1. **职位描述输入**：粘贴职位描述文本
2. **搜索条件设置**：地点、经验、技能关键词
3. **搜索按钮**：开始搜索LinkedIn候选人
4. **结果展示**：匹配度排序的候选人列表

### 候选人详情
- 基本信息：姓名、头像、职位、公司
- 技能匹配：匹配的技能列表
- 经验匹配：工作经验匹配度
- 完整个人资料链接

## 🔒 隐私与安全
- 所有数据本地处理，不上传服务器
- 不存储用户密码，仅用于登录会话
- 可配置使用cookie文件避免重复登录

## 📊 匹配算法

### 第一阶段简单匹配
```python
总匹配度 = 技能匹配度 * 0.5 + 经验匹配度 * 0.3 + 地点匹配度 * 0.2
```

### 技能匹配
- 从职位描述提取技能关键词
- 与候选人技能列表对比
- 计算匹配百分比

### 经验匹配
- 解析经验要求（如"3年经验"）
- 与候选人工作经验对比
- 分级评分

## 🔍 技术实现

### LinkedIn渠道
- 使用Selenium自动化浏览器
- 模拟用户搜索操作
- 提取搜索结果页面信息

### 关键词提取
- 正则表达式提取技能关键词
- NLP技术提取经验要求
- 地名识别和匹配

### Web界面
- Streamlit快速开发
- 响应式布局
- 实时搜索和筛选

## 🚧 开发计划

### ✅ Phase 1 已完成 (MVP版本)
- [x] **项目基础架构**：完整项目结构
- [x] **GitHub仓库创建**：代码已推送至GitHub
- [x] **LinkedIn渠道实现**：真实渠道 + 模拟测试渠道
- [x] **匹配算法**：简化测试版本（真实算法在Phase 2）
- [x] **Streamlit界面**：完整的Web应用界面
- [x] **基础测试**：自动化测试脚本，100%通过
- [x] **配置文件系统**：完整的YAML配置管理
- [x] **文档和指南**：完整的README和启动脚本

### 🔄 Phase 1 核心交付物
1. **可运行的Web应用**：`streamlit run app.py`
2. **测试验证系统**：`python3 test_basic_flow.py`
3. **模拟数据支持**：无需真实LinkedIn账号即可测试
4. **可扩展架构**：准备接入Phase 2的真实数据源

### Phase 2 (下一步)
- [ ] **真实LinkedIn集成**：基于cookie的自动化搜索
- [ ] **高级匹配算法**：基于真实数据的智能匹配
- [ ] **更多数据源**：GitHub、招聘网站等
- [ ] **本地简历解析**：PDF/DOCX简历处理
- [ ] **性能优化**：缓存、异步处理
- [ ] **单元测试覆盖**：完整的测试套件

### Phase 3 (未来)
- [ ] **文化契合度分析**
- [ ] **发展潜力评估**
- [ ] **面试准备助手**
- [ ] **API服务**
- [ ] **多用户支持**

### Phase 2 (下一步)
- [ ] 更多数据源（GitHub、招聘网站）
- [ ] 本地简历解析
- [ ] 高级匹配算法
- [ ] 数据库集成

### Phase 3 (未来)
- [ ] 文化契合度分析
- [ ] 发展潜力评估
- [ ] API服务
- [ ] 多用户支持

## 🤝 贡献指南
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

## 📝 许可证
MIT License

## 📞 联系
- GitHub: [zhangj012595-cloud](https://github.com/zhangj012595-cloud)
- 项目地址: [smartrecruiter](https://github.com/zhangj012595-cloud/smartrecruiter)

## 🙏 致谢
- 感谢Agent-Reach项目提供架构灵感
- 感谢所有开源社区的工具和库
- 感谢测试用户的反馈和建议