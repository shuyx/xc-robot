# XC-ROBOT 双臂机器人控制系统

> 集成FR3双臂机械臂、Hermes底盘和视觉系统的智能机器人控制平台

**版本**: v3.1  
**更新**: 2025-07-25  
**状态**: 生产就绪 🚀

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](./CROSS_PLATFORM_SETUP.md)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](./LICENSE)

---

## 🤖 系统概览

XC-ROBOT是一个专业的双臂机器人控制系统，支持FR3机械臂双臂协调控制、Hermes移动底盘导航和Gemini 335视觉识别，提供Web GUI、Desktop GUI和RESTful API多种交互方式。

### 🎯 核心特性

- **🦾 双臂协调控制**: FR3机械臂精确同步与独立控制
- **🚗 移动底盘集成**: Hermes底盘自主导航与路径规划  
- **👁️ 视觉感知系统**: Gemini 335相机物体识别与跟踪
- **🌐 多界面支持**: Web界面、桌面GUI、API接口
- **⚖️ 跨平台兼容**: Windows、macOS、Linux全平台支持
- **📦 精简架构**: 优化后仅662M，61%空间节省

### 🏗️ 系统架构

```
XC-ROBOT System Architecture
┌─────────────────────────────────────────────────────┐
│                 用户交互层                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │   Web GUI   │ │ Desktop GUI │ │  RESTful API │    │
│  └─────────────┘ └─────────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│                 应用业务层                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │  任务管理   │ │  路径规划   │ │  视觉处理   │    │
│  └─────────────┘ └─────────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│                 硬件抽象层                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │ FR3双臂控制 │ │ Hermes底盘  │ │ Gemini视觉  │    │
│  └─────────────┘ └─────────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 📋 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|----------|
| **操作系统** | Windows 10, macOS 10.14, Ubuntu 18.04 | Windows 11, macOS 12+, Ubuntu 20.04+ |
| **Python** | 3.7+ | 3.9+ |
| **内存** | 4GB | 8GB+ |
| **存储** | 1GB | 2GB+ |
| **网络** | 以太网连接机器人 | 千兆以太网 |

### ⚡ 一键安装

#### Windows用户
```batch
# 1. 克隆项目
git clone <repository-url>
cd xc-robot

# 2. 运行自动配置
python scripts/setup_windows.py

# 3. 启动应用
start_xc_robot.bat
```

#### macOS/Linux用户
```bash
# 1. 克隆项目
git clone <repository-url>
cd xc-robot

# 2. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 启动应用
python apps/launchers/start_desktop_gui.py
```

### 🔗 详细部署指南

- **📘 跨平台部署**: [CROSS_PLATFORM_SETUP.md](./CROSS_PLATFORM_SETUP.md)
- **📖 完整文档**: [docs/README.md](./docs/README.md)
- **🚀 快速开始**: [docs/QUICKSTART.md](./docs/QUICKSTART.md)

---

## 📁 项目结构

```
xc-robot/                    # 项目根目录 (662M)
├── 📁 docs/                 # 完整文档系统
├── 📁 testing/              # 专业测试框架 (SAT/DAT系列)
├── 📁 tools/                # 开发工具集
├── 📁 core/                 # 核心业务逻辑
├── 📁 apps/                 # 应用程序层
│   ├── desktop/             # 桌面GUI应用
│   ├── web/                 # Web应用
│   └── launchers/           # 启动器集合
├── 📁 api/                  # RESTful API服务
├── 📁 services/             # 后台服务组件
├── 📁 config/               # 配置文件管理
├── 📁 fr3_control/          # FR3机械臂控制库
├── 📁 requirements/         # 分层依赖管理
│   ├── base.txt             # 核心依赖
│   ├── dev.txt              # 开发工具
│   ├── monitoring.txt       # 监控图表
│   └── simulation_vtk.txt   # VTK 3D仿真(可选)
├── requirements.txt         # 主依赖配置
├── CROSS_PLATFORM_SETUP.md  # 跨平台部署指南
└── PROJECT_STRUCTURE_ANALYSIS.md  # 项目架构分析
```

---

## 🎮 使用方式

### 🖥️ 桌面GUI版本

```bash
# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat  # Windows

# 启动桌面GUI
python apps/launchers/start_desktop_gui.py
```

**功能特性**:
- 双臂机械臂实时控制
- 3D仿真显示 (可选VTK)
- 任务编程界面
- 状态监控面板

### 🌐 Web界面版本

```bash
# 启动Web服务
python apps/launchers/start_web_dev.py

# 浏览器访问: http://localhost:8080
```

**功能特性**:
- 响应式Web界面
- 实时状态监控
- 远程控制能力
- 多用户支持

### 🔌 API接口版本

```bash
# 启动API服务
python apps/launchers/start_api_server.py

