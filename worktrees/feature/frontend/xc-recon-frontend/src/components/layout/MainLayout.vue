<template>
  <el-container class="layout-container">
    <!-- Header Component -->
    <el-header class="layout-header" height="64px">
      <HeaderComponent @toggle-log-panel="handleLogPanelToggle" />
    </el-header>
    
    <!-- Body Container -->
    <el-container class="layout-body">
      <!-- Sidebar Component -->
      <el-aside 
        class="layout-sidebar" 
        :width="sidebarCollapsed ? '60px' : '240px'"
      >
        <SidebarComponent 
          :collapsed="sidebarCollapsed"
          @toggle-collapse="handleSidebarToggle"
          @menu-click="handleMenuClick"
        />
      </el-aside>
      
      <!-- Main Content Area -->
      <el-main class="layout-main">
        <router-view />
      </el-main>
      
      <!-- Log Panel Component -->
      <LogPanelComponent 
        :is-open="logPanelOpen"
        @update:isOpen="handleLogPanelToggle"
        @toggle="handleLogPanelToggle"
      />
    </el-container>
    
    <!-- Footer Component -->
    <FooterComponent />
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import HeaderComponent from './Header.vue'
import SidebarComponent from './Sidebar.vue'
import FooterComponent from './Footer.vue'
import LogPanelComponent from './LogPanel.vue'
import type { MenuItem } from '@/config/menu'

const router = useRouter()

// 侧边栏折叠状态
const sidebarCollapsed = ref(false)
// 日志面板开关状态
const logPanelOpen = ref(false)

// 处理侧边栏折叠切换
const handleSidebarToggle = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 处理日志面板切换
const handleLogPanelToggle = () => {
  console.log('LogPanel切换前:', logPanelOpen.value)
  logPanelOpen.value = !logPanelOpen.value
  console.log('LogPanel切换后:', logPanelOpen.value)
}

// 处理菜单点击
const handleMenuClick = (menuItem: MenuItem) => {
  console.log('菜单点击:', menuItem)
  
  // 如果菜单项有路径，进行路由跳转
  if (menuItem.path) {
    router.push(menuItem.path)
  }
  
  // 在移动端点击菜单项后自动折叠侧边栏
  if (window.innerWidth <= 768) {
    sidebarCollapsed.value = true
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  font-family: 'Inter', sans-serif;
}

.layout-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.layout-body {
  padding-top: 64px;
  height: calc(100vh - 64px - 48px);
  position: relative;
}

.layout-sidebar {
  background: var(--el-color-primary-dark-2, #2c3e50);
  transition: width 0.3s ease;
  border-right: 1px solid #e4e7ed;
  overflow: hidden;
  height: 100%;
}

.layout-main {
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 68px; /* 给footer留出空间 */
  overflow-y: auto;
  height: 100%;
  position: relative;
}

/* CSS变量定义 - 匹配sidebar_nav.html的配色 */
:root {
  --primary-color: #409EFF;
  --secondary-color: #2c3e50;
  --success-color: #00A870;
  --warning-color: #E6A23C;
  --danger-color: #F56C6C;
  --info-color: #909399;
  --hover-color: rgba(255,255,255,0.1);
  --group-bg-color: rgba(255,255,255,0.05);
}
</style>