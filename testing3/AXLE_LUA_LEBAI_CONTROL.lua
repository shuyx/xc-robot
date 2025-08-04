-- 乐白夹爪控制程序
-- 文件名：AXLE_LUA_LEBAI_CONTROL.lua
-- 实现简单的张开->闭合动作序列
-- 只通过力矩控制，只读取位置和力矩状态

-- 连接机器人
robot = Robot.RPC('192.168.58.2')
robot.LoggerInit(output_model=0)
robot.SetLoggerLevel(4)

-- 激活夹爪
print("=== 激活乐白夹爪 ===")
error = robot.ActGripper(1, 0)  -- 复位
print("复位结果:", error)
Sleep(1000)

error = robot.ActGripper(1, 1)  -- 激活  
print("激活结果:", error)
Sleep(2000)

-- 夹爪动作序列函数
function execute_gripper_sequence()
    print("=== 开始夹爪动作序列 ===")
    
    -- 步骤1: 张开夹爪 (力矩控制25%)
    print("步骤1: 张开夹爪")
    local open_result = robot.MoveGripper(1, 0, 41, 25, 5000, 0)
    print("张开结果:", open_result)
    Sleep(3000)  -- 等待动作完成
    
    -- 读取张开后的状态
    local status_open = robot.GetGripperMotionDone()
    print("张开后状态:", status_open)
    Sleep(1000)
    
    -- 步骤2: 闭合夹爪 (力矩控制50%)
    print("步骤2: 闭合夹爪")
    local close_result = robot.MoveGripper(1, 100, 41, 50, 5000, 0)
    print("闭合结果:", close_result)
    Sleep(3000)  -- 等待动作完成
    
    -- 读取闭合后的状态
    local status_close = robot.GetGripperMotionDone()
    print("闭合后状态:", status_close)
    Sleep(1000)
    
    -- 步骤3: 半开状态 (力矩控制35%)
    print("步骤3: 设置半开状态")
    local half_result = robot.MoveGripper(1, 50, 41, 35, 5000, 0)
    print("半开结果:", half_result)
    Sleep(2000)  -- 等待动作完成
    
    -- 读取最终状态
    local status_half = robot.GetGripperMotionDone()
    print("半开后状态:", status_half)
    
    return open_result, close_result, half_result
end

-- 执行主程序
print("=== AXLE_LUA_LEBAI_CONTROL 启动 ===")
print("时间:", os.date())

-- 执行夹爪动作序列
local result_open, result_close, result_half = execute_gripper_sequence()

-- 输出执行总结
print("=== 执行总结 ===")
print("张开夹爪结果:", result_open)
print("闭合夹爪结果:", result_close)
print("半开夹爪结果:", result_half)

-- 简单的结果判断
if result_open == 0 and result_close == 0 and result_half == 0 then
    print("✓ 所有动作执行成功")
elseif result_open ~= 0 or result_close ~= 0 or result_half ~= 0 then
    print("⚠ 部分动作返回非零代码（可能是正常的状态码）")
end

print("=== 程序执行完毕 ===")
print("AXLE_LUA_LEBAI_CONTROL 结束")