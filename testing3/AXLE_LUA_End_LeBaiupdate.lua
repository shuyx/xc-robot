�U�Z.G�X-- =============================================================================
-- 乐白夹爪末端通讯协议 (LeBai Gripper End Protocol)
-- 版本: 1.0
-- 适用: FR3机器人控制器
-- 协议: Modbus RTU, 115200bps, 8N1
-- 设备地址: 1-8 (可配置)
-- 开发: 基于FR3官方末端协议模板
-- =============================================================================

-- 获取机器人发送的控制命令
-- Rcmd1: 命令类型 (1=夹爪控制)
-- Rcmd2: 设备地址 (1-8)
-- Rcmd3: 功能码 (1-12对应不同操作)
-- Rcmd4: 参数值 (0-100)
Rcmd1,Rcmd2,Rcmd3,Rcmd4 = GetGripCmd()

-- =============================================================================
-- 命令数组定义 (基于乐白夹爪Modbus寄存器)
-- =============================================================================

-- T1: 夹爪激活命令 (写入状态寄存器，激活夹爪)
T1 = {0x01,0x10,0x9C,0x9A,0x00,0x01,0x02,0x00,0x01,0x00,0x00}

-- T2: 夹爪复位命令 (复位夹爪到初始状态)
T2 = {0x01,0x10,0x9C,0x9A,0x00,0x01,0x02,0x00,0x00,0x00,0x00}

-- T3: 位置控制命令 (寄存器40000, 0x9C40)
T3 = {0x01,0x10,0x9C,0x40,0x00,0x01,0x02,0x00,0x64,0x00,0x00}

-- T4: 力度控制命令 (寄存器40001, 0x9C41)
T4 = {0x01,0x10,0x9C,0x41,0x00,0x01,0x02,0x00,0x32,0x00,0x00}

-- T5: 速度控制命令 (寄存器40010, 0x9C4A)
T5 = {0x01,0x10,0x9C,0x4A,0x00,0x01,0x02,0x00,0x32,0x00,0x00}

-- T6: 读取当前位置命令 (寄存器40005, 0x9C45)
T6 = {0x01,0x03,0x9C,0x45,0x00,0x01,0x00,0x00}

-- T7: 读取当前力矩命令 (寄存器40006, 0x9C46)
T7 = {0x01,0x03,0x9C,0x46,0x00,0x01,0x00,0x00}

-- T8: 读取夹爪状态命令 (寄存器40020, 0x9C54)
T8 = {0x01,0x03,0x9C,0x54,0x00,0x01,0x00,0x00}

-- T9: 综合状态查询命令 (读取多个寄存器)
T9 = {0x01,0x03,0x9C,0x45,0x00,0x03,0x00,0x00}

-- T10: 停止命令 (紧急停止夹爪运动)
T10 = {0x01,0x10,0x9C,0x42,0x00,0x01,0x02,0x00,0x01,0x00,0x00}

-- T11: 保留命令
T11 = {0x01,0x03,0x9C,0x47,0x00,0x01,0x00,0x00}

-- =============================================================================
-- 主控制逻辑
-- =============================================================================

