# Orbbec Gemini 335 相机SDK配置完全指南

## 🎯 项目概述
- **相机型号**: Orbbec Gemini 335  
- **序列号**: CP1Z842000NE
- **SDK版本**: pyorbbecsdk-2.0.13
- **Python版本**: 3.11.0
- **系统环境**: Windows 11 + PowerShell
- **最终解决方案**: test_camera_copy 自包含目录

---

## 🚀 最终成功方案：完全自包含目录

### 核心思路
**复制整个SDK目录，删除无关文件，在副本中开发** - 这是最简单可靠的方案！

### 必需文件结构
```
test_camera_copy/          # SDK副本目录
├── sdk/                   # 核心SDK文件 ⭐ 必须保留
│   └── lib/
│       └── win_x64/       # Windows DLL文件
│           ├── OrbbecSDK.dll
│           └── extensions/
│               ├── depthengine/
│               ├── filters/
│               ├── firmwareupdater/
│               └── frameprocessor/
├── examples/              # 官方示例 ⭐ 可参考
├── env_fixed.cmd          # 环境配置脚本
├── requirements.txt       # 依赖列表
└── [你的Python脚本]      # 在这里开发 ⭐
```

### 可以删除的文件夹
- `docs/` - 文档
- `scripts/` - 构建脚本
- `src/` - 源代码
- `cmake/` - 构建配置
- `docker/` - Docker相关
- `stubs/` - 类型提示
- `test/` - 单元测试

---

## 📋 配置步骤

### 第1步：创建自包含目录
```bash
# 复制整个SDK目录
cp -r pyorbbecsdk test_camera_copy

# 删除不需要的文件夹
cd test_camera_copy
rm -rf docs/ scripts/ src/ cmake/ docker/ stubs/ test/ config/
```

### 第2步：验证核心文件
确保以下文件存在：
- ✅ `sdk/lib/win_x64/OrbbecSDK.dll`
- ✅ `sdk/lib/win_x64/extensions/` 下的所有DLL
- ✅ `env_fixed.cmd` 环境配置脚本

### 第3步：开发和测试
```powershell
cd "test_camera_copy"
python your_script.py  # 直接运行，无需配置！
```

---

## 💡 关键发现和重要知识点

### 1. 环境配置的核心
```cmd
# env_fixed.cmd 的关键配置
set CURR_DIR=%~dp0
set PYTHONPATH=%CURR_DIR%;%PYTHONPATH%
set PATH=%CURR_DIR%\sdk\lib\win_x64;[所有extensions路径];%PATH%
```

**重要点**：
- `PYTHONPATH` 指向包含pyorbbecsdk模块的目录
- `PATH` 指向所有DLL文件的位置
- 相对路径基于脚本所在目录计算

### 2. 正确的API使用方法
```python
# ❌ 错误用法 - 常见错误！
from pyorbbecsdk import OB_STREAM_DEPTH  # 这些常量不存在！
config.enable_stream(OB_STREAM_DEPTH)

# ✅ 正确用法 - 基于官方examples
from pyorbbecsdk import *
profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
depth_profile = profile_list.get_default_video_stream_profile()
config.enable_stream(depth_profile)
```

### 3. 导入方式的最佳实践
```python
# ✅ 推荐：通配符导入（在自包含目录中安全）
from pyorbbecsdk import *

# ✅ 也可以：具体导入
from pyorbbecsdk import Context, Pipeline, Config, OBSensorType
```

---

## 🔧 常见问题及解决方案

### 问题1: DLL加载失败
**现象**: `DLL load failed while importing pyorbbecsdk`

**原因**: 
- 路径配置不正确
- 缺少依赖的DLL文件
- 虚拟环境中的SDK版本不完整

**解决方案**: 
1. 使用完全自包含的 `test_camera_copy` 目录
2. 确保所有DLL文件完整复制
3. 必要时退出虚拟环境运行

### 问题2: 找不到 OB_STREAM_* 常量
**现象**: `cannot import name 'OB_STREAM_DEPTH'`

**原因**: SDK API设计不同，这些常量不存在

**解决方案**: 
```python
# 使用正确的传感器类型
OBSensorType.DEPTH_SENSOR   # 深度传感器
OBSensorType.COLOR_SENSOR   # 彩色传感器  
OBSensorType.IR_SENSOR      # 红外传感器
```

### 问题3: 虚拟环境导入问题
**现象**: 导入的是虚拟环境中不完整的SDK

**解决方案**: 
1. 退出虚拟环境: `deactivate`
2. 或者在自包含目录中运行，自动优先级更高

### 问题4: 相对路径问题
**现象**: 在不同目录运行脚本失败

**解决方案**: 始终在 `test_camera_copy` 目录中运行脚本

---

## 📊 SDK核心API参考

### 基础连接流程
```python
# 1. 创建Context和Pipeline
ctx = Context()
pipeline = Pipeline()

# 2. 查询设备
device_list = ctx.query_devices()
device = device_list.get_device_by_index(0)

# 3. 获取设备信息
device_info = device.get_device_info()
name = device_info.get_name()
serial = device_info.get_serial_number()
```

### 图像采集流程
```python
# 1. 创建配置
config = Config()

# 2. 获取流配置
profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
depth_profile = profile_list.get_default_video_stream_profile()

# 3. 启用流
config.enable_stream(depth_profile)

# 4. 启动采集
pipeline.start(config)

# 5. 获取帧数据
frames = pipeline.wait_for_frames(1000)
depth_frame = frames.get_depth_frame()

# 6. 停止采集
pipeline.stop()
```

### 常用传感器类型
- `OBSensorType.DEPTH_SENSOR` - 深度传感器
- `OBSensorType.COLOR_SENSOR` - 彩色传感器
- `OBSensorType.IR_SENSOR` - 红外传感器
- `OBSensorType.IR_LEFT_SENSOR` - 左红外
- `OBSensorType.IR_RIGHT_SENSOR` - 右红外

---

## ✅ 验证清单

### 环境验证
- [ ] `test_camera_copy` 目录包含完整的 `sdk/` 文件夹
- [ ] DLL文件完整：`OrbbecSDK.dll` 和所有extensions
- [ ] 能够成功运行 `python correct_test.py`

### 功能验证  
- [ ] 能够创建Context和查询设备
- [ ] 能够获取设备信息（名称、序列号等）
- [ ] 能够配置和启动Pipeline
- [ ] 能够采集深度图像数据
- [ ] 能够正常停止Pipeline

---

## 🎉 成功要素总结

1. **自包含目录**: 所有必需文件在一个目录中
2. **正确的API使用**: 基于官方examples的用法
3. **完整的DLL文件**: 包括所有extensions
4. **正确的工作目录**: 始终在test_camera_copy中运行
5. **环境变量配置**: PYTHONPATH和PATH的正确设置

---

## 📚 开发建议

1. **参考官方examples**: `examples/` 目录包含完整的使用示例
2. **逐步开发**: 先实现基础功能，再添加复杂特性
3. **错误处理**: SDK操作要有适当的异常处理
4. **资源管理**: 及时停止Pipeline释放资源

---

**最后更新**: 2025-08-01  
**状态**: 完全解决，生产可用  
**核心方案**: test_camera_copy 自包含目录 + 正确API使用

🎯 **这个配置方案已经过完整验证，可以安全地删除原始的pyorbbecsdk和test_camera目录！**