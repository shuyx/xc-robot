# XC-ROBOT 依赖管理说明

## 📦 分层依赖结构

本项目采用分层依赖管理，将不同功能的依赖分离，便于按需安装和维护。

### 核心依赖

- **`base.txt`** - 运行XC-ROBOT基本功能的必需依赖
  ```bash
  pip install -r requirements/base.txt
  ```

### 可选依赖

- **`dev.txt`** - 开发工具（代码检查、测试框架等）
  ```bash
  pip install -r requirements/dev.txt
  ```

- **`monitoring.txt`** - 监控和图表功能
  ```bash
  pip install -r requirements/monitoring.txt
  ```

- **`simulation_vtk.txt`** - VTK 3D仿真（⚠️ 不推荐）
  ```bash
  pip install -r requirements/simulation_vtk.txt
  ```

## 🚀 快速安装

### 最小安装（推荐）
```bash
pip install -r requirements.txt
```

### 完整开发环境
```bash
pip install -r requirements.txt
pip install -r requirements/dev.txt
pip install -r requirements/monitoring.txt
```

## ⚠️ 重要说明

### VTK仿真模块
- **包大小**: 约380M
- **状态**: 已移至可选依赖
- **推荐**: 使用Web端Three.js方案替代
- **仅在以下情况安装VTK**:
  - 需要使用旧版桌面端仿真功能
  - 确实需要VTK的高级科学计算功能

### 空间优化效果
- **移除VTK前**: venv ~864M
- **移除VTK后**: venv ~489M
- **节省空间**: 375M (43%)

## 📝 版本历史

- **v1.0** (2025-07-25): 建立分层依赖结构，VTK移至可选依赖