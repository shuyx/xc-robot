Rcmd1,Rcmd2,Rcmd3,Rcmd4 = GetGripCmd()
T1 = {0x01,0x10,0x9C,0x9A,0x00,0x01,0x02,0x00,0x01,0x26,0x63}
T2 = {0x01,0x10,0x9C,0x48,0x00,0x01,0x02,0x00,0x01,0x34,0x11}
T3 = {0x01,0x10,0x9C,0x40,0x00,0x01,0x02,0x00,0x64,0x00,0x00}
T4 = {0x01,0x10,0x9C,0x41,0x00,0x01,0x02,0x00,0x32,0x00,0x00}
T5 = {0x01,0x03,0x9C,0x45,0x00,0x01,0xBB,0x8F}
T6 = {0x01,0x03,0x9C,0x46,0x00,0x01,0x4B,0x8F}
if(Rcmd1 == 1) then
    DelayMs(3)
    T1[1] = Rcmd2
    T2[1] = Rcmd2
    T3[1] = Rcmd2
    T4[1] = Rcmd2
    T5[1] = Rcmd2
    T6[1] = Rcmd2
    if(Rcmd3 == 0x01) then
    T1[10],T1[11] = CrcValue(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6],T1[7],T1[8],T1[9])
    EndTxGripData(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6],T1[7],T1[8],T1[9],T1[10],T1[11])
    DelayMs(10)
    Rxd1,Rxd2,Rxd3,Rxd4,Rxd5= EndRxGripData()
    GripStateBack(1)
    end
    if(Rcmd3 == 0x02) then
    T2[10],T2[11] = CrcValue(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6],T2[7],T2[8],T2[9])
    EndTxGripData(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6],T2[7],T2[8],T2[9],T2[10],T2[11])
    DelayMs(10)
    Rxd1,Rxd2,Rxd3,Rxd4,Rxd5= EndRxGripData()
    GripStateBack(1)
    end
    if(Rcmd3 == 0x03) then
    T3[9] = Rcmd4
    T3[10],T3[11] = CrcValue(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6],T3[7],T3[8],T3[9])
    EndTxGripData(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6],T3[7],T3[8],T3[9],T3[10],T3[11])
    DelayMs(10)
    Rxd1,Rxd2,Rxd3,Rxd4,Rxd5= EndRxGripData()
    GripStateBack(Rcmd4)
    end
    if(Rcmd3 == 0x05) then
    T4[9] = Rcmd4
    T4[10],T4[11] = CrcValue(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6],T4[7],T4[8],T4[9])
    EndTxGripData(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6],T4[7],T4[8],T4[9],T4[10],T4[11])
    DelayMs(10)
    Rxd1,Rxd2,Rxd3,Rxd4,Rxd5= EndRxGripData()
    GripStateBack(Rcmd4)
    end
    if(Rcmd3 == 0x07) then
    T5[7],T5[8] = CrcValue(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6])
    EndTxGripData(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6],T5[7],T5[8])
    DelayMs(10)
    a,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5 = EndRxGripData()
        if ((a == 7) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02)) then
            P = (Rxd4<<8)+Rxd5
            GripStateBack(P)
        end
    end
    if (Rcmd3 == 0x08) then
    T6[7],T6[8] = CrcValue(T6[1],T6[2],T6[3],T6[4],T6[5],T6[6])
    EndTxGripData(T6[1],T6[2],T6[3],T6[4],T6[5],T6[6],T6[7],T6[8])
    DelayMs(10)
    a, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5 = EndRxGripData()
        if ((a == 7) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02)) then
            F = (Rxd4<<8)+Rxd5
            GripStateBack(F)
        end
    end
end