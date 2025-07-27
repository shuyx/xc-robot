#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Webhook守护服务
统一管理文件监控、调试检测、Git钩子等自动化通知功能
"""

import time
import signal
import sys
import threading
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from .file_monitor import FileMonitor
from .debug_monitor import DebugMonitor
from .git_hooks import GitHookManager
from .webhook_service import get_webhook_notifier


class WebhookDaemon:
    """Webhook守护服务"""
    
    def __init__(self, config_path: str = None, work_dir: str = None):
        self.config_path = config_path
        self.work_dir = work_dir or "."
        self.config = self._load_config()
        self.logger = self._setup_logger()
        
        # 服务组件
        self.file_monitor: Optional[FileMonitor] = None
        self.debug_monitor: Optional[DebugMonitor] = None
        self.git_manager: Optional[GitHookManager] = None
        
        # 运行状态
        self.running = False
        self.services_started = []
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if not self.config_path:
            # 查找配置文件
            possible_paths = [
                Path(__file__).parent.parent.parent / "config" / "webhook_config.yaml",
                Path("config/webhook_config.yaml"),
                Path("webhook_config.yaml")
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
        logger = logging.getLogger('webhook_daemon')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 文件处理器
            try:
                log_dir = Path(self.work_dir) / "logs"
                log_dir.mkdir(exist_ok=True)
                log_file = log_dir / "webhook_daemon.log"
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"创建日志文件处理器失败: {e}")
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，正在停止服务...")
        self.stop()
        sys.exit(0)
    
    def _initialize_services(self):
        """初始化服务组件"""
        try:
            # 初始化文件监控
            if self.config.get('monitoring', {}).get('file_watch', {}).get('enabled', False):
                self.file_monitor = FileMonitor(self.config_path, self.work_dir)
                self.logger.info("文件监控服务已初始化")
            
            # 初始化调试监控
            if self.config.get('monitoring', {}).get('debug_watch', {}).get('enabled', False):
                self.debug_monitor = DebugMonitor(self.config_path)
                self.logger.info("调试监控服务已初始化")
            
            # 初始化Git钩子管理器
            if self.config.get('monitoring', {}).get('git_watch', {}).get('enabled', False):
                self.git_manager = GitHookManager(self.config_path, self.work_dir)
                self.logger.info("Git钩子管理器已初始化")
            
        except Exception as e:
            self.logger.error(f"初始化服务组件时出错: {e}")
    
    def start(self):
        """启动守护服务"""
        if self.running:
            self.logger.warning("守护服务已在运行")
            return
        
        if not self.config.get('webhook', {}).get('enabled', False):
            self.logger.error("Webhook未启用，无法启动守护服务")
            return
        
        webhook_url = self.config.get('webhook', {}).get('url', '')
        if not webhook_url or webhook_url == "YOUR_WEBHOOK_URL_HERE":
            self.logger.error("Webhook URL未配置，请在配置文件中设置正确的URL")
            return
        
        self.logger.info("正在启动XC-ROBOT Webhook守护服务...")
        
        # 初始化服务组件
        self._initialize_services()
        
        # 启动各个服务
        self._start_services()
        
        self.running = True
        self.logger.info("Webhook守护服务启动成功")
        
        # 发送启动通知
        try:
            notifier = get_webhook_notifier()
            notifier.send_debug_success(
                "XC-ROBOT Webhook守护服务",
                f"服务启动成功，已启用 {len(self.services_started)} 个监控模块"
            )
        except Exception as e:
            self.logger.error(f"发送启动通知失败: {e}")
    
    def _start_services(self):
        """启动各个服务"""
        # 启动文件监控
        if self.file_monitor:
            try:
                self.file_monitor.start()
                self.services_started.append("文件监控")
                self.logger.info("文件监控服务已启动")
            except Exception as e:
                self.logger.error(f"启动文件监控服务失败: {e}")
        
        # 启动调试监控
        if self.debug_monitor:
            try:
                self.debug_monitor.start()
                self.services_started.append("调试监控")
                self.logger.info("调试监控服务已启动")
            except Exception as e:
                self.logger.error(f"启动调试监控服务失败: {e}")
        
        # 安装Git钩子
        if self.git_manager:
            try:
                if self.git_manager.install_hooks():
                    self.services_started.append("Git钩子")
                    self.logger.info("Git钩子已安装")
                else:
                    self.logger.warning("Git钩子安装失败")
            except Exception as e:
                self.logger.error(f"安装Git钩子失败: {e}")
    
    def stop(self):
        """停止守护服务"""
        if not self.running:
            return
        
        self.logger.info("正在停止Webhook守护服务...")
        
        # 停止文件监控
        if self.file_monitor:
            try:
                self.file_monitor.stop()
                self.logger.info("文件监控服务已停止")
            except Exception as e:
                self.logger.error(f"停止文件监控服务失败: {e}")
        
        # 停止调试监控
        if self.debug_monitor:
            try:
                self.debug_monitor.stop()
                self.logger.info("调试监控服务已停止")
            except Exception as e:
                self.logger.error(f"停止调试监控服务失败: {e}")
        
        self.running = False
        self.services_started.clear()
        self.logger.info("Webhook守护服务已停止")
    
    def status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status_info = {
            'running': self.running,
            'services': self.services_started.copy(),
            'config_loaded': bool(self.config),
            'webhook_enabled': self.config.get('webhook', {}).get('enabled', False),
            'webhook_url_configured': bool(
                self.config.get('webhook', {}).get('url', '') and 
                self.config.get('webhook', {}).get('url', '') != "YOUR_WEBHOOK_URL_HERE"
            )
        }
        
        # Git钩子状态
        if self.git_manager:
            status_info['git_hooks'] = self.git_manager.check_hooks_status()
        
        return status_info
    
    def run_forever(self):
        """运行守护服务（阻塞模式）"""
        self.start()
        
        if not self.running:
            self.logger.error("守护服务启动失败")
            return
        
        try:
            self.logger.info("守护服务正在运行，按Ctrl+C停止...")
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在停止...")
        finally:
            self.stop()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XC-ROBOT Webhook守护服务')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--work-dir', help='工作目录', default='.')
    parser.add_argument('--daemon', action='store_true', help='以守护进程模式运行')
    parser.add_argument('--status', action='store_true', help='显示服务状态')
    parser.add_argument('--stop', action='store_true', help='停止服务')
    
    args = parser.parse_args()
    
    # 创建守护服务实例
    daemon = WebhookDaemon(args.config, args.work_dir)
    
    if args.status:
        # 显示状态
        status = daemon.status()
        print("XC-ROBOT Webhook守护服务状态:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
    
    if args.stop:
        # 停止服务
        daemon.stop()
        return
    
    if args.daemon:
        # 守护进程模式（简化实现）
        print("守护进程模式启动...")
        daemon.run_forever()
    else:
        # 前台模式
        daemon.run_forever()


if __name__ == "__main__":
    main()