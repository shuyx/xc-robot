#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 文件监控服务
自动监控代码文件的创建和修改，并发送webhook通知
"""

import os
import time
import threading
from pathlib import Path
from typing import Set, Dict, Any
import yaml
import logging
from datetime import datetime, timedelta

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # 创建占位符类
    class FileSystemEventHandler:
        def on_created(self, event): pass
        def on_modified(self, event): pass
    print("警告: watchdog库未安装，将使用轮询监控")

from .webhook_service import get_webhook_notifier


class CodeFileAnalyzer:
    """代码文件分析器"""
    
    @staticmethod
    def analyze_python_file(filepath: str) -> str:
        """分析Python文件功能"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单分析文件功能
            if 'class ' in content and 'def ' in content:
                return "包含类和方法定义"
            elif 'def ' in content:
                return "包含函数定义"
            elif 'import ' in content or 'from ' in content:
                return "脚本文件"
            elif '#!/usr/bin/env python' in content:
                return "可执行脚本"
            else:
                return "Python代码文件"
                
        except Exception:
            return "Python文件"
    
    @staticmethod
    def analyze_file(filepath: str) -> str:
        """分析文件功能"""
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name
        
        if file_ext == '.py':
            return CodeFileAnalyzer.analyze_python_file(filepath)
        elif file_ext == '.js':
            return "JavaScript代码文件"
        elif file_ext == '.html':
            return "HTML界面文件"
        elif file_ext == '.css':
            return "CSS样式文件"
        elif file_ext == '.md':
            return "Markdown文档文件"
        elif file_ext == '.yaml' or file_ext == '.yml':
            return "YAML配置文件"
        elif file_ext == '.json':
            return "JSON配置/数据文件"
        else:
            return f"{file_ext[1:].upper()}文件"


class FileMonitorHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.notifier = get_webhook_notifier()
        self.logger = logging.getLogger('file_monitor')
        self.debounce_time = config.get('monitoring', {}).get('file_watch', {}).get('debounce_seconds', 2)
        self.recent_events: Dict[str, datetime] = {}
        
        # 监控文件模式
        self.patterns = config.get('monitoring', {}).get('file_watch', {}).get('patterns', ['*.py'])
        self.exclude_dirs = set(config.get('monitoring', {}).get('file_watch', {}).get('exclude_dirs', []))
        
    def _should_monitor_file(self, filepath: str) -> bool:
        """检查是否应该监控该文件"""
        path = Path(filepath)
        
        # 检查排除目录
        for part in path.parts:
            if part in self.exclude_dirs:
                return False
        
        # 检查文件扩展名
        for pattern in self.patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def _is_debounced(self, filepath: str) -> bool:
        """检查事件是否在防抖动时间内"""
        now = datetime.now()
        if filepath in self.recent_events:
            if now - self.recent_events[filepath] < timedelta(seconds=self.debounce_time):
                return True
        
        self.recent_events[filepath] = now
        return False
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
            
        filepath = event.src_path
        if not self._should_monitor_file(filepath) or self._is_debounced(filepath):
            return
        
        try:
            filename = Path(filepath).name
            description = CodeFileAnalyzer.analyze_file(filepath)
            
            self.logger.info(f"检测到文件创建: {filename}")
            self.notifier.send_file_event(filename, "created", description)
            
        except Exception as e:
            self.logger.error(f"处理文件创建事件时出错: {e}")
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
            
        filepath = event.src_path
        if not self._should_monitor_file(filepath) or self._is_debounced(filepath):
            return
        
        try:
            filename = Path(filepath).name
            changes = f"文件内容已更新"
            
            self.logger.info(f"检测到文件修改: {filename}")
            self.notifier.send_file_event(filename, "modified", changes=changes)
            
        except Exception as e:
            self.logger.error(f"处理文件修改事件时出错: {e}")


