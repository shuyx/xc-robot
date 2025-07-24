# 智能机器人界面 - 设计规格

## 整体布局（基于smart_interface_chat.html）
- **总体结构**: 侧边栏 + 主内容区域
- **侧边栏宽度**: 64px (w-16)  
- **主内容区**: 自适应宽度，左边距64px (ml-16)
- **最小高度**: 100vh (min-h-screen)
- **整体背景**: gray-100 (#f3f4f6)

## 侧边栏设计 (Sidebar)
### 尺寸与布局
- 宽度: 64px (w-16)
- 位置: 固定定位 (fixed left-0 top-0 bottom-0)
- 背景: 白色 (#ffffff)
- 右边框: gray-200 (#e5e7eb)
- 内边距: 垂直16px (py-4)

### 导航图标
- 机器人LOGO: 40px圆形 (w-10 h-10)，primary-600背景
- 导航按钮: 40px圆形，激活状态为primary-100背景 + primary-600边框
- 图标: FontAwesome 6.4.0
  - 首页: fa-house
  - 对话: fa-comments  
  - 位置: fa-map-location-dot
  - 设置: fa-gear
  - 帮助: fa-question

## 头部区域 (Header)
### 尺寸与布局
- 高度: 56px (h-14)
- 背景: 白色 (#ffffff)
- 下边框: gray-200 (#e5e7eb)
- 水平内边距: 24px (px-6)

### 头部内容
- 标题: text-lg font-semibold text-gray-800
- 状态标签: primary-100背景，primary-700文字，rounded-full
- 右侧: 通知图标 + 用户头像 (32px圆形)

## 主内容区域 (Main Content)
### 配置与连接区 (Top Panel)
- 背景: 白色，圆角 (rounded-lg)，阴影 (shadow-sm)
- 内边距: 20px (p-5)，底部间距: 24px (mb-6)
- 网格布局: 响应式 (grid-cols-1 lg:grid-cols-2)

#### 移动端接入卡片
- 边框: gray-200，圆角 (rounded-lg)
- 内边距: 16px (p-4)
- 输入框: gray-50背景，只读状态
- 按钮: primary-50背景，primary-700文字

#### 系统状态卡片  
- 状态指示器: 
  - 活跃状态: green-50背景，green-700文字，绿色脉动点
  - 状态点颜色: gray-300(监听), blue-300(解析), yellow-300(等待), green-500(执行)

### 主面板区域 (Main Panel)
- 网格布局: md:grid-cols-2 (响应式两列)
- 固定高度: 500px (h-[500px])
- 列间距: 24px (gap-6)

#### 实时对话记录 (Left Side)
- 背景: 白色，圆角，阴影
- 头部: 边框分割，内边距 (px-4 py-3)
- 开关控件: primary-500背景的自定义toggle
- 聊天区域: gray-50背景，可滚动 (overflow-y-auto)
- 消息气泡: 
  - 用户消息: 白色背景，max-width 85%
  - 机器人消息: primary-50背景，带品牌色头像

#### 解析任务详情 (Right Side)  
- 任务卡片: primary-100背景的圆形图标
- 状态徽章: green-100背景，green-800文字，脉动动画
- 信息网格: 2列布局 (grid-cols-2)
- 任务详情: gray-50背景，4个信息项，带图标
- 进度条: primary-500背景，45%宽度
- 终止按钮: red-50背景，red-700文字，red-200边框

## 颜色方案映射指南

⚠️ **重要**: 严格使用HTML设计中的具体颜色值，但需要映射到项目现有配色系统

### Element Plus主题变量
```scss
// 基于项目现有配色系统的Element Plus主题定制
$--color-primary: #409EFF;           // Element Plus蓝色主题
$--color-success: #67C23A;           // 成功色（绿色）
$--color-warning: #E6A23C;           // 警告色（橙色）
$--color-danger: #F56C6C;            // 危险色（红色）
$--color-info: #909399;              // 信息色（灰色）

// 项目特定配色
$--color-brand-primary: #2c3e50;     // 深蓝灰（项目主色）
$--color-brand-accent: #00A870;      // 绿色（项目强调色）
```

### CSS变量定义
```css
:root {
  /* 映射HTML设计配色到项目配色系统 */
  --xc-bg-primary: #f8f8f8;         /* 主背景 */
  --xc-bg-secondary: #ffffff;       /* 次背景 */
  --xc-bg-tertiary: #f2f2f2;       /* 第三背景 */
  
  --xc-text-primary: #2c3e50;       /* 主文字色 */
  --xc-text-secondary: rgba(60,60,60,0.66); /* 次文字色 */
  
  --xc-border-light: #e5e7eb;       /* 浅边框 */
  --xc-border-medium: #d1d5db;      /* 中等边框 */
  
  --xc-primary: #409EFF;            /* Element Plus主色 */
  --xc-accent: #00A870;             /* 项目强调色 */
  --xc-brand: #2c3e50;              /* 品牌色 */
}
```

### 使用方式
```vue
<style scoped>
.custom-button {
  background-color: var(--xc-primary);
  color: var(--xc-bg-secondary);
  border: 1px solid var(--xc-border-light);
}

.status-active {
  background-color: var(--xc-accent);
  color: white;
}
</style>
```

## 字体规格
- 字体家族: Inter sans-serif
- 主标题: text-2xl
- 次标题: text-xl
- 正文: text-sm
- 小文字: text-xs

## 间距标准
- 组件间距: space-y-6 (24px)
- 内容间距: space-y-4 (16px)
- 小间距: space-y-2 (8px)
- 卡片内边距: p-6 (24px)

## 交互效果
- 按钮悬停: transition-colors
- 状态变化: 平滑过渡
- 滚动条: 隐藏样式 (::-webkit-scrollbar { display: none; })

## Vue 3 + Element Plus实现要点

### 技术栈映射
1. **布局系统**: Element Plus Layout组件 (el-container, el-aside, el-main)
2. **样式实现**: TailwindCSS工具类 + Element Plus组件样式
3. **状态管理**: Pinia Store管理应用状态
4. **路由导航**: Vue Router实现页面导航
5. **API通信**: Axios HTTP客户端 + WebSocket实时通信

### 核心组件实现
```vue
<!-- 示例：侧边栏导航组件 -->
<template>
  <el-aside width="64px" class="sidebar-container">
    <div class="nav-items">
      <el-avatar :size="40" class="logo" :src="robotLogo" />
      <nav-item 
        v-for="item in navItems" 
        :key="item.id"
        :icon="item.icon"
        :active="activeRoute === item.route"
        @click="navigateTo(item.route)"
      />
    </div>
  </el-aside>
</template>
```

### 响应式设计
- **断点系统**: Element Plus响应式工具 (xs, sm, md, lg, xl)
- **网格布局**: el-row + el-col响应式网格
- **移动端适配**: 侧边栏折叠、触摸优化交互

### 实时数据更新
- **WebSocket连接**: Socket.io客户端实现实时通信
- **状态同步**: Pinia响应式状态管理
- **组件通信**: Event Bus + Props/Emit模式