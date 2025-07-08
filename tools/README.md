# FR3机械臂分析工具包

本工具包包含用于分析和验证FR3机械臂STL文件、DH参数和RoboDK转换的完整工具集。

## 📁 文件概述

### 核心工具
- `stl_validation.py` - STL文件验证和质量检查工具
- `dh_parameter_analyzer.py` - DH参数分析和运动学验证工具
- `robodk_converter.py` - RoboDK参数转换工具
- `quick_test.py` - 快速功能测试脚本

### 支持文件
- `__init__.py` - 工具包初始化文件
- `README.md` - 本说明文档

## 🚀 快速开始

### 运行快速测试
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行快速测试
python tools/quick_test.py
```

### STL文件验证
```bash
# 验证所有STL文件
python tools/stl_validation.py

# 生成详细报告
python tools/stl_validation.py --report stl_report.txt
```

### DH参数分析
```bash
# 完整分析
python tools/dh_parameter_analyzer.py

# 指定测试类型
python tools/dh_parameter_analyzer.py --test forward
python tools/dh_parameter_analyzer.py --test workspace

# 生成报告
python tools/dh_parameter_analyzer.py --output dh_analysis.json
```

### RoboDK转换
```bash
# 运行转换测试
python tools/robodk_converter.py

# 生成RoboDK程序
python tools/robodk_converter.py --generate-program fr3_program.py
```

## 🔧 工具详解

### 1. STL验证工具 (`stl_validation.py`)

**功能**：
- 检查STL文件完整性和格式
- 验证文件大小和三角形数量
- 计算模型边界和尺寸
- 检测退化三角形和质量问题

**支持格式**：
- STL Binary (推荐)
- STL ASCII

**质量检查**：
- 文件大小 (建议 ≤ 10MB)
- 三角形数量 (建议 10K-100K)
- 模型尺寸合理性
- 几何完整性

### 2. DH参数分析工具 (`dh_parameter_analyzer.py`)

**功能**：
- 正向运动学计算和验证
- 逆向运动学求解 (几何法)
- 工作空间分析
- 奇异性检测
- 精度验证

**DH参数**：
```python
# FR3精确DH参数 (Modified DH Convention)
dh_params = {
    'alpha': [0, -90, 0, 90, -90, 90],      # 连杆扭转角 (度)
    'a': [0, 0, 316, 0, 0, 0],              # 连杆长度 (mm)
    'd': [333, 0, 0, 384, 0, 107],          # 连杆偏移 (mm)
    'theta_offset': [0, -90, 90, 0, 0, 0]   # 关节角偏移 (度)
}
```

**测试用例**：
- 零位位置
- 初始位姿
- 典型工作位置
- 边界测试
- 工作空间分析

### 3. RoboDK转换工具 (`robodk_converter.py`)

**功能**：
- RoboDK角度 ↔ 实际机器人角度转换
- 参数差异分析
- 正向运动学对比验证
- RoboDK程序代码生成

**关键转换**：
```python
# RoboDK → 机器人
robot_angles[1] += 90   # J2补偿
robot_angles[2] -= 90   # J3补偿

# 机器人 → RoboDK  
robodk_angles[1] -= 90  # J2逆向补偿
robodk_angles[2] += 90  # J3逆向补偿
```

## 📊 输出报告

### STL验证报告
- 文件存在性检查
- 格式和大小信息
- 三角形数量统计
- 边界框和尺寸
- 质量问题列表

### DH分析报告
- 正向运动学结果
- 逆向运动学精度
- 工作空间统计
- 奇异性检测
- 综合精度评估

### RoboDK转换报告
- 参数差异对比
- 角度转换验证
- 运动学一致性检查
- 生成的程序代码

## 🛠️ 在代码中使用

```python
# 导入工具包
from tools import STLValidator, DHParameterAnalyzer, RoboDKConverter

# STL验证
validator = STLValidator("models")
results = validator.validate_all_files()

# DH参数分析
analyzer = DHParameterAnalyzer()
T = analyzer.forward_kinematics([0, -30, 90, 0, 60, 0])
pose = analyzer.extract_pose(T)

# RoboDK转换
converter = RoboDKConverter()
robot_angles = [0, -30, 90, 0, 60, 0]
robodk_angles = converter.robot_to_robodk_angles(robot_angles)
```

## 📋 测试结果示例

运行 `python tools/quick_test.py` 的输出：

```
🚀 FR3机械臂分析工具快速测试
==================================================
🔧 测试STL文件验证工具...
✅ STL验证工具测试成功

🔧 测试DH参数分析工具...
  测试角度: [0, -30, 90, 0, 60, 0]
  末端位置: ['267.2', '0.0', '745.2'] mm
✅ DH参数分析工具测试成功

🔧 测试RoboDK转换工具...
  机器人角度: [0, -30, 90, 0, 60, 0]
  RoboDK角度: [0, -120, 180, 0, 60, 0]
  转换回来: [0, -30, 90, 0, 60, 0]
  转换误差: 0.000000 °
✅ RoboDK转换工具测试成功

🔧 集成测试...
  工具包导入: ✅
  工具实例化: ✅
  运动学一致性: 0.000000 mm
✅ 集成测试成功

==================================================
📊 测试结果: 4/4 通过
🎉 所有测试通过！工具包运行正常
```

## 🔗 相关文档

- `../FR3_STL_DH_ANALYSIS.md` - 完整技术分析文档
- `../FR3_ROBOT_ANALYSIS.md` - FR3机械臂运动学分析
- `../STL_NAMING_GUIDE.md` - STL文件命名规范
- `../PROJECT_TECHNICAL_OVERVIEW.md` - 项目技术全览

## 📝 注意事项

1. **STL文件**：当前只有 `fr3_base.stl`，其他连杆STL文件需要补充
2. **精度**：逆向运动学使用简化几何法，精度有限
3. **依赖**：需要 numpy 库，VTK 为可选依赖
4. **单位**：所有长度单位为毫米(mm)，角度单位为度(°)

## 🚧 待完善功能

- [ ] 完整的解析逆运动学求解器
- [ ] STL文件批量转换工具
- [ ] 碰撞检测集成
- [ ] URDF文件生成器
- [ ] 可视化分析界面

---

**版本**: v1.0  
**更新**: 2025-07-08  
**维护**: Claude Code Assistant