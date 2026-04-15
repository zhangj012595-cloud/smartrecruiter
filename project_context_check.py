#!/usr/bin/env python3
"""
项目上下文检查工具
用于验证当前工作目录是否正确，避免在错误位置创建新项目
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
from typing import Dict, List, Optional, Tuple


class ProjectContextChecker:
    """项目上下文检查器"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.path.expanduser("~/.openclaw/workspace")
        self.context_file = os.path.join(self.workspace_root, "project_context.json")
        self.checklist_file = os.path.join(self.workspace_root, "PROJECT_CONTEXT_CHECKLIST.md")
        
    def check_current_context(self) -> Dict:
        """检查当前项目上下文"""
        print("=" * 70)
        print("🔍 项目上下文检查")
        print("=" * 70)
        
        current_dir = os.getcwd()
        relative_path = os.path.relpath(current_dir, self.workspace_root)
        
        context = {
            'timestamp': datetime.now().isoformat(),
            'current_directory': current_dir,
            'relative_to_workspace': relative_path,
            'is_in_workspace': current_dir.startswith(self.workspace_root),
            'is_root_workspace': current_dir == self.workspace_root,
            'potential_projects': [],
            'recommendations': []
        }
        
        # 检查当前目录内容
        print(f"\n📂 当前目录: {current_dir}")
        print(f"   相对于工作空间: {relative_path}")
        
        # 扫描潜在项目
        context['potential_projects'] = self.scan_potential_projects()
        
        # 生成建议
        context['recommendations'] = self.generate_recommendations(context)
        
        return context
    
    def scan_potential_projects(self) -> List[Dict]:
        """扫描潜在项目目录"""
        projects = []
        
        # 在当前目录及其父目录中查找项目迹象
        for dir_path in [os.getcwd()] + list(Path(os.getcwd()).parents):
            if dir_path == self.workspace_root:
                break
            
            # 检查常见项目指标
            project_indicators = self.check_project_indicators(dir_path)
            if project_indicators['is_project']:
                projects.append({
                    'path': dir_path,
                    'name': os.path.basename(dir_path),
                    'indicators': project_indicators,
                    'last_modified': self.get_last_modified(dir_path)
                })
        
        return sorted(projects, key=lambda x: x['last_modified'], reverse=True)
    
    def check_project_indicators(self, dir_path: str) -> Dict:
        """检查项目指标"""
        indicators = {
            'is_project': False,
            'has_git': False,
            'has_requirements': False,
            'has_readme': False,
            'has_source_code': False,
            'has_config': False,
            'file_count': 0,
            'project_type': 'unknown'
        }
        
        if not os.path.isdir(dir_path):
            return indicators
        
        try:
            files = os.listdir(dir_path)
            indicators['file_count'] = len(files)
            
            # 检查常见项目文件
            project_files = {
                '.git': 'has_git',
                'requirements.txt': 'has_requirements',
                'requirements-dev.txt': 'has_requirements',
                'pyproject.toml': 'has_requirements',
                'README.md': 'has_readme',
                'README.txt': 'has_readme',
                'setup.py': 'has_source_code',
                'package.json': 'has_source_code',
                'config': 'has_config',
                'src': 'has_source_code',
                'app.py': 'has_source_code',
                'main.py': 'has_source_code',
                'index.js': 'has_source_code',
                'index.py': 'has_source_code'
            }
            
            for file, indicator in project_files.items():
                if os.path.exists(os.path.join(dir_path, file)):
                    indicators[indicator] = True
            
            # 确定项目类型
            try:
                indicators['project_type'] = self.detect_project_type(dir_path, indicators)
            except:
                indicators['project_type'] = 'unknown'
            
            # 判断是否为项目
            indicators['is_project'] = (
                indicators['has_git'] or 
                indicators['has_requirements'] or 
                indicators['has_source_code'] or
                (indicators['file_count'] > 5 and indicators['has_readme'])
            )
            
        except Exception as e:
            print(f"检查目录失败 {dir_path}: {e}")
        
        return indicators
    
    def detect_project_type(self, dir_path: str, indicators: Dict) -> str:
        """检测项目类型"""
        if indicators['has_git']:
            try:
                # 检查Git远程仓库
                result = subprocess.run(
                    ['git', '-C', dir_path, 'remote', '-v'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if 'github.com' in result.stdout:
                    return 'github-project'
                elif 'gitlab.com' in result.stdout:
                    return 'gitlab-project'
                return 'git-project'
            except:
                pass
        
        # 基于文件判断
        if os.path.exists(os.path.join(dir_path, 'requirements.txt')):
            return 'python-project'
        elif os.path.exists(os.path.join(dir_path, 'package.json')):
            return 'nodejs-project'
        elif os.path.exists(os.path.join(dir_path, 'Cargo.toml')):
            return 'rust-project'
        elif os.path.exists(os.path.join(dir_path, 'go.mod')):
            return 'go-project'
        
        return 'unknown'
    
    def get_last_modified(self, dir_path: str) -> str:
        """获取最后修改时间"""
        try:
            # 获取目录中最新文件的修改时间
            latest_time = 0
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        latest_time = max(latest_time, mtime)
                    except:
                        continue
            
            if latest_time > 0:
                return datetime.fromtimestamp(latest_time).isoformat()
        except:
            pass
        
        return datetime.now().isoformat()
    
    def generate_recommendations(self, context: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        current_dir = context['current_directory']
        
        # 情况1：在工作空间根目录
        if context['is_root_workspace']:
            projects = context['potential_projects']
            if projects:
                recent_project = projects[0]
                recommendations.append(
                    f"⚠️  你在工作空间根目录。建议切换到最近的项目: "
                    f"{recent_project['name']} ({recent_project['path']})"
                )
                recommendations.append(
                    f"   命令: cd {recent_project['path']}"
                )
            else:
                recommendations.append(
                    "📁 你在工作空间根目录。如果没有特定项目，可以在这里工作。"
                )
        
        # 情况2：在项目目录中
        elif context['potential_projects'] and context['potential_projects'][0]['path'] == current_dir:
            project = context['potential_projects'][0]
            recommendations.append(
                f"✅ 你在项目目录中: {project['name']}"
            )
            
            # 显示项目状态
            if project['indicators']['has_git']:
                recommendations.append("   📦 Git仓库: 已初始化")
            if project['indicators']['has_requirements']:
                recommendations.append("   📋 依赖管理: 已配置")
            if project['indicators']['has_readme']:
                recommendations.append("   📖 文档: README存在")
        
        # 情况3：在非项目目录中
        else:
            recommendations.append(
                f"❓ 当前目录可能不是项目目录: {context['relative_to_workspace']}"
            )
            
            # 建议切换到项目目录
            if context['potential_projects']:
                for project in context['potential_projects'][:3]:
                    recommendations.append(
                        f"   备选项目: {project['name']} ({project['path']})"
                    )
        
        # 通用建议
        if not os.path.exists(self.checklist_file):
            recommendations.append(
                "📝 创建项目上下文检查清单: PROJECT_CONTEXT_CHECKLIST.md"
            )
        
        return recommendations
    
    def save_context(self, context: Dict):
        """保存上下文到文件"""
        try:
            # 加载现有上下文
            existing_context = {}
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    existing_context = json.load(f)
            
            # 更新上下文
            existing_context['last_check'] = context
            existing_context['check_history'] = existing_context.get('check_history', [])
            existing_context['check_history'].append({
                'timestamp': context['timestamp'],
                'directory': context['current_directory'],
                'recommendations': context['recommendations']
            })
            
            # 限制历史记录长度
            if len(existing_context['check_history']) > 50:
                existing_context['check_history'] = existing_context['check_history'][-50:]
            
            # 保存
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(existing_context, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 上下文已保存到: {self.context_file}")
            
        except Exception as e:
            print(f"❌ 保存上下文失败: {e}")
    
    def print_summary(self, context: Dict):
        """打印检查摘要"""
        print("\n" + "=" * 70)
        print("📊 检查摘要")
        print("=" * 70)
        
        # 当前状态
        print(f"\n📍 当前位置: {context['relative_to_workspace']}")
        
        if context['is_root_workspace']:
            print("   ⚠️  状态: 工作空间根目录 (容易创建新项目)")
        elif context['potential_projects'] and context['potential_projects'][0]['path'] == os.getcwd():
            print(f"   ✅ 状态: 项目目录 ({context['potential_projects'][0]['name']})")
        else:
            print("   ❓ 状态: 非项目目录")
        
        # 发现的项目
        if context['potential_projects']:
            print(f"\n📁 发现 {len(context['potential_projects'])} 个潜在项目:")
            for i, project in enumerate(context['potential_projects'][:5], 1):
                print(f"   {i}. {project['name']}")
                print(f"      路径: {project['path']}")
                print(f"      类型: {project['project_type']}")
                print(f"      最后修改: {project['last_modified'][:10]}")
                
                # 显示关键指标
                indicators = []
                if project['indicators'].get('has_git'):
                    indicators.append("Git")
                if project['indicators'].get('has_requirements'):
                    indicators.append("依赖文件")
                if project['indicators'].get('has_readme'):
                    indicators.append("文档")
                if project['indicators'].get('has_source_code'):
                    indicators.append("源代码")
                
                if indicators:
                    print(f"      特征: {', '.join(indicators)}")
                print()
        
        # 建议
        if context['recommendations']:
            print("💡 建议:")
            for recommendation in context['recommendations']:
                print(f"   • {recommendation}")
        
        print("\n" + "=" * 70)
        
        # 关键提醒
        if context['is_root_workspace']:
            print("🚨 重要提醒: 你在工作空间根目录，容易错误创建新项目！")
            print("   请确保你在正确的项目目录中工作。")
            print("   使用 'cd 项目路径' 切换到项目目录。")
        elif not context['potential_projects']:
            print("ℹ️  提示: 未发现明显项目结构，请确认工作目录。")
        
        print("=" * 70)
    
    def create_checklist(self):
        """创建检查清单文件"""
        checklist_content = """# PROJECT_CONTEXT_CHECKLIST.md - 项目上下文检查清单

## 🎯 目的
避免在错误位置创建新项目，确保始终在正确的项目上下文中工作。

## 📋 检查清单

### 启动新会话时
1. **📍 检查当前目录**
   ```bash
   pwd  # 查看当前目录
   ls -la  # 查看目录内容
   ```

2. **🔍 识别项目迹象**
   - 检查Git仓库: `.git/` 目录
   - 检查依赖文件: `requirements.txt`, `package.json`, `pyproject.toml`
   - 检查项目文档: `README.md`, `docs/`
   - 检查源代码: `src/`, `app/`, `main.py`

3. **📊 评估项目状态**
   - 最近修改时间
   - 文件数量和类型
   - 项目活跃度

4. **🤔 确认用户意图**
   - 用户是否提到特定项目?
   - 对话历史中是否有项目线索?
   - 用户是否希望继续现有项目?

### 发现问题的处理

#### 情况A: 在工作空间根目录
**症状**: `pwd` 显示为工作空间根目录
**风险**: 容易错误创建新项目
**行动**:
1. 扫描子目录查找项目
2. 询问用户是否继续特定项目
3. 建议切换到项目目录

#### 情况B: 在非项目目录中
**症状**: 没有项目迹象 (无Git、无依赖文件、无文档)
**风险**: 可能不是正确的工作目录
**行动**:
1. 检查父目录是否有项目
2. 询问用户是否创建新项目
3. 确认工作目录正确性

#### 情况C: 在项目目录中
**症状**: 有明显的项目结构
**行动**:
1. ✅ 确认项目上下文正确
2. 检查项目状态 (Git状态、最近修改)
3. 继续在现有项目中工作

## 🔧 工具使用

### 自动检查
```bash
# 运行项目上下文检查
python project_context_check.py
```

### 手动检查命令
```bash
# 查看当前位置
pwd
ls -la

# 检查Git状态
git status 2>/dev/null || echo "Not a git repository"

# 检查项目文件
test -f requirements.txt && echo "Python project"
test -f package.json && echo "Node.js project"
test -f Cargo.toml && echo "Rust project"
```

## 📝 记录与学习

### 记录检查结果
每次检查后更新:
- `project_context.json`: 自动记录检查历史
- `memory/YYYY-MM-DD.md`: 记录重要决策

### 从错误中学习
如果发现错误的工作目录:
1. 记录错误模式
2. 分析根本原因
3. 更新检查清单
4. 改进识别算法

## 🚀 最佳实践

### 开发前
1. 运行项目上下文检查
2. 确认工作目录正确
3. 查看最近的项目状态

### 开发中
1. 定期检查项目上下文
2. 避免切换到其他目录
3. 保持项目状态一致

### 开发后
1. 记录工作成果
2. 更新项目状态
3. 准备下次继续

## 📞 紧急处理

### 如果在错误位置开始工作
1. **立即停止**: 不要继续在错误位置开发
2. **识别正确位置**: 找到正确的项目目录
3. **迁移工作成果**: 将文件移动到正确位置
4. **记录教训**: 更新检查清单避免重复

### 如果项目混淆
1. **澄清意图**: 询问用户具体项目
2. **列出选项**: 显示所有可能项目
3. **用户确认**: 让用户选择正确项目
4. **切换目录**: 切换到确认的项目

---

## 🎯 记住

**核心原则**: 总是在正确的项目上下文中工作
**关键检查**: 启动时、疑惑时、切换时
**成功标准**: 零错误创建新项目，100%继续正确项目

---
*创建: 2026-04-16*
*版本: 1.0*
"""
        
        try:
            with open(self.checklist_file, 'w', encoding='utf-8') as f:
                f.write(checklist_content)
            print(f"✅ 检查清单已创建: {self.checklist_file}")
        except Exception as e:
            print(f"❌ 创建检查清单失败: {e}")
    
    def run_full_check(self):
        """运行完整检查"""
        context = self.check_current_context()
        self.print_summary(context)
        self.save_context(context)
        
        # 如果检查清单不存在，创建它
        if not os.path.exists(self.checklist_file):
            self.create_checklist()
        
        return context


def main():
    """主函数"""
    try:
        checker = ProjectContextChecker()
        context = checker.run_full_check()
        
        # 根据检查结果建议行动
        print("\n🚀 建议的下一步:")
        
        if context['is_root_workspace'] and context['potential_projects']:
            project = context['potential_projects'][0]
            print(f"1. 切换到最近项目: cd {project['path']}")
            print(f"2. 查看项目状态: cd {project['path']} && ls -la")
        
        elif not context['potential_projects']:
            print("1. 确认是否要创建新项目")
            print("2. 或者指定项目目录")
        
        else:
            print("1. 继续在当前项目中工作")
            print("2. 运行项目测试或开发任务")
        
        print("\n💡 提示: 将此检查集成到会话启动流程中")
        print("   参考: TODO_LOBSTER_3.md (工作流程优化)")
        
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()