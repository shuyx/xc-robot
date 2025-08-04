ªU¥Z ï£Rcmd1,Rcmd2,Rcmd3,Rcmd4 = GetGripCmd()
T1 = {0x01,0x06,0x9C,0x40,0x00,0x64,0xA7,0xA5}
T2 = {0x01,0x06,0x9C,0x41,0x00,0x32,0x76,0x5B}
T3 = {0x01,0x03,0x9C,0x45,0x00,0x01,0xBB,0x8F}
T4 = {0x01,0x03,0x9C,0x46,0x00,0x01,0x4B,0x8F}
T5 = {0x01,0x06,0x9C,0x4A,0x00,0x32,0x07,0x99}
if(Rcmd1 == 1) then
    DelayMs(3)
    T1[1] = Rcmd2
    T2[1] = Rcmd2
    T3[1] = Rcmd2
    T4[1] = Rcmd2
    T5[1] = Rcmd2
    if(Rcmd3 == 0x03) then
        T1[5] = 0x00
        T1[6] = Rcmd4
        T1[7],T1[8] = CrcValue(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6])
        EndTxGripData(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6],T1[7],T1[8])
        DelayMs(10)
        Rxd1,Rxd2,Rxd3,Rxd4,Rxd5= EndRxGripData()
        GripStateBack(Rcmd4)
    end
    if(Rcmd3 == 0x04) then
        T5[5] = 0x00
        T5[6] = Rcmd4
        T5[7],T5[8] = CrcValue(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6])
        EndTxGripData(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6],T5[7],T5[8])
        DelayMs(10)
        Rxd1,Rxd2,Rxd3,Rxd4,Rxd5= EndRxGripData()
        GripStateBack(Rcmd4)
    end
    if(Rcmd3 == 0x05) then
        T2[5] = 0x00
        T2[6] = Rcmd4
        T2[7],T2[8] = CrcValue(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6])
        EndTxGripData(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6],T2[7],T2[8])
        DelayMs(10)
        Rxd1,Rxd2,Rxd3,Rxd4,Rxd5= EndRxGripData()
        GripStateBack(Rcmd4)
    end
    if(Rcmd3 == 0x0A) then
        T3[1] = Rcmd2
        T3[7],T3[8] = CrcValue(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6])
        EndTxGripData(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6],T3[7],T3[8])
        DelayMs(10)
        a,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5 = EndRxGripData()
        if ((a == 8) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02)) then
            P = (Rxd4<<8)+Rxd5
            GripStateBack(P)
        end
    end
    if (Rcmd3 == 0x0C) then
        T4[1] = Rcmd2
        T4[7],T4[8] = CrcValue(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6])
        EndTxGripData(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6],T4[7],T4[8])
        DelayMs(10)
        a, Rxd1, Rxd2, Rxd3, Rxd4, Rxd5 = EndRxGripData()
        if ((a == 8) and (Rxd1 == Rcmd2) and (Rxd2 == 0x03) and (Rxd3 == 0x02)) then
            F = (Rxd4<<8)+Rxd5
            GripStateBack(F)
        end
    end
end