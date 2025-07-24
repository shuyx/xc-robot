<template>
  <div class="sidebar-container">
    <!-- 展开状态的侧边栏 -->
    <div v-if="!collapsed" class="sidebar-expanded">
      <!-- 系统Logo区域 -->
      <div class="logo-area">
        <div class="logo-content" @click="goToDashboard">
          <el-icon class="logo-icon">
            <Avatar />
          </el-icon>
          <span class="logo-text">机器人系统</span>
        </div>
        <button class="collapse-button" @click="toggleCollapse">
          <el-icon>
            <ArrowLeft />
          </el-icon>
        </button>
      </div>
      
      
      <!-- 菜单组区域 -->
      <div class="menu-groups">
        <div 
          v-for="(menu, index) in menuConfig" 
          :key="menu.id" 
          class="menu-group"
          :data-menu-id="menu.id"
        >
          <!-- 菜单组标题 -->
          <div 
            class="menu-group-header"
            :class="{ 'active': activeGroupId === menu.id }"
            @click="toggleMenuGroup(menu.id)"
          >
            <div class="group-title">
              <el-icon :color="getMenuColor(menu.id)">
                <component :is="menu.icon" />
              </el-icon>
              <span>{{ menu.title }}</span>
            </div>
            <div class="group-toggle">
              <el-icon>
                <ArrowUp v-if="expandedGroups.includes(menu.id)" />
                <ArrowDown v-else />
              </el-icon>
            </div>
          </div>
          
          <!-- 菜单项列表 -->
          <div 
            v-if="expandedGroups.includes(menu.id)" 
            class="menu-items"
          >
            <div 
              v-for="child in menu.children" 
              :key="child.id"
              class="menu-item"
              :class="{ 'active': activeMenuId === child.id }"
              @click="handleMenuItemClick(child)"
            >
              <el-icon class="item-icon">
                <component :is="child.icon" />
              </el-icon>
              <span class="item-title">{{ child.title }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 系统状态区域 -->
      <div class="system-status">
        <div class="status-item">
          <el-icon class="status-online">
            <Connection />
          </el-icon>
          <span class="status-text">系统状态: 正常</span>
        </div>
        <div class="status-item">
          <el-icon class="status-signal">
            <Promotion />
          </el-icon>
          <span class="status-text">连接设备: 3台</span>
        </div>
      </div>
    </div>
    
    <!-- 折叠状态的侧边栏 -->
    <div v-else class="sidebar-collapsed">
      <!-- 系统Logo图标 -->
      <div class="collapsed-logo" @click="goToDashboard">
        <el-icon class="logo-icon">
          <Avatar />
        </el-icon>
      </div>
      
      <!-- 折叠状态菜单图标 -->
      <div class="collapsed-menu-icons">
        <div 
          v-for="(menu, index) in menuConfig" 
          :key="menu.id"
          class="collapsed-menu-item"
          :class="{ 'active': activeGroupId === menu.id }"
          :title="menu.title"
          @click="handleCollapsedMenuClick(menu, index)"
        >
          <el-icon :color="getMenuColor(menu.id)">
            <component :is="menu.icon" />
          </el-icon>
        </div>
      </div>
      
      <!-- 折叠状态系统状态图标 -->
      <div class="collapsed-status">
        <div class="collapsed-status-item" title="系统状态: 正常">
          <el-icon class="status-online">
            <Connection />
          </el-icon>
        </div>
        <div class="collapsed-status-item" title="连接设备: 3台">
          <el-icon class="status-signal">
            <Promotion />
          </el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { menuConfig, menuIconColors, type MenuItem } from '@/config/menu'
import { 
  Avatar, 
  ArrowLeft, 
  ArrowUp, 
  ArrowDown, 
  Connection,
  Promotion,
  SetUp,
  Tools,
  Lightning,
  House,
  Star,
  Clock,
  Link,
  Operation,
  Aim,
  Refresh,
  ChatDotRound,
  User,
  ChatRound,
  OfficeBuilding,
  View,
  Coordinate,
  VideoPlay,
  Map,
  Document,
  TrendCharts,
  PieChart,
  LineChart,
  Setting,
  Cloudy,
  Picture,
  Camera
} from '@element-plus/icons-vue'

// Props
interface Props {
  collapsed: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'toggle-collapse': []
  'menu-click': [menuItem: MenuItem]
}>()

// Router
const router = useRouter()
const route = useRoute()

// 响应式数据
const expandedGroups = ref([]) // 默认所有菜单组都折叠
const activeGroupId = ref('') // 当前激活的菜单组，初始化时为空，由路由决定
const activeMenuId = ref('') // 当前激活的菜单项，初始化时为空，由路由决定


// 获取菜单图标颜色
const getMenuColor = (menuId: string): string => {
  const colorClass = menuIconColors[menuId]
  const colorMap: Record<string, string> = {
    'text-yellow-400': '#FBBF24',
    'text-green-400': '#34D399', 
    'text-primary': '#409EFF',
    'text-blue-400': '#60A5FA',
    'text-purple-400': '#A78BFA',
    'text-red-400': '#F87171',
    'text-teal-400': '#2DD4BF',
    'text-indigo-400': '#818CF8',
    'text-gray-400': '#9CA3AF'
  }
  return colorMap[colorClass] || '#9CA3AF'
}

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  emit('toggle-collapse')
}

