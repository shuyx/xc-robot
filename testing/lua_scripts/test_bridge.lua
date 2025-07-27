-- XC-ROBOT 测试桥接脚本
-- 用于Web GUI调用各种测试功能的Lua接口

-- 导入必要的模块
require "json"
local http = require "http"

-- 全局配置
local config = {
    left_arm_ip = "192.168.58.3",
    right_arm_ip = "192.168.58.2",
    chassis_ip = "192.168.31.211:1448",
    test_timeout = 30,
    safe_distance = 300.0  -- 双臂安全距离(mm)
}

-- 测试结果存储
local test_results = {}

-- 日志函数
function log_info(message)
    print("[INFO] " .. message)
    io.flush()
end

function log_error(message)
    print("[ERROR] " .. message)
    io.flush()
end

function log_warning(message)
    print("[WARNING] " .. message)
    io.flush()
end

-- 连接测试函数
function test_connection(device_type, device_ip)
    log_info("开始连接测试: " .. device_type .. " @ " .. device_ip)
    
    local result = {
        device = device_type,
        ip = device_ip,
        status = "failed",
        message = "",
        timestamp = os.time()
    }
    
    if device_type == "fr3_left" or device_type == "fr3_right" then
        -- FR3机械臂连接测试
        result = test_fr3_connection(device_ip, device_type)
    elseif device_type == "chassis" then
        -- Hermes底盘连接测试
        result = test_chassis_connection(device_ip)
    elseif device_type == "vision" then
        -- 视觉模块连接测试
        result = test_vision_connection()
    elseif device_type == "gripper" then
        -- 夹爪连接测试
        result = test_gripper_connection()
    else
        result.message = "未知设备类型: " .. device_type
    end
    
    -- 存储结果
    test_results[device_type] = result
    
    return result
end

-- FR3机械臂连接测试
function test_fr3_connection(ip, arm_type)
    local result = {
        device = arm_type,
        ip = ip,
        status = "testing",
        message = "正在测试FR3连接...",
        timestamp = os.time(),
        details = {}
    }
    
    -- 调用Python测试脚本
    local python_cmd = string.format(
        "cd testing/hardware && python SAT001.py --arm %s --ip %s --lua-mode",
        arm_type == "fr3_left" and "left" or "right",
        ip
    )
    
    log_info("执行命令: " .. python_cmd)
    
    local handle = io.popen(python_cmd)
    local output = handle:read("*a")
    local success = handle:close()
    
    if success then
        result.status = "passed"
        result.message = "FR3连接测试通过"
        result.details.output = output
        log_info("FR3连接测试成功: " .. arm_type)
    else
        result.status = "failed"
        result.message = "FR3连接测试失败"
        result.details.error = output
        log_error("FR3连接测试失败: " .. arm_type)
    end
    
    return result
end

-- 底盘连接测试
function test_chassis_connection(ip)
    local result = {
        device = "chassis",
        ip = ip,
        status = "testing",
        message = "正在测试底盘连接...",
        timestamp = os.time(),
        details = {}
    }
    
    -- 调用底盘状态API
    local curl_cmd = string.format('curl -s -X GET "http://%s/api/core/robot/status" --connect-timeout 5', ip)
    local handle = io.popen(curl_cmd)
    local output = handle:read("*a")
    local success = handle:close()
    
    if success and output and output ~= "" then
        local status_data = json.decode(output)
        if status_data then
            result.status = "passed"
            result.message = "底盘连接正常"
            result.details.status = status_data
            log_info("底盘连接测试成功")
        else
            result.status = "failed"
            result.message = "底盘返回数据格式错误"
            log_error("底盘数据解析失败")
        end
    else
        result.status = "failed"
        result.message = "无法连接到底盘"
        log_error("底盘连接失败")
    end
    
    return result
end

-- 视觉模块连接测试
function test_vision_connection()
    local result = {
        device = "vision",
        status = "testing",
        message = "正在测试视觉模块连接...",
        timestamp = os.time(),
        details = {}
    }
    
    -- 检查Gemini335相关进程或服务
    local ps_cmd = "ps aux | grep -i gemini || ps aux | grep -i vision || echo 'NO_VISION_PROCESS'"
    local handle = io.popen(ps_cmd)
    local output = handle:read("*a")
    handle:close()
    
    if output and not string.find(output, "NO_VISION_PROCESS") then
        result.status = "passed"
        result.message = "视觉模块检测正常"
        result.details.processes = output
        log_info("视觉模块连接测试成功")
    else
        result.status = "warning"
        result.message = "未检测到视觉模块进程"
        log_warning("视觉模块状态未知")
    end
    
    return result