class PollingFileMonitor:
    """轮询文件监控器（watchdog不可用时的备选方案）"""
    
    def __init__(self, config: Dict[str, Any], watch_path: str):
        self.config = config
        self.watch_path = watch_path
        self.notifier = get_webhook_notifier()
        self.logger = logging.getLogger('polling_monitor')
        self.running = False
        self.thread = None
        
        # 文件状态缓存
        self.file_states: Dict[str, float] = {}
        self.patterns = config.get('monitoring', {}).get('file_watch', {}).get('patterns', ['*.py'])
        self.exclude_dirs = set(config.get('monitoring', {}).get('file_watch', {}).get('exclude_dirs', []))
        
    def _should_monitor_file(self, filepath: str) -> bool:
        """检查是否应该监控该文件"""
        path = Path(filepath)
        
        # 检查排除目录
        for part in path.parts:
            if part in self.exclude_dirs:
                return False
        
        # 检查文件扩展名
        for pattern in self.patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def _scan_files(self):
        """扫描文件变化"""
        try:
            for root, dirs, files in os.walk(self.watch_path):
                # 过滤排除目录
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    if not self._should_monitor_file(filepath):
                        continue
                    
                    try:
                        mtime = os.path.getmtime(filepath)
                        
                        if filepath not in self.file_states:
                            # 新文件
                            self.file_states[filepath] = mtime
                            filename = Path(filepath).name
                            description = CodeFileAnalyzer.analyze_file(filepath)
                            self.notifier.send_file_event(filename, "created", description)
                            self.logger.info(f"检测到新文件: {filename}")
                            
                        elif self.file_states[filepath] < mtime:
                            # 文件修改
                            self.file_states[filepath] = mtime
                            filename = Path(filepath).name
                            self.notifier.send_file_event(filename, "modified", changes="文件内容已更新")
                            self.logger.info(f"检测到文件修改: {filename}")
                            
                    except Exception as e:
                        self.logger.error(f"检查文件 {filepath} 时出错: {e}")
                        
        except Exception as e:
            self.logger.error(f"扫描文件时出错: {e}")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            self._scan_files()
            time.sleep(5)  # 每5秒扫描一次
    
    def start(self):
        """启动监控"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"轮询文件监控已启动: {self.watch_path}")
    
    def stop(self):
        """停止监控"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("轮询文件监控已停止")


class FileMonitor:
    """文件监控服务"""
    
    def __init__(self, config_path: str = None, watch_path: str = None):
        self.config_path = config_path
        self.watch_path = watch_path or os.getcwd()
        self.config = self._load_config()
        self.observer = None
        self.polling_monitor = None
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
        logger = logging.getLogger('file_monitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def start(self):
        """启动文件监控"""
        if not self.config.get('webhook', {}).get('enabled', False):
            self.logger.info("Webhook未启用，跳过文件监控")
            return
            
        if not self.config.get('monitoring', {}).get('file_watch', {}).get('enabled', False):
            self.logger.info("文件监控未启用")
            return
        
        self.logger.info(f"启动文件监控: {self.watch_path}")
        
        if WATCHDOG_AVAILABLE:
            # 使用watchdog监控
            event_handler = FileMonitorHandler(self.config)
            self.observer = Observer()
            self.observer.schedule(event_handler, self.watch_path, recursive=True)
            self.observer.start()
            self.logger.info("使用watchdog文件监控")
        else:
            # 使用轮询监控
            self.polling_monitor = PollingFileMonitor(self.config, self.watch_path)
            self.polling_monitor.start()
            self.logger.info("使用轮询文件监控")
    
    def stop(self):
        """停止文件监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("watchdog文件监控已停止")
            
        if self.polling_monitor:
            self.polling_monitor.stop()
            self.logger.info("轮询文件监控已停止")


if __name__ == "__main__":
    # 测试文件监控
    monitor = FileMonitor()
    monitor.start()
    
    try:
        print("文件监控已启动，按Ctrl+C停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print("文件监控已停止")