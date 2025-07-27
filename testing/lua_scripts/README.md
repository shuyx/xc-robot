# XC-ROBOT Lua-based 测试系统

## 系统概述

XC-ROBOT Lua-based 测试系统是一个基于Lua脚本和Web API的新型测试架构，用于替代传统的直接Python调用方式。该系统通过Web API接口，让Web GUI能够调用Lua测试脚本，实现更灵活、更安全的测试程序执行。

## 架构设计

```
Web GUI (HTML/JavaScript)
      ↓ HTTP API调用
Flask Web API (Python)
      ↓ subprocess调用
Lua测试桥接脚本 (Lua)
      ↓ 调用Python测试程序
现有测试程序 (Python)
      ↓ 设备通信
FR3机械臂 / Hermes底盘 / 视觉系统
```

## 核心组件

### 1. Lua测试桥接脚本 (`test_bridge.lua`)

**功能**：
- 设备连接测试
- 测试程序执行管理
- 安全校验和验证
- 系统日志收集
- 测试结果存储

**主要函数**：
- `test_connection(device_type, device_ip)` - 设备连接测试
- `run_test_program(test_type, test_file)` - 运行测试程序
- `validate_test_safety(test_type, test_params)` - 安全验证
- `get_test_results()` - 获取测试结果
- `get_system_logs(filter_level, max_lines)` - 获取系统日志

### 2. Python桥接器 (`lua_bridge.py`)

**功能**：
- Lua脚本调用封装
- 测试程序管理
- 文件验证功能
- 异常处理

**主要类**：
- `LuaBridge` - Lua脚本调用接口
- `TestProgramManager` - 测试程序分类管理

### 3. Web API服务器 (`web_api.py`)

**功能**：
- RESTful API服务
- HTTP请求处理
- 跨域支持
- 紧急停止功能

**API端点**：
```
POST /api/test/connection      - 设备连接测试
POST /api/test/run             - 运行测试程序
POST /api/test/validate        - 安全验证
POST /api/test/file/validate   - 测试文件验证
GET  /api/test/categories      - 获取测试分类
GET  /api/test/programs/<cat>  - 获取测试程序列表
GET  /api/test/results         - 获取测试结果
GET  /api/logs                 - 获取系统日志
GET  /api/status               - API状态检查
POST /api/emergency_stop       - 紧急停止
```

## 测试分类

系统将测试程序分为7个主要类别：

### 1. 底盘测试 (`chassis_test`)
- 连接测试
- 移动控制测试
- 导航功能测试

### 2. 左臂测试 (`left_arm_test`)
- SAT001: 连接性测试
- SAT002: 基础运动测试
- SAT003: 笛卡尔空间运动测试
- SAT004: 工作空间测试

### 3. 右臂测试 (`right_arm_test`)
- SAT001-004 系列测试（同左臂）

### 4. 双臂协作测试 (`dual_arm_test`)
- DAT001: 同步连接测试
- DAT002: 安全距离测试
- 双臂协调操作测试

### 5. 功能验证测试 (`function_validation`)
- 机械臂功能验证
- 底盘功能验证
- 视觉系统功能验证

### 6. 集成测试 (`integration_test`)
- 双臂实时监控
- 底盘相对移动
- 系统集成测试

### 7. 场景测试 (`scenario_test`)
- 抓取场景测试
- 装配场景测试
- 巡检场景测试

## 安全机制

### 1. 测试前安全检查
- 双臂距离验证（最小300mm安全距离）
- 设备状态检查
- 环境安全确认

### 2. 运行时安全监控
- 实时状态监控
- 异常情况检测
- 自动安全停止

### 3. 紧急停止功能
- 全局紧急停止API
- FR3机械臂立即停止
- 底盘运动立即停止
- 快捷键支持（Ctrl+Shift+E 或 空格键）

## 使用方法

### 1. 启动测试API服务器

```bash
# 方法1：使用启动脚本
python scripts/startup/start_test_api.py

# 方法2：直接启动
cd testing/lua_scripts
python web_api.py
```

### 2. 在Web GUI中使用

Web GUI会自动连接测试API服务器（localhost:5000），提供：
- 可视化设备连接测试
- 交互式测试程序选择
- 实时测试进度显示
- 测试结果查看
- 系统日志监控

### 3. 命令行使用

```bash
# 设备连接测试
python lua_bridge.py test_connection fr3_left 192.168.58.3

# 运行测试程序
python lua_bridge.py run_test left_arm_test SAT001.py

# 获取测试结果
python lua_bridge.py get_results

# 获取系统日志
python lua_bridge.py get_logs info 50
```

## 配置说明

### 设备IP配置
```lua
local config = {
    left_arm_ip = "192.168.58.3",
    right_arm_ip = "192.168.58.2",
    chassis_ip = "192.168.31.211:1448",
    test_timeout = 30,
    safe_distance = 300.0  -- 双臂安全距离(mm)
}
```

### API服务器配置
```python
# web_api.py中的配置
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True
```

## 扩展说明

### 添加新的测试类型

1. 在`test_bridge.lua`中添加新的测试逻辑
2. 在`TestProgramManager`中添加新的测试分类
3. 更新Web GUI中对应的UI元素

### 添加新的设备类型

1. 在`test_bridge.lua`中添加设备连接函数
2. 在`web_api.py`中添加对应的API处理
3. 更新Web GUI中的设备列表

## 故障排除

### 常见问题

1. **Lua解释器未找到**
   ```bash
   # Windows
   choco install lua
   
   # Linux
   sudo apt-get install lua5.3
   
   # macOS
   brew install lua
   ```

2. **API连接失败**
   - 检查测试API服务器是否启动
   - 确认端口5000未被占用
   - 检查防火墙设置

3. **测试程序执行失败**
   - 检查设备网络连接
   - 确认设备IP地址配置
   - 查看详细错误日志

### 调试模式

启用调试模式获取更多信息：
```bash
export FLASK_ENV=development
python web_api.py
```

## 日志文件位置

- 测试日志：`testing/hardware/logs/`
- API日志：控制台输出
- 系统日志：`/var/log/xc-robot/`（如果存在）

## 版本信息

- **版本**: 1.0
- **创建日期**: 2025-07-25
- **Python要求**: 3.7+
- **Lua要求**: 5.3+
- **主要依赖**: Flask, Flask-CORS, requests

## 贡献指南

欢迎提交改进建议和bug报告：
1. Fork项目
2. 创建功能分支
3. 提交变更
4. 创建Pull Request

---

**注意**: 该系统仍在开发中，部分功能可能需要进一步完善。在生产环境中使用前，请充分测试所有功能。