// 跳转到Dashboard
const goToDashboard = () => {
  router.push('/dashboard')
}

// 切换菜单组展开/折叠
const toggleMenuGroup = (groupId: string) => {
  const index = expandedGroups.value.indexOf(groupId)
  if (index > -1) {
    expandedGroups.value.splice(index, 1)
  } else {
    expandedGroups.value.push(groupId)
  }
  // 只有当点击的菜单组包含当前活跃菜单项时，才更新activeGroupId
  // 否则保持当前的高亮状态
  const currentMenuParentGroup = findParentGroupId(activeMenuId.value)
  if (currentMenuParentGroup !== groupId) {
    // 如果点击的不是当前活跃菜单项的父组，不改变活跃组
    // 这样可以避免点击其他菜单组时高亮状态的意外改变
  }
}

// 处理菜单项点击
const handleMenuItemClick = (menuItem: MenuItem) => {
  activeMenuId.value = menuItem.id
  activeGroupId.value = findParentGroupId(menuItem.id) || ''
  
  // 导航到路由
  if (menuItem.path) {
    router.push(menuItem.path)
  }
  
  // 触发事件
  emit('menu-click', menuItem)
}

// 处理折叠状态菜单点击
const handleCollapsedMenuClick = (menu: MenuItem, index: number) => {
  // 在折叠状态下点击菜单组，展开侧边栏并展开该菜单组
  emit('toggle-collapse')
  
  setTimeout(() => {
    if (!expandedGroups.value.includes(menu.id)) {
      expandedGroups.value.push(menu.id)
    }
    // 只有当该菜单组包含子菜单项且有默认选择时，才设置为活跃组
    if (menu.children && menu.children.length > 0) {
      // 检查该组是否包含当前活跃的菜单项
      const hasActiveChild = menu.children.some(child => child.id === activeMenuId.value)
      if (!hasActiveChild) {
        // 如果当前活跃菜单项不在这个组中，可以选择第一个子菜单作为活跃项
        // 但为了避免意外跳转，这里只展开菜单组而不设置活跃状态
      }
    }
  }, 300) // 等待侧边栏展开动画完成
}

