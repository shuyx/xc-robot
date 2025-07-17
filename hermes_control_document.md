# **Hermes 底盘控制与API详解**

**版本**: 1.0  
**日期**: 2025-07-18  
**来源**: 本文档综合了`hermes_datas`中的API手册、`fr3_hermes_testing`中的测试代码、以及`gui/widgets/chassis_widget.py`和`main_control/hermer_controller.py`中的现有实现。

---

## 1. 概述与核心架构

### 1.1 基本信息
- **设备**: 思岚科技 (Slamtec) Hermes 移动底盘
- **通信协议**: **HTTP RESTful API**
- **数据格式**: JSON
- **默认地址**: `http://192.168.31.211:1448`

### 1.2 项目控制架构
在`xc-robot`项目中，我们不直接在业务逻辑中调用HTTP API，而是通过一个专门的控制器类 `main_control/hermer_controller.py` (应为 `hermes_controller.py`) 进行封装。这种设计极大地简化了底盘控制，并统一了接口。

**核心思想**: 将底盘的每一个功能（如移动、获取状态）都封装成一个Python方法。GUI或上层应用只需调用这些方法，而无需关心底层HTTP请求的细节。

```python
# main_control/hermes_controller.py (概念性)
import requests

class HermesController:
    def __init__(self, base_url="http://192.168.31.211:1448"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_status(self):
        # ... 封装 GET 请求 ...
        pass

    def move_to(self, x, y, theta):
        # ... 封装 POST 请求 ...
        pass

    # ... 其他方法 ...
```

## 2. 状态读取功能

这些功能通常使用 **HTTP GET** 请求，用于获取底盘的实时信息。

### 2.1 获取电源状态
- **说明**: 获取电池电量、是否在充电等信息。
- **API 端点**: `GET /api/core/system/v1/power/status`
- **响应示例**:
  ```json
  {
    "battery_percentage": 85.0,
    "is_charging": false
  }
  ```
- **封装与代码示例**:
  ```python
  def get_power_status(self):
      """获取电池和充电状态。"""
      try:
          response = self.session.get(f"{self.base_url}/api/core/system/v1/power/status", timeout=2)
          response.raise_for_status() # 检查HTTP错误
          return response.json()
      except requests.RequestException as e:
          print(f"获取电源状态失败: {e}")
          return None
  ```

### 2.2 获取底盘位姿
- **说明**: 获取底盘在当前地图中的精确位置和朝向（里程计信息）。
- **API 端点**: `GET /api/core/motion/v1/odometer`
- **响应示例**:
  ```json
  {
    "x": 1.23, "y": -0.45, "z": 0.0, 
    "roll": 0.0, "pitch": 0.0, "yaw": 90.5 
  }
  ```
- **封装与代码示例**:
  ```python
  import math

  def get_robot_pose(self):
      """获取底盘的X, Y坐标和偏航角(theta)。"""
      try:
          response = self.session.get(f"{self.base_url}/api/core/motion/v1/odometer", timeout=2)
          response.raise_for_status()
          data = response.json()
          # 将yaw(弧度)转换为角度
          theta_degrees = math.degrees(data.get('yaw', 0.0))
          return {
              "x": data.get('x'),
              "y": data.get('y'),
              "theta": theta_degrees
          }
      except requests.RequestException as e:
          print(f"获取底盘位姿失败: {e}")
          return None
  ```

### 2.3 检查运动状态
- **说明**: 检查底盘当前是否在运动中。
- **API 端点**: `GET /api/core/motion/v1/status`
- **响应示例**:
  ```json
  {
    "is_moving": true
  }
  ```
- **封装与代码示例**:
  ```python
  def is_moving(self):
      """检查底盘是否正在运动。"""
      try:
          response = self.session.get(f"{self.base_url}/api/core/motion/v1/status", timeout=2)
          response.raise_for_status()
          return response.json().get('is_moving', False)
      except requests.RequestException:
          return False # 通信失败时，保守地认为未在运动
  ```

## 3. 运动控制功能

这些功能通常使用 **HTTP POST** 请求，向底盘发送运动指令。

### 3.1 移动到指定坐标 (绝对位置)
- **说明**: 命令底盘移动到地图上的一个绝对坐标点。
- **API 端点**: `POST /api/core/motion/v1/actions`
- **请求体示例**:
  ```json
  {
    "action_type": "MoveToAction",
    "target": {
      "x": 2.5, 
      "y": 1.8, 
      "yaw": -180.0
    }
  }
  ```
- **封装与代码示例**:
  ```python
  def move_to(self, x: float, y: float, theta: float):
      """移动到底图上的绝对坐标。theta单位为度。"""
      endpoint = f"{self.base_url}/api/core/motion/v1/actions"
      payload = {
          "action_type": "MoveToAction",
          "target": {"x": x, "y": y, "yaw": math.radians(theta)} # API需要弧度
      }
      try:
          response = self.session.post(endpoint, json=payload, timeout=5)
          response.raise_for_status()
          print(f"成功发送移动指令: 移动到({x}, {y}, {theta}°)")
          return True
      except requests.RequestException as e:
          print(f"移动指令发送失败: {e}")
          return False
  ```

