-- 乐白夹爪简单控制程序
-- 只通过力矩控制动作，只读取位置和力矩
-- 实现：先张开再闭合

-- 与机器人控制器建立连接
robot = Robot.RPC('192.168.58.2')
robot.LoggerInit(output_model=0)
robot.SetLoggerLevel(4)

-- 激活夹爪
print("激活夹爪...")
error = robot.ActGripper(1, 0)  -- 复位
print("ActGripper复位:", error)
Sleep(1000)

error = robot.ActGripper(1, 1)  -- 激活
print("ActGripper激活:", error)  
Sleep(2000)

-- 第一步：张开夹爪（低力矩）
print("=== 第一步：张开夹爪 ===")
-- 使用MoveGripper，力矩控制模式
-- MoveGripper(设备ID, 位置, 速度, 力矩, 超时, 标志)
error = robot.MoveGripper(1, 0, 50, 20, 5000, 0)  -- 位置0(张开), 力矩20%
print("张开夹爪结果:", error)
Sleep(3000)  -- 等待3秒

-- 读取当前位置
print("--- 读取当前状态 ---")
-- 这里可能需要根据你的具体配置调整读取方式
-- 通常通过GetGripperMotionDone或其他状态查询函数
status = robot.GetGripperMotionDone()
print("夹爪状态:", status)

-- 第二步：闭合夹爪（中等力矩）
print("=== 第二步：闭合夹爪 ===")  
error = robot.MoveGripper(1, 100, 50, 50, 5000, 0)  -- 位置100(闭合), 力矩50%
print("闭合夹爪结果:", error)
Sleep(3000)  -- 等待3秒

-- 再次读取状态
print("--- 读取最终状态 ---")
status = robot.GetGripperMotionDone()
print("最终夹爪状态:", status)

-- 第三步：回到半开状态
print("=== 第三步：回到半开状态 ===")
error = robot.MoveGripper(1, 50, 50, 30, 5000, 0)  -- 位置50(半开), 力矩30%
print("半开夹爪结果:", error)
Sleep(2000)

print("=== 夹爪控制序列完成 ===")
print("程序执行完毕")