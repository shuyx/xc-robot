# XC-ROBOT 跨平台部署指南

> 完整的Windows、macOS、Linux跨平台部署和环境配置指南

**更新时间**: 2025-07-25  
**支持平台**: Windows 11, macOS, Linux  
**架构版本**: v3.1

---

## 📋 目录

- [平台兼容性概览](#平台兼容性概览)
- [Windows部署指南](#windows部署指南)
- [macOS部署指南](#macos部署指南)
- [Linux部署指南](#linux部署指南)
- [Git同步策略](#git同步策略)
- [环境验证](#环境验证)
- [常见问题](#常见问题)

---

## 🎯 平台兼容性概览

### ✅ 完全支持的平台

| 平台 | 版本要求 | Python | GUI框架 | 状态 |
|------|---------|--------|---------|------|
| **Windows** | Windows 10/11 | Python 3.7+ | PyQt5 | ✅ 完全支持 |
| **macOS** | macOS 10.14+ | Python 3.7+ | PyQt5 | ✅ 完全支持 |
| **Linux** | Ubuntu 18.04+ | Python 3.7+ | PyQt5 | ✅ 完全支持 |

### 🔧 自动适配特性

- ✅ **依赖管理**: 平台特定依赖自动安装
- ✅ **路径处理**: 文件路径分隔符自动适配
- ✅ **GUI配置**: 字体、缩放、主题自动适配
- ✅ **启动脚本**: 平台特定启动脚本自动生成
- ✅ **网络配置**: 机器人IP配置统一管理

---

## 🖥️ Windows部署指南

### 前置要求

- Windows 10/11 (64位)
- Python 3.7+ ([下载地址](https://www.python.org/downloads/))
- Git ([下载地址](https://git-scm.com/download/win))
- 管理员权限 (推荐)

### 🚀 一键自动配置

#### 方法1: 自动配置脚本 (推荐)

```batch
# 1. 克隆项目
git clone <repository-url>
cd xc-robot
git checkout mac-dev

# 2. 运行自动配置
python scripts/setup_windows.py
```

**自动配置包含**:
- ✅ 环境检测 (Python版本、Git等)
- ✅ 虚拟环境创建
- ✅ 依赖自动安装
- ✅ 平台配置生成
- ✅ 启动脚本创建
- ✅ 环境验证

#### 方法2: 手动配置

```batch
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate.bat

# 2. 安装核心依赖
pip install -r requirements.txt

# 3. 可选: 安装额外功能
pip install -r requirements/dev.txt          # 开发工具
pip install -r requirements/monitoring.txt   # 监控图表
pip install -r requirements/simulation_vtk.txt  # VTK 3D仿真

# 4. 配置平台
python core/platform/config.py

# 5. 验证安装
python -c "import PyQt5, numpy, cv2; print('✅ 环境配置成功')"
```

### 📱 启动应用

#### GUI桌面版
```batch
# 方式1: 双击启动脚本
start_xc_robot.bat

# 方式2: 命令行启动
venv\Scripts\activate.bat
python apps/launchers/start_desktop_gui.py
```

#### Web界面版
```batch
# 方式1: 双击Web启动脚本
start_web_interface.bat

# 方式2: 命令行启动
venv\Scripts\activate.bat
python apps/launchers/start_web_dev.py
```

### 🔗 快捷方式

配置完成后，项目根目录会生成:
- `start_xc_robot.bat` - 桌面GUI启动器
- `start_web_interface.bat` - Web界面启动器

---

## 🍎 macOS部署指南

### 前置要求

- macOS 10.14+ 
- Python 3.7+ (推荐使用Homebrew安装)
- Git (通常系统自带)
- Xcode Command Line Tools

### 🚀 快速配置

```bash
# 1. 安装Homebrew (如未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装Python
brew install python@3.9

# 3. 克隆项目
git clone <repository-url>
cd xc-robot
git checkout mac-dev

# 4. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt

# 6. 配置平台
python core/platform/config.py

# 7. 启动应用
python apps/launchers/start_desktop_gui.py
```

### 📱 启动应用

```bash
# GUI桌面版
source venv/bin/activate
python apps/launchers/start_desktop_gui.py

# Web界面版
source venv/bin/activate  
python apps/launchers/start_web_dev.py

# 或使用生成的启动脚本
./start_xc_robot.sh
```

---

## 🐧 Linux部署指南

### 前置要求 (Ubuntu/Debian)

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install python3 python3-venv python3-pip git -y

# 安装PyQt5系统依赖
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine -y

# 安装OpenCV系统依赖
sudo apt install libopencv-dev python3-opencv -y
```

### 🚀 快速配置

```bash
# 1. 克隆项目
git clone <repository-url>
cd xc-robot
git checkout mac-dev

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置平台
python core/platform/config.py

# 5. 启动应用
python apps/launchers/start_desktop_gui.py
```

---

## 🔄 Git同步策略

### 💡 重要提醒

**Git代码可以直接同步，但虚拟环境需要重建**

### Windows从Mac同步

```batch
# 1. 切换到目标分支
git checkout mac-dev
git fetch origin
git merge origin/mac-dev

# 2. ⚠️ 重要: 重建虚拟环境
rmdir /s venv  # 删除现有虚拟环境
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt

# 3. 运行平台适配
python core/platform/config.py

# 4. 验证环境
python scripts/setup_windows.py
```

### Mac从Windows同步

```bash
# 1. 切换到目标分支
git checkout mac-dev  
git fetch origin
git merge origin/mac-dev

# 2. ⚠️ 重要: 重建虚拟环境
rm -rf venv  # 删除现有虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 运行平台适配
python core/platform/config.py
```

### 📋 同步检查清单

- [ ] 代码已同步到最新版本
- [ ] 虚拟环境已重建
- [ ] 依赖已重新安装
- [ ] 平台配置已更新
- [ ] 启动脚本已生成
- [ ] 环境验证通过

---

## ✅ 环境验证

### 自动验证脚本

```python
# 运行环境检查
python scripts/setup_windows.py  # Windows
python core/platform/config.py   # Mac/Linux
```

### 手动验证

```python
# 检查关键依赖
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import PyQt5
    print('✅ PyQt5: 可用')
except ImportError:
    print('❌ PyQt5: 未安装')

try:
    import numpy
    print('✅ NumPy: 可用')
except ImportError:
    print('❌ NumPy: 未安装')

try:
    import cv2
    print('✅ OpenCV: 可用')
except ImportError:
    print('❌ OpenCV: 未安装')

try:
    import requests
    print('✅ Requests: 可用')
except ImportError:
    print('❌ Requests: 未安装')
"
```

### 功能验证

```bash
# 测试硬件连接
python testing/hardware/SAT001.py

# 测试双臂协调
python testing/hardware/DAT001.py

# 测试Web界面
python apps/launchers/start_web_dev.py
```

---

## ❓ 常见问题

### Q1: Git同步后程序无法启动

**原因**: 虚拟环境未重建，依赖不匹配

**解决**:
```bash
# 删除旧虚拟环境
rm -rf venv  # Mac/Linux
rmdir /s venv  # Windows

# 重建环境
python -m venv venv
# 激活并安装依赖...
```

### Q2: PyQt5安装失败

**Windows解决**:
```batch
# 使用预编译版本
pip install PyQt5 --only-binary=all

# 或安装Microsoft Visual C++ 14.0+
```

**Linux解决**:
```bash
# 安装系统依赖
sudo apt install python3-pyqt5-dev
```

### Q3: OpenCV导入错误

**解决**:
```bash
# 重新安装opencv-python
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python==4.5.5.64
```

### Q4: 权限问题 (Linux/Mac)

**解决**:
```bash
# 设置启动脚本执行权限
chmod +x start_xc_robot.sh

# 设置项目目录权限
sudo chown -R $USER:$USER /path/to/xc-robot
```

### Q5: Windows防火墙阻止

**解决**:
1. Windows安全中心 → 防火墙和网络保护
2. 允许应用通过防火墙
3. 添加Python.exe和项目应用

### Q6: 网络连接问题

**检查**:
```python
# 测试机器人连接
python -c "
import requests
try:
    r = requests.get('http://192.168.58.2', timeout=5)
    print('✅ FR3右臂连接正常')
except:
    print('❌ FR3右臂连接失败')
"
```

---

## 📞 技术支持

### 📖 文档资源

- **完整文档**: [docs/README.md](docs/README.md)
- **快速开始**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **硬件配置**: [docs/hardware/README.md](docs/hardware/README.md)
- **API文档**: [docs/api/README.md](docs/api/README.md)

### 🔧 调试工具

```bash
# 系统诊断
python tools/quick_test.py

# 硬件诊断  
python testing/scripts/fr3_diagnostic.py

# 平台配置检查
python core/platform/config.py
```

### 📝 日志位置

- **Windows**: `logs\xc-robot.log`
- **Mac/Linux**: `logs/xc-robot.log`
- **运行时错误**: 控制台输出

### 🔧 Windows特有功能

- **自动启动脚本**: 项目根目录已提供 `start_xc_robot.bat` 和 `start_web_interface.bat`
- **环境检测**: 启动时自动检查 PyQt5、NumPy 等关键依赖
- **中文支持**: 启动脚本支持中文界面和提示信息
- **权限管理**: 自动检测管理员权限，提供权限相关指导

---

**📝 维护信息**  
**文档版本**: v3.1  
**最后更新**: 2025-07-25  
**维护人员**: XC-ROBOT开发团队

> 💡 **提示**: 如遇到问题，请先查看[常见问题](#常见问题)部分，或运行自动诊断脚本进行环境检查。