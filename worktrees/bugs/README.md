# XC-RECON System v2.0

## 项目概述

XC-RECON System v2.0 是XC-ROBOT轮式双臂类人形机器人控制系统的全新重构版本。原项目采用Python + PyQt5技术栈，现重构为现代化的企业级Web应用，支持跨平台部署、AI集成、3D可视化等高级功能。

### 硬件平台
- **FR3双机械臂**: 高精度协作机械臂，IP配置192.168.58.2(右臂)/192.168.58.3(左臂)
- **Hermes移动底盘**: 全向移动平台，支持自主导航
- **Gemini 335视觉系统**: 深度相机和视觉处理模块

## 技术架构

### 后端技术栈
- **框架**: FastAPI + Python 3.11.10 (前后端分离架构)
- **数据库**: SQLite(开发) / PostgreSQL(生产) + Redis
- **ORM**: SQLAlchemy + Alembic (数据库迁移)
- **认证**: JWT令牌认证 + 基于角色的访问控制
- **数据验证**: Pydantic严格验证所有API输入
- **容器化**: Docker + Docker Compose

### 前端技术栈
- **框架**: Vue 3 + TypeScript + Composition API
- **UI组件**: Element Plus (企业级组件库)
- **响应式工具**: VueUse (现代化组合式函数)
- **3D渲染**: Three.js + VTK.js (3D可视化和仿真)
- **状态管理**: Pinia (Vue 3官方状态管理)
- **构建工具**: Vite (快速开发和构建)

### 跨平台支持
- **Web应用**: 现代浏览器支持，响应式设计优先
- **开发环境**: Mac/Windows协作开发解决方案
- **部署环境**: 支持容器化部署和传统部署

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
├── backend/           # FastAPI后端服务
│   ├── api/v1/endpoints/  # API端点实现
│   ├── services/      # 业务服务层 (设备管理、FR3控制、Hermes控制)
│   ├── models/        # SQLAlchemy数据模型
│   ├── core/          # 核心功能 (配置、认证、数据库)
│   ├── plugins/       # 插件系统
│   └── migrations/    # Alembic数据库迁移
├── frontend/xc-recon-frontend/  # Vue 3前端应用
│   ├── src/components/layout/   # 布局组件 (MainLayout.vue)
│   ├── src/views/     # 页面组件 (Dashboard.vue等)
│   ├── src/stores/    # Pinia状态管理 (user.ts)
│   └── src/services/  # API服务层
├── config/            # 应用配置文件 (app.yml)
├── docs/              # 技术文档知识库
│   ├── technical/     # 技术文档 (项目背景、系统架构)
│   ├── hardware/      # 硬件文档 (FR3分析、配置参考)
│   ├── design/        # 设计文档 (UI/UX规范)
│   ├── testing/       # 测试文档 (测试计划、安全规范)
│   └── development/   # 开发文档 (部署指南、集成指南)
├── tests/             # 测试用例
└── scripts/           # 工具脚本
```

## 快速开始

### 环境要求
- **Python**: 3.11.10 (已统一版本)
- **Node.js**: 18+ (推荐使用LTS版本)
- **数据库**: SQLite(开发) / PostgreSQL 12+(生产)
- **其他**: Redis 6+ (可选，用于缓存)

### 当前开发状态
- **Phase 3**: 前端开发90%完成 ✅
- **进度**: API集成对接中，WebSocket实时通信和3D可视化组件待开发
- **访问地址**: http://localhost:5173/ (自动模拟登录)

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
cd frontend/xc-recon-frontend
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
# 后端服务 (FastAPI)
cd backend
python -m uvicorn main:app --reload    # http://localhost:8000

# 前端服务 (Vue 3 + Vite)
cd frontend/xc-recon-frontend
npm run dev                           # http://localhost:5173
```

## 部署指南

### Docker部署
```bash
docker-compose up -d
```

### 生产环境
详见 [部署文档](docs/deployment.md)

## 分支策略

### 分支说明
- **main**: 主分支，稳定版本
- **develop**: 开发分支，功能集成
- **feature/***: 功能分支，新功能开发
- **release/***: 发布分支，版本发布
- **hotfix/***: 热修复分支，紧急修复

### 开发流程
1. 从 `develop` 分支创建 `feature/功能名` 分支
2. 在功能分支完成开发和测试
3. 提交 Pull Request 合并到 `develop`
4. 测试通过后，从 `develop` 创建 `release/版本号` 分支
5. 发布测试通过后，合并到 `main` 并打标签

### 重构文档
- [重构系统设计](xc_recon_system.md)
- [重构实施记录 Phase 1-8](xc_recon_1.md) - [最新状态](xc_recon_8.md)

## 开发指南与文档

### 📚 技术文档知识库
- **[docs/README.md](docs/README.md)** - 完整文档导航和索引
- **[docs/technical/](docs/technical/)** - 技术架构和系统设计
- **[docs/hardware/](docs/hardware/)** - 硬件规格和配置文档
- **[docs/design/](docs/design/)** - UI/UX设计规范和组件规格
- **[docs/testing/](docs/testing/)** - 测试计划和质量保证规范
- **[docs/development/](docs/development/)** - 开发指南和部署文档

### 🤖 AI协作指南
- **[CLAUDE.md](CLAUDE.md)** - Claude AI工作指南和快速参考
- **核心约束**: 开发环境仿真模式，遵循现有代码风格
- **参考优先级**: 项目背景 → 最新状态 → 技术架构 → 详细文档

### 💻 开发规范
#### TypeScript/Vue 3 前端
- 严格类型定义，使用联合类型和接口
- VueUse现代化组合式函数，避免手写响应式逻辑
- 环境隔离：`import.meta.env.DEV` 开发环境检查

#### Python/FastAPI 后端  
- Pydantic数据模型，严格类型注解
- 标准API结构，完整错误处理
- snake_case命名约定，完整文档字符串

### 📈 当前技术亮点
- **前端**: Vue 3 + VueUse现代化实践，100%类型安全保障
- **后端**: FastAPI完整数据库驱动，生产级JWT认证
- **质量**: 企业级代码标准，完整测试和验证体系

## 许可证

Copyright © 2025 XC-ROBOT Team. All rights reserved.