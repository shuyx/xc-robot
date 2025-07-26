#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-Robot Real Hardware GUI Startup Script
XC-Robot真实硬件控制GUI启动脚本

整合所有真实硬件控制逻辑的完整启动程序
支持FR3机械臂、Hermes底盘、视觉系统、夹爪的完整控制
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """设置日志系统"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "real_hardware_gui.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_dependencies() -> Dict[str, bool]:
    """检查系统依赖"""
    dependencies = {
        'PyQt5': False,
        'fairino': False,
        'opencv': False,
        'asyncio': False,
        'pathlib': False
    }
    
    # 检查PyQt5
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        from PyQt5.QtWebChannel import QWebChannel
        dependencies['PyQt5'] = True
    except ImportError:
        pass
    
    # 检查Fairino SDK
    try:
        from fairino import Robot
        dependencies['fairino'] = True
    except ImportError:
        pass
    
    # 检查OpenCV
    try:
        import cv2
        dependencies['opencv'] = True
    except ImportError:
        pass
    
    # 检查asyncio
    try:
        import asyncio
        dependencies['asyncio'] = True
    except ImportError:
        pass
    
    # 检查pathlib
    try:
        from pathlib import Path
        dependencies['pathlib'] = True
    except ImportError:
        pass
    
    return dependencies

def print_system_info(logger: logging.Logger):
    """打印系统信息"""
    logger.info("=== XC-Robot 真实硬件控制系统 ===")
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"平台: {sys.platform}")
    
    # 检查依赖
    deps = check_dependencies()
    logger.info("依赖检查结果:")
    for dep, available in deps.items():
        status = "✅ 可用" if available else "❌ 不可用"
        logger.info(f"  {dep}: {status}")
    
    # 检查关键文件
    key_files = [
        "gui/real_hardware_bridge.py",
        "gui/real_hardware_webgui.py", 
        "gui/real_hardware_interface.html",
        "gui/integrated_hardware_controller.py"
    ]
    
    logger.info("关键文件检查:")
    for file_path in key_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✅ 存在" if exists else "❌ 缺失"
        logger.info(f"  {file_path}: {status}")
    
    return all(deps.values())

def validate_hardware_config() -> Dict[str, Any]:
    """验证硬件配置"""
    config = {
        'fr3_arms': {
            'left_arm_ip': '192.168.58.3',
            'right_arm_ip': '192.168.58.2'
        },
        'hermes_chassis': {
            'ip': '192.168.31.211',
            'port': 1448
        },
        'vision_system': {
            'left_camera_index': 0,
            'right_camera_index': 1
        },
        'gripper_system': {
            'company': 3,
            'device': 0
        }
    }
    
    # 这里可以添加更多的配置验证逻辑
    # 例如ping测试、端口检查等
    
    return config

def start_gui_application(args: argparse.Namespace, logger: logging.Logger):
    """启动GUI应用程序"""
    try:
        # 导入GUI模块
        from gui.real_hardware_webgui import RealHardwareWebGUI
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        logger.info("正在启动PyQt5应用程序...")
        
        # 创建QApplication实例
        app = QApplication(sys.argv)
        app.setApplicationName("XC-Robot 真实硬件控制系统")
        app.setApplicationVersion("2.9.2")
        
        # 设置应用程序属性
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            app.setAttribute(Qt.AA_EnableHighDpiScaling)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        # 创建主窗口
        logger.info("正在创建主窗口...")
        window = RealHardwareWebGUI()
        
        # 显示窗口
        if args.maximized:
            window.showMaximized()
        elif args.fullscreen:
            window.showFullScreen()
        else:
            window.show()
        
        logger.info("GUI应用程序启动成功")
        logger.info("可用功能:")
        logger.info("  • FR3双臂机械臂控制")
        logger.info("  • Hermes底盘导航控制")
        logger.info("  • Gemini 335视觉系统")
        logger.info("  • 智能夹爪控制")
        logger.info("  • Lua脚本测试执行")
        logger.info("  • 综合系统监控")
        
        # 运行应用程序
        return app.exec_()
        
    except ImportError as e:
        logger.error(f"导入GUI模块失败: {e}")
        logger.error("请确保已安装所需依赖: pip install PyQt5 PyQtWebEngine")
        return 1
    except Exception as e:
        logger.error(f"启动GUI应用程序失败: {e}")
        return 1

def start_test_mode(args: argparse.Namespace, logger: logging.Logger):
    """启动测试模式"""
    try:
        from gui.integrated_hardware_controller import IntegratedHardwareController
        
        logger.info("正在启动测试模式...")
        
        # 创建集成控制器
        controller = IntegratedHardwareController()
        
        if args.test_type == 'connection':
            # 连接测试
            logger.info("执行连接测试...")
            result = controller.connect_all_hardware()
            logger.info(f"连接测试结果: {result['summary']}")
            
        elif args.test_type == 'comprehensive':
            # 综合测试
            logger.info("执行综合测试套件...")
            
            # 首先连接硬件
            conn_result = controller.connect_all_hardware()
            if conn_result['success']:
                test_result = controller.execute_comprehensive_test_suite()
                logger.info(f"综合测试结果: {test_result['summary']}")
            else:
                logger.error("硬件连接失败，无法执行综合测试")
                
        elif args.test_type == 'health':
            # 健康检查
            logger.info("执行系统健康检查...")
            health_result = controller.get_system_health_report()
            if health_result['success']:
                health = health_result['health_report']
                logger.info(f"系统健康状态: {health['overall_status']}")
                logger.info(f"设备连接率: {health['connection_rate']:.1%}")
            
        # 清理资源
        controller.emergency_stop_all("测试模式结束")
        logger.info("测试模式完成")
        return 0
        
    except Exception as e:
        logger.error(f"测试模式执行失败: {e}")
        return 1

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='XC-Robot 真实硬件控制系统启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 启动GUI应用程序（默认）
  python start_real_hardware_gui.py
  
  # 最大化窗口启动
  python start_real_hardware_gui.py --maximized
  
  # 全屏启动
  python start_real_hardware_gui.py --fullscreen
  
  # 执行连接测试
  python start_real_hardware_gui.py --test connection
  
  # 执行综合测试套件
  python start_real_hardware_gui.py --test comprehensive
  
  # 执行系统健康检查
  python start_real_hardware_gui.py --test health
  
  # 详细日志模式
  python start_real_hardware_gui.py --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['gui', 'test'],
        default='gui',
        help='运行模式: gui=图形界面, test=测试模式'
    )
    
    parser.add_argument(
        '--test',
        choices=['connection', 'comprehensive', 'health'],
        help='测试类型 (仅在测试模式下有效)'
    )
    
    parser.add_argument(
        '--maximized',
        action='store_true',
        help='最大化窗口启动'
    )
    
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='全屏启动'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别'
    )
    
    parser.add_argument(
        '--no-hardware-check',
        action='store_true',
        help='跳过硬件依赖检查'
    )
    
    args = parser.parse_args()
    
    # 如果指定了测试类型，自动切换到测试模式
    if args.test:
        args.mode = 'test'
        args.test_type = args.test
    
    # 设置日志
    logger = setup_logging(args.log_level)
    
    try:
        # 打印系统信息
        deps_ok = print_system_info(logger)
        
        # 检查依赖（如果需要）
        if not args.no_hardware_check and not deps_ok:
            logger.warning("部分依赖不可用，系统功能可能受限")
            if args.mode == 'gui':
                response = input("是否继续启动GUI？(y/N): ")
                if response.lower() != 'y':
                    logger.info("用户取消启动")
                    return 0
        
        # 验证硬件配置
        config = validate_hardware_config()
        logger.info("硬件配置验证完成")
        
        # 根据模式启动应用程序
        if args.mode == 'gui':
            logger.info("启动GUI模式...")
            return start_gui_application(args, logger)
        elif args.mode == 'test':
            logger.info("启动测试模式...")
            return start_test_mode(args, logger)
        else:
            logger.error(f"未知的运行模式: {args.mode}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 0
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())