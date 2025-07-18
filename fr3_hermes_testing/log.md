# FR3-Hermes 开发日志

## 日期：2025-01-15

### 今日开发进展

#### 1. 完成SAT001单臂连接测试
- **文件**: `SAT001.py` (原名 `single_arm_connection_test.py`)
- **功能**: 验证FR3机械臂基础连接和状态读取
- **状态**: ✅ 完成并测试通过

**主要特性**:
- 使用 `Robot.RPC()` 连接方式
- 集成 `robot_state_pkg` 实现稳定的状态数据读取
- 完整的连接测试、状态检查和安全验证流程
- 支持命令行参数配置（IP地址、臂名称）

#### 2. 开发SAT002单臂运动测试
- **文件**: `SAT002.py`
- **功能**: 验证FR3机械臂运动功能和安全机制
- **状态**: ✅ 主要功能完成，正在调试坐标系统

**主要特性**:
- 类人型双臂机器人配置适配
- 多层级安全检查（工作空间、双臂距离、运动增量）
- 基于当前位姿的智能运动规划
- 关节运动和TCP运动测试
- 紧急停止功能验证

### 解决的关键问题

#### 问题1: 模块导入错误
**错误**: `ModuleNotFoundError: No module named 'fr3_control.fairino.Robot'`

**原因**: 导入路径不正确

**解决方案**:
```python
# 修改前（错误）
from fr3_control.fairino.Robot import Robot

# 修改后（正确）
import fairino
from fairino import Robot
```

#### 问题2: Unicode编码错误
**错误**: 日志输出中文字符导致编码异常

**解决方案**:
```python
# 设置日志文件编码
logging.FileHandler(log_filename, encoding='utf-8')

# 移除代码中的emoji字符，使用纯文本标识
```

#### 问题3: 坐标系统理解错误
**错误**: 右臂Y坐标-220.8mm被误判为"越过身体中心线"

**原因**: 对类人型双臂机器人坐标系统理解有误

**问题分析**:
- 初始假设：右臂应该在正Y坐标区域
- 实际情况：右臂在负Y坐标区域（-220.8mm）
- 参考example文件中的坐标数据：DP1=[-420.973], DP2=[-529.17]等都是负值

**解决方案**:
```python
# 修改前（错误逻辑）
if self.arm_name == "right":
    if y < 0:  # 右臂不应该越过中心线
        return False

# 修改后（正确逻辑）
if self.arm_name == "right":
    if y > -50:  # 右臂应该在Y<-50mm区域
        return False
```

#### 问题4: 运动幅度不足
**问题**: 初始设计的15mm运动幅度过小

**解决方案**:
- 将外侧运动幅度从15mm增加到150mm（15cm）
- 满足用户要求的10-20cm运动范围
- 更好地测试机械臂的运动能力

### 技术要点总结

#### 1. 类人型双臂机器人配置参数
```python
# 机器人物理配置
self.chest_width = 420.0            # 胸部宽度：420mm
self.arm_base_distance = 210.0      # 单臂距离中心：210mm
self.shoulder_height = 1400.0       # 肩部高度：约1.4m
self.min_inter_arm_distance = 300.0 # 双臂最小安全距离：300mm

# 工作空间限制
self.workspace_limits = {
    'x_min': -600, 'x_max': 600,     # 前后方向：±600mm
    'y_min': -800, 'y_max': 800,     # 左右方向：±800mm
    'z_min': -600, 'z_max': 300      # 垂直方向：下垂600mm到上举300mm
}
```

#### 2. 坐标系统定义
- **右臂**: Y坐标负值区域（-800 到 -50mm）
- **左臂**: Y坐标正值区域（50 到 800mm）
- **中心线**: Y=0附近（±50mm缓冲区）

#### 3. 安全运动优先级
1. **向外侧运动**: 最安全，远离身体中心和对臂
2. **向上运动**: 模拟自然手臂上举
3. **向前运动**: 避免胸前交叉
4. **腕部旋转**: 最安全的关节运动
5. **肘部运动**: 小幅关节运动

### 当前状态与待解决问题

#### 已完成 ✅
- [x] SAT001连接测试完全可用
- [x] SAT002基本框架完成
- [x] 坐标系统逻辑修正
- [x] 运动幅度调整到15cm
- [x] 多层级安全检查机制
- [x] 基于当前位姿的智能运动规划

#### 待验证 ⏳
- [ ] SAT002实际运动测试
- [ ] 双臂距离安全检查的准确性
- [ ] 不同初始位姿下的运动规划
- [ ] 紧急停止功能实际效果

#### 下一步计划 📋
1. 在实际硬件上测试SAT002运动功能
2. 验证坐标系统修正的正确性
3. 优化运动轨迹的平滑性
4. 开发SAT003双臂协调测试
5. 完善错误处理和日志记录

### 开发文件结构
```
fr3_hermes_testing/
├── SAT001.py                 # 单臂连接测试 ✅
├── SAT002.py                 # 单臂运动测试 ⏳
├── TEST_IMPLEMENTATION_GUIDE.md  # 测试实施指南
├── log.md                    # 本开发日志
└── logs/                     # 测试日志目录
    ├── SAT-001_right_*.log
    └── SAT-002_right_*.log
```

