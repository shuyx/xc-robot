#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂开发环境配置脚本
帮助配置法奥意威FR3协作机器人的Python开发环境
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime

def print_banner():
    """打印横幅"""
    print("=" * 70)
    print("    FR3机械臂开发环境配置工具")
    print("    法奥意威 FAIRINO FR3 协作机器人")
    print("=" * 70)
    print(f"    配置时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    操作系统: {platform.system()} {platform.release()}")
    print(f"    Python版本: {sys.version}")
    print("=" * 70)

def check_system_requirements():
    """检查系统要求"""
    print("\n🔍 [步骤1/5] 检查系统要求")
    print("-" * 50)
    
    requirements_met = True
    
    # 检查操作系统
    if platform.system() == "Windows":
        print("  ✅ 操作系统: Windows (支持)")
        
        # 检查架构
        if platform.machine().endswith('64'):
            print("  ✅ 系统架构: 64位 (推荐)")
        else:
            print("  ⚠️  系统架构: 32位 (可能有兼容性问题)")
            
    elif platform.system() == "Linux":
        print("  ✅ 操作系统: Linux (支持)")
    else:
        print(f"  ⚠️  操作系统: {platform.system()} (未测试兼容性)")
    
    # 检查Python版本
    if sys.version_info >= (3, 8):
        print(f"  ✅ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} (符合要求)")
    else:
        print(f"  ❌ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} (需要3.8+)")
        requirements_met = False
    
    # 检查网络连接工具
    try:
        subprocess.run(["ping", "-h"], capture_output=True, timeout=5)
        print("  ✅ 网络测试工具: 可用")
    except:
        print("  ⚠️  网络测试工具: 不可用")
    
    return requirements_met

def setup_fr3_directory_structure():
    """设置FR3目录结构"""
    print("\n📁 [步骤2/5] 设置FR3目录结构")
    print("-" * 50)
    
    # FR3控制相关目录
    directories = [
        "fr3_control",
        "fr3_control/fairino",
        "fr3_control/config",
        "fr3_control/examples",
        "fr3_control/logs",
        "fr3_control/docs"
    ]
    
    created_dirs = []
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"  ✅ 创建目录: {directory}/")
                created_dirs.append(directory)
            else:
                print(f"  ℹ️  目录已存在: {directory}/")
        except Exception as e:
            print(f"  ❌ 创建目录失败: {directory}/ - {e}")
    
    return created_dirs

def download_fr3_sdk():
    """下载/检查FR3 SDK"""
    print("\n📦 [步骤3/5] 配置FR3 SDK")
    print("-" * 50)
    
    print("  📋 FR3 SDK配置说明:")
    print("  1. 请从法奥意威官网下载最新的FR3 SDK")
    print("  2. 网址: https://www.fairino.cn/")
    print("  3. 查找 'FR3机器人' -> '软件下载' -> 'Python SDK'")
    print("  4. 下载后解压到 fr3_control/ 目录")
    print()
    
    # 检查是否已有SDK文件
    sdk_files = [
        "fr3_control/fairino/__init__.py",
        "fr3_control/fairino/Robot.py"
    ]
    
    existing_files = []
    for file_path in sdk_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"  ✅ 已存在: {file_path}")
        else:
            print(f"  ❌ 缺失: {file_path}")
    
    if existing_files:
        print(f"\n  ✅ 找到 {len(existing_files)} 个SDK文件")
    else:
        print(f"\n  ⚠️  未找到SDK文件，需要手动配置")
    
    # 创建基础的fairino __init__.py（如果不存在）
    init_file = "fr3_control/fairino/__init__.py"
    if not os.path.exists(init_file):
        try:
            init_content = '''"""
FAIRINO FR3机器人Python SDK
法奥意威协作机器人控制库
"""

# SDK版本信息
__version__ = "1.0.0"
__author__ = "FAIRINO"

# 导入主要类
try:
    from .Robot import Robot
    print("FAIRINO SDK 导入成功")
except ImportError as e:
    print(f"FAIRINO SDK 导入失败: {e}")
    print("请确保已正确安装FR3 SDK")
'''
            
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(init_content)
            print(f"  ✅ 创建基础 __init__.py")
            
        except Exception as e:
            print(f"  ❌ 创建 __init__.py 失败: {e}")
    
    return len(existing_files) > 0

