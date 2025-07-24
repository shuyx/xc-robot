<template>
  <header class="header-container">
    <div class="header-content">
      <!-- Brand Logo Area -->
      <div class="brand-area">
        <div class="logo-icon">
          <img src="@/assets/xclogo.png" alt="XC Logo" class="logo-image" />
        </div>
        <span class="brand-text">
          XC-OS <span class="version-text">v3.0</span>
        </span>
      </div>

      <!-- Search Area -->
      <div class="search-area">
        <div class="search-input-wrapper">
          <input 
            v-model="searchQuery"
            type="text" 
            class="search-input" 
            placeholder="搜索功能模块..."
            @focus="showSearchSuggestions = true"
            @blur="handleSearchBlur"
          >
          <div class="search-icon">
            <el-icon>
              <Search />
            </el-icon>
          </div>
          <div class="search-shortcut">
            Ctrl+K
          </div>
        </div>
        
        <!-- Search Suggestions -->
        <div v-if="showSearchSuggestions" class="search-suggestions">
          <div class="suggestions-content">
            <div 
              v-for="suggestion in searchSuggestions" 
              :key="suggestion.id"
              class="suggestion-item"
              @click="handleSuggestionClick(suggestion)"
            >
              <i :class="suggestion.icon" class="suggestion-icon"></i>
              <span>{{ suggestion.title }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side Area -->
      <div class="right-area">
        <!-- Log Panel Toggle -->
        <div class="log-panel-toggle">
          <button class="log-panel-button" @click="handleLogPanelClick" title="切换日志面板">
            <el-icon>
              <Document />
            </el-icon>
            <span>日志</span>
          </button>
        </div>


        <!-- System Status Area -->
        <div class="status-area">
          <!-- Connection Status -->
          <div class="status-item">
            <button class="status-button">
              <el-icon class="status-normal">
                <Bell />
              </el-icon>
              <span>连接</span>
            </button>
            <div class="status-tooltip">
              <div class="tooltip-title">连接状态</div>
              <div class="tooltip-desc">所有设备连接正常</div>
              <div class="tooltip-details">
                <div class="detail-row">
                  <span>主服务器</span>
                  <span class="status-normal">已连接</span>
                </div>
                <div class="detail-row">
                  <span>备用服务器</span>
                  <span class="status-normal">已连接</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Running Status -->
          <div class="status-item">
            <button class="status-button">
              <el-icon class="status-info">
                <SwitchButton />
              </el-icon>
              <span>运行</span>
            </button>
            <div class="status-tooltip">
              <div class="tooltip-title">系统运行状态</div>
              <div class="tooltip-desc">系统正常运行中</div>
              <div class="tooltip-details">
                <div class="detail-row">
                  <span>CPU使用率</span>
                  <span>32%</span>
                </div>
                <div class="detail-row">
                  <span>内存使用率</span>
                  <span>45%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Notifications -->
          <div class="status-item">
            <button class="status-button notification-button">
              <el-icon>
                <Bell />
              </el-icon>
              <span>告警</span>
              <span class="notification-badge">3</span>
            </button>
            <div class="notification-tooltip">
              <div class="notification-header">
                <div class="notification-title">通知</div>
                <button class="mark-all-read">全部标为已读</button>
              </div>
              <div class="notification-list">
                <div class="notification-item">
                  <div class="notification-icon">
                    <el-icon class="text-warning"><Warning /></el-icon>
                  </div>
                  <div class="notification-content">
                    <div class="notification-text">温度告警</div>
                    <div class="notification-desc">设备A温度超过阈值</div>
                    <div class="notification-time">10分钟前</div>
                  </div>
                </div>
                <div class="notification-item">
                  <div class="notification-icon">
                    <el-icon class="text-danger"><Warning /></el-icon>
                  </div>
                  <div class="notification-content">
                    <div class="notification-text">存储空间不足</div>
                    <div class="notification-desc">存储空间低于10%</div>
                    <div class="notification-time">30分钟前</div>
                  </div>
                </div>
                <div class="notification-item">
                  <div class="notification-icon">
                    <el-icon class="text-primary"><CircleCheck /></el-icon>
                  </div>
                  <div class="notification-content">
                    <div class="notification-text">系统更新</div>
                    <div class="notification-desc">新版本V3.1可用</div>
                    <div class="notification-time">1小时前</div>
                  </div>
                </div>
              </div>
              <div class="notification-footer">
                <button class="view-all-button">查看全部通知</button>
              </div>
            </div>
          </div>
        </div>

        <!-- User Area -->
        <div class="user-area">
          <button class="user-button">
            <div class="user-avatar">
              <span>K</span>
            </div>
            <span class="user-name">Kevin Yuan</span>
            <el-icon class="user-chevron">
              <ArrowDown />
            </el-icon>
          </button>
          <div class="user-menu">
            <div class="user-info">
              <div class="user-avatar">
                <span>K</span>
              </div>
              <div class="user-details">
                <div class="user-full-name">Kevin Yuan</div>
                <div class="user-role">管理员</div>
              </div>
            </div>
            <div class="menu-items">
              <span class="menu-item">
                <el-icon><User /></el-icon>个人设置
              </span>
              <span class="menu-item">
                <el-icon><Setting /></el-icon>系统设置
              </span>
              <span class="menu-item">
                <el-icon><QuestionFilled /></el-icon>帮助文档
              </span>
              <div class="menu-divider"></div>
              <span class="menu-item logout-item">
                <el-icon><SwitchButton /></el-icon>退出登录
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Search, 
  Bell, 
  User, 
  Setting, 
  QuestionFilled, 
  SwitchButton,
  Document,
  ArrowDown,
  Warning,
  CircleCheck
} from '@element-plus/icons-vue'

