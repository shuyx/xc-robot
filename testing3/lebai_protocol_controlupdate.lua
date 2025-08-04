�U�Z��l-- 乐白夹爪协议控制程序
-- 基于末端协议模板格式
-- 实现简单的张开->闭合动作序列

-- 连接机器人
robot = Robot.RPC('192.168.58.2')
robot.LoggerInit(output_model=0)
robot.SetLoggerLevel(4)

-- 激活夹爪
print("=== 激活夹爪 ===")
error = robot.ActGripper(1, 0)  -- 复位
print("复位结果:", error)
Sleep(1000)

error = robot.ActGripper(1, 1)  -- 激活  
print("激活结果:", error)
Sleep(2000)

-- 动作序列函数
function gripper_sequence()
    print("=== 开始夹爪动作序列 ===")
    
    -- 步骤1: 张开夹爪 (力矩控制)
    print("步骤1: 张开夹爪")
    local error1 = robot.MoveGripper(1, 0, 41, 25, 5000, 0)  -- 张开，力矩25%
    print("张开结果:", error1)
    Sleep(3000)
    
    -- 读取状态
    local status1 = robot.GetGripperMotionDone()
    print("张开后状态:", status1)
    Sleep(500)
    
    -- 步骤2: 闭合夹爪 (力矩控制)
    print("步骤2: 闭合夹爪")
    local error2 = robot.MoveGripper(1, 100, 41, 50, 5000, 0)  -- 闭合，力矩50%
    print("闭合结果:", error2)
    Sleep(3000)
    
    -- 读取状态
    local status2 = robot.GetGripperMotionDone()
    print("闭合后状态:", status2)
    Sleep(500)
    
    -- 步骤3: 半开状态
    print("步骤3: 半开状态")
    local error3 = robot.MoveGripper(1, 50, 41, 35, 5000, 0)  -- 半开，力矩35%
    print("半开结果:", error3)
    Sleep(2000)
    
    -- 读取最终状态
    local status3 = robot.GetGripperMotionDone()
    print("半开后状态:", status3)
    
    return error1, error2, error3
end

-- 执行动作序列
local result1, result2, result3 = gripper_sequence()

-- 输出总结
print("=== 动作序列完成 ===")
print("张开结果:", result1)
print("闭合结果:", result2) 
print("半开结果:", result3)
print("程序执行完毕")

-- 简单的错误检查
if result1 == 0 and result2 == 0 and result3 == 0 then
    print("✓ 所有动作执行成功")
else
    print("⚠ 部分动作可能有警告或错误")
end