def create_fr3_config_files():
    """创建FR3配置文件"""
    print("\n⚙️  [步骤4/5] 创建FR3配置文件")
    print("-" * 50)
    
    created_files = []
    
    # 1. 创建机械臂配置文件
    robot_config = """# FR3机械臂配置文件
robots:
  right_arm:
    ip: "192.168.58.2"
    name: "FR3右臂"
    description: "机器人右侧机械臂"
    
  left_arm:
    ip: "192.168.58.3" 
    name: "FR3左臂"
    description: "机器人左侧机械臂"

# 运动参数
motion:
  default_velocity: 20          # 默认速度 (%)
  default_acceleration: 50      # 默认加速度 (%)
  timeout: 30                   # 超时时间 (秒)
  
  # 安全位置（关节角度，单位：度）
  home_position: [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]
  safe_position: [0.0, -30.0, -120.0, -60.0, 90.0, 0.0]

# 工具和用户坐标系
coordinate_systems:
  tool: 0      # 默认工具坐标系
  user: 0      # 默认用户坐标系

# 通信设置
communication:
  connection_timeout: 10        # 连接超时 (秒)
  command_timeout: 5           # 命令超时 (秒)
  retry_attempts: 3            # 重试次数
  
# 日志设置
logging:
  level: "INFO"                # DEBUG, INFO, WARNING, ERROR
  log_to_file: true
  log_file: "fr3_control/logs/fr3_robot.log"
"""
    
    try:
        config_file = "fr3_control/config/robot_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(robot_config)
        print(f"  ✅ 创建机械臂配置: {config_file}")
        created_files.append(config_file)
    except Exception as e:
        print(f"  ❌ 创建配置文件失败: {e}")
    
    # 2. 创建网络配置文件
    network_config = """# FR3网络配置
# 请根据实际网络环境修改IP地址

# 机械臂网络配置
arms:
  right_arm:
    ip: "192.168.58.2"
    port: 20003
    subnet: "192.168.58.0/24"
    
  left_arm:
    ip: "192.168.58.3"  
    port: 20003
    subnet: "192.168.58.0/24"

# 主控PC网络配置
host:
  # 请根据实际情况修改主控PC的IP
  ip: "192.168.58.100"  
  
# 网络测试配置
network_test:
  ping_timeout: 5
  ping_count: 4
  connection_test_timeout: 10

# 防火墙和安全设置提醒
security_notes: |
  1. 确保Windows防火墙允许Python程序访问网络
  2. 确保机械臂和PC在同一网段
  3. 检查网络交换机配置
  4. 机械臂默认端口为20003
"""
    
    try:
        network_file = "fr3_control/config/network_config.yaml"
        with open(network_file, 'w', encoding='utf-8') as f:
            f.write(network_config)
        print(f"  ✅ 创建网络配置: {network_file}")
        created_files.append(network_file)
    except Exception as e:
        print(f"  ❌ 创建网络配置失败: {e}")
    
    # 3. 创建示例代码
    example_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂基础控制示例
