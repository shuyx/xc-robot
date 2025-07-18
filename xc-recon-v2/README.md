# XC-RECON System v2.0

## 项目概述

XC-RECON System v2.0 是XC-ROBOT机器人控制系统的全新重构版本，采用现代化的微服务架构，支持跨平台部署、AI集成、3D可视化等高级功能。

## 技术架构

### 后端技术栈
- **框架**: FastAPI + Python 3.9+
- **数据库**: PostgreSQL + Redis
- **ORM**: SQLAlchemy + Alembic
- **认证**: JWT + OAuth2
- **容器化**: Docker + Docker Compose

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI组件**: Element Plus
- **3D渲染**: Three.js + VTK.js
- **状态管理**: Pinia
- **构建工具**: Vite

### 跨平台支持
- **Web应用**: 现代浏览器支持
- **桌面应用**: Electron
- **移动端**: 响应式Web应用

## 核心功能

### 设备控制
- FR3双机械臂控制
- Hermes移动底盘控制
- 多相机视觉系统
- 传感器数据采集

### 智能功能
- AI对话交互
- 自然语言任务规划
- 智能运动规划
- 自主导航

### 3D可视化
- STL/STP文件支持
- 实时3D仿真
- 点云数据显示
- 运动轨迹可视化

### 系统管理
- 用户权限管理
- 设备状态监控
- 任务调度管理
- 数据分析统计

## 项目结构

```
xc-recon-v2/
├── backend/           # 后端服务
│   ├── api/          # API接口
│   ├── services/     # 业务服务
│   ├── models/       # 数据模型
│   ├── core/         # 核心功能
│   ├── plugins/      # 插件系统
│   └── migrations/   # 数据库迁移
├── frontend/         # 前端应用
├── desktop/          # 桌面应用
├── config/           # 配置文件
├── tests/            # 测试用例
├── docs/             # 文档
└── scripts/          # 工具脚本
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 开发环境搭建

1. **克隆项目**
```bash
git clone <repository-url>
cd xc-recon-v2
```

2. **后端环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. **前端环境**
```bash
cd frontend
npm install
```

4. **数据库配置**
```bash
# 创建数据库
createdb xc_recon

# 运行迁移
cd backend
alembic upgrade head
```

5. **启动服务**
```bash
# 后端服务
cd backend
uvicorn main:app --reload

# 前端服务
cd frontend
npm run dev
```

## 部署指南

### Docker部署
```bash
docker-compose up -d
```

### 生产环境
详见 [部署文档](docs/deployment.md)

## 开发指南

- [API文档](docs/api.md)
- [前端开发指南](docs/frontend.md)
- [插件开发指南](docs/plugins.md)
- [数据库设计](docs/database.md)

## 许可证

Copyright © 2025 XC-ROBOT Team. All rights reserved.