# 部署和配置文档

> XC-ROBOT 系统部署、配置和环境管理完整指南

## 🚀 部署概述

XC-ROBOT系统支持跨平台部署，提供完整的自动化部署解决方案。支持Windows 11、macOS和Linux系统，具备智能平台检测、依赖管理和配置优化功能。

## 🏗️ 部署架构

```
        XC-ROBOT 部署架构
    ┌─────────────────────────────┐
    │        平台检测层            │
    │   ├─ Windows 11            │
    │   ├─ macOS (Darwin)        │
    │   └─ Linux (Ubuntu/CentOS) │
    ├─────────────────────────────┤
    │        配置管理层            │
    │   ├─ 平台特定配置           │
    │   ├─ 依赖管理              │
    │   └─ 环境变量设置           │
    ├─────────────────────────────┤
    │        服务部署层            │
    │   ├─ Web GUI服务           │
    │   ├─ 硬件驱动服务           │
    │   └─ 仿真服务              │
    └─────────────────────────────┘
```

## 📁 部署文档模块

### 📦 安装部署 (`installation/`)
- [🎯 **DEPLOYMENT_GUIDE.md**](./installation/DEPLOYMENT_GUIDE.md) - FR3机械臂系统完整部署指南
- [📋 **requirements_basic.txt**](./installation/requirements_basic.txt) - 基础Python依赖配置

### ⚙️ 配置管理 (`configuration/`)
- [🖥️ **CROSS_PLATFORM_SOLUTION.md**](./configuration/CROSS_PLATFORM_SOLUTION.md) - 跨平台开发和部署解决方案

### 🔧 部署脚本 (`scripts/`)
- 自动化部署脚本和工具集合（待完善）

## 🎯 快速部署指南

### 1. 系统要求

#### 最低配置
- **CPU**: Intel i5 或 AMD Ryzen 5 (4核心)
- **内存**: 8GB RAM
- **存储**: 20GB 可用空间
- **网络**: 千兆以太网
- **GPU**: 集成显卡（仿真需要独立显卡）

#### 推荐配置
- **CPU**: Intel i7 或 AMD Ryzen 7 (8核心)
- **内存**: 16GB RAM
- **存储**: 50GB SSD空间
- **网络**: 千兆以太网 + WiFi
- **GPU**: 独立显卡（NVIDIA GTX 1060+）

### 2. 平台支持

#### Windows 11
```powershell
# 系统要求
- Windows 11 (Build 22000+)
- PowerShell 5.1+
- Visual Studio Build Tools
- Python 3.8-3.11

# 依赖安装
pip install pywin32>=227 PyQtWebEngine>=5.15.0
```

#### macOS
```bash
# 系统要求
- macOS 12.0+ (Monterey)
- Xcode Command Line Tools
- Homebrew
- Python 3.8-3.11

# 依赖安装
brew install python-tk
pip install PyQt5 PyQtWebEngine
```

#### Linux (Ubuntu/CentOS)
```bash
# 系统要求
- Ubuntu 20.04+ / CentOS 8+
- GCC 9.0+
- X11 display server
- Python 3.8-3.11

# 依赖安装
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine
```

### 3. 安装步骤

#### 自动安装（推荐）
```bash
# 克隆项目
git clone https://github.com/your-org/xc-robot.git
cd xc-robot

# 运行自动安装脚本
python auto_platform_setup.py

# 启动系统
python start_web_gui.py
```

#### 手动安装
```bash
# 1. 环境检查
python --version  # 确保3.8-3.11
pip --version     # 确保最新版本

# 2. 创建虚拟环境
python -m venv xc_robot_env
source xc_robot_env/bin/activate  # Linux/macOS
# xc_robot_env\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置检查
python platform_config.py --check

# 5. 启动系统
python start_web_gui.py
```

## ⚙️ 配置管理

### 平台适配配置

#### 自动平台检测
```python
# platform_config.py
class PlatformAdapter:
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_mac = self.platform == 'darwin'
        self.is_windows = self.platform == 'windows' 
        self.is_linux = self.platform == 'linux'
```

#### 配置文件结构
```
config/
├── platform_configs.json      # 主配置文件
├── gui_config_darwin.json     # macOS GUI配置
├── gui_config_windows.json    # Windows GUI配置
├── gui_config_linux.json      # Linux GUI配置
├── network_config.json        # 网络配置
└── robot_config.yaml          # 机器人配置
```

### 网络配置

#### 设备网络地址
```yaml
# robot_config.yaml
network:
  hermes_url: "http://192.168.31.211:1448"
  right_arm_ip: "192.168.58.2"
  left_arm_ip: "192.168.58.3"
  controller_ip: "192.168.58.1"
  
# 网络测试
ping 192.168.58.2  # 测试右臂连接
ping 192.168.58.3  # 测试左臂连接
curl http://192.168.31.211:1448/api/v1/status  # 测试底盘API
```

