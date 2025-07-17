#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台分支同步脚本
自动处理 Mac/Windows 分支同步和平台适配
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from platform_config import get_platform_adapter

class BranchSyncManager:
    """分支同步管理器"""
    
    def __init__(self):
        self.adapter = get_platform_adapter()
        self.project_root = Path(__file__).parent
        
    def get_current_branch(self) -> str:
        """获取当前分支名"""
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    
    def get_branch_commits(self, branch: str, count: int = 10) -> List[str]:
        """获取分支的最近提交"""
        result = subprocess.run(['git', 'log', f'{branch}', '--oneline', f'-{count}'], 
                              capture_output=True, text=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    def has_uncommitted_changes(self) -> bool:
        """检查是否有未提交的更改"""
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        return bool(result.stdout.strip())
    
    def create_platform_sync_config(self):
        """创建平台同步配置"""
        sync_config = {
            "sync_strategy": {
                "mac-dev": {
                    "target_branch": "gui-dev",
                    "auto_adapt": True,
                    "platform_specific_files": [
                        "start_xc_robot.sh",
                        "config/gui_config_darwin.json",
                        "config/network_config_darwin.json"
                    ]
                },
                "win-dev": {
                    "target_branch": "gui-dev", 
                    "auto_adapt": True,
                    "platform_specific_files": [
                        "start_xc_robot.bat",
                        "config/gui_config_windows.json",
                        "config/network_config_windows.json"
                    ]
                }
            },
            "ignore_patterns": [
                "*.pyc",
                "__pycache__/",
                ".DS_Store",
                "Thumbs.db",
                "venv/",
                ".vscode/",
                "*.log"
            ],
            "platform_adaptations": {
                "file_paths": {
                    "mac_to_win": {
                        "/": "\\\\",
                        "./venv/bin/activate": ".\\\\venv\\\\Scripts\\\\activate.bat"
                    },
                    "win_to_mac": {
                        "\\\\": "/",
                        ".\\\\venv\\\\Scripts\\\\activate.bat": "./venv/bin/activate"
                    }
                }
            }
        }
        
        config_file = self.project_root / 'config' / 'sync_config.json'
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sync_config, f, indent=2, ensure_ascii=False)
        
        return sync_config
    
    def rename_branch_strategy(self):
        """分支重命名策略"""
        current_branch = self.get_current_branch()
        
        print("🔄 分支重命名策略建议:")
        print(f"当前分支: {current_branch}")
        
        if current_branch == "mac-dev":
            print("""
建议的分支策略:
1. 将 mac-dev 重命名为 gui-dev (统一GUI开发分支)
2. 创建平台特定分支:
   - gui-dev-mac (Mac平台优化)
   - gui-dev-win (Windows平台优化)
3. 主要开发在 gui-dev 进行
4. 平台特定修改在对应平台分支
            """)
            
            response = input("是否执行分支重命名? (y/n): ")
            if response.lower() == 'y':
                self._execute_branch_rename()
    
    def _execute_branch_rename(self):
        """执行分支重命名"""
        try:
            # 检查未提交更改
            if self.has_uncommitted_changes():
                print("❌ 有未提交的更改，请先提交")
                return False
            
            # 重命名当前分支
            print("🔄 重命名 mac-dev -> gui-dev...")
            subprocess.run(['git', 'branch', '-m', 'mac-dev', 'gui-dev'], check=True)
            
            # 推送重命名后的分支
            print("📤 推送重命名分支...")
            subprocess.run(['git', 'push', 'origin', '-u', 'gui-dev'], check=True)
            
            # 删除远程旧分支
            print("🗑️ 删除远程旧分支...")
            subprocess.run(['git', 'push', 'origin', '--delete', 'mac-dev'], check=True)
            
            print("✅ 分支重命名完成!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 分支重命名失败: {e}")
            return False
    
    def sync_with_platform_adaptation(self, source_branch: str, target_branch: str):
        """带平台适配的分支同步"""
        print(f"🔄 同步分支: {source_branch} -> {target_branch}")
        
        try:
            # 1. 获取最新代码
            subprocess.run(['git', 'fetch', 'origin'], check=True)
            
            # 2. 切换到目标分支
            subprocess.run(['git', 'checkout', target_branch], check=True)
            
            # 3. 合并源分支
            subprocess.run(['git', 'merge', f'origin/{source_branch}'], check=True)
            
            # 4. 应用平台适配
            self._apply_platform_adaptations(target_branch)
            
            # 5. 提交适配更改
            if self.has_uncommitted_changes():
                commit_msg = f"Auto-adapt for {self.adapter.platform} platform from {source_branch}"
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            print(f"✅ 分支同步完成: {target_branch}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 分支同步失败: {e}")
    
    def _apply_platform_adaptations(self, branch: str):
        """应用平台特定适配"""
        print(f"🔧 应用 {self.adapter.platform} 平台适配...")
        
        # 生成平台特定文件
        self.adapter.generate_platform_specific_files()
        
        # 适配配置文件中的路径
        self._adapt_config_files()
        
        print("✅ 平台适配完成")
    
    def _adapt_config_files(self):
        """适配配置文件"""
        config_files = [
            'robot_config.yaml',
            'config/robot_config.json'
        ]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                self._adapt_file_paths(file_path)
    
    def _adapt_file_paths(self, file_path: Path):
        """适配文件中的路径"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 根据平台适配路径
            if self.adapter.is_windows:
                content = content.replace('/', '\\')
                content = content.replace('./venv/bin/activate', '.\\venv\\Scripts\\activate.bat')
            else:
                content = content.replace('\\', '/')
                content = content.replace('.\\venv\\Scripts\\activate.bat', './venv/bin/activate')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"警告: 无法适配文件 {file_path}: {e}")

def main():
    """主函数"""
    sync_manager = BranchSyncManager()
    
    print("🚀 XC-ROBOT 跨平台分支同步工具")
    print(f"当前平台: {sync_manager.adapter.platform.title()}")
    print(f"当前分支: {sync_manager.get_current_branch()}")
    
    # 创建同步配置
    sync_manager.create_platform_sync_config()
    
    print("\n可用操作:")
    print("1. 查看分支状态")
    print("2. 分支重命名策略") 
    print("3. 同步远程分支")
    print("4. 生成平台配置")
    print("0. 退出")
    
    while True:
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            # 显示分支状态
            current = sync_manager.get_current_branch()
            commits = sync_manager.get_branch_commits(current, 5)
            print(f"\n当前分支: {current}")
            print("最近提交:")
            for commit in commits:
                print(f"  {commit}")
                
        elif choice == '2':
            sync_manager.rename_branch_strategy()
            
        elif choice == '3':
            source = input("源分支: ").strip()
            target = input("目标分支: ").strip()
            if source and target:
                sync_manager.sync_with_platform_adaptation(source, target)
                
        elif choice == '4':
            sync_manager.adapter.generate_platform_specific_files()
            print("✅ 平台配置已生成")
            
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()