演示如何连接和控制FR3机械臂
"""

import sys
import os
import time

# 添加FR3控制路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from fairino import Robot
    print("✅ FR3库导入成功")
except ImportError as e:
    print(f"❌ FR3库导入失败: {e}")
    print("请确保已正确安装和配置FR3 SDK")
    sys.exit(1)

class FR3Controller:
    def __init__(self, robot_ip="192.168.58.2"):
        """
        初始化FR3控制器
        
        Args:
            robot_ip (str): 机械臂IP地址
        """
        self.robot_ip = robot_ip
        self.robot = None
        self.connected = False
    
    def connect(self):
        """连接机械臂"""
        try:
            print(f"正在连接FR3机械臂: {self.robot_ip}")
            self.robot = Robot.RPC(self.robot_ip)
            self.connected = True
            print("✅ 机械臂连接成功")
            return True
        except Exception as e:
            print(f"❌ 机械臂连接失败: {e}")
            self.connected = False
            return False
    
    def get_basic_info(self):
        """获取机械臂基本信息"""
        if not self.connected:
            print("❌ 机械臂未连接")
            return False
        
        try:
            # SDK版本
            sdk_version = self.robot.GetSDKVersion()
            print(f"SDK版本: {sdk_version}")
            
            # 控制器IP
            controller_ip = self.robot.GetControllerIP()
            print(f"控制器IP: {controller_ip}")
            
            return True
        except Exception as e:
            print(f"❌ 获取信息失败: {e}")
            return False
    
    def set_auto_mode(self):
        """设置为自动模式"""
        if not self.connected:
            return False
        
        try:
            ret = self.robot.Mode(0)  # 0为自动模式
            if ret == 0:
                print("✅ 已切换到自动模式")
                return True
            else:
                print(f"❌ 切换模式失败，错误码: {ret}")
                return False
        except Exception as e:
            print(f"❌ 设置模式异常: {e}")
            return False
    
    def enable_robot(self):
        """使能机械臂"""
        if not self.connected:
            return False
        
        try:
            ret = self.robot.RobotEnable(1)  # 1为上使能
            if ret == 0:
                print("✅ 机械臂已使能")
                return True
            else:
                print(f"❌ 使能失败，错误码: {ret}")
                return False
        except Exception as e:
            print(f"❌ 使能异常: {e}")
            return False
    
    def move_to_home(self):
        """移动到初始位置"""
        if not self.connected:
            return False
        
        try:
            # 安全的初始位置（关节角度）
            home_position = [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]
            
            print("⚠️  准备移动到初始位置...")
            print("确保机械臂周围安全！")
            
            user_input = input("继续？(y/N): ").strip().lower()
            if user_input != 'y':
                print("❌ 用户取消运动")
                return False
            
            ret = self.robot.MoveJ(
                joint_pos=home_position,
                tool=0,
                user=0,
                vel=20  # 较慢速度
            )
            
            if ret == 0:
                print("✅ 运动指令发送成功")
                print("等待运动完成...")
                time.sleep(5)  # 等待运动完成
                return True
            else:
                print(f"❌ 运动失败，错误码: {ret}")
                return False
                
        except Exception as e:
            print(f"❌ 运动异常: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.robot and self.connected:
                self.robot.CloseRPC()
                print("✅ 机械臂连接已断开")
            self.connected = False
        except Exception as e:
            print(f"❌ 断开连接异常: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("FR3机械臂基础控制示例")
    print("=" * 60)
    
    # 创建控制器实例
    controller = FR3Controller("192.168.58.2")
    
    try:
        # 1. 连接机械臂
        if not controller.connect():
            return 1
        
        # 2. 获取基本信息
        controller.get_basic_info()
        
        # 3. 设置模式和使能
        controller.set_auto_mode()
        time.sleep(1)
        controller.enable_robot()
        time.sleep(1)
        
        # 4. 询问是否运动测试
        print("\\n" + "="*40)
        print("是否进行运动测试？")
        move_test = input("输入y进行运动测试，其他键跳过: ").strip().lower()
        
        if move_test == 'y':
            controller.move_to_home()
        
        print("\\n✅ 示例程序完成")
        return 0
        
    except KeyboardInterrupt:
        print("\\n⚠️  用户中断程序")
        return 1
    except Exception as e:
        print(f"\\n❌ 程序异常: {e}")
        return 1
    finally:
        # 确保断开连接
        controller.disconnect()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
'''
    
    try:
        example_file = "fr3_control/examples/basic_control_example.py"
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write(example_code)
        print(f"  ✅ 创建示例代码: {example_file}")
        created_files.append(example_file)
    except Exception as e:
        print(f"  ❌ 创建示例代码失败: {e}")
    
    return created_files

def create_fr3_wrapper():
    """创建FR3包装器模块"""
    print("\n🔧 [步骤5/5] 创建FR3包装器模块")
    print("-" * 50)
    
    wrapper_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂包装器模块
提供更友好的API接口和错误处理
"""

import time
import logging
from typing import List, Tuple, Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from fairino import Robot
except ImportError as e:
    logger.error(f"无法导入FR3库: {e}")
    Robot = None