end

-- 夹爪连接测试
function test_gripper_connection()
    local result = {
        device = "gripper",
        status = "testing",
        message = "正在测试夹爪连接...",
        timestamp = os.time(),
        details = {}
    }
    
    -- 检查RS485通信或相关设备文件
    local serial_cmd = "ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo 'NO_SERIAL_DEVICES'"
    local handle = io.popen(serial_cmd)
    local output = handle:read("*a")
    handle:close()
    
    if output and not string.find(output, "NO_SERIAL_DEVICES") then
        result.status = "passed"
        result.message = "检测到串口设备"
        result.details.devices = output
        log_info("夹爪连接测试成功")
    else
        result.status = "warning"
        result.message = "未检测到串口设备"
        log_warning("夹爪连接状态未知")
    end
    
    return result
end

-- 执行测试程序
function run_test_program(test_type, test_file)
    log_info("开始执行测试程序: " .. test_type)
    
    local result = {
        test_type = test_type,
        test_file = test_file,
        status = "running",
        message = "正在执行测试程序...",
        timestamp = os.time(),
        details = {}
    }
    
    local python_script = ""
    
    -- 根据测试类型选择对应的测试脚本
    if test_type == "chassis_test" then
        python_script = "testing/functional/chassis_tests/" .. test_file
    elseif test_type == "left_arm_test" then
        python_script = "testing/hardware/SAT002.py --arm left --ip " .. config.left_arm_ip
    elseif test_type == "right_arm_test" then
        python_script = "testing/hardware/SAT002.py --arm right --ip " .. config.right_arm_ip
    elseif test_type == "dual_arm_test" then
        python_script = string.format(
            "testing/hardware/DAT001.py --left-ip %s --right-ip %s",
            config.left_arm_ip, config.right_arm_ip
        )
    elseif test_type == "function_validation" then
        python_script = "testing/functional/" .. test_file
    elseif test_type == "integration_test" then
        python_script = "testing/integration/" .. test_file
    elseif test_type == "scenario_test" then
        python_script = "testing/scenarios/" .. test_file
    else
        result.status = "failed"
        result.message = "未知的测试类型: " .. test_type
        return result
    end
    
    -- 执行测试脚本
    log_info("执行测试脚本: " .. python_script)
    
    local handle = io.popen("cd /mnt/c/xc\\ robot/mvp-1/xc-robot && python " .. python_script .. " 2>&1")
    local output = handle:read("*a")
    local success = handle:close()
    
    if success then
        result.status = "passed"
        result.message = "测试程序执行完成"
        result.details.output = output
        log_info("测试程序执行成功: " .. test_type)
    else
        result.status = "failed"
        result.message = "测试程序执行失败"
        result.details.error = output
        log_error("测试程序执行失败: " .. test_type)
    end
    
    -- 存储结果
    test_results[test_type .. "_" .. os.time()] = result
    
    return result
end

