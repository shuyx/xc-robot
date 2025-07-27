# FR3机械臂Lua程序执行器

这个文件夹包含了用于控制FR3机械臂执行Lua程序的Python工具。

## 📁 文件说明

### 1. `fr3_lua_executor.py` - 主执行器
功能完整的FR3 Lua程序执行器，支持：
- 连接FR3机械臂 (192.168.58.2)
- 加载指定路径的Lua程序
- 运行、暂停、恢复、停止程序
- 实时监控程序执行状态
- 完整的日志记录

### 2. `execute_test1.py` - 专用执行脚本
专门用于执行`/fruser/test1.lua`程序的简化脚本，提供友好的用户界面。

### 3. `official_test1_executor.py` - 官方示例执行器 ⭐推荐
**完全基于FR3官方示例代码**的test1.lua执行器，严格按照官方WebAPP程序使用接口实现，最贴近官方标准。

### 4. `test_import.py` - 模块导入测试
检查fairino模块导入是否正常，自动修复常见的导入问题。

### 5. `quick_test.py` - 快速连接测试
快速测试与FR3机械臂的连接状态。

## 🚀 快速使用

### 首次使用 - 测试模块导入
```bash
cd testing2
python test_import.py    # 检查fairino模块导入
python quick_test.py     # 测试FR3连接
```

### 方法1: 官方标准执行器 (⭐最推荐)
```bash
cd testing2
python official_test1_executor.py
```

### 方法2: 简化专用执行器
```bash
cd testing2
python execute_test1.py
```

### 方法3: 使用通用执行器
```bash
cd testing2

# 执行指定程序
python fr3_lua_executor.py execute /fruser/test1.lua

# 查看程序状态
python fr3_lua_executor.py status

# 停止程序
python fr3_lua_executor.py stop
```

## 📋 详细命令说明

### 通用执行器命令

```bash
# 执行程序并监控
python fr3_lua_executor.py execute <program_path>

# 仅加载程序
python fr3_lua_executor.py load <program_path>

# 运行当前加载的程序
python fr3_lua_executor.py run

# 停止当前程序
python fr3_lua_executor.py stop

# 暂停当前程序
python fr3_lua_executor.py pause

# 恢复暂停的程序
python fr3_lua_executor.py resume

# 查看程序状态
python fr3_lua_executor.py status

# 仅监控执行
python fr3_lua_executor.py monitor
```

### 使用示例

```bash
# 执行test1.lua程序
python fr3_lua_executor.py execute /fruser/test1.lua

# 执行其他程序
python fr3_lua_executor.py execute /fruser/my_program.lua

# 检查当前状态
python fr3_lua_executor.py status
```

## 🔧 程序功能特点

### 1. 安全连接管理
- 自动设置机械臂为自动模式
- 连接异常处理和重试机制
- 优雅的断开连接

### 2. 完整的程序控制
- **加载程序**: 将Lua程序从机械臂存储加载到内存
- **执行程序**: 开始执行加载的程序
- **暂停/恢复**: 中途暂停和恢复执行
- **停止程序**: 立即停止当前程序

### 3. 实时状态监控
- 程序执行状态 (停止/运行中/暂停)
- 当前执行行号
- 已加载的程序名称
- 执行时间记录

### 4. 完善的日志系统
- 控制台实时输出
- 自动保存日志文件
- 时间戳和执行记录

## ⚙️ 配置说明

### 机械臂IP地址
默认IP: `192.168.58.2`

如需修改，请编辑文件中的IP地址设置：
```python
robot_ip = "192.168.58.2"  # 修改为你的机械臂IP
```

### 程序路径格式
FR3机械臂中Lua程序的标准路径格式：
```
/fruser/program_name.lua
```

其中 `/fruser/` 是FR3固定的用户程序目录。

## 🛠️ 故障排除

### 1. 连接失败
- 检查机械臂是否开机且完全启动
- 确认网络连接: `ping 192.168.58.2`
- 检查机械臂示教器上的网络设置

### 2. 程序加载失败
- 确认程序路径格式正确: `/fruser/test1.lua`
- 检查程序是否存在于机械臂中
- 确保程序文件没有语法错误

### 3. 程序执行失败
- 检查机械臂是否处于自动模式
- 确认机械臂没有报错或急停状态
- 查看程序执行日志获取详细信息

### 4. 权限问题
- 确保机械臂允许外部程序控制
- 检查示教器上的安全设置

## 📊 执行日志

程序会自动生成执行日志文件：
```
fr3_lua_executor_YYYYMMDD_HHMMSS.log
```

日志包含：
- 连接状态
- 程序加载结果
- 执行过程记录
- 错误信息和异常

## 🔍 程序状态说明

| 状态码 | 描述 | 说明 |
|--------|------|------|
| 1 | 程序停止或无程序运行 | 初始状态或执行完成 |
| 2 | 程序运行中 | 正在执行程序 |
| 3 | 程序暂停 | 程序已暂停，可恢复执行 |

## ⚠️ 重要提醒

1. **安全第一**: 确保机械臂周围环境安全，无人员和障碍物
2. **急停准备**: 保持急停按钮在可触及范围内
3. **程序验证**: 执行前确认Lua程序的安全性
4. **网络稳定**: 保持与机械臂的网络连接稳定
5. **日志查看**: 出现问题时及时查看日志文件获取详细信息

## 📞 使用支持

如果遇到问题，请：
1. 查看执行日志文件
2. 检查机械臂示教器状态
3. 确认网络连接和程序路径
4. 联系技术支持团队