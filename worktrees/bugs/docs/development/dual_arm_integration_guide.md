# 双臂机器人安全避障模型集成指南

## 概述

本指南说明如何将双臂安全避障模型集成到你的机器人控制系统中。该模型提供了碰撞检测、工作空间验证和路径规划功能。

## 模型架构

### 坐标系定义
- **全局坐标系**：以左臂基座为原点
- **左臂基座**：位于原点 (0, 0, 0)
- **右臂基座**：位于 (base_distance, 0, 0)，默认 base_distance = 400mm
- **Z轴**：垂直向上
- **X轴**：从左臂指向右臂
- **Y轴**：根据右手坐标系确定

### 关键参数
- **基座间距**：380-420mm（可配置）
- **安全裕度**：50mm
- **连杆半径**：40mm（简化模型）
- **最大臂展**：630mm
- **最小工作半径**：100mm

## 快速开始

### 1. 基本使用

```python
from dual_arm_safety_model import DualArmSafetyModel, check_dual_arm_safety
import numpy as np

# 创建安全模型实例
model = DualArmSafetyModel()
model.base_distance = 400  # 设置实际的基座间距

# 定义目标位姿
left_target = np.eye(4)
left_target[:3, 3] = [200, 150, 400]  # 位置向量

# 当前关节角度
current_angles = [0, -np.pi/4, np.pi/4, 0, 0, 0]

# 安全检查
result = check_dual_arm_safety(left_target, right_target, 
                               left_angles, right_angles)
```

### 2. 正向运动学

```python
# 计算末端位姿
pose = model.forward_kinematics(joint_angles, arm='left')
position = pose[:3, 3]  # 提取位置
rotation = pose[:3, :3]  # 提取旋转矩阵
```

### 3. 逆运动学

```python
# 求解关节角度
target_pose = np.eye(4)
target_pose[:3, 3] = [300, 200, 400]
joint_angles = model.inverse_kinematics(target_pose, arm='left')
```

### 4. 碰撞检测

```python
# 检查自碰撞
self_collision = model.check_self_collision(joint_angles, 'left')

# 检查双臂碰撞
dual_collision = model.check_dual_arm_collision(left_angles, right_angles)
```

## 集成步骤

### 步骤1：初始化

```python
class RobotController:
    def __init__(self):
        self.safety_model = DualArmSafetyModel()
        self.safety_model.base_distance = 400  # 根据实际情况设置
        
    def set_safety_parameters(self, margin=50, link_radius=40):
        self.safety_model.safety_margin = margin
        self.safety_model.link_radius = link_radius
```

### 步骤2：运动前检查

```python
def plan_motion(self, target_pose, arm='left'):
    # 1. 检查目标是否在安全区域
    if not self.safety_model.check_safety_zone(target_pose, arm):
        return None, "目标超出安全工作空间"
    
    # 2. 求解逆运动学
    target_angles = self.safety_model.inverse_kinematics(
        target_pose, arm, self.current_angles[arm]
    )
    
    if target_angles is None:
        return None, "逆运动学无解"
    
    # 3. 规划路径
    other_arm = 'right' if arm == 'left' else 'left'
    path = self.safety_model.plan_collision_free_motion(
        self.current_angles[arm],
        target_pose,
        arm,
        self.current_angles[other_arm]
    )
    
    if path is None:
        return None, "无法规划安全路径"
    
    return path, "成功"
```

### 步骤3：实时监控

```python
def execute_motion(self, path, arm='left'):
    for waypoint in path:
        # 1. 设置关节角度
        self.set_joint_angles(waypoint, arm)
        
        # 2. 实时安全检查
        if self.check_emergency_stop():
            self.stop_motion()
            return False
        
        # 3. 等待运动完成
        self.wait_motion_complete()
    
    return True

def check_emergency_stop(self):
    # 获取当前状态
    left_angles = self.get_current_angles('left')
    right_angles = self.get_current_angles('right')
    
    # 检查碰撞
    if self.safety_model.check_dual_arm_collision(left_angles, right_angles):
        return True
    
    return False
```

## 高级功能

### 1. 自定义安全区域