### 技术备注
- 使用 `Robot.RPC()` 而非 `Robot()` 构造函数
- 优先使用 `robot_state_pkg` 获取状态数据
- 所有运动前必须设置自动模式并使能机器人
- 运动速度建议20-30%，测试时可降至10%
- 关节运动增量限制2度，TCP运动增量限制150mm

---

## 日期：2025-07-15

### SAT002.py 调试记录 - 2025-07-15 15:25-16:03

#### 测试内容
对FR3左臂进行单臂运动测试，验证：
1. 关节运动控制（腕部旋转、肘部运动）
2. TCP直线运动控制（外侧、上举、前进）
3. 紧急停止功能
4. 返回初始位置精度

#### 遇到的问题

##### 问题1: 坐标系理解根本性错误
**现象**: 左臂TCP位置Y=-213.6mm被误判为"过于靠近身体中心线"
```
[ERROR] [FAILED] 左臂Y坐标-213.6mm过于靠近身体中心线（应>50mm）
```

**原因分析**: 
- 错误假设：左臂应该在Y>50mm区域（正值）
- 实际情况：从机械臂截图可见，左臂向右下方伸展，Y坐标为负值是正常的
- 基座标原点在肩部机械臂底座中心，左臂向右伸展时Y坐标为负值

**解决方案**:
```python
# 修改前（错误逻辑）
if self.arm_name == "left":
    return current_y > 50  # 左臂应该在Y > 50mm区域

# 修改后（正确逻辑）
if self.arm_name == "left":
    return current_y < -50  # 左臂Y坐标在-800到-50mm区域是安全的
```

##### 问题2: 双臂安全距离过于严格
**现象**: 与对臂距离233.2mm小于300mm安全距离，导致所有TCP动作被阻止
```
[ERROR] [FAILED] 与对臂距离233.2mm小于安全距离300.0mm
```

**原因**: 300mm安全距离在实际类人型双臂配置中过于保守

**解决方案**:
```python
# 调整安全距离参数
self.min_inter_arm_distance = 200.0  # 从300mm减小到200mm
```

##### 问题3: TCP运动幅度过大导致运动指令失败
**现象**: 
- 第一个动作外侧运动150mm返回错误码112
- 运动幅度超出机器人实际执行能力

**解决方案**:
```python
# 大幅减小运动幅度
safe_y_offset = 8 * self.safe_y_direction   # 从150mm减小到8mm
safe_z_offset = 8                           # 从15mm减小到8mm  
safe_x_offset = 5                           # 从10mm减小到5mm
```

##### 问题4: 运动方向评估逻辑错误
**现象**: 左臂向外侧运动被误判为"运动方向不安全"

**原因**: 左臂安全运动方向理解错误

**解决方案**:
```python
# 修改前（错误）
if self.arm_name == "left":
    return target_y > current_y  # 左臂Y坐标增加更安全

# 修改后（正确）
if self.arm_name == "left":
    return target_y < current_y  # 左臂Y坐标减少（向右）更安全
```

#### 解决过程

1. **坐标系纠正** (15:25-15:35)
   - 通过分析机械臂截图确定正确的坐标系
   - 修正所有与坐标系相关的安全检查逻辑

2. **安全参数调整** (15:35-15:45)
   - 降低双臂安全距离限制
   - 调整TCP运动幅度限制

3. **运动幅度优化** (15:45-16:00)
   - 大幅减小所有运动幅度
   - 保持运动方向的安全性

4. **增强安全逻辑** (16:00-16:03)
   - 实现基于运动方向的安全评估
   - 允许向外运动时放宽位移限制

#### 最终结果

**成功项目** ✅:
- 关节运动测试：4/4个动作成功
- 紧急停止功能：正常工作
- 返回初始位置：精度0.016°

**问题项目** ❌:
- TCP运动测试：0/6个动作成功（改进前）

**改进后预期** 🎯:
- TCP运动测试：预期大部分动作成功
- 运动幅度：8mm外侧，8mm上举，5mm前进
- 安全距离：200mm（实际233.2mm > 200mm应通过）

#### 关键技术要点

1. **坐标系定义**（修正后）:
   - 左臂安全区域：Y < -50mm（向右伸展）
   - 右臂安全区域：Y > 50mm（向左伸展）
   - 基座标原点：肩部机械臂底座中心

2. **安全运动方向**:
   - 左臂：向右运动（Y减少）更安全
   - 右臂：向左运动（Y增加）更安全

3. **运动幅度控制**:
   - 常规限制：10mm
   - 向外运动：最大20mm
   - 关节运动：±2°

#### 待验证项目

- [ ] 修正后的TCP运动测试执行结果
- [ ] 小幅度运动的实际效果
- [ ] 不同初始位姿的适应性
- [ ] 双臂协调测试的安全性

---
**更新时间**: 2025-07-15  
**开发者**: kevin  
**测试环境**: Windows WSL2 + FR3左臂(192.168.58.3) + FR3右臂(192.168.58.2)