#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 调试状态监控服务
自动检测调试和测试的成功状态，并发送webhook通知
"""

import os
import re
import time
import threading
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
import json
import yaml
from datetime import datetime, timedelta

from .webhook_service import get_webhook_notifier


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.success_patterns = config.get('monitoring', {}).get('debug_watch', {}).get('success_patterns', [])
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.success_patterns]
        
    def analyze_log_content(self, content: str) -> List[Dict[str, str]]:
        """分析日志内容，查找成功标识"""
        results = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.compiled_patterns:
                if pattern.search(line):
                    results.append({
                        'line_number': i + 1,
                        'content': line.strip(),
                        'pattern': pattern.pattern,
                        'context': self._get_context(lines, i, 2)
                    })
        
        return results
    
    def _get_context(self, lines: List[str], center: int, radius: int) -> str:
        """获取匹配行的上下文"""
        start = max(0, center - radius)
        end = min(len(lines), center + radius + 1)
        context_lines = lines[start:end]
        return '\n'.join(context_lines)
    
    def analyze_test_result(self, content: str) -> Dict[str, Any]:
        """分析测试结果"""
        # 检查是否包含测试成功的标识
        success_indicators = [
            r'test.*passed',
            r'success',
            r'完成',
            r'成功',
            r'✓',
            r'all.*tests.*passed',
            r'no.*errors',
            r'status.*ok'
        ]
        
        fail_indicators = [
            r'test.*failed',
            r'error',
            r'错误',
            r'失败',
            r'✗',
            r'exception',
            r'traceback'
        ]
        
        success_count = 0
        fail_count = 0
        
        for pattern in success_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                success_count += 1
                
        for pattern in fail_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                fail_count += 1
        
        return {
            'success_score': success_count,
            'fail_score': fail_count,
            'likely_success': success_count > fail_count and success_count > 0
        }


class DebugMonitor:
    """调试监控服务"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self._load_config()
        self.notifier = get_webhook_notifier()
        self.logger = self._setup_logger()
        self.analyzer = LogAnalyzer(self.config)
        
        # 监控状态
        self.running = False
        self.monitor_thread = None
        self.processed_entries: Set[str] = set()
        
        # 日志文件状态
        self.log_file_states: Dict[str, float] = {}
        
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
        logger = logging.getLogger('debug_monitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_log_files(self) -> List[str]:
        """获取要监控的日志文件列表"""
        log_patterns = self.config.get('monitoring', {}).get('debug_watch', {}).get('log_files', [])
        log_files = []
        
        for pattern in log_patterns:
            try:
                # 使用glob模式匹配日志文件
                from glob import glob
                matched_files = glob(pattern)
                log_files.extend(matched_files)
            except Exception as e:
                self.logger.error(f"匹配日志文件模式 {pattern} 时出错: {e}")
        
        return log_files
    
    def _monitor_log_file(self, log_file: str):
        """监控单个日志文件"""
        try:
            if not os.path.exists(log_file):
                return
            
            # 检查文件修改时间
            mtime = os.path.getmtime(log_file)
            
            if log_file not in self.log_file_states:
                # 新文件，记录状态但不处理（避免处理历史数据）
                self.log_file_states[log_file] = mtime
                return
            
            if self.log_file_states[log_file] >= mtime:
                # 文件未更新
                return
            
            # 文件已更新，读取新内容
            self.log_file_states[log_file] = mtime
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self._process_log_content(log_file, content)
            
        except Exception as e:
            self.logger.error(f"监控日志文件 {log_file} 时出错: {e}")
    
    def _process_log_content(self, log_file: str, content: str):
        """处理日志内容"""
        try:
            # 分析日志内容
            matches = self.analyzer.analyze_log_content(content)
            
            if not matches:
                return
            
            # 检查是否为测试相关的日志
            filename = Path(log_file).name
            
            if 'test' in filename.lower() or filename.endswith('.json'):
                # 测试日志文件
                self._process_test_log(log_file, content, matches)
            else:
                # 普通调试日志
                self._process_debug_log(log_file, content, matches)
                
        except Exception as e:
            self.logger.error(f"处理日志内容时出错: {e}")
    
    def _process_test_log(self, log_file: str, content: str, matches: List[Dict[str, str]]):
        """处理测试日志"""
        try:
            filename = Path(log_file).name
            
            # 分析测试结果
            test_analysis = self.analyzer.analyze_test_result(content)
            
            if test_analysis['likely_success']:
                # 测试成功
                test_info = f"测试文件: {filename}"
                if filename.endswith('.json'):
                    # 尝试解析JSON测试报告
                    try:
                        data = json.loads(content)
                        if 'test_type' in data:
                            test_info = f"{data.get('test_type', '测试')} - {filename}"
                    except:
                        pass
                
                result = "测试通过"
                self.notifier.send_test_complete(test_info, result)
                self.logger.info(f"检测到测试成功: {filename}")
            
        except Exception as e:
            self.logger.error(f"处理测试日志时出错: {e}")
    
    def _process_debug_log(self, log_file: str, content: str, matches: List[Dict[str, str]]):
        """处理调试日志"""
        try:
            filename = Path(log_file).name
            
            # 提取调试信息
            debug_info = f"调试日志: {filename}"
            result_details = []
            
            for match in matches[-3:]:  # 最多取最近3个匹配
                result_details.append(match['content'])
            
            if result_details:
                result = "成功 - " + "; ".join(result_details)
                self.notifier.send_debug_success(debug_info, result)
                self.logger.info(f"检测到调试成功: {filename}")
                
        except Exception as e:
            self.logger.error(f"处理调试日志时出错: {e}")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                log_files = self._get_log_files()
                
                for log_file in log_files:
                    self._monitor_log_file(log_file)
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                self.logger.error(f"监控循环出错: {e}")
                time.sleep(10)  # 出错时等待更长时间
    
    def start(self):
        """启动调试监控"""
        if not self.config.get('webhook', {}).get('enabled', False):
            self.logger.info("Webhook未启用，跳过调试监控")
            return
            
        if not self.config.get('monitoring', {}).get('debug_watch', {}).get('enabled', False):
            self.logger.info("调试监控未启用")
            return
        
        if self.running:
            self.logger.warning("调试监控已在运行")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("调试监控已启动")
    
    def stop(self):
        """停止调试监控"""
        if not self.running:
            return
            
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("调试监控已停止")
    
    def manual_check_success(self, info: str, result: str = "手动确认成功"):
        """手动报告调试成功"""
        self.notifier.send_debug_success(info, result)
        self.logger.info(f"手动报告调试成功: {info}")


# 便捷函数
def start_debug_monitor():
    """启动调试监控"""
    monitor = DebugMonitor()
    monitor.start()
    return monitor

def report_debug_success(info: str, result: str = "成功"):
    """手动报告调试成功"""
    monitor = DebugMonitor()
    monitor.manual_check_success(info, result)


if __name__ == "__main__":
    # 测试调试监控
    monitor = DebugMonitor()
    monitor.start()
    
    try:
        print("调试监控已启动，按Ctrl+C停止...")
        
        # 测试手动报告
        time.sleep(2)
        monitor.manual_check_success("系统启动测试", "所有模块加载成功")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print("调试监控已停止")