// Props & Emits
const emit = defineEmits<{
  'toggle-log-panel': []
}>()

const searchQuery = ref('')
const showSearchSuggestions = ref(false)

// 搜索建议数据
const searchSuggestions = ref([
  { id: 'smart-chat', icon: 'fa-solid fa-comments text-primary', title: '智能对话' },
  { id: 'face-recognition', icon: 'fa-solid fa-user-check text-primary', title: '人脸识别' },
  { id: 'arm-control', icon: 'fa-solid fa-robot text-primary', title: '机械臂控制' },
  { id: 'device-connection', icon: 'fa-solid fa-plug-circle-check text-primary', title: '设备连接' }
])

// 处理搜索失焦
const handleSearchBlur = () => {
  setTimeout(() => {
    showSearchSuggestions.value = false
  }, 200)
}

// 处理建议点击
const handleSuggestionClick = (suggestion: any) => {
  console.log('选择建议:', suggestion)
  showSearchSuggestions.value = false
}

// 处理日志面板按钮点击
const handleLogPanelClick = () => {
  console.log('Header: 日志按钮被点击')
  emit('toggle-log-panel')
}


// 监听Ctrl+K快捷键
onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault()
      const searchInput = document.querySelector('.search-input') as HTMLInputElement
      searchInput?.focus()
    }
  })
})
</script>

<style scoped>
.header-container {
  width: 100%;
  height: 64px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 16px;
}

/* Brand Area */
.brand-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand-text {
  font-weight: bold;
  color: var(--secondary-color, #2c3e50);
  font-size: 18px;
}

.version-text {
  font-size: 14px;
  font-weight: bold;
  color: var(--primary-color, #409EFF);
}

/* Search Area */
.search-area {
  flex: 1;
  max-width: 400px;
  margin: 0 32px;
  position: relative;
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 40px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: var(--primary-color, #409EFF);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #909399;
}

.search-shortcut {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #909399;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border: 1px solid #e4e7ed;
  z-index: 50;
}

.suggestions-content {
  padding: 8px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.suggestion-item:hover {
  background: #f5f7fa;
}

.suggestion-icon {
  color: var(--primary-color, #409EFF);
}

/* Right Area */
.right-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Log Panel Toggle */
.log-panel-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  color: #606266;
}

.log-panel-button:hover {
  border-color: var(--primary-color, #409EFF);
  background: #f0f8ff;
}

.log-panel-button .el-icon {
  color: var(--primary-color, #409EFF);
}


/* Status Area */
.status-area {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 16px;
  border-left: 1px solid #e4e7ed;
  border-right: 1px solid #e4e7ed;
}

.status-item {
  position: relative;
}

.status-button {
  display: flex;
  align-items: center;
  gap: 4px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.notification-button {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--danger-color, #F56C6C);
  color: white;
  font-size: 12px;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Status Colors */
.status-normal {
  color: var(--success-color, #00A870);
}

.status-info {
  color: var(--primary-color, #409EFF);
}

.text-warning {
  color: var(--warning-color, #E6A23C);
}

.text-danger {
  color: var(--danger-color, #F56C6C);
}

.text-primary {
  color: var(--primary-color, #409EFF);
}

/* Tooltips */
.status-tooltip,
.notification-tooltip {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border: 1px solid #e4e7ed;
  padding: 8px;
  width: 192px;
  z-index: 50;
  display: none;
}

.status-item:hover .status-tooltip,
.status-item:hover .notification-tooltip {
  display: block;
}

.tooltip-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.tooltip-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.tooltip-details {
  font-size: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin: 4px 0;
}

/* Notification Tooltip */
.notification-tooltip {
  width: 256px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notification-title {
  font-size: 14px;
  font-weight: 500;
}

.mark-all-read {
  font-size: 12px;
  color: var(--primary-color, #409EFF);
  border: none;
  background: none;
  cursor: pointer;
}

.notification-list {
  max-height: 192px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f7fa;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-content {
  flex: 1;
}

.notification-text {
  font-size: 12px;
  font-weight: 500;
}

.notification-desc {
  font-size: 12px;
  color: #909399;
}

.notification-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.notification-footer {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f5f7fa;
}

.view-all-button {
  width: 100%;
  text-align: center;
  font-size: 12px;
  color: var(--primary-color, #409EFF);
  border: none;
  background: none;
  cursor: pointer;
}

/* User Area */
.user-area {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  background: none;
  cursor: pointer;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-color, #409EFF);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--secondary-color, #2c3e50);
}

.user-chevron {
  font-size: 12px;
  color: #909399;
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border: 1px solid #e4e7ed;
  padding: 8px;
  width: 192px;
  z-index: 50;
  display: none;
}

.user-area:hover .user-menu {
  display: block;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid #f5f7fa;
  margin-bottom: 8px;
}

.user-details {
  flex: 1;
}

.user-full-name {
  font-size: 14px;
  font-weight: 500;
}

.user-role {
  font-size: 12px;
  color: #909399;
}

.menu-items {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  font-size: 14px;
  color: #606266;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.menu-item:hover {
  background: #f5f7fa;
}

.menu-item i {
  color: #909399;
  width: 16px;
}

.logout-item {
  color: var(--danger-color, #F56C6C);
}

.logout-item i {
  color: var(--danger-color, #F56C6C);
}

.menu-divider {
  height: 1px;
  background: #f5f7fa;
  margin: 4px 0;
}
</style>