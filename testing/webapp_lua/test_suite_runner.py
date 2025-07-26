#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebApp Lua Test Suite Runner
批量执行所有基于webapp lua调用的测试

提供统一的测试入口，支持选择性执行和结果汇总
"""

import time
import logging
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入所有lua测试模块
try:
    from SAT001_lua_left import LuaLeftArmTest
    from SAT001_lua_right import LuaRightArmTest
    from DAT001_lua_sync import LuaDualArmSyncTest
    from chassis_lua_basic import LuaChassisBasicTest
    from vision_lua_test import LuaVisionTest
    from integration_lua_full import LuaFullSystemTest
except ImportError as e:
    print(f"Warning: 无法导入某些测试模块: {e}")

class WebAppLuaTestSuiteRunner:
    """WebApp Lua测试套件运行器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化测试套件运行器
        
        Args:
            config: 测试配置
        """
        self.config = config or self._load_default_config()
        
        # 测试套件定义
        self.test_suites = {
            'basic': {
                'name': '基础功能测试',
                'description': '单臂连接和基础移动测试',
                'tests': ['sat001_left', 'sat001_right', 'chassis_basic']
            },
            'coordination': {
                'name': '协作功能测试', 
                'description': '双臂协作和同步测试',
                'tests': ['dat001_sync']
            },
            'vision': {
                'name': '视觉系统测试',
                'description': '视觉引导和目标检测测试',
                'tests': ['vision_test']
            },
            'integration': {
                'name': '集成测试',
                'description': '全系统集成测试',
                'tests': ['integration_full']
            },
            'full': {
                'name': '完整测试套件',
                'description': '所有测试项目',
                'tests': ['sat001_left', 'sat001_right', 'dat001_sync', 
                         'chassis_basic', 'vision_test', 'integration_full']
            }
        }
        
        # 测试执行器映射
        self.test_executors = {
            'sat001_left': lambda: LuaLeftArmTest(self.config['hardware']['left_arm_ip']),
            'sat001_right': lambda: LuaRightArmTest(self.config['hardware']['right_arm_ip']),
            'dat001_sync': lambda: LuaDualArmSyncTest(
                self.config['hardware']['left_arm_ip'],
                self.config['hardware']['right_arm_ip']
            ),
            'chassis_basic': lambda: LuaChassisBasicTest(
                self.config['hardware']['chassis_ip'],
                self.config['hardware']['chassis_port']
            ),
            'vision_test': lambda: LuaVisionTest(self.config['hardware']['left_arm_ip']),
            'integration_full': lambda: LuaFullSystemTest(
                self.config['hardware']['left_arm_ip'],
                self.config['hardware']['right_arm_ip'],
                self.config['hardware']['chassis_ip'],
                self.config['hardware']['chassis_port']
            )
        }
        
        # 配置日志
        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__name__)
        
        # 测试结果存储
        self.test_results = {}
        
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            'hardware': {
                'left_arm_ip': '192.168.58.3',
                'right_arm_ip': '192.168.58.2',
                'chassis_ip': '192.168.31.211',
                'chassis_port': 1448
            },
            'execution': {
                'parallel_execution': False,
                'max_workers': 3,
                'timeout_per_test': 300,  # 5分钟
                'retry_failed_tests': True,
                'max_retries': 1
            },
            'reporting': {
                'generate_html_report': True,
                'generate_json_report': True,
                'save_detailed_logs': True,
                'report_directory': './test_reports'
            },
            'log_level': 'INFO'
        }
    
    def load_config_from_file(self, config_file: str):
        """从文件加载配置"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # 合并配置
                self.config.update(file_config)
                self.logger.info(f"已加载配置文件: {config_file}")
            else:
                self.logger.warning(f"配置文件不存在: {config_file}")
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
    
    def list_available_tests(self):
        """列出所有可用的测试"""
        print("=== 可用的测试套件 ===")
        for suite_name, suite_info in self.test_suites.items():
            print(f"\n套件: {suite_name}")
            print(f"名称: {suite_info['name']}")
            print(f"描述: {suite_info['description']}")
            print(f"包含测试: {', '.join(suite_info['tests'])}")
        
        print("\n=== 单独测试项目 ===")
        for test_name in self.test_executors.keys():
            print(f"- {test_name}")
    
    def run_single_test(self, test_name: str, retry_count: int = 0) -> Dict[str, Any]:
        """运行单个测试"""
        test_result = {
            'test_name': test_name,
            'start_time': time.time(),
            'success': False,
            'retry_count': retry_count,
            'error_message': None,
            'duration': 0
        }
        
        try:
            if test_name not in self.test_executors:
                test_result['error_message'] = f"未知的测试: {test_name}"
                return test_result
            
            self.logger.info(f"开始执行测试: {test_name} (重试次数: {retry_count})")
            
            # 创建并运行测试实例
            test_instance = self.test_executors[test_name]()
            result = test_instance.run_test()
            
            # 处理测试结果
            test_result.update({
                'success': result.get('success', False),
                'detailed_result': result,
                'error_message': result.get('error_message') if not result.get('success', False) else None
            })
            
            if test_result['success']:
                self.logger.info(f"测试 {test_name} 执行成功")
            else:
                self.logger.warning(f"测试 {test_name} 执行失败: {test_result['error_message']}")
            
        except Exception as e:
            test_result['error_message'] = f"测试执行异常: {str(e)}"
            self.logger.error(f"测试 {test_name} 执行异常: {str(e)}")
        
        finally:
            test_result['end_time'] = time.time()
            test_result['duration'] = test_result['end_time'] - test_result['start_time']
        
        return test_result
    
    def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """运行测试套件"""
        if suite_name not in self.test_suites:
            raise ValueError(f"未知的测试套件: {suite_name}")
        
        suite_info = self.test_suites[suite_name]
        suite_result = {
            'suite_name': suite_name,
            'suite_info': suite_info,
            'start_time': time.time(),
            'test_results': {},
            'summary': {
                'total_tests': len(suite_info['tests']),
                'passed_tests': 0,
                'failed_tests': 0,
                'success_rate': 0.0
            }
        }
        
        self.logger.info(f"开始执行测试套件: {suite_info['name']}")
        self.logger.info(f"包含 {len(suite_info['tests'])} 个测试项目")
        
        try:
            if self.config['execution']['parallel_execution']:
                # 并行执行
                suite_result['test_results'] = self._run_tests_parallel(suite_info['tests'])
            else:
                # 串行执行
                suite_result['test_results'] = self._run_tests_sequential(suite_info['tests'])
            
            # 计算汇总统计
            for test_name, test_result in suite_result['test_results'].items():
                if test_result['success']:
                    suite_result['summary']['passed_tests'] += 1
                else:
                    suite_result['summary']['failed_tests'] += 1
            
            suite_result['summary']['success_rate'] = (
                suite_result['summary']['passed_tests'] / 
                suite_result['summary']['total_tests'] * 100
            )
            
        except Exception as e:
            suite_result['error'] = str(e)
            self.logger.error(f"执行测试套件时发生异常: {str(e)}")
        
        finally:
            suite_result['end_time'] = time.time()
            suite_result['duration'] = suite_result['end_time'] - suite_result['start_time']
        
        return suite_result
    
    def _run_tests_sequential(self, test_names: List[str]) -> Dict[str, Any]:
        """串行执行测试"""
        results = {}
        
        for test_name in test_names:
            # 执行测试
            result = self.run_single_test(test_name)
            
            # 重试失败的测试
            if (not result['success'] and 
                self.config['execution']['retry_failed_tests'] and
                result['retry_count'] < self.config['execution']['max_retries']):
                
                self.logger.info(f"重试失败的测试: {test_name}")
                result = self.run_single_test(test_name, result['retry_count'] + 1)
            
            results[test_name] = result
            
            # 测试间短暂停顿
            if len(test_names) > 1:
                time.sleep(2)
        
        return results
    
    def _run_tests_parallel(self, test_names: List[str]) -> Dict[str, Any]:
        """并行执行测试"""
        results = {}
        max_workers = min(self.config['execution']['max_workers'], len(test_names))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有测试任务
            future_to_test = {
                executor.submit(self.run_single_test, test_name): test_name
                for test_name in test_names
            }
            
            # 收集结果
            for future in as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    result = future.result(timeout=self.config['execution']['timeout_per_test'])
                    
                    # 重试失败的测试
                    if (not result['success'] and 
                        self.config['execution']['retry_failed_tests'] and
                        result['retry_count'] < self.config['execution']['max_retries']):
                        
                        self.logger.info(f"重试失败的测试: {test_name}")
                        retry_future = executor.submit(self.run_single_test, test_name, result['retry_count'] + 1)
                        result = retry_future.result(timeout=self.config['execution']['timeout_per_test'])
                    
                    results[test_name] = result
                    
                except Exception as e:
                    results[test_name] = {
                        'test_name': test_name,
                        'success': False,
                        'error_message': f"并行执行异常: {str(e)}",
                        'duration': 0
                    }
        
        return results
    
    def generate_reports(self, suite_result: Dict[str, Any]):
        """生成测试报告"""
        try:
            report_dir = Path(self.config['reporting']['report_directory'])
            report_dir.mkdir(exist_ok=True)
            
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            
            # 生成JSON报告
            if self.config['reporting']['generate_json_report']:
                json_file = report_dir / f"test_report_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(suite_result, f, indent=2, ensure_ascii=False, default=str)
                self.logger.info(f"JSON报告已生成: {json_file}")
            
            # 生成HTML报告
            if self.config['reporting']['generate_html_report']:
                html_file = report_dir / f"test_report_{timestamp}.html"
                self._generate_html_report(suite_result, html_file)
                self.logger.info(f"HTML报告已生成: {html_file}")
            
            # 生成控制台摘要
            self._print_test_summary(suite_result)
            
        except Exception as e:
            self.logger.error(f"生成报告时发生异常: {str(e)}")
    
    def _generate_html_report(self, suite_result: Dict[str, Any], html_file: Path):
        """生成HTML格式报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebApp Lua测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; padding: 15px; background-color: #e8f5e8; border-radius: 5px; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .success {{ border-left-color: #4CAF50; background-color: #f9fff9; }}
        .failure {{ border-left-color: #f44336; background-color: #fff9f9; }}
        .details {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WebApp Lua测试报告</h1>
        <p>测试套件: {suite_result['suite_info']['name']}</p>
        <p>执行时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(suite_result['start_time']))}</p>
        <p>总耗时: {suite_result['duration']:.2f}秒</p>
    </div>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <p>总测试数: {suite_result['summary']['total_tests']}</p>
        <p>通过测试: {suite_result['summary']['passed_tests']}</p>
        <p>失败测试: {suite_result['summary']['failed_tests']}</p>
        <p>成功率: {suite_result['summary']['success_rate']:.1f}%</p>
    </div>
    
    <h2>详细结果</h2>
"""
        
        for test_name, test_result in suite_result['test_results'].items():
            status_class = 'success' if test_result['success'] else 'failure'
            status_text = '通过' if test_result['success'] else '失败'
            error_info = f"<p><strong>错误信息:</strong> {test_result['error_message']}</p>" if test_result['error_message'] else ""
            
            html_content += f"""
    <div class="test-result {status_class}">
        <h3>{test_name} - {status_text}</h3>
        <p><strong>执行时间:</strong> {test_result['duration']:.2f}秒</p>
        {error_info}
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _print_test_summary(self, suite_result: Dict[str, Any]):
        """打印测试摘要到控制台"""
        print("\n" + "="*60)
        print(f"测试套件执行完成: {suite_result['suite_info']['name']}")
        print("="*60)
        
        summary = suite_result['summary']
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过测试: {summary['passed_tests']}")
        print(f"失败测试: {summary['failed_tests']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"总耗时: {suite_result['duration']:.2f}秒")
        
        print("\n详细结果:")
        for test_name, test_result in suite_result['test_results'].items():
            status = "✓" if test_result['success'] else "✗"
            duration = test_result['duration']
            print(f"  {status} {test_name}: {'通过' if test_result['success'] else '失败'} ({duration:.1f}s)")
            
            if not test_result['success'] and test_result['error_message']:
                print(f"    错误: {test_result['error_message']}")
        
        print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WebApp Lua测试套件运行器')
    parser.add_argument('--suite', '-s', 
                       choices=['basic', 'coordination', 'vision', 'integration', 'full'],
                       default='basic',
                       help='要执行的测试套件')
    parser.add_argument('--test', '-t',
                       help='执行单个测试 (例如: sat001_left)')
    parser.add_argument('--list', '-l',
                       action='store_true',
                       help='列出所有可用的测试')
    parser.add_argument('--config', '-c',
                       help='配置文件路径')
    parser.add_argument('--parallel', '-p',
                       action='store_true',
                       help='并行执行测试')
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = WebAppLuaTestSuiteRunner()
    
    # 加载配置文件
    if args.config:
        runner.load_config_from_file(args.config)
    
    # 设置并行执行
    if args.parallel:
        runner.config['execution']['parallel_execution'] = True
    
    # 执行命令
    if args.list:
        runner.list_available_tests()
    elif args.test:
        # 执行单个测试
        result = runner.run_single_test(args.test)
        print(f"\n测试结果: {args.test}")
        print(f"状态: {'通过' if result['success'] else '失败'}")
        print(f"耗时: {result['duration']:.2f}秒")
        if not result['success']:
            print(f"错误: {result['error_message']}")
    else:
        # 执行测试套件
        suite_result = runner.run_test_suite(args.suite)
        runner.generate_reports(suite_result)


if __name__ == "__main__":
    main()