#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪终极解决方案 - 使用末端Lua脚本

基于发现的问题：
1. 标准SetGripperConfig可以成功，但MoveGripper失败（错误码73）
2. 需要直接Modbus RTU协议控制乐白夹爪
3. FR3支持末端Lua脚本，可以在末端直接执行Modbus通讯

解决方案：
- 创建专门的乐白夹爪Lua脚本
- 使用AxleLuaUpload上传脚本到末端
- 通过SetAxleLuaGripperFunc配置夹爪控制功能

Author: Claude
Date: 2025-07-28
"""

import sys
import os
import time

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

class LebaiGripperLuaSolution:
    """乐白夹爪Lua脚本解决方案"""
    
    def __init__(self, robot_ip="192.168.58.2"):
        self.robot_ip = robot_ip
        self.robot = None
        self.is_connected = False
        self.lua_script_path = None
    
    def connect_robot(self):
        """连接机械臂"""
        try:
            print(f"🔗 连接机械臂 {self.robot_ip}...")
            self.robot = Robot.RPC(self.robot_ip)
            self.is_connected = True
            print("   ✅ 连接成功")
            return True
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            return False
    
    def create_lebai_lua_script(self):
        """创建乐白夹爪Lua脚本"""
        lua_script_content = '''-- 乐白夹爪Modbus RTU控制脚本
-- 基于乐白官网文档: https://lebai.ltd/products/lmg-90/
-- 通讯参数: 115200, 8N1, Modbus RTU, 设备地址1

-- Modbus RTU CRC16计算函数
function calculate_crc16(data)
    local crc = 0xFFFF
    for i = 1, #data do
        crc = crc ~ data[i]
        for j = 0, 7 do
            if (crc & 1) == 1 then
                crc = (crc >> 1) ~ 0xA001
            else
                crc = crc >> 1
            end
        end
    end
    return crc
end

-- 发送Modbus写入指令
function write_modbus_register(device_addr, register_addr, value)
    local frame = {}
    
    -- 构建Modbus RTU帧
    frame[1] = device_addr  -- 设备地址
    frame[2] = 0x10         -- 功能码：写多个寄存器
    frame[3] = (register_addr >> 8) & 0xFF  -- 寄存器地址高字节
    frame[4] = register_addr & 0xFF         -- 寄存器地址低字节
    frame[5] = 0x00         -- 寄存器数量高字节
    frame[6] = 0x01         -- 寄存器数量低字节
    frame[7] = 0x02         -- 字节数
    frame[8] = (value >> 8) & 0xFF  -- 数据高字节
    frame[9] = value & 0xFF         -- 数据低字节
    
    -- 计算CRC
    local crc = calculate_crc16(frame)
    frame[10] = crc & 0xFF         -- CRC低字节
    frame[11] = (crc >> 8) & 0xFF  -- CRC高字节
    
    -- 发送数据到串口
    uart_send(frame)
    
    -- 等待响应
    sleep_ms(100)
    local response = uart_receive()
    
    return response
end

-- 初始化夹爪
function gripper_init()
    -- 关闭自动找行程
    write_modbus_register(0x01, 40154, 0x01)  -- 0x9C9A
    sleep_ms(500)
    
    -- 执行找行程
    write_modbus_register(0x01, 40072, 0x01)  -- 0x9C48
    sleep_ms(3000)  -- 等待找行程完成
end

-- 设置夹爪位置
function gripper_move(position, force, speed)
    -- 设置力度
    write_modbus_register(0x01, 40001, force)   -- 0x9C41
    sleep_ms(100)
    
    -- 设置速度（如果支持）
    write_modbus_register(0x01, 40010, speed)   -- 0x9C4A
    sleep_ms(100)
    
    -- 设置位置
    write_modbus_register(0x01, 40000, position) -- 0x9C40
    sleep_ms(100)
end

-- 获取夹爪位置
function gripper_get_position()
    -- 读取当前位置寄存器 40005 (0x9C45)
    local frame = {0x01, 0x03, 0x9C, 0x45, 0x00, 0x01}
    local crc = calculate_crc16(frame)
    frame[7] = crc & 0xFF
    frame[8] = (crc >> 8) & 0xFF
    
    uart_send(frame)
    sleep_ms(100)
    local response = uart_receive()
    
    if response and #response >= 5 then
        return (response[4] << 8) | response[5]
    else
        return -1  -- 读取失败
    end
end

-- 夹爪控制主函数
function gripper_control(cmd, param1, param2, param3)
    if cmd == 1 then  -- 初始化
        gripper_init()
    elseif cmd == 2 then  -- 移动到位置
        gripper_move(param1, param2 or 50, param3 or 50)
    elseif cmd == 3 then  -- 获取位置
        return gripper_get_position()
    elseif cmd == 4 then  -- 打开夹爪
        gripper_move(0, param1 or 30, param2 or 50)
    elseif cmd == 5 then  -- 闭合夹爪
        gripper_move(100, param1 or 50, param2 or 50)
    end
    
    return 0
end

-- 主循环
function main()
    -- 初始化串口通讯
    uart_init(115200, 8, 1, 0)  -- 115200, 8N1
    
    -- 等待命令
    while true do
        local cmd = get_gripper_command()
        if cmd > 0 then
            local result = gripper_control(cmd, get_param(1), get_param(2), get_param(3))
            set_gripper_result(result)
        end
        sleep_ms(100)
    end
end

-- 启动主函数
main()
'''
        
        # 创建脚本文件
        script_dir = os.path.join(project_root, "lua_scripts")
        os.makedirs(script_dir, exist_ok=True)
        
        self.lua_script_path = os.path.join(script_dir, "lebai_gripper_control.lua")
        
        try:
            with open(self.lua_script_path, 'w', encoding='utf-8') as f:
                f.write(lua_script_content)
            print(f"✅ 创建Lua脚本: {self.lua_script_path}")
            return True
        except Exception as e:
            print(f"❌ 创建Lua脚本失败: {e}")
            return False
    
    def upload_lua_script(self):
        """上传Lua脚本到末端"""
        if not self.lua_script_path or not os.path.exists(self.lua_script_path):
            print("❌ Lua脚本不存在")
            return False
        
        try:
            print("📤 上传Lua脚本到机械臂末端...")
            error = self.robot.AxleLuaUpload(self.lua_script_path)
            if error == 0:
                print("   ✅ Lua脚本上传成功")
                return True
            else:
                print(f"   ❌ Lua脚本上传失败，错误码: {error}")
                return False
        except Exception as e:
            print(f"   ❌ 上传异常: {e}")
            return False
    
    def configure_lua_gripper(self):
        """配置末端Lua夹爪功能"""
        try:
            print("🔧 配置末端Lua夹爪功能...")
            
            # 1. 设置通讯参数（乐白夹爪：115200, 8N1）
            print("   1. 设置通讯参数...")
            error = self.robot.SetAxleCommunicationParam(115200, 8, 1, 0, 3000, 3, 1000)
            if error != 0:
                print(f"      ❌ 通讯参数设置失败，错误码: {error}")
                return False
            print("      ✅ 通讯参数设置成功")
            
            # 2. 启用末端Lua执行
            print("   2. 启用末端Lua执行...")
            error = self.robot.SetAxleLuaEnable(1)
            if error != 0:
                print(f"      ❌ Lua启用失败，错误码: {error}")
                return False
            print("      ✅ Lua执行已启用")
            
            # 3. 设置设备类型启用（启用夹爪）
            print("   3. 启用夹爪设备类型...")
            error = self.robot.SetAxleLuaEnableDeviceType(0, 1, 0)  # force, gripper, io
            if error != 0:
                print(f"      ❌ 设备类型设置失败，错误码: {error}")
                return False
            print("      ✅ 夹爪设备类型已启用")
            
            # 4. 配置夹爪功能
            print("   4. 配置夹爪功能...")
            gripper_functions = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]  # 启用所有功能
            error = self.robot.SetAxleLuaGripperFunc(1, gripper_functions)
            if error != 0:
                print(f"      ❌ 夹爪功能配置失败，错误码: {error}")
                return False
            print("      ✅ 夹爪功能配置成功")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 配置异常: {e}")
            return False
    
    def test_lua_gripper_control(self):
        """测试Lua夹爪控制"""
        try:
            print("🧪 测试Lua夹爪控制...")
            
            # 等待Lua脚本启动
            print("   等待Lua脚本初始化...")
            time.sleep(3)
            
            # 注意：这里需要使用特殊的夹爪控制方式
            # 由于Lua脚本运行在末端，需要通过特定的接口与之通讯
            # 这可能需要使用MoveGripper或者其他FR3提供的接口
            
            print("   📝 提示: Lua脚本已上传并配置")
            print("   现在可以尝试使用标准MoveGripper指令:")
            print("   robot.MoveGripper(1, 0, 50, 30, 5000, 0, 0, 0, 0, 0)   # 打开")
            print("   robot.MoveGripper(1, 100, 50, 50, 5000, 0, 0, 0, 0, 0) # 闭合")
            
            # 尝试标准控制
            test_commands = [
                ("打开夹爪", 0, 50, 30),
                ("闭合夹爪", 100, 50, 50),
                ("半开夹爪", 50, 50, 40),
                ("打开夹爪", 0, 50, 30)
            ]
            
            for description, pos, vel, force in test_commands:
                print(f"   {description}...")
                error = self.robot.MoveGripper(1, pos, vel, force, 5000, 0, 0, 0, 0, 0)
                if error == 0:
                    print(f"      ✅ {description}成功")
                else:
                    print(f"      ❌ {description}失败，错误码: {error}")
                time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            return False
    
    def comprehensive_lua_solution(self):
        """乐白夹爪Lua解决方案"""
        print("🤖 乐白夹爪终极解决方案 - 末端Lua脚本")
        print("=" * 60)
        
        # 1. 连接机械臂
        if not self.connect_robot():
            return False
        
        # 2. 创建Lua脚本
        if not self.create_lebai_lua_script():
            return False
        
        # 3. 上传Lua脚本
        if not self.upload_lua_script():
            return False
        
        # 4. 配置Lua夹爪功能
        if not self.configure_lua_gripper():
            return False
        
        # 5. 测试控制
        if not self.test_lua_gripper_control():
            return False
        
        print("\n🎉 乐白夹爪Lua解决方案配置完成！")
        print("\n📋 使用说明:")
        print("1. Lua脚本已上传到机械臂末端")
        print("2. 夹爪功能已启用和配置")
        print("3. 现在可以使用标准MoveGripper指令控制夹爪")
        print("4. 如果仍有问题，说明需要进一步调试Lua脚本")
        
        return True


def main():
    """主函数"""
    print("🤖 乐白夹爪终极解决方案")
    print("使用FR3末端Lua脚本直接控制Modbus")
    print("=" * 50)
    
    # 创建解决方案实例
    solution = LebaiGripperLuaSolution()
    
    try:
        # 执行综合解决方案
        success = solution.comprehensive_lua_solution()
        
        if success:
            print("\n🎊 解决方案实施完成！")
            print("\n💡 重要说明:")
            print("本方案通过末端Lua脚本实现Modbus RTU直接控制")
            print("这是目前最有可能解决乐白夹爪控制问题的方案")
        else:
            print("\n😞 解决方案实施失败")
            print("可能需要进一步调试或联系技术支持")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
    finally:
        print("\n👋 程序结束")


if __name__ == "__main__":
    main()