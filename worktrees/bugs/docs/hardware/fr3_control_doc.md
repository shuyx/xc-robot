# **FR3 机械臂 Python SDK 综合控制手册**

**版本**: 2.0  
**日期**: 2025-07-18  
**来源**: 本文档综合了FR3官方SDK文档、`xc-robot`项目代码 (`fr3_control/example`, `fr3_hermes_testing`, `main_control`) 及技术分析文档 (`Md_files`)。

## 目录
1.  [机械臂结构与运动学模型](#1-机械臂结构与运动学模型)
2.  [核心控制流程](#2-核心控制流程)
3.  [Python SDK 核心函数详解](#3-python-sdk-核心函数详解)
4.  [运动控制与规划详解](#4-运动控制与规划详解)
5.  [实时伺服控制 (Servo)](#5-实时伺服控制-servo)
6.  [坐标系管理](#6-坐标系管理)
7.  [I/O 控制](#7-io-控制)
8.  [安全与错误处理](#8-安全与错误处理)
9.  [项目最佳实践：封装与分层](#9-项目最佳实践封装与分层)
10. [运动控制代码参考案例](#10-运动控制代码参考案例)

---

## 1. 机械臂结构与运动学模型

### 1.1 物理结构
- **自由度 (DOF)**: 6个旋转关节 (6-DOF)
- **工作半径**: 约 630mm
- **额定负载**: 3kg

### 1.2 坐标系定义
- **基坐标系 {B}**: 固定于机械臂底座中心。Z轴垂直向上，X轴朝向机械臂正前方。
- **工具坐标系 {T}**: 位于末端法兰盘中心，可通过SDK设置为实际工具的TCP。

### 1.3 运动学模型 (Modified DH Convention)
基于项目分析，我们采用以下精确的**改进型DH参数表**：

| 关节 (i) | 连杆扭转 α(i-1) | 连杆长度 a(i-1) | 连杆偏移 d(i) | 关节角度 θ(i) |
|:---:|:---:|:---:|:---:|:---:|
| J1 | 0° | 0 mm | 333 mm | q1 |
| J2 | -90° | 0 mm | 0 mm | q2 - 90° |
| J3 | 0° | 316 mm | 0 mm | q3 + 90° |
| J4 | 90° | 0 mm | 384 mm | q4 |
| J5 | -90° | 0 mm | 0 mm | q5 |
| J6 | 90° | 0 mm | 107 mm | q6 |

**注意**: `q1` 到 `q6` 是SDK接口中使用的实际关节角度。`θ(i)` 列中的偏移是为了DH建模的数学一致性。

## 2. 核心控制流程

一个标准的机器人控制流程如下：
1.  **建立连接**: `robot = Robot.RPC(ip)`
2.  **设置模式**: `robot.Mode(0)` (自动模式)
3.  **使能机器人**: `robot.RobotEnable(1)`
4.  **执行任务**: 发送运动或I/O指令。
5.  **任务结束**: `robot.RobotEnable(0)`

## 3. Python SDK 核心函数详解

### 3.1 连接与状态
- `Robot.RPC(ip)`: **推荐的连接方式**。
- `GetRobotState()`: 获取机器人综合状态 (停止, 运动中, 错误等)。
- `GetActualJointPosDegree()`: 获取当前6个关节的**实际角度** (度)。
- `GetActualTCPPose()`: 获取当前工具中心点(TCP)相对于基坐标系的**位姿** `[x,y,z,rx,ry,rz]` (mm, 度)。

### 3.2 基础控制
- `Mode(mode_id)`: **必须先设置为自动模式(0)** 才能远程控制。
- `RobotEnable(enable_status)`: 上使能(1)或去使能(0)伺服电机。
- `SetSpeed(speed)`: 设置全局运行速度百分比 (0-100)。

### 3.3 运动学求解
- `GetForwardKin(joint_pos)`: **正运动学**。根据关节角度计算末端位姿。
- `GetInverseKin(type, desc_pos, config)`: **逆运动学**。根据末端位姿计算关节角度。**最佳实践**: 使用 `config=-1`，让求解器参考当前姿态找到最合理的解。

## 4. 运动控制与规划详解

### 4.1 运动规划 vs. 运动控制
- **运动规划 (Motion Planning)**: 在上层软件（Python脚本）中计算出一个从起点到终点的**路径(Path)**。
- **运动控制 (Motion Control)**: 由机器人控制器（硬件）执行，负责精确地跟随上层给出的路径。SDK中的`MoveJ`, `MoveL`等函数就是向控制器下达运动控制指令。

### 4.2 关节空间运动 (MoveJ)
- **函数**: `robot.MoveJ(joint_pos, vel, ...)`
- **说明**: **点到点的关节空间运动**。机器人控制器会自行规划一条从当前关节角度到目标关节角度的最优、平滑的路径。
- **特点**:
    - **高效且安全**: 通常是机器人最快、最不容易触发奇异点的运动方式。
    - **路径不可预测**: 末端TCP在笛卡尔空间中的路径**不是一条直线**。
- **适用场景**: 对中间路径没有要求的快速位姿变换。

### 4.3 直线运动 (MoveL)
- **函数**: `robot.MoveL(desc_pos, vel, ...)`
- **说明**: **笛卡尔空间直线运动**。确保TCP从当前点到目标点走出一条空间直线。
- **特点**:
    - **路径可预测**: TCP路径是直线，非常直观。
    - **潜在风险**: 如果直线路径穿过或靠近奇异点，可能导致机器人报错或剧烈抖动。
- **适用场景**: 需要精确路径控制的工艺，如涂胶、焊接、打磨。

### 4.4 圆弧运动 (MoveC)
- **函数**: `robot.MoveC(mid_pos, end_pos, vel, ...)`
- **说明**: **笛卡尔空间圆弧运动**。TCP会从当前点出发，经过一个**中间点(mid_pos)**，最终以圆弧轨迹运动到**终点(end_pos)**。
- **适用场景**: 绕开障碍物、加工圆形或弧形工件。

## 5. 实时伺服控制 (Servo)

伺服模式允许用户以高频率（如100Hz）发送目标点，实现对机器人轨迹的精确、实时控制。

### 5.1 伺服模式核心概念
- **高频控制**: 替代了`MoveJ/L/C`这种“一次性”指令，变为连续不断地发送微小目标。
- **固定流程**: 所有伺服控制都必须遵循 `ServoMoveStart()` -> `循环发送指令` -> `ServoMoveEnd()` 的结构。**强烈建议使用 `try...finally` 结构确保 `ServoMoveEnd()` 总能被执行**。

### 5.2 关节伺服 (ServoJ)
- **函数**: `robot.ServoJ(joint_pos, ...)`
- **说明**: 在伺服模式下，实时发送**目标关节角度**。
- **适用场景**: 精确复现一条以关节角度序列形式存在的复杂轨迹。

### 5.3 笛卡尔伺服 (ServoCart)
- **函数**: `robot.ServoCart(pose, ...)`
- **说明**: 在伺服模式下，实时发送**目标笛卡尔位姿**。
- **适用场景**: 根据传感器（如视觉）反馈实时调整工具位姿。

### 5.4 选择正确的运动指令

| 当你的目标是... | 最佳指令 | 原因 |
|:---|:---|:---|
| **快速、安全地改变姿态** (路径不重要) | `MoveJ` | 效率最高，最不易出错。 |
| **让工具沿直线移动** | `MoveL` | 精确的笛卡尔路径控制。 |
| **让工具沿圆弧移动** | `MoveC` | 专用的圆弧运动指令。 |
| **精确复现一条复杂的、预先算好的轨迹** | `ServoJ` | 对轨迹的控制力最强。 |
| **根据实时传感器数据动态引导工具** | `ServoCart` | 无需在用户端进行IK计算，简化实时应用。 |

## 6. 坐标系管理
- `SetToolCoord(id, pose)`: 设置**工具坐标系**，定义TCP相对于法兰盘的位姿。运动指令中可通过 `tool=id` 参数选用。
- `SetUserCoord(id, pose)`: 设置**用户/工件坐标系**，定义一个相对于基坐标系的新坐标系。运动指令中可通过 `user=id` 参数选用。

## 7. I/O 控制
- `SetDO(addr, status)` / `GetDI(addr)`: 控制/读取**数字I/O**，用于开关量信号。
- `SetAO(addr, value)` / `GetAI(addr)`: 控制/读取**模拟I/O**，用于连续量信号。

## 8. 安全与错误处理
- `SetCollisionStrategy(level)`: 设置碰撞检测灵敏度 (0:关闭, 5:最灵敏)。
- **错误处理**: SDK中大部分函数返回的第一个值是 `error` 码。**0代表成功，非零代表失败**。必须对返回值进行检查。常见错误码有 `112` (逆解失败), `113` (超关节限位), `123` (碰撞)。

## 9. 项目最佳实践：封装与分层

在`xc-robot`项目中，一个非常好的设计模式是**通过一个中间层（控制器类）对SDK进行封装**。

- **为什么要封装？**
    - **简化接口**: 将复杂的多参数函数封装成更简单的意图驱动的函数。
    - **增加安全性**: 在封装层内自动加入项目的特定安全检查（如双臂碰撞检测）。
    - **状态管理**: 控制器类可以维护机器人的状态，避免频繁查询。
    - **解耦**: 主逻辑与具体SDK解耦。未来更换机器人品牌，只需重写控制器，主逻辑不变。

- **项目中的实践 (`main_control/robot_controller.py`)**:
    - 应用逻辑层调用 `FR3Controller` 里的高级方法，如 `move_to_pose_safe()`。
    - `FR3Controller` 内部处理IK计算、错误检查、日志记录等，然后调用最底层的 `robot.MoveJ()` 等SDK函数。
    - 这种分层架构是构建复杂、可靠机器人系统的基石。

## 10. 运动控制代码参考案例

本节提供一个完整的、可运行的Python代码示例，演示了各类运动函数的标准用法。

```python
import time
import sys

# 假设fr3_control文件夹在项目根目录
# sys.path.append('.') 
from fr3_control.fairino import Robot

class RobotController:
    """一个封装了FR3机器人基本操作的控制器类，用于演示。"""
    
    def __init__(self, ip: str):
        """
        初始化控制器并连接到机器人。
        :param ip: 机器人的IP地址。
        """
        self.robot = Robot.RPC(ip)
        if self.robot is None:
            raise ConnectionError(f"无法连接到机器人 at {ip}")
        print(f"成功连接到机器人 {ip}")
        self.initialize_robot()

    def initialize_robot(self):
        """初始化机器人，设置为自动模式并使能。"""
        print("初始化机器人...")
        self.robot.Mode(0)
        self.robot.RobotEnable(1)
        # 设置一个较低的默认速度用于示例
        self.robot.SetSpeed(20)
        print("机器人已使能，模式：自动，速度：20%")

    def shutdown(self):
        """安全地去使能机器人。"""
        if self.robot:
            print("任务结束，去使能机器人。")
            self.robot.RobotEnable(0)
    
    def wait_for_motion_done(self):
        """阻塞式等待，直到当前运动完成。"""
        while True:
            err, state = self.robot.GetRobotState()
            if err == 0 and state != 2:  # 2 表示运动中
                break
            time.sleep(0.1)
        print("运动完成。")

    def example_move_j(self, target_joints: list):
        """MoveJ: 关节空间运动示例。"""
        print(f"\n--- MoveJ 示例 ---")
        print(f"目标关节角度: {[round(j, 2) for j in target_joints]}")
        err = self.robot.MoveJ(target_joints, vel=25)
        if err != 0:
            print(f"MoveJ 指令失败，错误码: {err}")
            return
        self.wait_for_motion_done()

    def example_move_l(self):
        """MoveL: 笛卡尔直线运动示例。"""
        print(f"\n--- MoveL 示例 ---")
        err, current_pose = self.robot.GetActualTCPPose()
        if err != 0:
            print("无法获取当前位姿。")
            return
        
        target_pose = current_pose[:]
        target_pose[0] += 80.0  # 沿基坐标系X轴正向移动80mm
        print(f"准备从当前位姿沿X轴直线移动80mm...")
        
        err = self.robot.MoveL(target_pose, vel=15)
        if err != 0:
            print(f"MoveL 指令失败，错误码: {err}")
            return
        self.wait_for_motion_done()

    def example_move_c(self):
        """MoveC: 笛卡尔圆弧运动示例。"""
        print(f"\n--- MoveC 示例 ---")
        err, p1 = self.robot.GetActualTCPPose()
        if err != 0:
            print("无法获取当前位姿。")
            return

        # 基于当前点P1，定义中间点P2和终点P3
        p2 = p1[:]; p2[0] += 50; p2[1] += 50
        p3 = p1[:]; p3[0] += 100
        print(f"准备执行圆弧运动：经过中间点，到达终点。")
        
        err = self.robot.MoveC(p2, p3, vel=15)
        if err != 0:
            print(f"MoveC 指令失败，错误码: {err}")
            return
        self.wait_for_motion_done()

    def example_servo_j(self):
        """ServoJ: 关节伺服模式示例。"""
        print(f"\n--- ServoJ 示例 ---")
        err, initial_joints = self.robot.GetActualJointPosDegree()
        if err != 0:
            print("无法获取当前关节角度。")
            return

        # 创建一个简单的轨迹：让J1关节来回摆动5度
        trajectory = []
        for i in range(-50, 51, 2):  # 从-5度到+5度
            waypoint = initial_joints[:]
            waypoint[0] += i / 10.0
            trajectory.append(waypoint)
        for i in range(50, -51, -2):  # 从+5度回到-5度
            waypoint = initial_joints[:]
            waypoint[0] += i / 10.0
            trajectory.append(waypoint)
        
        print(f"准备执行包含 {len(trajectory)} 个路径点的伺服轨迹...")
        
        try:
            self.robot.ServoMoveStart()
            for point in trajectory:
                self.robot.ServoJ(point)
                time.sleep(0.01)  # 控制发送频率为100Hz
        except Exception as e:
            print(f"伺服运动中发生错误: {e}")
        finally:
            self.robot.ServoMoveEnd()
            print("伺服模式结束。")
        self.wait_for_motion_done()

if __name__ == "__main__":
    # ------------------- 主执行程序 -------------------
    # 注意：运行此脚本会使真实机器人运动，请确保安全！
    
    ROBOT_IP = "192.168.58.2"  # 请修改为你的机器人IP
    controller = None
    try:
        controller = RobotController(ROBOT_IP)
        
        # 定义一个安全的起始/回归点
        home_joints = [0, -30, 100, 0, 30, 0]
        
        # 演示1: MoveJ 示例
        controller.example_move_j(home_joints)
        
        # 演示2: MoveL 示例
        controller.example_move_l()
        controller.example_move_j(home_joints)  # 每次演示后回到原位
        
        # 演示3: MoveC 示例
        controller.example_move_c()
        controller.example_move_j(home_joints)  # 每次演示后回到原位
        
        # 演示4: ServoJ 示例
        controller.example_servo_j()
        
    except ConnectionError as e:
        print(f"连接错误: {e}")
    except Exception as e:
        print(f"发生未知异常: {e}")
    finally:
        if controller:
            controller.shutdown()

```