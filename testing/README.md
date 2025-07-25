# XC-ROBOT 测试系统

> 完整的测试框架和质量保证体系

## 📋 测试架构

XC-ROBOT采用分层测试架构，确保系统的可靠性、安全性和性能表现。

```
testing/
├── hardware/           # 硬件层测试
│   ├── SAT*.py        # 单臂测试 (Single Arm Tests)
│   ├── DAT*.py        # 双臂协调测试 (Dual Arm Tests)
│   ├── logs/          # 测试日志和报告
│   └── *.md           # 测试文档和指南
├── integration/       # 集成测试
│   ├── chassis_relative_move.py     # 底盘移动测试
│   ├── dual_arm_realtime_monitor.py # 双臂实时监控
│   └── acceptance/    # 验收测试
├── simulation/        # 仿真测试
│   └── dual_arm_simulation_trajectory.py # 双臂仿真轨迹
├── unit/             # 单元测试
├── scripts/          # 测试工具脚本
│   └── fr3_diagnostic.py # FR3诊断工具
└── README.md         # 本文档
```

## 🎯 测试分类

### 1. 硬件层测试 (`hardware/`)

**SAT系列 - 单臂测试**:
- `SAT001.py` - 连接性测试
- `SAT002.py` - 基础运动测试  
- `SAT003.py` - 笛卡尔空间运动测试
- `SAT004.py` - 工作空间测试

**DAT系列 - 双臂协调测试**:
- `DAT001.py` - 双臂同步连接测试
- `DAT002.py` - 双臂安全距离测试

**测试文档**:
- `Testing_Plan.md` - 综合测试规划
- `Testing_Programs_Guide.md` - 测试程序详细指南
- `Testing_implement_guide.md` - 实施指南

### 2. 集成测试 (`integration/`)

- **底盘集成**: `chassis_relative_move.py` - 底盘相对移动控制
- **双臂监控**: `dual_arm_realtime_monitor.py` - 双臂实时状态监控
- **验收测试**: `acceptance/` - 系统验收测试用例

### 3. 仿真测试 (`simulation/`)

- **轨迹仿真**: `dual_arm_simulation_trajectory.py` - 双臂仿真轨迹测试

### 4. 工具脚本 (`scripts/`)

- **诊断工具**: `fr3_diagnostic.py` - FR3库和环境诊断

## 🚀 快速开始

### 环境准备
```bash
# 激活虚拟环境
source venv/bin/activate

# 检查依赖
python testing/scripts/fr3_diagnostic.py

# 检查网络连接
ping 192.168.58.2  # 右臂FR3
ping 192.168.58.3  # 左臂FR3
ping 192.168.31.211  # Hermes底盘
```

### 运行测试

**硬件连接测试**:
```bash
# 单臂连接测试
cd testing/hardware
python SAT001.py --arm right --ip 192.168.58.2

# 双臂协调测试
python DAT001.py --left-ip 192.168.58.3 --right-ip 192.168.58.2
```

**集成测试**:
```bash
# 双臂实时监控
cd testing/integration
python dual_arm_realtime_monitor.py

# 底盘移动测试
python chassis_relative_move.py
```

## 📊 测试报告

所有测试会生成详细报告：
- **JSON报告**: `logs/[TEST_ID]_[arm]_report_[timestamp].json`
- **详细日志**: `logs/[TEST_ID]_[arm]_[timestamp].log`
- **数据文件**: CSV格式数据文件（工作空间测试等）

## 🛡️ 安全注意事项

1. **测试前检查**:
   - [ ] 机械臂周围无人员和障碍物
   - [ ] 急停按钮可正常使用
   - [ ] 网络连接稳定
   - [ ] 机械臂状态正常

2. **测试过程中**:
   - 随时准备按下急停按钮
   - 监控机械臂运动状态
   - 注意双臂安全距离

3. **异常处理**:
   - 立即按下急停按钮
   - 记录异常现象
   - 检查日志文件

## 🔗 相关文档

- [项目测试规划](./hardware/Testing_Plan.md)
- [测试程序指南](./hardware/Testing_Programs_Guide.md)
- [完整文档中心](../docs/README.md)
- [硬件系统文档](../docs/hardware/)

---

**更新时间**: 2025-07-25  
**测试覆盖**: 硬件/集成/仿真/工具  
**状态**: 重构完成，结构优化