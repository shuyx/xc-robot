# 🚀 XC-ROBOT 快速开始指南

> 5分钟快速上手 XC-ROBOT 轮式双臂类人形机器人系统

## ⚡ 30秒概览

**XC-ROBOT** 是一个基于FR3双臂机械臂 + Hermes移动底盘的综合机器人控制系统，采用现代化Web GUI界面，支持跨平台部署。

```
🤖 XC-ROBOT = FR3双臂 + Hermes底盘 + Gemini视觉 + Web GUI 2.0
```

## 📋 前置条件检查

### 硬件要求
- [ ] FR3机械臂（双臂配置）已连接
- [ ] Hermes移动底盘已上电
- [ ] Gemini深度相机已连接
- [ ] 所有设备在同一网络（192.168.58.x）

### 软件要求
- [ ] Python 3.8-3.11
- [ ] Git
- [ ] 网络连接正常

### 系统支持
- [ ] ✅ Windows 11
- [ ] ✅ macOS 12+
- [ ] ✅ Ubuntu 20.04+

## 🎯 5分钟快速启动

### 步骤1: 获取代码
```bash
# 克隆项目
git clone https://github.com/your-org/xc-robot.git
cd xc-robot

# 检查Python版本
python --version  # 应该是3.8-3.11
```

### 步骤2: 自动环境设置
```bash
# 运行自动安装脚本
python auto_platform_setup.py

# 如果自动安装失败，使用手动安装：
pip install -r requirements.txt
```

### 步骤3: 启动系统
```bash
# 启动Web GUI
python start_web_gui.py

# 或使用启动脚本
cd scripts/startup
./start_xc_robot.sh    # Linux/macOS
start_xc_robot.bat     # Windows
```

### 步骤4: 验证连接
1. 🌐 Web界面应在2-3秒内启动
2. 🔍 点击"连接测试"验证设备状态
3. ✅ 确认所有设备显示绿色（已连接）

## 🎮 第一次使用

### 1. 界面概览
```
┌─────────────────────────────────────────┐
│  🎛️ 控制面板    📊 状态监控    ⚙️ 设置   │
├─────────────────────────────────────────┤
│                                         │
│     🤖 机械臂控制区                      │
│                                         │
├─────────────────────────────────────────┤
│  🚚 底盘导航    👁️ 视觉系统    🎮 仿真    │
└─────────────────────────────────────────┘
```

### 2. 基础操作流程
1. **连接验证** → 点击"测试所有设备"
2. **机械臂控制** → 选择"基础运动"
3. **底盘导航** → 设置目标点并执行
4. **视觉系统** → 查看实时图像
5. **安全停止** → Ctrl+E 紧急停止

### 3. 常用功能
- 🎯 **机械臂归零**: 点击"回到初始位置"
- 🗺️ **底盘定位**: 查看当前位置和地图
- 📸 **视觉捕获**: 保存当前图像
- 📝 **查看日志**: 右侧实时日志面板

## 🔧 常见问题快速解决

### ❌ 启动失败
```bash
# 检查Python环境
which python
python --version

# 检查依赖
pip list | grep PyQt5
pip install PyQt5 PyQtWebEngine

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 🌐 网络连接问题
```bash
# 测试设备连接
ping 192.168.58.2    # FR3右臂
ping 192.168.58.3    # FR3左臂
curl http://192.168.31.211:1448/api/v1/status  # Hermes底盘

# 检查防火墙
sudo ufw allow 8080  # Linux
# Windows: 手动配置防火墙端口
```

### 🖥️ GUI显示问题
```bash
# Linux显示问题
export DISPLAY=:0.0
export QT_QPA_PLATFORM=xcb

# macOS显示问题  
export QT_QPA_PLATFORM=cocoa

# Windows显示问题
# 检查显卡驱动是否最新
```

### 📱 界面响应缓慢
1. 检查系统资源使用率
2. 关闭不必要的后台程序
3. 降低界面刷新频率（设置→界面→刷新率）
4. 考虑升级硬件配置

## 📚 下一步学习路径

### 🎯 初学者路径
1. 📖 [项目技术全览](./project/overview/PROJECT_TECHNICAL_OVERVIEW.md) - 了解整体架构
2. 🎮 [GUI使用手册](./interfaces/web_gui/README_WEB_GUI.md) - 掌握界面操作
3. 🤖 [硬件系统文档](./hardware/README.md) - 了解硬件特性

### 🔧 开发者路径
1. 🏗️ [系统架构设计](./project/design/XC_OS_SYSTEM_DESIGN.md) - 理解系统设计
2. 📓 [开发调试日志](./project/development/development_log.md) - 学习开发经验
3. 🧪 [测试计划](./testing/plans/ROBOT_TESTING_PLAN.md) - 了解测试策略

### 🚀 部署运维路径
1. 📦 [部署指南](./deployment/installation/DEPLOYMENT_GUIDE.md) - 掌握部署技能
2. 🖥️ [跨平台方案](./deployment/configuration/CROSS_PLATFORM_SOLUTION.md) - 多平台适配
3. 🔧 [故障排除](./hardware/fr3_mechanical_arm/troubleshooting/) - 问题解决

## 🆘 紧急情况处理

### 🛑 紧急停止
- **全局停止**: `Ctrl + E`
- **机械臂急停**: 物理急停按钮
- **底盘急停**: 遥控器急停键
- **软件重启**: 关闭程序重新启动

### 📞 获取帮助
1. **文档查找**: 使用本文档中心的搜索功能
2. **日志分析**: 查看右侧实时日志和错误信息
3. **系统诊断**: 运行 `python scripts/health_check.py`
4. **重置系统**: 重启所有硬件设备和软件

## 🎉 成功标志

完成快速开始后，你应该能够：
- ✅ 成功启动Web GUI界面
- ✅ 看到所有设备连接状态为绿色
- ✅ 执行基础的机械臂运动
- ✅ 控制底盘进行简单移动
- ✅ 查看视觉系统实时图像
- ✅ 理解紧急停止操作

## 🔗 快速链接

### 📖 核心文档
- [📋 完整文档中心](./README.md)
- [🎯 项目概述](./project/overview/)
- [🤖 硬件系统](./hardware/)
- [💻 用户界面](./interfaces/)

### 🛠️ 工具和资源
- [⚙️ 配置文件](../config/)
- [🔧 启动脚本](../scripts/startup/)
- [📊 日志文件](../logs/)
- [🎮 仿真系统](./hardware/simulation/)

### 🆘 支持资源
- [❓ 常见问题](./project/development/development_log.md)
- [🔧 故障排除](./deployment/#故障排除)
- [📞 技术支持](./README.md#获取帮助)

---

**🎯 目标**: 让你在5分钟内成功运行XC-ROBOT系统  
**📅 更新**: 2025-07-25  
**🤖 支持**: 如有问题请查看完整文档或联系技术支持  

*祝你使用愉快！🚀*