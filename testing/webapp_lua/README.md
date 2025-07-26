# WebApp Lua调用测试文件

本目录包含基于webapp lua调用机制的新逻辑测试文件，替代传统的Python状态读取方式。

## 测试架构

### 传统方式（Python状态读取）
```python
# 读取机器人状态
robot_state = robot.GetRobotRealTimeState()
# 基于状态进行判断和测试
if robot_state.status == "ready":
    # 执行测试逻辑
```

### 新方式（WebApp Lua调用）
```python
# 加载并执行lua程序
robot.ProgramLoad(program_name="/fruser/test_program.lua")
robot.ProgramRun()
# 监控lua程序执行状态
while True:
    error, state = robot.GetProgramState()
    if state == "completed":
        break
```

## 文件分类

### 单臂测试 (SAT系列)
- `SAT001_lua_left.py` - 左臂lua连接测试 ✅
- `SAT001_lua_right.py` - 右臂lua连接测试 ✅
- `SAT002_lua_motion.py` - 单臂运动lua测试

### 双臂协作 (DAT系列)
- `DAT001_lua_sync.py` - 双臂同步lua测试 ✅
- `DAT002_lua_coordination.py` - 双臂协作lua测试

### 底盘测试
- `chassis_lua_basic.py` - 底盘基础移动lua测试 ✅
- `chassis_lua_navigation.py` - 底盘导航lua测试

### 视觉系统测试
- `vision_lua_test.py` - 视觉引导操作lua测试 ✅

### 集成测试
- `integration_lua_full.py` - 全系统集成lua测试 ✅
- `e2e_lua_scenario.py` - 端到端场景lua测试

### 夹爪测试
- `gripper_lua_test.py` - 夹爪控制lua测试

### 完整测试套件
- `test_suite_runner.py` - 批量执行所有lua测试

## Lua脚本管理

每个测试文件都包含：
1. **Lua脚本上传** - 将测试脚本上传到机器人控制器
2. **程序加载** - 加载对应的lua程序
3. **执行监控** - 监控lua程序执行状态
4. **结果验证** - 验证lua程序执行结果
5. **资源清理** - 清理lua脚本和状态

## 使用方法

```python
from testing.webapp_lua.SAT001_lua_left import LuaLeftArmTest

# 创建测试实例
test = LuaLeftArmTest(robot_ip="192.168.58.3")

# 执行测试
result = test.run_test()
print(f"测试结果: {result}")
```