class FR3RobotWrapper:
    """FR3机械臂包装器类"""
    
    def __init__(self, ip: str, name: str = "FR3"):
        """
        初始化FR3机械臂包装器
        
        Args:
            ip (str): 机械臂IP地址
            name (str): 机械臂名称
        """
        self.ip = ip
        self.name = name
        self.robot = None
        self.connected = False
        self.enabled = False
        
        logger.info(f"初始化 {self.name} 机械臂包装器，IP: {self.ip}")
    
    def connect(self, timeout: int = 10) -> bool:
        """
        连接机械臂
        
        Args:
            timeout (int): 连接超时时间
            
        Returns:
            bool: 连接是否成功
        """
        try:
            if Robot is None:
                logger.error("FR3库未正确导入")
                return False
            
            logger.info(f"正在连接 {self.name} ({self.ip})...")
            self.robot = Robot.RPC(self.ip)
            self.connected = True
            
            # 测试连接
            try:
                sdk_version = self.robot.GetSDKVersion()
                logger.info(f"{self.name} 连接成功，SDK版本: {sdk_version}")
                return True
            except Exception as test_e:
                logger.warning(f"{self.name} 连接成功但API测试失败: {test_e}")
                return True  # 连接成功，API可能有问题但不影响基本功能
                
        except Exception as e:
            logger.error(f"{self.name} 连接失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        断开机械臂连接
        
        Returns:
            bool: 断开是否成功
        """
        try:
            if self.robot and self.connected:
                self.robot.CloseRPC()
                logger.info(f"{self.name} 连接已断开")
            
            self.connected = False
            self.enabled = False
            return True
            
        except Exception as e:
            logger.error(f"{self.name} 断开连接失败: {e}")
            return False
    
    def set_mode(self, mode: int = 0) -> bool:
        """
        设置机械臂模式
        
        Args:
            mode (int): 模式 (0=自动, 1=手动)
            
        Returns:
            bool: 设置是否成功
        """
        if not self.connected:
            logger.error(f"{self.name} 未连接")
            return False
        
        try:
            ret = self.robot.Mode(mode)
            if ret == 0:
                mode_name = "自动" if mode == 0 else "手动"
                logger.info(f"{self.name} 已切换到{mode_name}模式")
                return True
            else:
                logger.error(f"{self.name} 设置模式失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"{self.name} 设置模式异常: {e}")
            return False
    
    def enable(self, enable: bool = True) -> bool:
        """
        使能/去使能机械臂
        
        Args:
            enable (bool): True为使能，False为去使能
            
        Returns:
            bool: 操作是否成功
        """
        if not self.connected:
            logger.error(f"{self.name} 未连接")
            return False
        
        try:
            ret = self.robot.RobotEnable(1 if enable else 0)
            if ret == 0:
                action = "使能" if enable else "去使能"
                logger.info(f"{self.name} {action}成功")
                self.enabled = enable
                return True
            else:
                action = "使能" if enable else "去使能"
                logger.error(f"{self.name} {action}失败，错误码: {ret}")
                return False
                
        except Exception as e:
            action = "使能" if enable else "去使能"
            logger.error(f"{self.name} {action}异常: {e}")
            return False
    
    def move_joint(self, joint_pos: List[float], velocity: int = 20, 
                   tool: int = 0, user: int = 0) -> bool:
        """
        关节运动
        
        Args:
            joint_pos (List[float]): 关节位置 [J1, J2, J3, J4, J5, J6]
            velocity (int): 速度百分比 (1-100)
            tool (int): 工具坐标系
            user (int): 用户坐标系
            
        Returns:
            bool: 运动是否成功
        """
        if not self.connected or not self.enabled:
            logger.error(f"{self.name} 未连接或未使能")
            return False
        
        if len(joint_pos) != 6:
            logger.error(f"{self.name} 关节位置参数错误，需要6个值")
            return False
        
        try:
            logger.info(f"{self.name} 开始关节运动: {joint_pos}")
            ret = self.robot.MoveJ(
                joint_pos=joint_pos,
                tool=tool,
                user=user,
                vel=velocity
            )
            
            if ret == 0:
                logger.info(f"{self.name} 关节运动指令发送成功")
                return True
            else:
                logger.error(f"{self.name} 关节运动失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"{self.name} 关节运动异常: {e}")
            return False
    
    def get_joint_position(self) -> Optional[List[float]]:
        """
        获取当前关节位置
        
        Returns:
            Optional[List[float]]: 关节位置或None
        """
        if not self.connected:
            logger.error(f"{self.name} 未连接")
            return None
        
        try:
            # 注意：具体API可能因SDK版本而异
            # 这里提供常见的获取方法
            joint_pos = self.robot.GetActualJointPos()
            logger.debug(f"{self.name} 当前关节位置: {joint_pos}")
            return joint_pos
            
        except Exception as e:
            logger.error(f"{self.name} 获取关节位置失败: {e}")
            return None
    
    def wait_motion_done(self, timeout: int = 30) -> bool:
        """
        等待运动完成
        
        Args:
            timeout (int): 超时时间（秒）
            
        Returns:
            bool: 运动是否完成
        """
        if not self.connected:
            logger.error(f"{self.name} 未连接")
            return False
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                try:
                    motion_done = self.robot.GetRobotMotionDone()
                    if motion_done:
                        logger.info(f"{self.name} 运动完成")
                        return True
                except:
                    # 如果API不可用，使用固定等待时间
                    time.sleep(1)
                    continue
                
                time.sleep(0.1)
            
            logger.warning(f"{self.name} 等待运动完成超时")
            return False
            
        except Exception as e:
            logger.error(f"{self.name} 等待运动完成异常: {e}")
            return False
    
    def emergency_stop(self) -> bool:
        """
        紧急停止
        
        Returns:
            bool: 停止是否成功
        """
        if not self.connected:
            return False
        
        try:
            # 紧急停止API（具体方法可能因SDK版本而异）
            ret = self.robot.StopMotion()
            if ret == 0:
                logger.warning(f"{self.name} 紧急停止成功")
                return True
            else:
                logger.error(f"{self.name} 紧急停止失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"{self.name} 紧急停止异常: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取机械臂状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        status = {
            "name": self.name,
            "ip": self.ip,
            "connected": self.connected,
            "enabled": self.enabled,
            "joint_position": None,
            "motion_done": None
        }
        
        if self.connected:
            try:
                status["joint_position"] = self.get_joint_position()
                status["motion_done"] = self.robot.GetRobotMotionDone()
            except:
                pass
        
        return status

class DualArmController:
    """双臂控制器"""
    
    def __init__(self, right_arm_ip: str = "192.168.58.2", 
                 left_arm_ip: str = "192.168.58.3"):
        """
        初始化双臂控制器
        
        Args:
            right_arm_ip (str): 右臂IP地址
            left_arm_ip (str): 左臂IP地址
        """
        self.right_arm = FR3RobotWrapper(right_arm_ip, "右臂")
        self.left_arm = FR3RobotWrapper(left_arm_ip, "左臂")
        
        logger.info("双臂控制器初始化完成")
    
    def connect_all(self) -> bool:
        """
        连接所有机械臂
        
        Returns:
            bool: 是否至少连接一个机械臂
        """
        right_connected = self.right_arm.connect()
        left_connected = self.left_arm.connect()
        
        if right_connected and left_connected:
            logger.info("双臂连接成功")
            return True
        elif right_connected or left_connected:
            logger.warning("部分机械臂连接成功")
            return True
        else:
            logger.error("所有机械臂连接失败")
            return False
    
    def enable_all(self) -> bool:
        """
        使能所有已连接的机械臂
        
        Returns:
            bool: 操作是否成功
        """
        results = []
        
        if self.right_arm.connected:
            self.right_arm.set_mode(0)  # 自动模式
            time.sleep(0.5)
            results.append(self.right_arm.enable())
        
        if self.left_arm.connected:
            self.left_arm.set_mode(0)  # 自动模式
            time.sleep(0.5)
            results.append(self.left_arm.enable())
        
        return any(results)
    
    def move_to_home(self) -> bool:
        """
        双臂移动到初始位置
        
        Returns:
            bool: 操作是否成功
        """
        home_position = [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]
        results = []
        
        if self.right_arm.connected and self.right_arm.enabled:
            results.append(self.right_arm.move_joint(home_position))
        
        if self.left_arm.connected and self.left_arm.enabled:
            results.append(self.left_arm.move_joint(home_position))
        
        return any(results)
    
    def wait_all_motion_done(self, timeout: int = 30) -> bool:
        """
        等待所有机械臂运动完成
        
        Args:
            timeout (int): 超时时间
            
        Returns:
            bool: 所有运动是否完成
        """
        results = []
        
        if self.right_arm.connected and self.right_arm.enabled:
            results.append(self.right_arm.wait_motion_done(timeout))
        
        if self.left_arm.connected and self.left_arm.enabled:
            results.append(self.left_arm.wait_motion_done(timeout))
        
        return all(results) if results else False
    
    def emergency_stop_all(self) -> bool:
        """
        所有机械臂紧急停止
        
        Returns:
            bool: 操作是否成功
        """
        results = []
        
        if self.right_arm.connected:
            results.append(self.right_arm.emergency_stop())
        
        if self.left_arm.connected:
            results.append(self.left_arm.emergency_stop())
        
        return any(results)
    
    def disconnect_all(self):
        """断开所有连接"""
        self.right_arm.disconnect()
        self.left_arm.disconnect()
        logger.info("双臂连接已断开")
    
    def get_all_status(self) -> Dict[str, Any]:
        """
        获取所有机械臂状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "right_arm": self.right_arm.get_status(),
            "left_arm": self.left_arm.get_status()
        }

