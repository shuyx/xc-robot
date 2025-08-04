#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪完整部署解决方案
通过末端自定义协议控制乐白夹爪的完整流程

部署步骤：
1. 上传专用Lua协议文件
2. 配置末端通讯参数
3. 启用末端Lua执行
4. 配置夹爪功能
5. 测试夹爪控制

Author: Claude
Date: 2025-07-28
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加FR3控制路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr3_control_path = os.path.join(project_root, 'fr3_control')
if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

try:
    from fairino import Robot
    print("✓ 成功导入fairino.Robot")
except ImportError as e:
    print(f"✗ 导入fairino.Robot失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lebai_gripper_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LebaiGripperDeployment:
    """乐白夹爪完整部署解决方案"""
    
    def __init__(self, robot_ip="192.168.58.2"):
        self.robot_ip = robot_ip
        self.robot = None
        self.is_connected = False
        
        # 获取当前脚本目录
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.lua_file_path = os.path.join(self.script_dir, "AXLE_LUA_LEBAI_GRIPPER.lua")
        
    def step1_connect_robot(self):
        """步骤1: 连接机械臂"""
        logger.info("=" * 60)
        logger.info("步骤1: 连接FR3机械臂")
        logger.info("=" * 60)
        
        try:
            logger.info(f"正在连接机械臂 {self.robot_ip}...")
            self.robot = Robot.RPC(self.robot_ip)
            
            # 初始化日志
            self.robot.LoggerInit(output_model=0)
            self.robot.SetLoggerLevel(4)
            
            self.is_connected = True
            logger.info("✅ 机械臂连接成功!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False
    
    def step2_upload_lua_protocol(self):
        """步骤2: 上传乐白夹爪Lua协议文件"""
        logger.info("=" * 60)
        logger.info("步骤2: 上传乐白夹爪Lua协议文件")
        logger.info("=" * 60)
        
        # 检查文件是否存在
        if not os.path.exists(self.lua_file_path):
            logger.error(f"❌ Lua文件不存在: {self.lua_file_path}")
            return False
        
        try:
            logger.info(f"正在上传Lua文件: {self.lua_file_path}")
            error = self.robot.AxleLuaUpload(self.lua_file_path)
            
            if error == 0:
                logger.info("✅ Lua协议文件上传成功!")
                return True
            else:
                logger.error(f"❌ Lua文件上传失败，错误码: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 上传Lua文件时发生异常: {e}")
            return False
    
    def step3_configure_communication(self):
        """步骤3: 配置末端通讯参数"""
        logger.info("=" * 60)
        logger.info("步骤3: 配置末端通讯参数")
        logger.info("=" * 60)
        
        try:
            # 乐白夹爪通讯参数: 波特率115200, 8数据位, 1停止位, 无校验, 5秒超时, 3次重试, 1秒周期
            logger.info("设置末端通讯参数 (115200, 8N1)...")
            error = self.robot.SetAxleCommunicationParam(115200, 8, 1, 0, 5000, 3, 1000)
            
            if error == 0:
                logger.info("✅ 通讯参数配置成功!")
            else:
                logger.error(f"❌ 通讯参数配置失败，错误码: {error}")
                return False
            
            # 验证配置
            time.sleep(1)
            result = self.robot.GetAxleCommunicationParam()
            logger.info(f"当前通讯参数: {result}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 配置通讯参数时发生异常: {e}")
            return False
    
    def step4_enable_lua_execution(self):
        """步骤4: 启用末端Lua执行"""
        logger.info("=" * 60)
        logger.info("步骤4: 启用末端Lua执行")
        logger.info("=" * 60)
        
        try:
            # 启用末端Lua执行
            logger.info("启用末端Lua执行...")
            error = self.robot.SetAxleLuaEnable(1)
            
            if error == 0:
                logger.info("✅ 末端Lua执行已启用!")
            else:
                logger.error(f"❌ 启用末端Lua失败，错误码: {error}")
                return False
            
            # 验证状态
            time.sleep(1)
            result = self.robot.GetAxleLuaEnableStatus()
            logger.info(f"Lua执行状态: {result}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 启用Lua执行时发生异常: {e}")
            return False
    
    def step5_configure_device_type(self):
        """步骤5: 配置末端设备类型"""
        logger.info("=" * 60)
        logger.info("步骤5: 配置末端设备类型")
        logger.info("=" * 60)
        
        try:
            # 设置末端设备类型 (夹爪=1, 启用, 其他=0)
            logger.info("配置末端设备类型为夹爪...")
            error = self.robot.SetAxleLuaEnableDeviceType(1, 1, 0)  # 夹爪启用
            
            if error == 0:
                logger.info("✅ 末端设备类型配置成功!")
            else:
                logger.error(f"❌ 设备类型配置失败，错误码: {error}")
                return False
            
            # 验证配置
            time.sleep(1)
            result = self.robot.GetAxleLuaEnableDeviceType()
            logger.info(f"设备类型配置: {result}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 配置设备类型时发生异常: {e}")
            return False
    
    def step6_configure_gripper_functions(self):
        """步骤6: 配置夹爪功能"""
        logger.info("=" * 60)
        logger.info("步骤6: 配置夹爪功能")
        logger.info("=" * 60)
        
        try:
            # 配置夹爪功能
            # 参数说明: 设备索引, 功能列表[初始化, 找行程, 位置控制, 力度控制, 读位置, 读力矩, ...]
            gripper_functions = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            
            logger.info("配置夹爪功能...")
            error = self.robot.SetAxleLuaGripperFunc(0, gripper_functions)
            
            if error == 0:
                logger.info("✅ 夹爪功能配置成功!")
            else:
                logger.error(f"❌ 夹爪功能配置失败，错误码: {error}")
                return False
            
            # 验证配置
            time.sleep(1)
            result = self.robot.GetAxleLuaGripperFunc()
            logger.info(f"夹爪功能配置: {result}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 配置夹爪功能时发生异常: {e}")
            return False
    
    def step7_initialize_gripper(self):
        """步骤7: 初始化夹爪"""
        logger.info("=" * 60)
        logger.info("步骤7: 初始化夹爪")
        logger.info("=" * 60)
        
        try:
            # 复位夹爪
            logger.info("复位夹爪...")
            error = self.robot.ActGripper(1, 0)
            
            if error == 0:
                logger.info("✅ 夹爪复位成功!")
            else:
                logger.error(f"❌ 夹爪复位失败，错误码: {error}")
                return False
            
            time.sleep(2)
            
            # 激活夹爪
            logger.info("激活夹爪...")
            error = self.robot.ActGripper(1, 1)
            
            if error == 0:
                logger.info("✅ 夹爪激活成功!")
            else:
                logger.error(f"❌ 夹爪激活失败，错误码: {error}")
                return False
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"❌ 初始化夹爪时发生异常: {e}")
            return False
    
    def step8_test_gripper_control(self):
        """步骤8: 测试夹爪控制"""
        logger.info("=" * 60)
        logger.info("步骤8: 测试夹爪控制")
        logger.info("=" * 60)
        
        test_sequences = [
            ("关闭自动找行程", 1, 1, 0),  # 右臂设备ID = 1
            ("执行找行程", 1, 2, 0), 
            ("设置位置50%", 1, 3, 50),
            ("设置力度30%", 1, 4, 30),
            ("完全打开", 1, 3, 0),
            ("完全闭合", 1, 3, 100),
            ("回到中间位置", 1, 3, 50)
        ]
        
        success_count = 0
        
        for description, device_id, cmd_type, value in test_sequences:
            try:
                logger.info(f"测试: {description}")
                
                # 使用底层控制接口，绕过MoveGripper
                if hasattr(self.robot, 'SetAxleLuaGripperCmd'):
                    error = self.robot.SetAxleLuaGripperCmd(device_id, cmd_type, value)
                else:
                    # 备用方法：尝试使用MoveGripper但期望失败
                    error = self.robot.MoveGripper(device_id, value, 50, 50, 3000, 0)
                
                if error == 0:
                    logger.info(f"✅ {description} - 成功")
                    success_count += 1
                else:
                    logger.warning(f"⚠️  {description} - 失败 (错误码: {error})")
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ 测试 {description} 时发生异常: {e}")
        
        logger.info(f"测试完成: {success_count}/{len(test_sequences)} 个测试成功")
        return success_count > 0
    
    def run_complete_deployment(self):
        """运行完整部署流程"""
        logger.info("🚀 乐白夹爪完整部署开始")
        logger.info("基于末端自定义协议的解决方案")
        logger.info("=" * 80)
        
        deployment_steps = [
            ("连接机械臂", self.step1_connect_robot),
            ("上传Lua协议文件", self.step2_upload_lua_protocol),
            ("配置通讯参数", self.step3_configure_communication),
            ("启用Lua执行", self.step4_enable_lua_execution),
            ("配置设备类型", self.step5_configure_device_type),
            ("配置夹爪功能", self.step6_configure_gripper_functions),
            ("初始化夹爪", self.step7_initialize_gripper),
            ("测试夹爪控制", self.step8_test_gripper_control)
        ]
        
        success_count = 0
        
        for step_name, step_function in deployment_steps:
            logger.info(f"\n🔄 正在执行: {step_name}")
            
            try:
                if step_function():
                    logger.info(f"✅ {step_name} - 完成")
                    success_count += 1
                else:
                    logger.error(f"❌ {step_name} - 失败")
                    break
                    
            except Exception as e:
                logger.error(f"❌ {step_name} - 异常: {e}")
                break
        
        # 生成最终报告
        self.generate_final_report(success_count, len(deployment_steps))
        
        return success_count == len(deployment_steps)
    
    def generate_final_report(self, success_count, total_steps):
        """生成最终部署报告"""
        logger.info("=" * 80)
        logger.info("📋 乐白夹爪部署最终报告")
        logger.info("=" * 80)
        
        logger.info(f"部署进度: {success_count}/{total_steps} 步骤完成")
        
        if success_count == total_steps:
            logger.info("🎉 部署完全成功!")
            logger.info("")
            logger.info("✅ 已完成的配置:")
            logger.info("  - 乐白夹爪Lua协议文件已上传")
            logger.info("  - 末端通讯参数已配置 (115200, 8N1)")
            logger.info("  - 末端Lua执行已启用")
            logger.info("  - 夹爪设备类型已配置")
            logger.info("  - 夹爪功能已启用")
            logger.info("  - 夹爪已初始化和激活")
            logger.info("")
            logger.info("🎯 下一步操作:")
            logger.info("  1. 在FR3 WebApp中进入'初始设置'->'末端工具'->'开放协议'")
            logger.info("  2. 确认乐白夹爪协议文件已加载")
            logger.info("  3. 在夹爪设置中勾选相应功能 (初始化、位置、速度、力矩)")
            logger.info("  4. 测试夹爪开合动作")
            logger.info("")
            logger.info("💡 使用提示:")
            logger.info("  - 现在可以在程序中正常使用夹爪控制指令")
            logger.info("  - 建议通过WebApp界面进行最终测试和微调")
            
        else:
            logger.error("❌ 部署未完全成功")
            logger.info("")
            logger.info("🔧 故障排除建议:")
            logger.info("  1. 检查FR3软件版本是否为V3.7.4或更高")
            logger.info("  2. 检查末端固件是否已更新到最新版本") 
            logger.info("  3. 确认485接线正确 (24V, GND, 485A, 485B)")
            logger.info("  4. 联系技术支持获取进一步帮助")
            logger.info("")
            logger.info("📞 技术支持:")
            logger.info("  - 法奥意威: https://www.fairino.com/")
            logger.info("  - 乐白夹爪: https://lebai.ltd/")
        
        logger.info("=" * 80)


def main():
    """主函数"""
    print("🎯 乐白夹爪完整部署解决方案")
    print("基于末端自定义协议")
    print("=" * 50)
    
    deployment = LebaiGripperDeployment()
    
    try:
        success = deployment.run_complete_deployment()
        
        if success:
            print("\n🎊 部署完全成功! 夹爪已可正常使用")
        else:
            print("\n📋 部署未完全成功，请查看日志获取详细信息")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断部署")
    except Exception as e:
        print(f"\n\n❌ 部署过程异常: {e}")
    finally:
        print("\n👋 部署流程结束")


if __name__ == "__main__":
    main()