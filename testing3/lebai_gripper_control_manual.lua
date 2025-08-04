-- 乐白夹爪手动控制程序
-- 基于手册第4章：编写控制夹爪运动的lua代码文件
-- 用于手册最后的升级lua文件步骤

-- 与机器人控制器建立连接
robot = Robot.RPC('192.168.58.2')  -- 右臂IP
robot.LoggerInit(output_model=0)
robot.SetLoggerLevel(4)

-- 设备ID配置
local DEVICE_ID = 1  -- 右臂设备ID

-- 延时函数
function delay_seconds(seconds)
    Sleep(seconds * 1000)
end

-- 打印日志函数
function log_info(message)
    print("[INFO] " .. os.date("%H:%M:%S") .. " - " .. message)
end

function log_error(message)
    print("[ERROR] " .. os.date("%H:%M:%S") .. " - " .. message)
end

-- 初始化夹爪
function initialize_gripper()
    log_info("=== 开始初始化乐白夹爪 ===")
    
    -- 激活夹爪
    log_info("激活夹爪...")
    local error = robot.ActGripper(DEVICE_ID, 1)
    if error == 0 then
        log_info("✓ 夹爪激活成功")
    else
        log_error("✗ 夹爪激活失败，错误码: " .. error)
        return false
    end
    delay_seconds(2)
    
    -- 关闭自动找行程 (使用指令1)
    log_info("关闭自动找行程...")
    error = robot.MoveGripper(DEVICE_ID, 0, 1, 0, 3000, 0)
    if error == 0 then
        log_info("✓ 关闭自动找行程成功")
    else
        log_info("⚠ 关闭自动找行程返回码: " .. error)
    end
    delay_seconds(1)
    
    -- 执行手动找行程 (使用指令2)
    log_info("执行手动找行程...")
    error = robot.MoveGripper(DEVICE_ID, 0, 2, 0, 5000, 0)
    if error == 0 then
        log_info("✓ 找行程指令发送成功")
    else
        log_info("⚠ 找行程指令返回码: " .. error)
    end
    
    log_info("等待找行程完成...")
    delay_seconds(5)
    
    log_info("=== 夹爪初始化完成 ===")
    return true
end

-- 设置夹爪位置
function set_gripper_position(position, force)
    if force == nil then force = 50 end
    
    -- 参数检查
    if position < 0 then position = 0 end
    if position > 100 then position = 100 end
    if force < 0 then force = 0 end
    if force > 100 then force = 100 end
    
    log_info("设置夹爪 - 位置: " .. position .. "%, 力度: " .. force .. "%")
    
    -- 先设置力度 (指令4)
    local error = robot.MoveGripper(DEVICE_ID, force, 4, 0, 3000, 0)
    if error ~= 0 then
        log_info("⚠ 设置力度返回码: " .. error)
    end
    delay_seconds(0.2)
    
    -- 再设置位置 (指令3)
    error = robot.MoveGripper(DEVICE_ID, position, 3, 0, 3000, 0)
    if error == 0 then
        log_info("✓ 位置设置成功")
    else
        log_info("⚠ 位置设置返回码: " .. error)
    end
    
    return error
end

-- 打开夹爪
function open_gripper(force)
    if force == nil then force = 30 end
    log_info("=== 打开夹爪 ===")
    return set_gripper_position(0, force)
end

-- 闭合夹爪
function close_gripper(force)
    if force == nil then force = 50 end
    log_info("=== 闭合夹爪 ===")
    return set_gripper_position(100, force)
end

-- 半开夹爪
function half_open_gripper(force)
    if force == nil then force = 40 end
    log_info("=== 半开夹爪 ===")
    return set_gripper_position(50, force)
end

-- 读取夹爪状态
function get_gripper_status()
    log_info("=== 读取夹爪状态 ===")
    
    -- 读取位置 (指令7)
    log_info("读取当前位置...")
    local error = robot.MoveGripper(DEVICE_ID, 0, 7, 0, 3000, 0)
    log_info("位置读取返回码: " .. error)
    delay_seconds(0.2)
    
    -- 读取力矩 (指令8)
    log_info("读取当前力矩...")
    error = robot.MoveGripper(DEVICE_ID, 0, 8, 0, 3000, 0)
    log_info("力矩读取返回码: " .. error)
    
    return error
end

-- 测试序列
function test_gripper_sequence()
    log_info("========================================")
    log_info("开始乐白夹爪测试序列")
    log_info("========================================")
    
    -- 初始化
    if not initialize_gripper() then
        log_error("初始化失败，测试终止")
        return false
    end
    
    -- 测试步骤
    local test_steps = {
        {name = "完全打开", func = function() return open_gripper(30) end, wait = 3},
        {name = "完全闭合", func = function() return close_gripper(50) end, wait = 3},
        {name = "半开状态", func = function() return half_open_gripper(40) end, wait = 3},
        {name = "再次打开", func = function() return open_gripper(30) end, wait = 2},
    }
    
    for i, step in ipairs(test_steps) do
        log_info("")
        log_info("步骤 " .. i .. ": " .. step.name)
        step.func()
        
        log_info("等待 " .. step.wait .. " 秒...")
        delay_seconds(step.wait)
        
        -- 读取状态
        get_gripper_status()
    end
    
    log_info("========================================")
    log_info("夹爪测试序列完成!")
    log_info("========================================")
    return true
end

-- 主程序
function main()
    log_info("乐白夹爪控制程序启动")
    log_info("当前时间: " .. os.date())
    log_info("机械臂IP: 192.168.58.2 (右臂)")
    log_info("设备ID: " .. DEVICE_ID)
    
    -- 运行测试序列
    test_gripper_sequence()
    
    log_info("程序执行完毕")
end

-- 执行主程序
main()