// 获取搜索关键词
const getSearchKeywords = (menuItem: MenuItem): string[] => {
  const keywords: string[] = []
  
  // 根据菜单ID添加相关关键词
  const keywordMap: Record<string, string[]> = {
    // 快速启动
    'main-dashboard': ['仪表板', '主页', '首页', 'dashboard', 'home'],
    'favorites': ['收藏', '书签', '常用', 'favorite', 'bookmark'],
    'recent': ['最近', '历史', '记录', 'recent', 'history'],
    
    // 设备连接
    'device-connect': ['连接', '设备', '网络', 'connect', 'device', 'network'],
    'network-config': ['网络', '配置', '设置', 'network', 'config', 'setting'],
    'device-test': ['测试', '检测', '诊断', 'test', 'check', 'diagnosis'],
    
    // 机器人控制
    'arm-control': ['机械臂', '机器手', '臂', 'arm', 'robot', 'manipulator'],
    'chassis-control': ['底盘', '移动', '导航', 'chassis', 'mobile', 'navigation'],
    'joint-control': ['联动', '协调', '同步', 'joint', 'coordinate', 'sync'],
    
    // 智能交互
    'face-recognition': ['人脸', '识别', '视觉', 'face', 'recognition', 'vision'],
    'smart-chat': ['对话', '聊天', '交流', 'chat', 'talk', 'conversation'],
    'elevator-control': ['电梯', '梯控', '楼层', 'elevator', 'floor', 'lift'],
    
    // 场景测试
    'component-test': ['组件', '模块', '单元', 'component', 'module', 'unit'],
    'integration-test': ['集成', '整合', '联调', 'integration', 'combine'],
    'vision-guided-test': ['视觉', '引导', '导航', 'vision', 'guided', 'visual'],
    'end-to-end-test': ['端到端', '全流程', '完整', 'e2e', 'end-to-end', 'complete'],
    
    // 仿真规划
    'robot-simulation': ['仿真', '模拟', '虚拟', 'simulation', 'simulate', 'virtual'],
    'path-planning': ['路径', '规划', '导航', 'path', 'planning', 'route'],
    'task-orchestration': ['任务', '编排', '调度', 'task', 'orchestration', 'schedule'],
    
    // 视觉感知
    'vision-system': ['视觉', '相机', '摄像', 'vision', 'camera', 'visual'],
    'camera-calibration': ['标定', '校准', '调试', 'calibration', 'calibrate'],
    'point-cloud': ['点云', '深度', '3D', 'pointcloud', 'depth', '3d'],
    'image-processing': ['图像', '处理', '分析', 'image', 'processing', 'analysis'],
    
    // 数据监控
    'system-monitor': ['监控', '监视', '状态', 'monitor', 'watch', 'status'],
    'data-analysis': ['数据', '分析', '统计', 'data', 'analysis', 'statistics'],
    'performance-stats': ['性能', '统计', '指标', 'performance', 'stats', 'metrics'],
    
    // 系统管理
    'system-settings': ['设置', '配置', '参数', 'settings', 'config', 'parameters'],
    'parameter-config': ['参数', '配置', '设定', 'parameter', 'config', 'setting'],
    'maintenance': ['维护', '保养', '管理', 'maintenance', 'manage', 'service']
  }
  
  keywords.push(...(keywordMap[menuItem.id] || []))
  return keywords.map(k => k.toLowerCase())
}


// 查找菜单项的父级菜单组ID
const findParentGroupId = (menuItemId: string): string | null => {
  for (const menu of menuConfig) {
    if (menu.children?.some(child => child.id === menuItemId)) {
      return menu.id
    }
  }
  return null
}

// 根据路径查找对应的菜单项ID
const findMenuItemByPath = (path: string): string | null => {
  for (const menu of menuConfig) {
    if (menu.children) {
      for (const child of menu.children) {
        if (child.path === path) {
          return child.id
        }
      }
    }
  }
  return null
}

// 更新当前路由对应的高亮状态
const updateActiveStateFromRoute = () => {
  const currentPath = route.path
  const menuItemId = findMenuItemByPath(currentPath)
  
  if (menuItemId) {
    activeMenuId.value = menuItemId
    const parentGroupId = findParentGroupId(menuItemId)
    if (parentGroupId) {
      activeGroupId.value = parentGroupId
      // 确保包含当前菜单项的菜单组是展开的
      if (!expandedGroups.value.includes(parentGroupId)) {
        expandedGroups.value.push(parentGroupId)
      }
    }
  } else {
    // 如果当前路径不在菜单配置中，清除高亮状态
    activeMenuId.value = ''
    activeGroupId.value = ''
  }
}

// 键盘快捷键处理
const handleKeyboardShortcut = (event: KeyboardEvent) => {
  // 数字键1-9快速跳转到对应菜单组
  if (event.key >= '1' && event.key <= '9') {
    const index = parseInt(event.key) - 1
    if (index < menuConfig.length) {
      const targetMenu = menuConfig[index]
      toggleMenuGroup(targetMenu.id)
      
      // 滚动到目标菜单组
      const element = document.querySelector(`[data-menu-id="${targetMenu.id}"]`)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }
}

// 监听路由变化，更新高亮状态
watch(() => route.path, () => {
  updateActiveStateFromRoute()
}, { immediate: true }) // 立即执行一次

// 组件挂载时设置键盘监听和初始化高亮状态
onMounted(() => {
  window.addEventListener('keydown', handleKeyboardShortcut)
  // 确保在组件挂载后和DOM更新后立即更新高亮状态
  nextTick(() => {
    updateActiveStateFromRoute()
  })
})

// 组件卸载时移除键盘监听
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboardShortcut)
})
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  font-family: 'Inter', sans-serif;
}

