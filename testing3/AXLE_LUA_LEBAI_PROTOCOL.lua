-- 乐白夹爪末端协议文件
-- 基于GripExample.lua模板，适配乐白夹爪Modbus RTU协议
-- 文件名必须以 AXLE_LUA_ 开头

-- 乐白夹爪Modbus指令定义（基于乐白夹爪通讯协议文档）
T1 = {0x01, 0x10, 0x9C, 0x9A, 0x00, 0x01, 0x02, 0x01}  -- 关闭自动找行程 (寄存器40154)
T2 = {0x01, 0x10, 0x9C, 0x48, 0x00, 0x01, 0x02, 0x01}  -- 手动执行找行程 (寄存器40072)
T3 = {0x01, 0x10, 0x9C, 0x40, 0x00, 0x01, 0x02, 0x00}  -- 设置夹爪位置 (寄存器40000)
T4 = {0x01, 0x10, 0x9C, 0x41, 0x00, 0x01, 0x02, 0x00}  -- 设置夹爪力度 (寄存器40001)
T5 = {0x01, 0x03, 0x9C, 0x45, 0x00, 0x01, 0x00, 0x00}  -- 读取当前位置 (寄存器40005)
T6 = {0x01, 0x03, 0x9C, 0x46, 0x00, 0x01, 0x00, 0x00}  -- 读取当前力矩 (寄存器40006)
T7 = {}
T8 = {}
T9 = {}
T10 = {}
T11 = {}

-- 获取上位机指令
Rcmd1, Rcmd2, Rcmd3, Rcmd4 = GetGripCmd()

if (Rcmd1 == 1) then
    -- 设置设备地址到所有指令
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
    
    -- 指令1: 关闭自动找行程
    if (Rcmd3 == 1) then
        T1[7], T1[8] = CrcValue(T1[1], T1[2], T1[3], T1[4], T1[5], T1[6])
        EndTxGripData(T1[1], T1[2], T1[3], T1[4], T1[5], T1[6], T1[7], T1[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
    end
    
    -- 指令2: 手动执行找行程
    if (Rcmd3 == 2) then
        T2[7], T2[8] = CrcValue(T2[1], T2[2], T2[3], T2[4], T2[5], T2[6])
        EndTxGripData(T2[1], T2[2], T2[3], T2[4], T2[5], T2[6], T2[7], T2[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
    end
    
    -- 指令3: 设置夹爪位置 (0-100%)
    if (Rcmd3 == 3) then
        X = Rcmd4
        if X > 100 then X = 100 end
        if X < 0 then X = 0 end
        T3[7] = 0x00
        T3[8] = X
        T3[7], T3[8] = CrcValue(T3[1], T3[2], T3[3], T3[4], T3[5], T3[6])
        EndTxGripData(T3[1], T3[2], T3[3], T3[4], T3[5], T3[6], T3[7], T3[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
    end
    
    -- 指令4: 设置夹爪力度 (0-100%)
    if (Rcmd3 == 4) then
        Force = Rcmd4
        if Force > 100 then Force = 100 end
        if Force < 0 then Force = 0 end
        T4[7] = 0x00
        T4[8] = Force
        T4[7], T4[8] = CrcValue(T4[1], T4[2], T4[3], T4[4], T4[5], T4[6])
        EndTxGripData(T4[1], T4[2], T4[3], T4[4], T4[5], T4[6], T4[7], T4[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        GripStateBack(Rxd3)
    end
    
    -- 指令7: 读取夹爪当前位置
    if (Rcmd3 == 7) then
        T5[7], T5[8] = CrcValue(T5[1], T5[2], T5[3], T5[4], T5[5], T5[6])
        EndTxGripData(T5[1], T5[2], T5[3], T5[4], T5[5], T5[6], T5[7], T5[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        RxdCrcH, RxdCrcL = CrcValue(Rxd1, Rxd2, Rxd3, Rxd4, Rxd5)
        if ((A == 7) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02) and (Rxd6 == RxdCrcH) and (Rxd7 == RxdCrcL)) then
            Position = Rxd4 * 256 + Rxd5
            GripStateBack(Position)
        end
    end
    
    -- 指令8: 读取夹爪当前力矩
    if (Rcmd3 == 8) then
        T6[7], T6[8] = CrcValue(T6[1], T6[2], T6[3], T6[4], T6[5], T6[6])
        EndTxGripData(T6[1], T6[2], T6[3], T6[4], T6[5], T6[6], T6[7], T6[8])
        DelayMs(10)
        A, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5, Rxd6, Rxd7 = EndRxGripData()
        RxdCrcH, RxdCrcL = CrcValue(Rxd1, Rxd2, Rxd3, Rxd4, Rxd5)
        if ((A == 7) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02) and (Rxd6 == RxdCrcH) and (Rxd7 == RxdCrcL)) then
            Force = Rxd4 * 256 + Rxd5
            GripStateBack(Force)
        end
    end
end