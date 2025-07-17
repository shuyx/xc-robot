#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 自动平台设置脚本
新团队成员或新平台的一键设置工具
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from platform_config import get_platform_adapter

class AutoPlatformSetup:
    """自动平台设置"""
    
    def __init__(self):
        self.adapter = get_platform_adapter()
        self.project_root = Path(__file__).parent
        
    def check_git_setup(self) -> bool:
        """检查Git设置"""
        try:
            # 检查是否在Git仓库中
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ 当前目录不是Git仓库")
                return False
            
            # 检查Git配置
            name_result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
            email_result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
            
            if not name_result.stdout.strip() or not email_result.stdout.strip():
                print("⚠️ Git用户信息未配置")
                self._setup_git_config()
            
            return True
            
        except Exception as e:
            print(f"❌ Git检查失败: {e}")
            return False
    
    def _setup_git_config(self):
        """设置Git配置"""
        print("\n🔧 配置Git用户信息:")
        name = input("请输入您的姓名: ").strip()
        email = input("请输入您的邮箱: ").strip()
        
        if name and email:
            subprocess.run(['git', 'config', 'user.name', name])
            subprocess.run(['git', 'config', 'user.email', email])
            print("✅ Git配置完成")
    
    def setup_virtual_environment(self) -> bool:
        """设置虚拟环境"""
        venv_path = self.project_root / 'venv'
        
        if venv_path.exists():
            print("✅ 虚拟环境已存在")
            return True
        
        try:
            print("📦 创建虚拟环境...")
            python_exe = self.adapter.get_platform_config().get('python_executable', 'python3')
            subprocess.run([python_exe, '-m', 'venv', 'venv'], check=True)
            
            # 安装依赖
            print("📦 安装依赖包...")
            if self.adapter.is_windows:
                pip_exe = str(venv_path / 'Scripts' / 'pip.exe')
            else:
                pip_exe = str(venv_path / 'bin' / 'pip')
            
            # 基础依赖
            packages = ['PyQt5', 'requests', 'numpy', 'PyYAML', 'pillow']
            subprocess.run([pip_exe, 'install'] + packages, check=True)
            
            print("✅ 虚拟环境设置完成")
            return True
            
        except Exception as e:
            print(f"❌ 虚拟环境设置失败: {e}")
            return False
    
    def create_ide_config(self):
        """创建IDE配置文件"""
        # VS Code配置
        vscode_dir = self.project_root / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        # settings.json
        vscode_settings = {
            "python.defaultInterpreterPath": "./venv/bin/python" if not self.adapter.is_windows else ".\\venv\\Scripts\\python.exe",
            "python.terminal.activateEnvironment": True,
            "files.encoding": "utf8",
            "editor.fontSize": 14 if self.adapter.is_mac else 12,
            "terminal.integrated.fontSize": 12,
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                ".DS_Store": True,
                "Thumbs.db": True
            }
        }
        
        with open(vscode_dir / 'settings.json', 'w', encoding='utf-8') as f:
            json.dump(vscode_settings, f, indent=2)
        
        # launch.json (调试配置)
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "XC-ROBOT GUI",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/start_gui.py",
                    "console": "integratedTerminal",
                    "justMyCode": True,
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                },
                {
                    "name": "Platform Config Test",
                    "type": "python", 
                    "request": "launch",
                    "program": "${workspaceFolder}/platform_config.py",
                    "console": "integratedTerminal"
                }
            ]
        }
        
        with open(vscode_dir / 'launch.json', 'w', encoding='utf-8') as f:
            json.dump(launch_config, f, indent=2)
        
        print("✅ IDE配置文件已创建")
    
    def create_branch_workflow_guide(self):
        """创建分支工作流指南"""
        guide_content = f"""# XC-ROBOT 跨平台开发工作流指南

## 当前环境
- 平台: {self.adapter.platform.title()}
- Python: {self.adapter.get_platform_config().get('python_executable', 'python')}
- GUI框架: {self.adapter.get_gui_config().get('framework', 'PyQt5')}

## 分支策略

### 主要分支
- **gui-dev**: 统一GUI开发分支（推荐重命名mac-dev为此）
- **robot-dev**: 机器人测试和控制功能开发
- **main**: 稳定版本分支（暂不合并）

### 平台分支
- **gui-dev-mac**: Mac平台特定优化
- **gui-dev-win**: Windows平台特定优化

## 跨平台开发流程

### 1. 日常开发
```bash
# 在主开发分支工作
git checkout gui-dev
# 开发功能...
git add .
git commit -m "Add new feature"
```

### 2. 平台同步
```bash
# 推送到远程
git push origin gui-dev

# 在另一平台
git fetch origin
git checkout gui-dev
git pull origin gui-dev

# 自动适配当前平台
python3 auto_platform_setup.py --sync
```

### 3. 平台特定修改
```bash
# 创建平台分支
git checkout -b gui-dev-{self.adapter.platform}
# 进行平台特定修改...
git commit -m "Platform-specific changes for {self.adapter.platform}"
git push origin gui-dev-{self.adapter.platform}
```

## 自动化工具

### 平台配置
```bash
python3 platform_config.py          # 生成平台配置
python3 auto_platform_setup.py      # 自动设置环境
python3 sync_branches.py            # 分支同步工具
```

### 启动命令
- Mac/Linux: `./start_xc_robot.sh`
- Windows: `start_xc_robot.bat`
- 通用: `python3 start_gui.py`

## 注意事项

1. **路径差异**: 自动适配器会处理 `/` 与 `\\` 的差异
2. **字体差异**: 自动选择平台最佳字体
3. **依赖检查**: 启动时自动检查平台依赖
4. **配置同步**: 使用 JSON 配置文件实现跨平台统一

## 故障排除

### 依赖问题
```bash
# 检查依赖状态
python3 platform_config.py

# 重新安装依赖
pip install -r requirements.txt
```

### 分支同步问题
```bash
# 检查分支状态
git status
git log --oneline -5

# 强制同步（谨慎使用）
git reset --hard origin/gui-dev
python3 auto_platform_setup.py --force-adapt
```

### 平台适配问题
```bash
# 重新生成平台配置
python3 platform_config.py
python3 auto_platform_setup.py --reconfigure
```

---
自动生成时间: {self.adapter.platform.title()} 平台
"""
        
        with open(self.project_root / 'CROSS_PLATFORM_WORKFLOW.md', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print("✅ 工作流指南已创建: CROSS_PLATFORM_WORKFLOW.md")
    
    def run_full_setup(self):
        """运行完整设置"""
        print(f"🚀 XC-ROBOT {self.adapter.platform.title()} 平台自动设置")
        print("=" * 50)
        
        # 1. Git检查
        if not self.check_git_setup():
            return False
        
        # 2. 平台配置
        print("\n📋 生成平台配置...")
        self.adapter.generate_platform_specific_files()
        
        # 3. 虚拟环境
        print("\n🐍 设置Python环境...")
        if not self.setup_virtual_environment():
            return False
        
        # 4. IDE配置
        print("\n⚙️ 创建IDE配置...")
        self.create_ide_config()
        
        # 5. 工作流指南
        print("\n📚 创建工作流指南...")
        self.create_branch_workflow_guide()
        
        # 6. 依赖检查
        print("\n🔍 最终依赖检查...")
        deps = self.adapter.check_dependencies()
        failed = [name for name, status in deps.items() if not status]
        
        if failed:
            print(f"⚠️ 仍有依赖问题: {', '.join(failed)}")
            print("请手动安装缺失的依赖")
        else:
            print("✅ 所有依赖检查通过")
        
        print("\n🎉 平台设置完成!")
        print(f"启动GUI: python3 start_gui.py")
        print(f"查看指南: cat CROSS_PLATFORM_WORKFLOW.md")
        
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XC-ROBOT自动平台设置')
    parser.add_argument('--sync', action='store_true', help='仅同步平台配置')
    parser.add_argument('--reconfigure', action='store_true', help='重新配置')
    parser.add_argument('--force-adapt', action='store_true', help='强制适配')
    
    args = parser.parse_args()
    
    setup = AutoPlatformSetup()
    
    if args.sync:
        setup.adapter.generate_platform_specific_files()
        print("✅ 平台配置已同步")
    elif args.reconfigure:
        setup.run_full_setup()
    elif args.force_adapt:
        setup.adapter.generate_platform_specific_files()
        setup.create_ide_config()
        print("✅ 平台强制适配完成")
    else:
        setup.run_full_setup()

if __name__ == "__main__":
    main()