/* 展开状态的侧边栏样式 */
.sidebar-expanded {
  width: 240px;
  height: 100%;
  background: var(--secondary-color, #2c3e50);
  color: white;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease-in-out;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 48px; /* 给footer留出空间 */
}

/* 系统Logo区域 */
.logo-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-content {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.logo-content:hover {
  background: var(--hover-color, rgba(255, 255, 255, 0.1));
}

.logo-icon {
  color: var(--primary-color, #409EFF);
  font-size: 20px;
  width: 24px;
  height: 24px;
}

.logo-text {
  font-weight: bold;
  font-size: 18px;
}

.collapse-button {
  background: none;
  border: none;
  color: #9CA3AF;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.3s ease;
}

.collapse-button:hover {
  color: white;
}


/* 菜单组区域 */
.menu-groups {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

.menu-group {
  margin-bottom: 0;
}

/* 菜单组标题 */
.menu-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.menu-group-header:hover {
  background: var(--hover-color, rgba(255, 255, 255, 0.1));
}

/* 父级菜单高亮 - 较淡的背景 */
.menu-group-header.active {
  background: rgba(64, 158, 255, 0.15);
  border-left: 3px solid var(--primary-color, #409EFF);
}

/* 父级菜单高亮时的标题颜色 */
.menu-group-header.active .group-title span {
  color: var(--primary-color, #409EFF);
  font-weight: 600;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.group-title .el-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.group-toggle .el-icon {
  font-size: 12px;
  color: #9CA3AF;
  transition: transform 0.3s ease;
  width: 16px;
  height: 16px;
}

/* 菜单项列表 */
.menu-items {
  background: var(--group-bg-color, rgba(255, 255, 255, 0.05));
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  margin: 0;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-radius: 0;
}

.menu-item:hover {
  background: var(--hover-color, rgba(255, 255, 255, 0.1));
}

/* 当前页面菜单项高亮 - 强烈的背景和边框 */
.menu-item.active {
  background: rgba(64, 158, 255, 0.4);
  border-left: 4px solid var(--primary-color, #409EFF);
  margin-left: 12px;
  border-radius: 4px;
  font-weight: bold;
}

.item-icon {
  color: #9CA3AF;
  font-size: 14px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-item.active .item-icon {
  color: white;
  background: var(--primary-color, #409EFF);
  border-radius: 3px;
  padding: 2px;
}

.menu-item.active .item-title {
  color: white;
}

.item-title {
  font-size: 14px;
}

/* 系统状态区域 */
.system-status {
  margin-top: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 16px;
  flex-shrink: 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.status-item:last-child {
  margin-bottom: 0;
}

.status-text {
  font-size: 14px;
}

.status-online {
  color: var(--success-color, #00A870);
}

.status-signal {
  color: var(--primary-color, #409EFF);
}

/* 折叠状态的侧边栏样式 */
.sidebar-collapsed {
  width: 60px;
  height: 100%;
  background: var(--secondary-color, #2c3e50);
  color: white;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease-in-out;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 48px; /* 给footer留出空间 */
}

/* 折叠状态Logo */
.collapsed-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.collapsed-logo:hover {
  background: var(--hover-color, rgba(255, 255, 255, 0.1));
}

.collapsed-logo .logo-icon {
  color: var(--primary-color, #409EFF);
  font-size: 20px;
}

/* 折叠状态菜单图标 */
.collapsed-menu-icons {
  flex: 1;
  padding: 8px 0;
}

.collapsed-menu-item {
  display: flex;
  justify-content: center;
  padding: 12px 0;
  cursor: pointer;
  transition: background-color 0.3s ease;
  position: relative;
}

.collapsed-menu-item:hover {
  background: var(--hover-color, rgba(255, 255, 255, 0.1));
}

.collapsed-menu-item.active {
  background: rgba(64, 158, 255, 0.2);
}

.collapsed-menu-item i {
  font-size: 16px;
}

/* 折叠状态系统状态 */
.collapsed-status {
  margin-top: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px 0;
  flex-shrink: 0;
}

.collapsed-status-item {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar-expanded {
    width: 240px;
    position: fixed;
    top: 64px;
    left: 0;
    z-index: 999;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  }
  
  .sidebar-collapsed {
    width: 60px;
    position: fixed;
    top: 64px;
    left: 0;
    z-index: 999;
  }
}

/* 滚动条样式 */
.sidebar-expanded::-webkit-scrollbar,
.sidebar-collapsed::-webkit-scrollbar,
.menu-groups::-webkit-scrollbar {
  display: none;
}

.sidebar-expanded,
.sidebar-collapsed,
.menu-groups {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>