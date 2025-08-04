# FR3机械臂Python控制脚本集

这个文件夹包含了基于法奥FR3机械臂Python SDK开发的控制脚本。

## 📁 脚本文件

### 1. fr3_point_recorder.py - 点位记录工具 ⭐推荐
**主要功能：**
- 实时显示机械臂当前TCP位置和关节角度
- 记录并命名当前点位
- 保存为JSON文件和Python代码格式
- 管理已记录的点位（查看、删除）
- 从JSON文件加载历史记录

**使用场景：**
- 将web界面示教的点位导入到Python脚本
- 记录关键作业点位
- 生成可直接使用的Python代码

**使用方法：**
```bash
python fr3_point_recorder.py
```

### 2. fr3_robot_controller.py - 完整控制程序
**主要功能：**
- 菜单驱动的交互式控制界面
- 机械臂连接管理和使能控制
- 预设安全位置运动
- 手动点动控制
- 实时位置查询

### 3. fr3_quick_test.py - 快速测试工具
**主要功能：**
- 快速连接测试
- 设备信息获取
- 位置信息查询
- 机器人状态检查

**使用方法：**
```bash
# 交互式测试
python fr3_quick_test.py

# 简单连接测试
python fr3_quick_test.py --simple

# 指定IP的完整测试
python fr3_quick_test.py --ip 192.168.58.2
```

### 4. fr3_motion_demo.py - 运动控制演示
**主要功能：**
- 关节运动演示
- TCP直线运动演示  
- 点动运动演示
- 完整运动序列展示

**⚠️ 注意：此脚本会使机械臂运动，使用前确保安全！**

## 🚀 快速开始

### 点位记录工作流程

1. **启动点位记录工具**
   ```bash
   cd "/mnt/c/xc robot/mvp-1/xc-robot/testpy"
   python fr3_point_recorder.py
   ```

2. **记录点位步骤**
   - 选择 `1` 查看当前位置
   - 手动示教机械臂到目标位置
   - 选择 `2` 记录当前点位
   - 输入点位名称（如：home, pick_point, place_point等）
   - 重复以上步骤记录所有需要的点位

3. **保存和使用**
   - 选择 `5` 保存为JSON文件（便于备份和加载）
   - 选择 `6` 保存为Python代码（可直接在程序中使用）

4. **生成的Python代码示例**
   ```python
   # TCP位置字典 (单位: mm, 度)
   TCP_POSITIONS = {
       'home': [  400.000,    0.000,  400.000, 180.000,   0.000,   0.000],
       'pick_point': [  350.000,  150.000,  300.000, 180.000,   0.000,   0.000],
       'place_point': [  350.000, -150.000,  300.000, 180.000,   0.000,   0.000],
   }
   
   # 使用示例
   robot.MoveL(TCP_POSITIONS['home'], tool=0, user=0, vel=15)
   ```

## 🔧 核心API使用

所有脚本都基于以下核心API：

```python
from fairino import Robot

# 连接机械臂
robot = Robot.RPC('192.168.58.2')

# 基本设置
robot.Mode(0)           # 自动模式
robot.RobotEnable(1)    # 使能

# 获取位置
error, tcp_pos = robot.GetActualToolFlangePose()        # TCP位置
error, joint_pos = robot.GetActualJointPosDegree()     # 关节角度

# 运动控制
robot.MoveJ(joint_angles, tool=0, user=0, vel=15)      # 关节运动
robot.MoveL(tcp_position, tool=0, user=0, vel=15)      # 直线运动

# 点动控制
robot.StartJOG(ref=0, nb=1, dir=1, max_dis=5.0, vel=10) # 开始点动
robot.StopJOG(1)                                        # 停止点动

# 断开连接
robot.CloseRPC()
```

## 📊 输出文件格式

### JSON格式
```json
{
  "home": {
    "name": "home",
    "tcp_position": [400.000, 0.000, 400.000, 180.000, 0.000, 0.000],
    "joint_position": [0.000, -30.000, -90.000, -90.000, 90.000, 0.000],
    "timestamp": "2025-07-30T10:30:45.123456",
    "description": "机械臂零位"
  }
}
```

### Python代码格式
生成可直接使用的Python字典和示例代码，包含：
- TCP_POSITIONS字典：TCP坐标位置
- JOINT_POSITIONS字典：关节角度位置
- 使用示例代码

## 🛡️ 安全提醒

1. **使用前检查**
   - 确保机械臂周围无人员和障碍物
   - 准备好急停按钮
   - 检查机械臂电源和网络连接

2. **记录点位时**
   - 手动示教到安全位置
   - 避免奇异点和关节限位
   - 确认位置准确后再记录

3. **运动控制时**
   - 首次使用建议降低速度
   - 随时准备按Ctrl+C中断程序
   - 注意工作空间限制

## 💡 使用技巧

1. **批量记录点位**
   - 先在web界面完成所有示教
   - 使用点位记录工具逐个记录
   - 给点位起有意义的名称

2. **点位命名建议**
   - 使用英文和下划线：`pick_point_1`
   - 体现功能：`home`, `safe_position`, `work_area_center`
   - 按序列编号：`path_point_01`, `path_point_02`

3. **文件管理**
   - 定期备份JSON文件
   - 给生成的文件加上日期时间戳
   - 为不同项目创建不同的点位文件

## 🔍 故障排除

**连接失败：**
- 检查IP地址是否正确（固定192.168.58.2）
- 确认机械臂电源开启
- 检查网络连接

**无法获取位置：**
- 确认机械臂正常启动
- 检查示教盒显示是否正常
- 尝试重新连接

**运动异常：**
- 检查机械臂是否已使能
- 确认目标位置在工作空间内
- 检查是否有故障报警

## 📞 技术支持

如有问题，请检查：
1. fr3_control文件夹是否存在
2. fairino库是否正确导入
3. 机械臂硬件连接状态
4. 网络配置是否正确