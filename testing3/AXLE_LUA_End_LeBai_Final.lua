T1={}
T2={}
T3={0x01,0x10,0x9C,0x40,0x00,0x01,0x02,0x00,0x64,0xF5,0x72}
T4={0x01,0x10,0x9C,0x4A,0x00,0x01,0x02,0x00,0x32,0x75,0xE6}
T5={0x01,0x10,0x9C,0x41,0x00,0x01,0x02,0x00,0x32,0x74,0x9D}
T6={}
T7={}
T8={}
T9={}
T10={0x01,0x03,0x9C,0x45,0x00,0x01,0xBB,0x8F}
T11={0x01,0x03,0x9C,0x46,0x00,0x01,0x4B,0x8F}
Rcmd1,Rcmd2,Rcmd3,Rcmd4=GetGripCmd()
if(Rcmd1==1) then
    T1[1]=Rcmd2
    T2[1]=Rcmd2
    T3[1]=Rcmd2
    T4[1]=Rcmd2
    T5[1]=Rcmd2
    T6[1]=Rcmd2
    T7[1]=Rcmd2
    T8[1]=Rcmd2
    T9[1]=Rcmd2
    T10[1]=Rcmd2
    T11[1]=Rcmd2
    if (Rcmd3==1) then
    T1[7],T1[8]=CrcValue(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6])
    EndTxGripData(T1[1],T1[2],T1[3],T1[4],T1[5],T1[6],T1[7],T1[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    GripStateBack(Rxd3)
    end
    if (Rcmd3==2) then
    T2[7],T2[8]=CrcValue(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6])
    EndTxGripData(T2[1],T2[2],T2[3],T2[4],T2[5],T2[6],T2[7],T2[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    GripStateBack(Rxd3)
    end
    if(Rcmd3==3) then
    X=Rcmd4
    T3[8]=0x00
    T3[9]=X
    T3[10],T3[11]=CrcValue(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6],T3[7],T3[8],T3[9])
    EndTxGripData(T3[1],T3[2],T3[3],T3[4],T3[5],T3[6],T3[7],T3[8],T3[9],T3[10],T3[11])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    GripStateBack(Rxd3)
    end
    if (Rcmd3==4) then
    Speed=Rcmd4
    X,Speed,Torque=GripperParaValue(Rcmd3,Speed)
    T4[8]=Torque
    T4[9]=Speed
    T4[10],T4[11]=CrcValue(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6],T4[7],T4[8],T4[9])
    EndTxGripData(T4[1],T4[2],T4[3],T4[4],T4[5],T4[6],T4[7],T4[8],T4[9],T4[10],T4[11])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    GripStateBack(Rxd3)
    end
    if(Rcmd3==5) then
    Torque=Rcmd4
    X,Speed,Torque=GripperParaValue(Rcmd3,Torque)
    T5[8]=Torque
    T5[9]=Speed
    T5[10],T5[11]=CrcValue(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6],T5[7],T5[8],T5[9])
    EndTxGripData(T5[1],T5[2],T5[3],T5[4],T5[5],T5[6],T5[7],T5[8],T5[9],T5[10],T5[11])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    GripStateBack(Rxd3)
    end
    if(Rcmd3 == 7) then
    T6[7],T6[8]=CrcValue(T6[1],T6[2],T6[3],T6[4],T6[5],T6[6])
    EndTxGripData(T6[1],T6[2],T6[3],T6[4],T6[5],T6[6],T6[7],T6[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    RxdCrcH,RxdCrcL = CrcValue(Rxd1,Rxd2,Rxd3,Rxd4,Rxd5)
        if((A==8)and(Rxd1==Rcmd2)and(Rxd2==0x03)and(Rxd3==0x02)and(Rxd6==RxdCrcH)and(Rxd7==RxdCrcL))then
        GripStateBack(Rxd4)
        end
    end
    if(Rcmd3==8) then
    T7[7],T7[8]=CrcValue(T7[1],T7[2],T7[3],T7[4],T7[5],T7[6])
    EndTxGripData(T7[1],T7[2],T7[3],T7[4],T7[5],T7[6],T7[7],T7[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    RxdCrcH,RxdCrcL = CrcValue(Rxd1,Rxd2,Rxd3,Rxd4,Rxd5)
        if((A==8)and(Rxd1==Rcmd2)and(Rxd2==0x03)and(Rxd3==0x02)and(Rxd6==RxdCrcH)and(Rxd7 ==RxdCrcL)) then
        GripStateBack(Rxd5)
        end
    end
    if(Rcmd3 == 9) then
    T8[7],T8[8]=CrcValue(T8[1],T8[2],T8[3],T8[4],T8[5],T8[6])
    EndTxGripData(T8[1],T8[2],T8[3],T8[4],T8[5],T8[6],T8[7],T8[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    RxdCrcH,RxdCrcL = CrcValue(Rxd1,Rxd2,Rxd3,Rxd4,Rxd5)
        if((A==8)and(Rxd1==Rcmd2)and(Rxd2==0x03)and(Rxd3==0x02)and(Rxd6==RxdCrcH)and(Rxd7==RxdCrcL)) then
        GripStateBack(Rxd5)
        end
    end
    if(Rcmd3 == 10) then
    T9[7],T9[8]=CrcValue(T9[1],T9[2],T9[3],T9[4],T9[5],T9[6])
    EndTxGripData(T9[1],T9[2],T9[3],T9[4],T9[5],T9[6],T9[7],T9[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    RxdCrcH,RxdCrcL = CrcValue(Rxd1,Rxd2,Rxd3,Rxd4,Rxd5)
        if((A==8)and(Rxd1==Rcmd2)and(Rxd2==0x03)and(Rxd3==0x02)and(Rxd6==RxdCrcH)and(Rxd7==RxdCrcL)) then
        GripStateBack(Rxd4)
        end
    end
    if(Rcmd3 == 11) then
    T10[7],T10[8]=CrcValue(T10[1],T10[2],T10[3],T10[4],T10[5],T10[6])
    EndTxGripData(T10[1],T10[2],T10[3],T10[4],T10[5],T10[6],T10[7],T10[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    RxdCrcH,RxdCrcL = CrcValue(Rxd1,Rxd2,Rxd3,Rxd4,Rxd5)
        if((A==8)and(Rxd1==Rcmd2)and(Rxd2==0x03)and(Rxd3==0x02)and(Rxd6==RxdCrcH)and(Rxd7==RxdCrcL)) then
        GripStateBack(Rxd5)
        end
    end
    if(Rcmd3 == 12) then
    T11[7],T11[8]=CrcValue(T11[1],T11[2],T11[3],T11[4],T11[5],T11[6])
    EndTxGripData(T11[1],T11[2],T11[3],T11[4],T11[5],T11[6],T11[7],T11[8])
    DelayMs(10)
    A,Rxd1,Rxd2,Rxd3,Rxd4,Rxd5,Rxd6,Rxd7=EndRxGripData()
    RxdCrcH,RxdCrcL = CrcValue(Rxd1,Rxd2,Rxd3,Rxd4,Rxd5)
        if((A==8)and(Rxd1==Rcmd2)and(Rxd2==0x03)and(Rxd3==0x02)and(Rxd6==RxdCrcH)and(Rxd7==RxdCrcL)) then
        GripStateBack(Rxd4)
        end
    end
end
