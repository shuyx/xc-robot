-- 乐白夹爪Modbus RTU控制脚本
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
