#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Git钩子服务
自动捕获Git提交事件并发送webhook通知
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

from .webhook_service import get_webhook_notifier


class GitHookManager:
    """Git钩子管理器"""
    
    def __init__(self, config_path: str = None, repo_path: str = None):
        self.config_path = config_path
        self.repo_path = repo_path or os.getcwd()
        self.config = self._load_config()
        self.notifier = get_webhook_notifier()
        self.logger = self._setup_logger()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if not self.config_path:
            # 查找配置文件
            possible_paths = [
                Path(__file__).parent.parent.parent / "config" / "webhook_config.yaml",
                Path("config/webhook_config.yaml")
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.config_path = str(path)
                    break
        
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        return {}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('git_hooks')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _is_git_repo(self) -> bool:
        """检查是否为Git仓库"""
        git_dir = Path(self.repo_path) / ".git"
        return git_dir.exists()
    
    def _get_git_hooks_dir(self) -> Path:
        """获取Git钩子目录"""
        return Path(self.repo_path) / ".git" / "hooks"
    
    def _get_last_commit_info(self) -> Dict[str, Any]:
        """获取最后一次提交信息"""
        try:
            # 获取提交信息
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%H|%an|%ae|%s|%ct'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_info = result.stdout.strip().split('|')
            if len(commit_info) >= 5:
                return {
                    'hash': commit_info[0],
                    'author_name': commit_info[1],
                    'author_email': commit_info[2],
                    'message': commit_info[3],
                    'timestamp': commit_info[4]
                }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"获取Git提交信息失败: {e}")
        
        return {}
    
    def _get_changed_files_count(self) -> int:
        """获取变更文件数量"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files = result.stdout.strip().split('\n')
            return len([f for f in files if f.strip()])
            
        except subprocess.CalledProcessError:
            return 0
    
    def handle_post_commit(self):
        """处理post-commit钩子"""
        try:
            commit_info = self._get_last_commit_info()
            if not commit_info:
                self.logger.warning("无法获取提交信息")
                return
            
            file_count = self._get_changed_files_count()
            
            # 发送webhook通知
            self.notifier.send_commit_event(
                commit_message=commit_info.get('message', ''),
                file_count=file_count,
                author=commit_info.get('author_name', '')
            )
            
            self.logger.info(f"Git提交通知已发送: {commit_info.get('message', '')}")
            
        except Exception as e:
            self.logger.error(f"处理post-commit钩子时出错: {e}")
    
    def handle_pre_push(self):
        """处理pre-push钩子"""
        try:
            # 获取即将推送的提交信息
            result = subprocess.run(
                ['git', 'log', '@{u}..HEAD', '--oneline'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                commits = result.stdout.strip().split('\n')
                commit_count = len(commits)
                
                if commit_count > 0:
                    # 发送推送通知（使用error_alert模板）
                    self.notifier.send_error_alert(
                        error_type="Git推送",
                        error_details=f"即将推送 {commit_count} 个提交到远程仓库"
                    )
                    
                    self.logger.info(f"Git推送通知已发送: {commit_count} 个提交")
            
        except Exception as e:
            self.logger.error(f"处理pre-push钩子时出错: {e}")
    
    def install_hooks(self) -> bool:
        """安装Git钩子"""
        if not self._is_git_repo():
            self.logger.error("当前目录不是Git仓库")
            return False
        
        if not self.config.get('webhook', {}).get('enabled', False):
            self.logger.info("Webhook未启用，跳过安装Git钩子")
            return False
        
        if not self.config.get('monitoring', {}).get('git_watch', {}).get('enabled', False):
            self.logger.info("Git监控未启用")
            return False
        
        hooks_dir = self._get_git_hooks_dir()
        hooks_dir.mkdir(exist_ok=True)
        
        hook_types = self.config.get('monitoring', {}).get('git_watch', {}).get('hook_types', ['post-commit'])
        
        success_count = 0
        
        for hook_type in hook_types:
            try:
                hook_file = hooks_dir / hook_type
                
                # 创建钩子脚本
                hook_content = self._generate_hook_script(hook_type)
                
                with open(hook_file, 'w', encoding='utf-8') as f:
                    f.write(hook_content)
                
                # 设置执行权限
                os.chmod(hook_file, 0o755)
                
                self.logger.info(f"Git钩子 {hook_type} 安装成功")
                success_count += 1
                
            except Exception as e:
                self.logger.error(f"安装Git钩子 {hook_type} 失败: {e}")
        
        return success_count > 0
    
    def _generate_hook_script(self, hook_type: str) -> str:
        """生成钩子脚本内容"""
        python_path = Path(__file__).resolve()
        
        script_content = f"""#!/bin/bash
# XC-ROBOT 自动生成的Git钩子: {hook_type}
# 自动发送webhook通知

# 设置环境变量
export PYTHONPATH="${python_path.parent.parent.parent}:$PYTHONPATH"

# 调用Python钩子处理器
python3 "{python_path}" --hook-type {hook_type} --repo-path "$(pwd)"
"""
        
        return script_content
    
    def uninstall_hooks(self) -> bool:
        """卸载Git钩子"""
        if not self._is_git_repo():
            self.logger.error("当前目录不是Git仓库")
            return False
        
        hooks_dir = self._get_git_hooks_dir()
        hook_types = ['post-commit', 'pre-push']
        
        success_count = 0
        
        for hook_type in hook_types:
            try:
                hook_file = hooks_dir / hook_type
                if hook_file.exists():
                    # 检查是否为我们安装的钩子
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'XC-ROBOT 自动生成的Git钩子' in content:
                        hook_file.unlink()
                        self.logger.info(f"Git钩子 {hook_type} 卸载成功")
                        success_count += 1
                    else:
                        self.logger.warning(f"Git钩子 {hook_type} 不是由XC-ROBOT安装，跳过卸载")
                
            except Exception as e:
                self.logger.error(f"卸载Git钩子 {hook_type} 失败: {e}")
        
        return success_count > 0
    
    def check_hooks_status(self) -> Dict[str, bool]:
        """检查钩子安装状态"""
        if not self._is_git_repo():
            return {}
        
        hooks_dir = self._get_git_hooks_dir()
        hook_types = ['post-commit', 'pre-push']
        status = {}
        
        for hook_type in hook_types:
            hook_file = hooks_dir / hook_type
            if hook_file.exists():
                try:
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    status[hook_type] = 'XC-ROBOT 自动生成的Git钩子' in content
                except:
                    status[hook_type] = False
            else:
                status[hook_type] = False
        
        return status


def main():
    """主函数，用于处理Git钩子调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XC-ROBOT Git钩子处理器')
    parser.add_argument('--hook-type', required=True, help='钩子类型')
    parser.add_argument('--repo-path', required=True, help='仓库路径')
    
    args = parser.parse_args()
    
    # 创建钩子管理器
    manager = GitHookManager(repo_path=args.repo_path)
    
    # 处理不同类型的钩子
    if args.hook_type == 'post-commit':
        manager.handle_post_commit()
    elif args.hook_type == 'pre-push':
        manager.handle_pre_push()
    else:
        print(f"不支持的钩子类型: {args.hook_type}")


if __name__ == "__main__":
    main()