# 导出主要类
__all__ = ["FR3RobotWrapper", "DualArmController"]
'''
    
    try:
        wrapper_file = "fr3_control/fr3_wrapper.py"
        with open(wrapper_file, 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
        print(f"  ✅ 创建FR3包装器: {wrapper_file}")
        return True
    except Exception as e:
        print(f"  ❌ 创建包装器失败: {e}")
        return False

def show_configuration_summary():
    """显示配置总结"""
    print("\n" + "=" * 70)
    print("    FR3机械臂环境配置总结")
    print("=" * 70)
    
    print("\n📁 已创建的目录和文件:")
    
    files_to_check = [
        ("fr3_control/", "主控制目录"),
        ("fr3_control/fairino/", "fairino库目录"),
        ("fr3_control/config/", "配置文件目录"),
        ("fr3_control/examples/", "示例代码目录"),
        ("fr3_control/logs/", "日志目录"),
        ("fr3_control/config/robot_config.yaml", "机械臂配置文件"),
        ("fr3_control/config/network_config.yaml", "网络配置文件"),
        ("fr3_control/examples/basic_control_example.py", "基础控制示例"),
        ("fr3_control/fr3_wrapper.py", "FR3包装器模块")
    ]
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {description}: {file_path}")
        else:
            print(f"  ❌ {description}: {file_path} - 未找到")
    
    print(f"\n🚀 下一步操作:")
    print(f"  1. 从法奥意威官网下载FR3 Python SDK")
    print(f"  2. 将SDK文件解压到 fr3_control/fairino/ 目录")
    print(f"  3. 确保包含 Robot.py 等核心文件")
    print(f"  4. 根据实际网络环境修改配置文件中的IP地址")
    print(f"  5. 运行示例代码测试连接: python fr3_control/examples/basic_control_example.py")
    
    print(f"\n🔧 配置检查:")
    print(f"  • 检查机械臂IP地址是否正确")
    print(f"  • 确保PC和机械臂在同一网段")
    print(f"  • 检查防火墙设置")
    print(f"  • 确保机械臂控制器已启动")
    
    print(f"\n💡 使用提示:")
    print(f"  • 使用 fr3_wrapper.py 获得更友好的API")
    print(f"  • 查看 examples/ 目录了解使用方法")
    print(f"  • 修改 config/ 目录中的配置文件")
    print(f"  • 查看 logs/ 目录中的运行日志")

def main():
    """主函数"""
    print_banner()
    
    try:
        # 执行配置步骤
        steps = [
            ("检查系统要求", check_system_requirements),
            ("设置目录结构", setup_fr3_directory_structure),
            ("配置SDK", download_fr3_sdk),
            ("创建配置文件", create_fr3_config_files),
            ("创建包装器", create_fr3_wrapper)
        ]
        
        results = []
        for step_name, step_func in steps:
            print(f"\n正在执行: {step_name}")
            try:
                result = step_func()
                results.append(result)
                print(f"✅ {step_name} 完成")
            except Exception as e:
                print(f"❌ {step_name} 失败: {e}")
                results.append(False)
        
        # 显示总结
        show_configuration_summary()
        
        # 评估整体结果
        success_count = sum(1 for r in results if r)
        total_count = len(results)
        
        if success_count == total_count:
            print(f"\n🎉 FR3环境配置完全成功！")
            print(f"📋 请按照上述说明完成SDK安装")
            return 0
        elif success_count >= total_count * 0.7:
            print(f"\n⚠️  FR3环境配置基本成功 ({success_count}/{total_count})")
            print(f"📋 请解决剩余问题")
            return 0
        else:
            print(f"\n❌ FR3环境配置失败 ({success_count}/{total_count})")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断配置")
        return 1
    except Exception as e:
        print(f"\n❌ 配置过程异常: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)