```python
def define_custom_safety_zone(self, arm):
    # 覆盖默认的安全区域检查
    def custom_check(pose):
        pos = pose[:3, 3]
        
        # 添加自定义约束
        if arm == 'left':
            # 左臂不能进入右半空间
            if pos[0] > 180:  # 比默认更严格
                return False
        
        # 高度限制
        if pos[2] < 200 or pos[2] > 600:
            return False
            
        return True
    
    return custom_check
```

### 2. 协调运动控制

```python
def coordinated_motion(self, left_target, right_target):
    # 同时规划两臂运动
    left_path = []
    right_path = []
    
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        
        # 插值计算
        left_interp = self.interpolate_pose(
            self.current_pose['left'], left_target, t
        )
        right_interp = self.interpolate_pose(
            self.current_pose['right'], right_target, t
        )
        
        # 求解关节角度
        left_angles = self.safety_model.inverse_kinematics(
            left_interp, 'left', left_path[-1] if left_path else None
        )
        right_angles = self.safety_model.inverse_kinematics(
            right_interp, 'right', right_path[-1] if right_path else None
        )
        
        # 安全检查
        if not left_angles or not right_angles:
            return None
            
        if self.safety_model.check_dual_arm_collision(left_angles, right_angles):
            return None
        
        left_path.append(left_angles)
        right_path.append(right_angles)
    
    return left_path, right_path
```

### 3. 动态避障

```python
def dynamic_obstacle_avoidance(self, obstacle_pos, obstacle_radius):
    # 修改安全检查以包含动态障碍物
    def check_obstacle_collision(joint_positions):
        for i in range(len(joint_positions) - 1):
            # 计算连杆到障碍物的距离
            dist = self.point_to_segment_distance(
                obstacle_pos,
                joint_positions[i],
                joint_positions[i+1]
            )
            
            if dist < obstacle_radius + self.safety_model.link_radius:
                return True
        
        return False
    
    return check_obstacle_collision
```

## 性能优化

### 1. 缓存优化

```python
class OptimizedSafetyModel(DualArmSafetyModel):
    def __init__(self):
        super().__init__()
        self._fk_cache = {}
    
    def forward_kinematics(self, joint_angles, arm='left'):
        # 缓存键
        key = (tuple(joint_angles), arm)
        
        if key in self._fk_cache:
            return self._fk_cache[key]
        
        result = super().forward_kinematics(joint_angles, arm)
        self._fk_cache[key] = result
        
        return result
```

### 2. 并行计算

```python
import concurrent.futures

def parallel_collision_check(self, paths):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        
        for i, (left_angles, right_angles) in enumerate(paths):
            future = executor.submit(
                self.safety_model.check_dual_arm_collision,
                left_angles, right_angles
            )
            futures.append((i, future))
        
        results = []
        for i, future in futures:
            collision = future.result()
            results.append((i, collision))
    
    return results
```

## 故障排除

### 常见问题

1. **逆运动学无解**
   - 检查目标位置是否在工作空间内
   - 尝试不同的初始关节角度
   - 验证目标姿态是否合理

2. **频繁碰撞检测**
   - 增加安全裕度
   - 减小运动速度
   - 优化路径规划算法

3. **性能问题**
   - 启用缓存机制
   - 减少路径点数量
   - 使用简化的碰撞检测

### 调试建议

```python
# 启用详细日志
import logging

logging.basicConfig(level=logging.DEBUG)

# 可视化调试
def visualize_configuration(self, joint_angles, arm):
    positions = self.safety_model.get_joint_positions(joint_angles, arm)
    
    print(f"{arm}臂关节位置:")
    for i, pos in enumerate(positions):
        print(f"  关节{i}: {pos}")
    
    # 检查每个连杆
    for i in range(len(positions) - 1):
        length = np.linalg.norm(positions[i+1] - positions[i])
        print(f"  连杆{i}长度: {length:.1f}mm")
```

## 最佳实践

1. **始终进行预检查**：在执行运动前验证路径安全性
2. **使用合理的安全裕度**：根据实际精度调整
3. **实时监控**：运动过程中持续检查安全状态
4. **异常处理**：为所有可能的失败情况准备处理方案
5. **定期校准**：确保模型参数与实际机器人一致

## 总结

双臂安全避障模型提供了完整的安全保障机制，通过合理的集成和配置，可以有效防止机械臂碰撞，确保系统安全可靠运行。在实际应用中，应根据具体需求调整参数和扩展功能。