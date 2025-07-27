#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂Lua程序执行器
直接控制机械臂执行指定的Lua程序文件
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, Any

# 添加FR3控制模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')
sys.path.insert(0, fr3_control_path)

try:
    from fairino import Robot
except ImportError as e:
    print(f"错误: 无法导入fairino模块: {e}")
    print(f"FR3控制路径: {fr3_control_path}")
    print("请确保以下文件存在:")
    print(f"  - {os.path.join(fr3_control_path, 'fairino', 'Robot.py')}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'fr3_lua_executor_{time.strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class FR3LuaExecutor:
    """FR3 Lua程序执行器"""
    
    def __init__(self, robot_ip: str = "192.168.58.2"):
        self.robot_ip = robot_ip
        self.robot: Optional[Robot.RPC] = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """连接到FR3机械臂"""
        try:
            logger.info(f"正在连接到FR3机械臂: {self.robot_ip}")
            self.robot = Robot.RPC(self.robot_ip)
            
            if self.robot is None:
                logger.error("连接失败: 无法建立RPC连接")
                return False
                
            # 设置为自动模式
            result = self.robot.Mode(0)
            logger.info(f"设置自动模式结果: {result}")
            
            self.is_connected = True
            logger.info("成功连接到FR3机械臂并设置为自动模式")
            return True
            
        except Exception as e:
            logger.error(f"连接FR3机械臂失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.robot and self.is_connected:
            try:
                self.robot.CloseRPC()
                logger.info("已断开与FR3机械臂的连接")
            except Exception as e:
                logger.warning(f"断开连接时发生错误: {e}")
            finally:
                self.is_connected = False
                self.robot = None
    
    def print_program_state(self):
        """打印程序状态信息 - 基于官方示例"""
        if not self.is_connected or not self.robot:
            logger.error("机械臂未连接")
            return
        
        try:
            # 按照官方示例格式获取状态
            pstate = self.robot.GetProgramState()  # 查询程序运行状态
            linenum = self.robot.GetCurrentLine()  # 查询当前作业程序执行的行号  
            name = self.robot.GetLoadedProgram()   # 查询已加载的作业程序名
            
            print("the robot program state is:", pstate[1])
            print("the robot program line number is:", linenum[1])
            print("the robot program name is:", name[1])
            
            logger.info(f"程序状态: {pstate[1]}, 执行行号: {linenum[1]}, 程序名: {name[1]}")
            
        except Exception as e:
            logger.error(f"获取程序状态失败: {e}")
    
    def get_program_state(self) -> Dict[str, Any]:
        """获取当前程序状态 - 返回结构化数据"""
        if not self.is_connected or not self.robot:
            return {'error': '机械臂未连接'}
        
        try:
            # 获取程序状态
            pstate = self.robot.GetProgramState()
            linenum = self.robot.GetCurrentLine()
            name = self.robot.GetLoadedProgram()
            
            state_info = {
                'program_state': {
                    'code': pstate[1] if len(pstate) > 1 else None,
                    'description': {1: "程序停止或无程序运行", 2: "程序运行中", 3: "程序暂停"}.get(pstate[1] if len(pstate) > 1 else 0, "未知状态"),
                    'error_code': pstate[0] if len(pstate) > 0 else None
                },
                'current_line': {
                    'line_number': linenum[1] if len(linenum) > 1 else None,
                    'error_code': linenum[0] if len(linenum) > 0 else None
                },
                'loaded_program': {
                    'program_name': name[1] if len(name) > 1 else None,
                    'error_code': name[0] if len(name) > 0 else None
                }
            }
            
            return state_info
            
        except Exception as e:
            logger.error(f"获取程序状态失败: {e}")
            return {'error': str(e)}
    
    def load_lua_program(self, program_path: str) -> bool:
        """加载指定的Lua程序 - 基于官方示例"""
        if not self.is_connected or not self.robot:
            logger.error("机械臂未连接")
            return False
        
        try:
            logger.info(f"正在加载Lua程序: {program_path}")
            ret = self.robot.ProgramLoad(program_path)  # 按照官方示例命名
            print(f"加载要执行的机器人程序错误码: {ret}")
            
            if ret == 0:
                logger.info(f"成功加载程序: {program_path}")
                return True
            else:
                logger.error(f"加载程序失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"加载程序异常: {e}")
            return False
    
    def run_lua_program(self) -> bool:
        """运行当前加载的Lua程序 - 基于官方示例"""
        if not self.is_connected or not self.robot:
            logger.error("机械臂未连接")
            return False
        
        try:
            logger.info("开始执行Lua程序")
            ret = self.robot.ProgramRun()  # 按照官方示例命名
            print(f"执行机器人程序错误码: {ret}")
            
            if ret == 0:
                logger.info("程序开始执行")
                return True
            else:
                logger.error(f"程序执行失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"执行程序异常: {e}")
            return False
    
    def stop_lua_program(self) -> bool:
        """停止当前运行的Lua程序 - 基于官方示例"""
        if not self.is_connected or not self.robot:
            logger.error("机械臂未连接")
            return False
        
        try:
            logger.info("停止Lua程序执行")
            ret = self.robot.ProgramStop()  # 停止正在执行的机器人程序
            print(f"停止正在执行的机器人程序错误码: {ret}")
            
            if ret == 0:
                logger.info("程序已停止")
                return True
            else:
                logger.error(f"停止程序失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"停止程序异常: {e}")
            return False
    
    def pause_lua_program(self) -> bool:
        """暂停当前运行的Lua程序 - 基于官方示例"""
        if not self.is_connected or not self.robot:
            logger.error("机械臂未连接")
            return False
        
        try:
            logger.info("暂停Lua程序执行")
            ret = self.robot.ProgramPause()  # 暂停正在执行的机器人程序
            print(f"暂停正在执行的机器人程序错误码: {ret}")
            
            if ret == 0:
                logger.info("程序已暂停")
                return True
            else:
                logger.error(f"暂停程序失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"暂停程序异常: {e}")
            return False
    
    def resume_lua_program(self) -> bool:
        """恢复暂停的Lua程序 - 基于官方示例"""
        if not self.is_connected or not self.robot:
            logger.error("机械臂未连接")
            return False
        
        try:
            logger.info("恢复Lua程序执行")
            ret = self.robot.ProgramResume()  # 恢复暂停执行的机器人程序
            print(f"恢复暂停执行的机器人程序错误码: {ret}")
            
            if ret == 0:
                logger.info("程序已恢复执行")
                return True
            else:
                logger.error(f"恢复程序失败，错误码: {ret}")
                return False
                
        except Exception as e:
            logger.error(f"恢复程序异常: {e}")
            return False
    
    def monitor_program_execution(self, check_interval: float = 1.0) -> Dict[str, Any]:
        """监控程序执行状态 - 基于官方示例"""
        if not self.is_connected or not self.robot:
            return {'error': '机械臂未连接'}
        
        logger.info("开始监控程序执行状态...")
        execution_log = []
        
        try:
            while True:
                # 使用官方示例的格式打印状态
                print("\n=== 程序状态监控 ===")
                self.print_program_state()
                
                # 同时获取结构化数据用于判断
                state_info = self.get_program_state()
                
                if 'error' in state_info:
                    break
                
                # 记录状态变化
                timestamp = time.strftime("%H:%M:%S")
                log_entry = {
                    'timestamp': timestamp,
                    'state': state_info
                }
                execution_log.append(log_entry)
                
                # 如果程序执行完成或停止，退出监控
                if 'program_state' in state_info and state_info['program_state']['code'] == 1:
                    logger.info("程序执行完成")
                    break
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("用户中断监控")
        except Exception as e:
            logger.error(f"监控程序执行异常: {e}")
        
        return {
            'execution_log': execution_log,
            'final_state': self.get_program_state()
        }
    
    def execute_lua_program(self, program_path: str, monitor: bool = True) -> Dict[str, Any]:
        """完整执行Lua程序流程：加载 -> 运行 -> 监控"""
        logger.info(f"开始执行完整的Lua程序流程: {program_path}")
        
        result = {
            'program_path': program_path,
            'success': False,
            'steps': {}
        }
        
        # 步骤1: 加载程序
        logger.info("=== 步骤1: 加载程序 ===")
        load_success = self.load_lua_program(program_path)
        result['steps']['load'] = load_success
        
        if not load_success:
            result['error'] = '程序加载失败'
            return result
        
        # 步骤2: 运行程序
        logger.info("=== 步骤2: 运行程序 ===")
        run_success = self.run_lua_program()
        result['steps']['run'] = run_success
        
        if not run_success:
            result['error'] = '程序运行失败'
            return result
        
        # 步骤3: 监控执行（可选）
        if monitor:
            logger.info("=== 步骤3: 监控执行 ===")
            monitor_result = self.monitor_program_execution()
            result['steps']['monitor'] = monitor_result
        
        result['success'] = True
        logger.info("Lua程序执行流程完成")
        return result

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("FR3机械臂Lua程序执行器")
        print("\n用法:")
        print("  python fr3_lua_executor.py <command> [options]")
        print("\n命令:")
        print("  execute <program_path>     - 执行指定的Lua程序")
        print("  load <program_path>        - 仅加载程序")
        print("  run                        - 运行当前加载的程序")
        print("  stop                       - 停止当前程序")
        print("  pause                      - 暂停当前程序")
        print("  resume                     - 恢复暂停的程序")
        print("  status                     - 查看程序状态")
        print("  monitor                    - 监控程序执行")
        print("\n示例:")
        print("  python fr3_lua_executor.py execute /fruser/test1.lua")
        print("  python fr3_lua_executor.py status")
        print("  python fr3_lua_executor.py stop")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    robot_ip = "192.168.58.2"  # 默认IP
    
    # 创建执行器实例
    executor = FR3LuaExecutor(robot_ip)
    
    try:
        # 连接到机械臂
        if not executor.connect():
            print("无法连接到FR3机械臂，请检查:")
            print("1. 机械臂IP地址是否正确 (当前: {})".format(robot_ip))
            print("2. 网络连接是否正常")
            print("3. 机械臂是否已开机并启动完成")
            sys.exit(1)
        
        # 执行命令
        if command == "execute":
            if len(sys.argv) < 3:
                print("错误: 请指定要执行的程序路径")
                print("示例: python fr3_lua_executor.py execute /fruser/test1.lua")
                sys.exit(1)
            
            program_path = sys.argv[2]
            result = executor.execute_lua_program(program_path, monitor=True)
            
            if result['success']:
                print(f"程序 {program_path} 执行完成！")
            else:
                print(f"程序执行失败: {result.get('error', '未知错误')}")
        
        elif command == "load":
            if len(sys.argv) < 3:
                print("错误: 请指定要加载的程序路径")
                sys.exit(1)
            
            program_path = sys.argv[2]
            success = executor.load_lua_program(program_path)
            if success:
                print(f"程序 {program_path} 加载成功")
            else:
                print(f"程序 {program_path} 加载失败")
        
        elif command == "run":
            success = executor.run_lua_program()
            if success:
                print("程序开始执行")
            else:
                print("程序执行失败")
        
        elif command == "stop":
            success = executor.stop_lua_program()
            if success:
                print("程序已停止")
            else:
                print("停止程序失败")
        
        elif command == "pause":
            success = executor.pause_lua_program()
            if success:
                print("程序已暂停")
            else:
                print("暂停程序失败")
        
        elif command == "resume":
            success = executor.resume_lua_program()
            if success:
                print("程序已恢复执行")
            else:
                print("恢复程序失败")
        
        elif command == "status":
            state_info = executor.get_program_state()
            if 'error' in state_info:
                print(f"获取状态失败: {state_info['error']}")
            else:
                print("\n=== FR3机械臂程序状态 ===")
                if 'program_state' in state_info:
                    print(f"程序状态: {state_info['program_state']['description']}")
                if 'current_line' in state_info:
                    print(f"执行行号: {state_info['current_line']['line_number']}")
                if 'loaded_program' in state_info:
                    print(f"已加载程序: {state_info['loaded_program']['program_name']}")
                print("========================")
        
        elif command == "monitor":
            result = executor.monitor_program_execution()
            print("监控结束")
        
        else:
            print(f"未知命令: {command}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        logger.error(f"程序执行异常: {e}")
        print(f"执行过程中发生错误: {e}")
    finally:
        executor.disconnect()

if __name__ == "__main__":
    main()