# API文档: http://localhost:8000/docs
```

**RESTful API**:
- `/api/v1/robots/` - 机器人控制
- `/api/v1/tasks/` - 任务管理
- `/api/v1/vision/` - 视觉识别
- `/api/v1/status/` - 系统状态

---

## 🧪 测试框架

### SAT系列 (单臂测试)
```bash
python testing/hardware/SAT001.py  # 连接性测试
python testing/hardware/SAT002.py  # 运动测试
python testing/hardware/SAT003.py  # 工作空间测试
python testing/hardware/SAT004.py  # 精度测试
```

### DAT系列 (双臂协调测试)
```bash
python testing/hardware/DAT001.py  # 双臂同步测试
python testing/hardware/DAT002.py  # 协调安全测试
```

### 集成测试
```bash
python testing/integration/dual_arm_realtime_monitor.py
python testing/integration/chassis_relative_move.py
```

---

## 🔧 配置管理

### 网络配置
```python
# config/network_config.json
{
  "fr3_right_ip": "192.168.58.2",
  "fr3_left_ip": "192.168.58.3", 
  "hermes_ip": "192.168.0.100",
  "gemini_ip": "192.168.0.101"
}
```

### 平台配置
系统自动检测操作系统并适配配置:
- Windows: Segoe UI字体, 1.25倍缩放
- macOS: SF Pro Display字体, 1.0倍缩放  
- Linux: Ubuntu字体, 1.0倍缩放

---

## 📊 性能优化

### 容量优化成果
- **项目大小**: 1.7GB → 662M (节省61%)
- **启动时间**: 优化依赖加载，提升30%
- **内存使用**: 分层依赖管理，减少40%

### 分层依赖管理
```bash
# 仅安装核心功能
pip install -r requirements.txt

# 按需安装可选功能
pip install -r requirements/dev.txt          # 开发工具
pip install -r requirements/monitoring.txt   # 监控图表  
pip install -r requirements/simulation_vtk.txt  # VTK 3D仿真
```

---

## 🛠️ 开发指南

### 开发环境搭建
```bash
# 1. 克隆项目
git clone <repository-url>
cd xc-robot

# 2. 创建开发环境
python -m venv venv
source venv/bin/activate

# 3. 安装开发依赖
pip install -r requirements/dev.txt

# 4. 运行测试
python -m pytest testing/
```

### 代码规范
- **语言**: Python 3.7+
- **GUI框架**: PyQt5
- **代码风格**: PEP 8
- **文档**: 中文注释 + 英文API

### 提交规范
```bash
# 功能开发
git checkout -b feature/new-feature
git commit -m "feat: 添加新功能描述"

# 问题修复  
git checkout -b fix/bug-description
git commit -m "fix: 修复问题描述"
```

---

## 📖 文档资源

### 📚 用户文档
- **[快速开始指南](docs/QUICKSTART.md)** - 5分钟上手指南
- **[硬件配置手册](docs/hardware/README.md)** - FR3、Hermes、Gemini配置
- **[界面操作手册](docs/interfaces/README.md)** - GUI和Web界面使用

### 🔧 开发文档  
- **[API参考文档](docs/api/README.md)** - RESTful API完整文档
- **[SDK开发指南](docs/development/README.md)** - 二次开发指南
- **[测试指南](testing/README.md)** - 测试框架和用例

### 🏗️ 架构文档
- **[项目架构分析](PROJECT_STRUCTURE_ANALYSIS.md)** - 完整架构文档
- **[跨平台部署](CROSS_PLATFORM_SETUP.md)** - 多平台部署指南

---

## 🤝 贡献指南

### 参与贡献
1. Fork项目到个人仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 问题报告
- **Bug报告**: [Issues](../../issues) - 详细描述复现步骤
- **功能请求**: [Issues](../../issues) - 说明使用场景和需求
- **技术支持**: [Discussions](../../discussions) - 使用问题和技术讨论

---

## 📞 技术支持

### 🔍 故障排除

```bash
# 环境诊断
python tools/quick_test.py

# 硬件连接测试
python testing/scripts/fr3_diagnostic.py

# 平台配置检查
python core/platform/config.py
```

### 📝 日志分析
- **应用日志**: `logs/xc-robot.log`
- **错误日志**: `logs/error.log`  
- **硬件日志**: `logs/hardware/`

### 🆘 常见问题
1. **环境配置问题** → 查看 [CROSS_PLATFORM_SETUP.md](./CROSS_PLATFORM_SETUP.md)
2. **硬件连接问题** → 查看 [docs/hardware/troubleshooting/](./docs/hardware/troubleshooting/)
3. **性能优化问题** → 查看 [docs/development/optimization/](./docs/development/optimization/)

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

感谢以下开源项目和技术社区:
- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/)** - GUI框架
- **[OpenCV](https://opencv.org/)** - 计算机视觉库
- **[NumPy](https://numpy.org/)** - 数值计算库
- **[FastAPI](https://fastapi.tiangolo.com/)** - Web API框架

---

**📝 项目信息**  
**开发团队**: XC-ROBOT开发团队  
**项目版本**: v3.1  
**最后更新**: 2025-07-25  
**项目状态**: 生产就绪 🚀

> 💡 **开始使用**: 建议从 [CROSS_PLATFORM_SETUP.md](./CROSS_PLATFORM_SETUP.md) 开始，选择适合你的平台进行部署。