-- 安全校验函数
function validate_test_safety(test_type, test_params)
    log_info("开始安全校验: " .. test_type)
    
    local safety_result = {
        test_type = test_type,
        safety_status = "checking",
        warnings = {},
        errors = {},
        approved = false
    }
    
    -- 双臂测试安全检查
    if test_type == "dual_arm_test" then
        -- 检查双臂是否在安全位置
        local left_status = get_arm_status(config.left_arm_ip)
        local right_status = get_arm_status(config.right_arm_ip)
        
        if left_status and right_status then
            local distance = calculate_arm_distance(left_status.position, right_status.position)
            if distance < config.safe_distance then
                table.insert(safety_result.errors, "双臂距离过近，当前距离: " .. string.format("%.1f", distance) .. "mm")
            else
                table.insert(safety_result.warnings, "双臂距离正常: " .. string.format("%.1f", distance) .. "mm")
            end
        else
            table.insert(safety_result.warnings, "无法获取双臂状态，请手动确认安全")
        end
    end
    
    -- 底盘测试安全检查
    if test_type == "chassis_test" then
        -- 检查周围环境
        table.insert(safety_result.warnings, "请确保底盘周围无障碍物")
        table.insert(safety_result.warnings, "请确保有足够的移动空间")
    end
    
    -- 运动测试通用安全检查
    if string.find(test_type, "motion") or string.find(test_type, "movement") then
        table.insert(safety_result.warnings, "请确保机器人周围无人员")
        table.insert(safety_result.warnings, "请准备好急停按钮")
    end
    
    -- 判定安全状态
    if #safety_result.errors == 0 then
        safety_result.safety_status = "approved"
        safety_result.approved = true
        log_info("安全校验通过: " .. test_type)
    else
        safety_result.safety_status = "rejected"
        safety_result.approved = false
        log_error("安全校验失败: " .. test_type)
    end
    
    return safety_result
end

-- 获取机械臂状态
function get_arm_status(ip)
    -- 这里应该调用FR3 API获取实际状态
    -- 简化实现，返回模拟数据
    return {
        position = {x = 300, y = 200, z = 400},
        connected = true
    }
end

-- 计算双臂距离
function calculate_arm_distance(pos1, pos2)
    local dx = pos1.x - pos2.x
    local dy = pos1.y - pos2.y
    local dz = pos1.z - pos2.z
    return math.sqrt(dx*dx + dy*dy + dz*dz)
end

-- 获取测试结果
function get_test_results()
    return test_results
end

-- 获取系统日志
function get_system_logs(filter_level, max_lines)
    local logs = {}
    local level_filter = filter_level or "all"
    local line_limit = max_lines or 100
    
    -- 读取测试日志文件
    local log_files = {
        "testing/hardware/logs/",
        "testing/integration/logs/",
        "/var/log/xc-robot/"
    }
    
    for _, log_dir in ipairs(log_files) do
        local ls_cmd = "ls -t " .. log_dir .. "*.log 2>/dev/null | head -5"
        local handle = io.popen(ls_cmd)
        local files = handle:read("*a")
        handle:close()
        
        if files and files ~= "" then
            for file in files:gmatch("[^\r\n]+") do
                local tail_cmd = string.format("tail -n %d %s", line_limit, file)
                local log_handle = io.popen(tail_cmd)
                local content = log_handle:read("*a")
                log_handle:close()
                
                if content then
                    for line in content:gmatch("[^\r\n]+") do
                        if level_filter == "all" or string.find(line:upper(), level_filter:upper()) then
                            table.insert(logs, {
                                timestamp = os.time(),
                                level = extract_log_level(line),
                                message = line,
                                source = file
                            })
                        end
                    end
                end
            end
        end
    end
    
    -- 按时间排序
    table.sort(logs, function(a, b) return a.timestamp > b.timestamp end)
    
    return logs
end

-- 提取日志级别
function extract_log_level(line)
    if string.find(line:upper(), "ERROR") then
        return "ERROR"
    elseif string.find(line:upper(), "WARNING") then
        return "WARNING"
    elseif string.find(line:upper(), "INFO") then
        return "INFO"
    else
        return "DEBUG"
    end
end

-- 主函数：处理Web GUI的调用
function main(action, params)
    local result = {}
    
    if action == "test_connection" then
        result = test_connection(params.device_type, params.device_ip)
    elseif action == "run_test_program" then
        result = run_test_program(params.test_type, params.test_file)
    elseif action == "validate_safety" then
        result = validate_test_safety(params.test_type, params.test_params)
    elseif action == "get_test_results" then
        result = get_test_results()
    elseif action == "get_system_logs" then
        result = get_system_logs(params.filter_level, params.max_lines)
    else
        result = {
            status = "error",
            message = "未知的操作: " .. (action or "nil")
        }
    end
    
    -- 返回JSON格式结果
    print(json.encode(result))
    return result
end

-- 如果直接运行此脚本
if arg and arg[1] then
    local action = arg[1]
    local params = {}
    
    -- 解析参数
    if arg[2] then
        params = json.decode(arg[2]) or {}
    end
    
    main(action, params)
end