if(Rcmd1==1) then
    -- 设置所有命令数组的设备地址
    T1[1] = Rcmd2
    T2[1] = Rcmd2
    T3[1] = Rcmd2
    T4[1] = Rcmd2
    T5[1] = Rcmd2
    T6[1] = Rcmd2
    T7[1] = Rcmd2
    T8[1] = Rcmd2
    T9[1] = Rcmd2
    T10[1] = Rcmd2
    T11[1] = Rcmd2
    
    -- 功能码1: 夹爪激活
    if(Rcmd3==1) then
        -- 计算CRC校验
        T1[10],T1[11] = CrcValue(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6],T1[7],T1[8],T1[9])
        -- 发送激活命令
        EndTxGripData(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6],T1[7],T1[8],T1[9],T1[10],T1[11])
        -- 延时等待响应
        DelayMs(100)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 状态反馈: 激活成功返回1
        if(A==1) then
            GripStateBack(1)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码2: 夹爪复位
    if(Rcmd3==2) then
        -- 计算CRC校验
        T2[10],T2[11] = CrcValue(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6],T2[7],T2[8],T2[9])
        -- 发送复位命令
        EndTxGripData(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6],T2[7],T2[8],T2[9],T2[10],T2[11])
        -- 延时等待响应
        DelayMs(100)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 状态反馈
        if(A==1) then
            GripStateBack(1)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码3: 位置控制
    if(Rcmd3==3) then
        -- 位置参数处理 (Web界面0-100% 直接对应乐白夹爪0-100)
        local position = Rcmd4
        if(position > 100) then position = 100 end
        if(position < 0) then position = 0 end
        
        -- 设置位置值 (乐白夹爪直接使用0-100范围)
        T3[9] = position
        
        -- 计算CRC校验
        T3[10],T3[11] = CrcValue(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6],T3[7],T3[8],T3[9])
        -- 发送位置控制命令
        EndTxGripData(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6],T3[7],T3[8],T3[9],T3[10],T3[11])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 状态反馈
        if(A==1) then
            GripStateBack(position)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码4: 速度控制
    if(Rcmd3==4) then
        -- 速度参数处理 (0-100%)
        local speed = Rcmd4
        if(speed > 100) then speed = 100 end
        if(speed < 0) then speed = 0 end
        
        -- 设置速度值
        T5[9] = speed
        
        -- 计算CRC校验
        T5[10],T5[11] = CrcValue(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6],T5[7],T5[8],T5[9])
        -- 发送速度控制命令
        EndTxGripData(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6],T5[7],T5[8],T5[9],T5[10],T5[11])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 状态反馈
        if(A==1) then
            GripStateBack(speed)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码5: 力矩控制
    if(Rcmd3==5) then
        -- 力矩参数处理 (0-100%)
        local force = Rcmd4
        if(force > 100) then force = 100 end
        if(force < 0) then force = 0 end
        
        -- 设置力矩值
        T4[9] = force
        
        -- 计算CRC校验
        T4[10],T4[11] = CrcValue(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6],T4[7],T4[8],T4[9])
        -- 发送力矩控制命令
        EndTxGripData(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6],T4[7],T4[8],T4[9],T4[10],T4[11])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 状态反馈
        if(A==1) then
            GripStateBack(force)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码7: 读取当前位置
    if(Rcmd3==7) then
        -- 计算CRC校验
        T6[7],T6[8] = CrcValue(T6[1],T6[2],T6[3],T6[4],T6[5],T6[6])
        -- 发送位置查询命令
        EndTxGripData(T6[1],T6[2],T6[3],T6[4],T6[5],T6[6],T6[7],T6[8])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 解析位置数据 (16位数据，高字节+低字节)
        if(A==1) then
            local current_pos = Rxd4 * 256 + Rxd5
            -- 乐白夹爪位置范围0-100，直接返回
            if(current_pos > 100) then current_pos = 100 end
            GripStateBack(current_pos)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码8: 读取当前力矩
    if(Rcmd3==8) then
        -- 计算CRC校验
        T7[7],T7[8] = CrcValue(T7[1],T7[2],T7[3],T7[4],T7[5],T7[6])
        -- 发送力矩查询命令
        EndTxGripData(T7[1],T7[2],T7[3],T7[4],T7[5],T7[6],T7[7],T7[8])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 解析力矩数据
        if(A==1) then
            local current_force = Rxd4 * 256 + Rxd5
            -- 乐白夹爪力矩范围0-100，直接返回
            if(current_force > 100) then current_force = 100 end
            GripStateBack(current_force)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码9: 读取夹爪状态
    if(Rcmd3==9) then
        -- 计算CRC校验
        T8[7],T8[8] = CrcValue(T8[1],T8[2],T8[3],T8[4],T8[5],T8[6])
        -- 发送状态查询命令
        EndTxGripData(T8[1],T8[2],T8[3],T8[4],T8[5],T8[6],T8[7],T8[8])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 解析状态数据
        if(A==1) then
            local status = Rxd4 * 256 + Rxd5
            -- 状态位解析 (根据乐白夹爪状态定义)
            -- bit0: 初始化完成, bit1: 运动中, bit2: 到达目标位置
            local init_done = status & 0x01
            local moving = (status & 0x02) >> 1
            local target_reached = (status & 0x04) >> 2
            
            -- 组合状态反馈 (0-100范围内的状态值)
            local combined_status = init_done * 1 + moving * 10 + target_reached * 50
            GripStateBack(combined_status)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码10: 综合状态查询
    if(Rcmd3==10) then
        -- 计算CRC校验
        T9[7],T9[8] = CrcValue(T9[1],T9[2],T9[3],T9[4],T9[5],T9[6])
        -- 发送综合查询命令 (读取位置、力矩、状态三个寄存器)
        EndTxGripData(T9[1],T9[2],T9[3],T9[4],T9[5],T9[6],T9[7],T9[8])
        -- 延时等待响应
        DelayMs(100)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 解析综合数据
        if(A==1) then
            -- 位置数据 (第1个寄存器)
            local position = Rxd4 * 256 + Rxd5
            -- 力矩数据 (第2个寄存器) 
            local force = Rxd6 * 256 + Rxd7
            -- 简化处理: 返回当前位置值
            if(position > 100) then position = 100 end
            GripStateBack(position)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码11: 紧急停止
    if(Rcmd3==11) then
        -- 计算CRC校验
        T10[10],T10[11] = CrcValue(T10[1],T10[2],T10[3],T10[4],T10[5],T10[6],T10[7],T10[8],T10[9])
        -- 发送停止命令
        EndTxGripData(T10[1],T10[2],T10[3],T10[4],T10[5],T10[6],T10[7],T10[8],T10[9],T10[10],T10[11])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 状态反馈
        if(A==1) then
            GripStateBack(1)
        else
            GripStateBack(0)
        end
    end
    
    -- 功能码12: 保留功能
    if(Rcmd3==12) then
        -- 计算CRC校验
        T11[7],T11[8] = CrcValue(T11[1],T11[2],T11[3],T11[4],T11[5],T11[6])
        -- 发送保留命令
        EndTxGripData(T11[1],T11[2],T11[3],T11[4],T11[5],T11[6],T11[7],T11[8])
        -- 延时等待响应
        DelayMs(50)
        -- 接收响应数据
        A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7 = EndRxGripData()
        -- 状态反馈
        if(A==1) then
            GripStateBack(1)
        else
            GripStateBack(0)
        end
    end
end

-- =============================================================================
-- 协议文件信息
-- =============================================================================
-- 文件名: AXLE_LUA_End_LeBai.lua
-- 协议: 乐白夹爪Modbus RTU通讯协议
-- 寄存器映射:
--   40000 (0x9C40): 夹爪幅度控制 (0-100)
--   40001 (0x9C41): 夹爪力度控制 (0-100)
--   40005 (0x9C45): 夹爪当前位置 (0-100)
--   40006 (0x9C46): 夹爪当前力矩 (0-100)
--   40010 (0x9C4A): 夹爪速度控制 (0-100)
--   40020 (0x9C54): 夹爪状态寄存器
--   40066 (0x9C42): 夹爪停止控制
-- 
-- Web界面功能对应:
--   功能码1: 夹爪激活
--   功能码2: 夹爪复位
--   功能码3: 位置控制
--   功能码4: 速度控制
--   功能码5: 力矩控制
--   功能码7: 读取位置
--   功能码8: 读取力矩
--   功能码9: 读取状态
--   功能码10: 综合查询
--   功能码11: 紧急停止
--   功能码12: 保留功能
-- =============================================================================