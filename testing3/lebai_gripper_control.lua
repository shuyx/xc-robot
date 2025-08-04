-- 乐白夹爪简单控制脚本
-- 基于手册第4章编写控制夹爪运动的lua代码
-- 实现基本的夹爪开合控制功能

-- 初始化变量
-- ⚠️ 重要：根据你的夹爪连接确定设备ID
-- 如果夹爪连接到右臂(192.168.58.2) → DEVICE_ID = 1
-- 如果夹爪连接到左臂(192.168.58.3) → DEVICE_ID = 2
local DEVICE_ID = 1  -- 右臂配置
local gripper_initialized = false

-- 延时函数
function delay_seconds(seconds)
    DelayMs(seconds * 1000)
end

-- 初始化夹爪函数
function initialize_gripper()
    print("=== 开始初始化乐白夹爪 ===")
    
    -- 步骤1: 关闭自动找行程
    print("1. 关闭自动找行程...")
    local result = robot.SetAxleLuaGripperCmd(DEVICE_ID, 1, 0)  -- 指令1
    if result == 0 then
        print("   ✓ 关闭自动找行程成功")
    else
        print("   ✗ 关闭自动找行程失败, 错误码:", result)
        return false
    end
    delay_seconds(1)
    
    -- 步骤2: 执行手动找行程
    print("2. 执行手动找行程...")
    result = robot.SetAxleLuaGripperCmd(DEVICE_ID, 2, 0)  -- 指令2
    if result == 0 then
        print("   ✓ 找行程指令发送成功")
    else
        print("   ✗ 找行程指令发送失败, 错误码:", result)
        return false
    end
    
    print("   等待找行程完成...")
    delay_seconds(5)  -- 等待找行程完成
    
    gripper_initialized = true
    print("=== 夹爪初始化完成 ===")
    return true
end

-- 设置夹爪位置函数
function set_gripper_position(position, force)
    if not gripper_initialized then
        print("错误: 夹爪未初始化，请先调用 initialize_gripper()")
        return false
    end
    
    -- 参数检查
    if position < 0 then position = 0 end
    if position > 100 then position = 100 end
    if force == nil then force = 50 end  -- 默认力度50%
    if force < 0 then force = 0 end
    if force > 100 then force = 100 end
    
    -- 先设置力度
    print("设置夹爪力度:", force, "%")
    local result = robot.SetAxleLuaGripperCmd(DEVICE_ID, 4, force)  -- 指令4
    if result ~= 0 then
        print("设置力度失败, 错误码:", result)
        return false
    end
    delay_seconds(0.2)
    
    -- 再设置位置
    print("设置夹爪位置:", position, "%")
    result = robot.SetAxleLuaGripperCmd(DEVICE_ID, 3, position)  -- 指令3
    if result == 0 then
        print("   ✓ 位置设置成功")
        return true
    else
        print("   ✗ 位置设置失败, 错误码:", result)
        return false
    end
end

-- 打开夹爪函数
function open_gripper(force)
    if force == nil then force = 30 end  -- 默认较小力度
    print("=== 打开夹爪 ===")
    return set_gripper_position(0, force)  -- 0% = 完全打开
end

-- 闭合夹爪函数  
function close_gripper(force)
    if force == nil then force = 50 end  -- 默认中等力度
    print("=== 闭合夹爪 ===")
    return set_gripper_position(100, force)  -- 100% = 完全闭合
end

-- 半开夹爪函数
function half_open_gripper(force)
    if force == nil then force = 40 end
    print("=== 半开夹爪 ===")
    return set_gripper_position(50, force)  -- 50% = 半开
end

-- 读取夹爪状态函数
function get_gripper_status()
    if not gripper_initialized then
        print("错误: 夹爪未初始化")
        return nil, nil
    end
    
    -- 读取位置
    local pos_result = robot.SetAxleLuaGripperCmd(DEVICE_ID, 7, 0)  -- 指令7
    if pos_result == 0 then
        print("位置读取指令发送成功")
    else
        print("位置读取失败, 错误码:", pos_result)
    end
    
    delay_seconds(0.1)
    
    -- 读取力矩
    local force_result = robot.SetAxleLuaGripperCmd(DEVICE_ID, 8, 0)  -- 指令8
    if force_result == 0 then
        print("力矩读取指令发送成功")
    else
        print("力矩读取失败, 错误码:", force_result)
    end
    
    return pos_result, force_result
end

-- 测试夹爪开合序列
function test_gripper_sequence()
    print("\n" .. "="*50)
    print("开始夹爪开合测试序列")
    print("="*50)
    
    -- 初始化
    if not initialize_gripper() then
        print("初始化失败，测试终止")
        return false
    end
    
    -- 测试序列
    local test_steps = {
        {name = "完全打开", func = function() return open_gripper(30) end, wait = 3},
        {name = "完全闭合", func = function() return close_gripper(50) end, wait = 3},
        {name = "半开状态", func = function() return half_open_gripper(40) end, wait = 3},
        {name = "再次打开", func = function() return open_gripper(30) end, wait = 2},
    }
    
    for i, step in ipairs(test_steps) do
        print("\n步骤", i, ":", step.name)
        if step.func() then
            print("   ✓ 执行成功")
        else
            print("   ✗ 执行失败")
            return false
        end
        
        print("   等待", step.wait, "秒...")
        delay_seconds(step.wait)
        
        -- 读取状态
        get_gripper_status()
    end
    
    print("\n" .. "="*50)
    print("夹爪测试序列完成!")
    print("="*50)
    return true
end

-- 主程序入口
function main()
    print("乐白夹爪控制程序启动")
    print("当前时间:", os.date())
    
    -- 检查机器人连接
    if robot == nil then
        print("错误: 机器人对象未定义，请先建立连接")
        return
    end
    
    -- 运行测试序列
    test_gripper_sequence()
    
    print("程序执行完毕")
end

-- 如果直接运行此脚本，执行主程序
if arg and arg[0] == "lebai_gripper_control.lua" then
    main()
end

-- 导出主要函数供外部调用
return {
    initialize_gripper = initialize_gripper,
    open_gripper = open_gripper,
    close_gripper = close_gripper,
    half_open_gripper = half_open_gripper,
    set_gripper_position = set_gripper_position,
    get_gripper_status = get_gripper_status,
    test_gripper_sequence = test_gripper_sequence
}