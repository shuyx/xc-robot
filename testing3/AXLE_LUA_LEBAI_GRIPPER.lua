-- 乐白夹爪末端Lua协议适配文件
-- 基于法奥意威末端开放协议标准
-- 适配乐白夹爪Modbus RTU协议
-- 文件名必须以 AXLE_LUA_ 开头

-- 乐白夹爪Modbus寄存器定义
local LEBAI_DEVICE_ADDR = 0x01
local REG_GRIP_POSITION = 0x9C40    -- 40000: 夹爪幅度控制(可写) 0-100%
local REG_GRIP_FORCE = 0x9C41       -- 40001: 夹爪力度控制(可写) 0-100% 
local REG_AUTO_CALIBRATE = 0x9C9A   -- 40154: 关闭自动找行程
local REG_MANUAL_CALIBRATE = 0x9C48 -- 40072: 手动找行程指令
local REG_CURRENT_POS = 0x9C45      -- 40005: 夹爪当前位置(只读)
local REG_CURRENT_FORCE = 0x9C46    -- 40006: 夹爪当前力矩(只读)

-- 定义指令数组 (根据GripExample.lua模板)
T1 = {LEBAI_DEVICE_ADDR, 0x10, 0x9C, 0x9A, 0x00, 0x01, 0x02, 0x00}  -- 关闭自动找行程
T2 = {LEBAI_DEVICE_ADDR, 0x10, 0x9C, 0x48, 0x00, 0x01, 0x02, 0x00}  -- 手动找行程
T3 = {LEBAI_DEVICE_ADDR, 0x10, 0x9C, 0x40, 0x00, 0x01, 0x02, 0x00}  -- 设置位置
T4 = {LEBAI_DEVICE_ADDR, 0x10, 0x9C, 0x41, 0x00, 0x01, 0x02, 0x00}  -- 设置力度
T5 = {LEBAI_DEVICE_ADDR, 0x03, 0x9C, 0x45, 0x00, 0x01, 0x00, 0x00}  -- 读取位置
T6 = {LEBAI_DEVICE_ADDR, 0x03, 0x9C, 0x46, 0x00, 0x01, 0x00, 0x00}  -- 读取力矩
T7 = {}
T8 = {}
T9 = {}
T10 = {}
T11 = {}

-- 主控制逻辑
Rcmd1, Rcmd2, Rcmd3, Rcmd4 = GetGripCmd()

if (Rcmd1 == 1) then
    -- 设置设备地址到所有命令
    T1[1] = Rcmd2
    T2[1] = Rcmd2
    T3[1] = Rcmd2
    T4[1] = Rcmd2
    T5[1] = Rcmd2
    T6[1] = Rcmd2
    
    -- 根据指令类型执行相应操作
    if (Rcmd3 == 1) then
        -- 初始化序列：关闭自动找行程
        T1[8] = 0x01  -- 设置数据为1
        T1[7], T1[8] = CrcValue(T1[1], T1[2], T1[3], T1[4], T1[5], T1[6])
        EndTxGripData(T1[1], T1[2], T1[3], T1[4], T1[5], T1[6], T1[7], T1[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
        
    elseif (Rcmd3 == 2) then
        -- 执行找行程指令
        T2[8] = 0x01  -- 设置数据为1
        T2[7], T2[8] = CrcValue(T2[1], T2[2], T2[3], T2[4], T2[5], T2[6])
        EndTxGripData(T2[1], T2[2], T2[3], T2[4], T2[5], T2[6], T2[7], T2[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
        
    elseif (Rcmd3 == 3) then
        -- 设置夹爪位置 (0-100%)
        local position = Rcmd4
        if position > 100 then position = 100 end
        if position < 0 then position = 0 end
        
        T3[7] = 0x00
        T3[8] = position
        T3[7], T3[8] = CrcValue(T3[1], T3[2], T3[3], T3[4], T3[5], T3[6])
        EndTxGripData(T3[1], T3[2], T3[3], T3[4], T3[5], T3[6], T3[7], T3[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
        
    elseif (Rcmd3 == 4) then
        -- 设置夹爪力度 (0-100%)
        local force = Rcmd4
        if force > 100 then force = 100 end
        if force < 0 then force = 0 end
        
        T4[7] = 0x00
        T4[8] = force
        T4[7], T4[8] = CrcValue(T4[1], T4[2], T4[3], T4[4], T4[5], T4[6])
        EndTxGripData(T4[1], T4[2], T4[3], T4[4], T4[5], T4[6], T4[7], T4[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
        
    elseif (Rcmd3 == 5) then
        -- 读取夹爪当前位置
        T5[7], T5[8] = CrcValue(T5[1], T5[2], T5[3], T5[4], T5[5], T5[6])
        EndTxGripData(T5[1], T5[2], T5[3], T5[4], T5[5], T5[6], T5[7], T5[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        if ((A == 7) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02)) then
            -- 返回位置数据 (Rxd4*256 + Rxd5)
            local position = Rxd4 * 256 + Rxd5
            GripStateBack(position)
        end
        
    elseif (Rcmd3 == 6) then
        -- 读取夹爪当前力矩
        T6[7], T6[8] = CrcValue(T6[1], T6[2], T6[3], T6[4], T6[5], T6[6])
        EndTxGripData(T6[1], T6[2], T6[3], T6[4], T6[5], T6[6], T6[7], T6[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        if ((A == 7) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02)) then
            -- 返回力矩数据 (Rxd4*256 + Rxd5)
            local force = Rxd4 * 256 + Rxd5
            GripStateBack(force)
        end
        
    end
    
end