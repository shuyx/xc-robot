# 机器人用户识别界面 - 设计规格

## 整体布局
- **总尺寸**: 800px 高度，自适应宽度
- **布局方式**: 左右分栏设计（1:2比例）
- **背景色**: 白色 (#ffffff)

## 左侧面板 (1/3宽度)
### 尺寸与布局
- 宽度: 33.33% (w-1/3)
- 背景: neutral-50 (#f9fafb)
- 右边框: neutral-200 (#e5e7eb)
- 内边距: 24px (p-6)

### 相机区域
- 标题: "实时相机画面" (text-xl, text-neutral-900)
- 视频窗口: 
  - 背景: neutral-600 (#4b5563)
  - 高度: 256px (h-64)
  - 圆角: rounded-lg
  - 图标: fa-video (4xl大小)
  - 文字: "Gemini 335 RGB流"

### 控制按钮
- 背景: neutral-900 (#111827)
- 文字: 白色
- 内边距: py-3 px-4
- 圆角: rounded-lg
- 悬停效果: hover:bg-neutral-800
- 图标: fa-scan-face
- 文字: "扫描并识别用户"

### 状态指示器
- 标题: "系统状态" (text-sm, text-neutral-700)
- 状态点: 12px圆形，neutral-500背景
- 状态文字: "待命中" (text-sm, text-neutral-600)

## 右侧面板 (2/3宽度)
### 用户信息卡片
- 背景: 白色
- 边框: neutral-200 (#e5e7eb)
- 圆角: rounded-lg
- 内边距: 24px (p-6)

#### 用户头像区域
- 头像: 64px圆形 (w-16 h-16 rounded-full)
- 用户名: Kevin Yuan (text-xl, text-neutral-900)
- 状态: "识别成功" (text-sm, text-neutral-500)

#### 信息网格 (2列)
- 授权工位: A-12
- 最后记录位置: 实验室
- 调度权限: 管理员徽章 (neutral-100背景，rounded-full)

### 历史任务卡片
- 标题: "最近5次呼叫任务" (text-lg, text-neutral-900)
- 最大高度: 256px，可滚动 (max-h-64 overflow-y-auto)

#### 任务项样式
- 左边框: 4px宽，neutral-500色
- 左内边距: 16px (pl-4)
- 上下内边距: 8px (py-2)
- 时间戳: text-sm, text-neutral-600
- 状态徽章: 
  - 已完成: neutral-100背景
  - 已取消: neutral-100背景
  - 圆角: rounded-full
  - 字体: text-xs

## 颜色方案
⚠️ **注意**: 颜色方案需要使用项目现有配色，以下仅为HTML参考中的配色结构，实际开发时使用软件自身的配色系统。

```css
/* HTML参考配色结构 - 请映射到项目现有配色 */
--color-background-primary: /* 主背景色 - 对应neutral-50 */
--color-background-secondary: /* 次背景色 - 对应white */
--color-border-light: /* 浅边框 - 对应neutral-200 */
--color-text-primary: /* 主文字 - 对应neutral-900 */
--color-text-secondary: /* 次文字 - 对应neutral-600 */
--color-button-primary: /* 主按钮 - 对应neutral-900 */
--color-button-hover: /* 按钮悬停 - 对应neutral-800 */
--color-status-inactive: /* 状态指示 - 对应neutral-500 */
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

## PyQt5实现要点
1. 使用QWebEngineView加载HTML内容
2. 通过QWebChannel实现Python与JavaScript通信
3. 相机画面使用QLabel或集成opencv显示
4. 按钮点击通过JavaScript调用Python方法
5. 实时状态更新通过信号槽机制