### 环境变量配置

#### 系统环境变量
```bash
# Linux/macOS (.bashrc 或 .zshrc)
export XC_ROBOT_HOME="/path/to/xc-robot"
export XC_ROBOT_CONFIG="$XC_ROBOT_HOME/config"
export PYTHONPATH="$XC_ROBOT_HOME:$PYTHONPATH"

# Windows 系统变量
XC_ROBOT_HOME=C:\path\to\xc-robot
XC_ROBOT_CONFIG=%XC_ROBOT_HOME%\config
PYTHONPATH=%XC_ROBOT_HOME%;%PYTHONPATH%
```

## 🔧 部署脚本

### 自动化部署脚本

#### 环境设置脚本
```bash
#!/bin/bash
# auto_platform_setup.sh

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "检测到 macOS 系统"
    ./scripts/setup_macos.sh
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "检测到 Linux 系统"
    ./scripts/setup_linux.sh
elif [[ "$OSTYPE" == "msys" ]]; then
    echo "检测到 Windows 系统"
    ./scripts/setup_windows.bat
fi
```

#### 依赖检查脚本
```python
# check_dependencies.py
def check_platform_dependencies():
    required_modules = [
        'PyQt5', 'PyQtWebEngine', 'requests', 
        'numpy', 'opencv-python', 'vtk'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - 已安装")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - 未安装")
    
    return missing_modules
```

### 启动脚本

#### 跨平台启动脚本
```bash
# scripts/startup/start_xc_robot.sh (Linux/macOS)
#!/bin/bash
cd "$(dirname "$0")/../.."
source venv/bin/activate
python start_web_gui.py

# scripts/startup/start_xc_robot.bat (Windows)
@echo off
cd /d "%~dp0..\.."
call venv\Scripts\activate.bat
python start_web_gui.py
```

## 🐛 故障排除

### 常见部署问题

#### 依赖问题
```bash
# Python版本冲突
pyenv versions  # 查看Python版本
pyenv global 3.9.7  # 设置全局版本

# Qt依赖问题（Linux）
sudo apt-get install libxcb-xinerama0
sudo apt-get install libqt5multimedia5-plugins

# 权限问题（macOS）
sudo xcode-select --install
```

#### 网络连接问题
```bash
# 测试设备连接
telnet 192.168.58.2 8080  # FR3右臂
telnet 192.168.58.3 8080  # FR3左臂
curl -v http://192.168.31.211:1448/api/v1/status  # Hermes底盘

# 防火墙设置
sudo ufw allow 8080  # Linux
# Windows防火墙需手动配置端口
```

#### GUI启动问题
```bash
# 显示服务器问题（Linux远程）
export DISPLAY=:0.0
xauth add $(xauth -f ~/.Xauthority list | tail -1)

# Qt平台插件问题
export QT_QPA_PLATFORM=xcb  # Linux
export QT_QPA_PLATFORM=cocoa  # macOS
```

### 日志和调试

#### 启用详细日志
```python
# 在start_web_gui.py中添加
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xc_robot.log'),
        logging.StreamHandler()
    ]
)
```

#### 系统诊断脚本
```bash
# system_diagnostic.py
python -c "
import platform, sys, pkg_resources
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print('Installed packages:')
for pkg in pkg_resources.working_set:
    print(f'  {pkg.key}: {pkg.version}')
"
```

## 📊 部署验证

### 系统健康检查
```bash
# 运行系统检查
python scripts/health_check.py

# 预期输出
✅ Python环境: 3.9.7
✅ 依赖检查: 所有模块已安装
✅ 网络连接: 设备响应正常
✅ GUI启动: 界面加载成功
✅ 硬件通信: 设备连接正常
```

### 性能基准测试
```bash
# 运行性能测试
python scripts/benchmark.py

# 预期指标
- 启动时间: <5秒
- 内存使用: <200MB
- GUI响应: <100ms
- 网络延迟: <50ms
```

## 🔗 相关链接

- **⬅️ 返回文档中心**: [../README.md](../README.md)
- **📋 项目文档**: [../project/](../project/)
- **🤖 硬件系统**: [../hardware/](../hardware/)
- **💻 界面系统**: [../interfaces/](../interfaces/)
- **🧪 测试文档**: [../testing/](../testing/)

## 📞 获取帮助

- **部署问题**: 查看 [部署指南](./installation/DEPLOYMENT_GUIDE.md)
- **跨平台支持**: 参考 [跨平台解决方案](./configuration/CROSS_PLATFORM_SOLUTION.md)
- **配置问题**: 检查config目录下的配置文件

---

**📝 维护信息**  
**更新时间**: 2025-07-25  
**支持平台**: Windows 11 / macOS 12+ / Ubuntu 20.04+  
**部署方式**: 自动化脚本 + 手动配置  
**状态**: 持续优化中