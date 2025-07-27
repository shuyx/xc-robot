-- XC-ROBOT 机械臂运动控制Lua脚本
-- 用于Web GUI直接调用控制FR3机械臂运动

-- 导入必要的模块
require "json"
local os = require "os"
local io = require "io"

-- 全局配置
local config = {
    left_arm_ip = "192.168.58.3",
    right_arm_ip = "192.168.58.2",
    default_speed = 20,        -- 默认速度 (度/秒 或 mm/秒)
    safe_joint_limits = {      -- 安全关节限位 (度)
        j1 = {-170, 170},
        j2 = {-120, 120}, 
        j3 = {-166, 166},
        j4 = {-120, 120},
        j5 = {-166, 166},
        j6 = {-180, 180}
    },
    workspace_limits = {       -- 工作空间限制 (mm)
        x = {-800, 800},
        y = {-800, 800}, 
        z = {100, 1000}
    }
}

-- 日志函数
function log_info(message)
    print("[INFO] " .. os.date("%H:%M:%S") .. " " .. message)
    io.flush()
end

function log_error(message)
    print("[ERROR] " .. os.date("%H:%M:%S") .. " " .. message)
    io.flush()
end

function log_warning(message)
    print("[WARNING] " .. os.date("%H:%M:%S") .. " " .. message)
    io.flush()
end

-- 安全检查函数
function check_joint_safety(joint_angles)
    for i, angle in ipairs(joint_angles) do
        local joint_name = "j" .. i
        local limits = config.safe_joint_limits[joint_name]
        
        if limits and (angle < limits[1] or angle > limits[2]) then
            log_error(string.format("关节%d角度超出安全范围: %.2f° (限制: [%.1f°, %.1f°])", 
                i, angle, limits[1], limits[2]))
            return false, string.format("关节%d角度超出安全范围", i)
        end
    end
    return true, "关节角度安全检查通过"
end

function check_cartesian_safety(position)
    local x, y, z = position[1], position[2], position[3]
    
    if x < config.workspace_limits.x[1] or x > config.workspace_limits.x[2] then
        return false, string.format("X坐标超出工作空间: %.1fmm", x)
    end
    
    if y < config.workspace_limits.y[1] or y > config.workspace_limits.y[2] then
        return false, string.format("Y坐标超出工作空间: %.1fmm", y)
    end
    
    if z < config.workspace_limits.z[1] or z > config.workspace_limits.z[2] then
        return false, string.format("Z坐标超出工作空间: %.1fmm", z)
    end
    
    return true, "笛卡尔位置安全检查通过"
end

-- 机械臂控制函数

-- 关节空间运动控制
function move_joints(arm_side, joint_angles, speed)
    log_info(string.format("开始关节运动控制: %s臂", arm_side))
    
    -- 参数验证
    if not joint_angles or #joint_angles ~= 6 then
        return {
            status = "error",
            message = "关节角度参数错误，需要6个关节角度值"
        }
    end
    
    -- 安全检查
    local safe, safety_msg = check_joint_safety(joint_angles)
    if not safe then
        return {
            status = "error", 
            message = safety_msg
        }
    end
    
    -- 确定机械臂IP
    local arm_ip = (arm_side == "left") and config.left_arm_ip or config.right_arm_ip
    local arm_name = (arm_side == "left") and "left" or "right"
    
    -- 构建Python控制脚本命令
    local joint_str = table.concat(joint_angles, ",")
    local python_cmd = string.format(
        "cd testing/hardware && python -c \"" ..
        "import sys; sys.path.insert(0, '../../fr3_control'); " ..
        "from fairino import Robot; " ..
        "robot = Robot.RPC('%s'); " ..
        "result = robot.MoveJ([%s], 0, 0, %d, 0.0, 0.0); " ..
        "robot.CloseRPC(); " ..
        "print('Joint movement result:', result)\"",
        arm_ip, joint_str, speed or config.default_speed
    )
    
    log_info("执行关节运动命令: " .. python_cmd)
    
    -- 执行运动命令
    local handle = io.popen(python_cmd .. " 2>&1")
    local output = handle:read("*a")
    local success = handle:close()
    
    if success then
        log_info(string.format("%s臂关节运动执行成功", arm_name))
        return {
            status = "success",
            message = string.format("%s臂关节运动完成", arm_name),
            arm = arm_name,
            target_joints = joint_angles,
            details = output
        }
    else
        log_error(string.format("%s臂关节运动执行失败", arm_name))
        return {
            status = "error",
            message = string.format("%s臂关节运动失败", arm_name),
            error = output
        }
    end