### 3.2 相对移动
- **说明**: 基于当前位置进行相对移动（例如，前进0.5米，原地左转30度）。
- **API 端点**: `POST /api/core/motion/v1/actions`
- **请求体示例** (前进0.5米):
  ```json
  {
    "action_type": "MoveByAction",
    "direction": "forward",
    "distance": 0.5
  }
  ```
- **封装与代码示例** (参考 `function_test/chassis_relative_move.py`):
  ```python
  def move_by(self, direction: str, distance: float = 0, angle: float = 0):
      """执行相对移动。"""
      endpoint = f"{self.base_url}/api/core/motion/v1/actions"
      payload = {"action_type": "MoveByAction", "direction": direction}
      if direction in ["forward", "backward", "leftward", "rightward"]:
          payload["distance"] = distance
      elif direction in ["turn_left", "turn_right"]:
          payload["angle"] = math.radians(angle) # API需要弧度
      
      # ... (省略POST请求和错误处理) ...
  ```

### 3.3 手动速度控制
- **说明**: 模拟遥控手柄，持续发送线速度和角速度指令。这是GUI中8方向控制盘的实现方式。
- **API 端点**: `POST /api/core/motion/v1/manual`
- **请求体示例** (前进并左转):
  ```json
  {
    "linear_velocity": 0.2,  // m/s
    "angular_velocity": 0.5   // rad/s
  }
  ```
- **封装与代码示例**:
  ```python
  def set_velocity(self, linear_v: float, angular_v: float):
      """设置底盘的线速度和角速度。"""
      endpoint = f"{self.base_url}/api/core/motion/v1/manual"
      payload = {"linear_velocity": linear_v, "angular_velocity": angular_v}
      # ... (省略POST请求和错误处理) ...
  ```

### 3.4 停止运动
- **说明**: **极其重要**。取消当前所有的运动任务，让底盘立即停止。
- **API 端点**: `POST /api/core/motion/v1/stop`
- **请求体**: 无
- **封装与代码示例**:
  ```python
  def stop_motion(self):
      """立即停止所有运动。"""
      endpoint = f"{self.base_url}/api/core/motion/v1/stop"
      try:
          response = self.session.post(endpoint, timeout=2)
          response.raise_for_status()
          print("已发送停止指令。")
          return True
      except requests.RequestException as e:
          print(f"停止指令发送失败: {e}")
          return False
  ```

## 4. 诊断与维护功能

### 4.1 复位电机刹车
- **说明**: 解决特定的 `motor brake released` 错误。这是一个从 `function_test/chassis_reset_brake.py` 中学到的重要维护操作。
- **API 端点**: `POST /api/core/motion/v1/actions`
- **请求体示例**:
  ```json
  {
    "action_type": "ResetMotorBrakeAction"
  }
  ```
- **封装与代码示例**:
  ```python
  def reset_brake_motor(self):
      """尝试复位电机刹车以清除特定错误。"""
      endpoint = f"{self.base_url}/api/core/motion/v1/actions"
      payload = {"action_type": "ResetMotorBrakeAction"}
      # ... (省略POST请求和错误处理) ...
  ```

## 5. 综合代码示例

这是一个演示如何使用封装好的控制器类来执行一系列操作的完整示例。

```python
import time
# 假设 HermesController 类已在 hermes_controller.py 中定义好
# from main_control.hermes_controller import HermesController

if __name__ == "__main__":
    # --- 初始化 ---
    try:
        controller = HermesController()
        print("成功连接到底盘控制器。")
    except Exception as e:
        print(f"初始化控制器失败: {e}")
        exit()

    try:
        # --- 1. 获取并打印初始状态 ---
        initial_status = controller.get_power_status()
        initial_pose = controller.get_robot_pose()
        if initial_status and initial_pose:
            print(f"初始状态: 电量 {initial_status['battery_percentage']}% | 位置 ({initial_pose['x']:.2f}, {initial_pose['y']:.2f}, {initial_pose['theta']:.1f}°)")

        # --- 2. 执行一个安全的相对运动：原地右转15度 ---
        print("\n执行任务: 原地右转15度...")
        controller.move_by(direction="turn_right", angle=15)
        
        # --- 3. 等待运动完成 ---
        while controller.is_moving():
            print("底盘运动中...")
            time.sleep(0.5)
        print("运动已结束。")

        # --- 4. 获取并打印最终状态 ---
        final_pose = controller.get_robot_pose()
        if final_pose:
            print(f"最终位置: ({final_pose['x']:.2f}, {final_pose['y']:.2f}, {final_pose['theta']:.1f}°)")

    except KeyboardInterrupt:
        print("\n检测到用户中断...")
    except Exception as e:
        print(f"\n任务执行中发生错误: {e}")
    finally:
        # --- 5. 确保停止 (安全保障) ---
        print("发送最终停止指令以确保安全。")
        controller.stop_motion()

```