end

-- 笛卡尔空间运动控制
function move_cartesian(arm_side, position, orientation, speed, motion_type)
    log_info(string.format("开始笛卡尔运动控制: %s臂", arm_side))
    
    -- 参数验证
    if not position or #position ~= 3 then
        return {
            status = "error",
            message = "位置参数错误，需要X,Y,Z三个坐标值"
        }
    end
    
    if not orientation or #orientation ~= 3 then
        return {
            status = "error", 
            message = "姿态参数错误，需要Rx,Ry,Rz三个角度值"
        }
    end
    
    -- 安全检查
    local safe, safety_msg = check_cartesian_safety(position)
    if not safe then
        return {
            status = "error",
            message = safety_msg
        }
    end
    
    -- 确定机械臂IP和运动类型
    local arm_ip = (arm_side == "left") and config.left_arm_ip or config.right_arm_ip
    local arm_name = (arm_side == "left") and "left" or "right"
    local move_func = (motion_type == "linear") and "MoveL" or "MoveJ"  -- 默认关节插补
    
    -- 组合位姿数据
    local pose = {}
    for i = 1, 3 do pose[i] = position[i] end
    for i = 1, 3 do pose[i+3] = orientation[i] end
    local pose_str = table.concat(pose, ",")
    
    -- 构建Python控制脚本命令
    local python_cmd = string.format(
        "cd testing/hardware && python -c \"" ..
        "import sys; sys.path.insert(0, '../../fr3_control'); " ..
        "from fairino import Robot; " ..
        "robot = Robot.RPC('%s'); " ..
        "result = robot.%s([%s], 0, 0, %d, 0.0); " ..
        "robot.CloseRPC(); " ..
        "print('Cartesian movement result:', result)\"",
        arm_ip, move_func, pose_str, speed or config.default_speed
    )
    
    log_info("执行笛卡尔运动命令: " .. python_cmd)
    
    -- 执行运动命令
    local handle = io.popen(python_cmd .. " 2>&1")
    local output = handle:read("*a")
    local success = handle:close()
    
    if success then
        log_info(string.format("%s臂笛卡尔运动执行成功", arm_name))
        return {
            status = "success",
            message = string.format("%s臂笛卡尔运动完成", arm_name),
            arm = arm_name,
            target_position = position,
            target_orientation = orientation,
            motion_type = motion_type,
            details = output
        }
    else
        log_error(string.format("%s臂笛卡尔运动执行失败", arm_name))
        return {
            status = "error",
            message = string.format("%s臂笛卡尔运动失败", arm_name),
            error = output
        }
    end
end

-- 获取机械臂当前状态
function get_arm_status(arm_side)
    log_info(string.format("获取%s臂状态", arm_side))
    
    local arm_ip = (arm_side == "left") and config.left_arm_ip or config.right_arm_ip
    local arm_name = (arm_side == "left") and "left" or "right"
    
    -- 构建Python状态获取命令
    local python_cmd = string.format(
        "cd testing/hardware && python -c \"" ..
        "import sys; sys.path.insert(0, '../../fr3_control'); " ..
        "from fairino import Robot; " ..
        "robot = Robot.RPC('%s'); " ..
        "error, joints = robot.GetActualJointPosDegree(); " ..
        "error2, tcp = robot.GetActualToolFlangePose(); " ..
        "robot_state = robot.robot_state_pkg.robot_state; " ..
        "robot.CloseRPC(); " ..
        "import json; " ..
        "result = {'joints': joints, 'tcp': tcp, 'robot_state': robot_state}; " ..
        "print(json.dumps(result))\"",
        arm_ip
    )
    
    local handle = io.popen(python_cmd .. " 2>&1")
    local output = handle:read("*a")
    local success = handle:close()
    
    if success then
        -- 尝试解析JSON输出
        local status_data = json.decode(output)
        if status_data then
            log_info(string.format("%s臂状态获取成功", arm_name))
            return {
                status = "success",
                arm = arm_name,
                data = {
                    joint_positions = status_data.joints,
                    tcp_position = status_data.tcp,
                    robot_state = status_data.robot_state,
                    timestamp = os.time()
                }
            }
        else
            log_warning(string.format("%s臂状态数据解析失败", arm_name))
            return {
                status = "warning",
                message = "状态数据解析失败",
                raw_output = output
            }
        end
    else
        log_error(string.format("%s臂状态获取失败", arm_name))
        return {
            status = "error",
            message = string.format("%s臂状态获取失败", arm_name),
            error = output
        }
    end
end

-- 机械臂使能/失能控制
function set_arm_enable(arm_side, enable)
    log_info(string.format("%s%s臂", enable and "使能" or "失能", arm_side))
    
    local arm_ip = (arm_side == "left") and config.left_arm_ip or config.right_arm_ip
    local arm_name = (arm_side == "left") and "left" or "right"
    local enable_value = enable and 1 or 0
    
    local python_cmd = string.format(
        "cd testing/hardware && python -c \"" ..
        "import sys; sys.path.insert(0, '../../fr3_control'); " ..
        "from fairino import Robot; " ..
        "robot = Robot.RPC('%s'); " ..
        "result = robot.RobotEnable(%d); " ..
        "robot.CloseRPC(); " ..
        "print('Enable result:', result)\"",
        arm_ip, enable_value
    )
    
    local handle = io.popen(python_cmd .. " 2>&1")
    local output = handle:read("*a")
    local success = handle:close()
    
    if success then
        log_info(string.format("%s臂%s成功", arm_name, enable and "使能" or "失能"))
        return {
            status = "success",
            message = string.format("%s臂%s成功", arm_name, enable and "使能" or "失能"),
            arm = arm_name,
            enabled = enable
        }
    else
        log_error(string.format("%s臂%s失败", arm_name, enable and "使能" or "失能"))
        return {
            status = "error",
            message = string.format("%s臂%s失败", arm_name, enable and "使能" or "失能"),
            error = output
        }
    end
end

-- 紧急停止
function emergency_stop(arm_side)
    log_warning(string.format("紧急停止%s臂", arm_side or "所有"))
    
    local arms_to_stop = {}
    if arm_side then
        table.insert(arms_to_stop, arm_side)
    else
        table.insert(arms_to_stop, "left")
        table.insert(arms_to_stop, "right")
    end
    
    local results = {}
    
    for _, arm in ipairs(arms_to_stop) do
        local arm_ip = (arm == "left") and config.left_arm_ip or config.right_arm_ip
        local arm_name = (arm == "left") and "left" or "right"
        
        local python_cmd = string.format(
            "cd testing/hardware && python -c \"" ..
            "import sys; sys.path.insert(0, '../../fr3_control'); " ..
            "from fairino import Robot; " ..
            "robot = Robot.RPC('%s'); " ..
            "result = robot.StopMotion(); " ..
            "robot.CloseRPC(); " ..
            "print('Emergency stop result:', result)\"",
            arm_ip
        )
        
        local handle = io.popen(python_cmd .. " 2>&1")
        local output = handle:read("*a")
        local success = handle:close()
        
        results[arm_name] = {
            success = success,
            output = output
        }
        
        if success then
            log_info(string.format("%s臂紧急停止成功", arm_name))
        else
            log_error(string.format("%s臂紧急停止失败", arm_name))
        end
    end
    
    return {
        status = "completed",
        message = "紧急停止指令已发送",
        results = results
    }
end

-- 主函数：处理Web GUI的调用
function main(action, params)
    local result = {}
    
    if action == "move_joints" then
        result = move_joints(
            params.arm_side, 
            params.joint_angles, 
            params.speed
        )
    elseif action == "move_cartesian" then
        result = move_cartesian(
            params.arm_side,
            params.position,
            params.orientation, 
            params.speed,
            params.motion_type
        )
    elseif action == "get_status" then
        result = get_arm_status(params.arm_side)
    elseif action == "set_enable" then
        result = set_arm_enable(params.arm_side, params.enable)
    elseif action == "emergency_stop" then
        result = emergency_stop(params.arm_side)
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