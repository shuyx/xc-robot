<template>
  <div id="settings-page" class="w-full h-[calc(100vh-100px)] bg-light-bg">
    <div class="p-6">
      <!-- Page Header -->
      <div id="settings-header" class="mb-6">
        <h1 class="text-2xl font-bold text-secondary">系统配置管理</h1>
        <p class="text-sm text-gray-500">机器人系统参数配置与管理</p>
      </div>
      
      <!-- Settings Container -->
      <div id="settings-container" class="flex gap-6 h-[calc(100vh-220px)]">
        <!-- Settings Categories -->
        <div id="settings-categories" class="w-64 bg-white rounded-lg shadow-sm overflow-hidden">
          <div class="p-3 bg-info text-white font-medium">
            <div class="flex items-center gap-2">
              <i class="fa-solid fa-list-check"></i>
              <span>设置分类</span>
            </div>
          </div>
          <div class="p-2">
            <div 
              id="category-basic" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer mb-1',
                activeCategory === 'basic' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('basic')"
            >
              <i class="fa-solid fa-globe"></i>
              <span>基础设置</span>
            </div>
            <div 
              id="category-device" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer mb-1',
                activeCategory === 'device' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('device')"
            >
              <i class="fa-solid fa-robot"></i>
              <span>设备配置</span>
            </div>
            <div 
              id="category-security" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer mb-1',
                activeCategory === 'security' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('security')"
            >
              <i class="fa-solid fa-lock"></i>
              <span>安全设置</span>
            </div>
            <div 
              id="category-maintenance" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer mb-1',
                activeCategory === 'maintenance' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('maintenance')"
            >
              <i class="fa-solid fa-wrench"></i>
              <span>系统维护</span>
            </div>
            <div 
              id="category-performance" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer mb-1',
                activeCategory === 'performance' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('performance')"
            >
              <i class="fa-solid fa-chart-line"></i>
              <span>性能调优</span>
            </div>
            <div 
              id="category-theme" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer mb-1',
                activeCategory === 'theme' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('theme')"
            >
              <i class="fa-solid fa-palette"></i>
              <span>界面主题</span>
            </div>
            <div 
              id="category-network" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer mb-1',
                activeCategory === 'network' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('network')"
            >
              <i class="fa-solid fa-wifi"></i>
              <span>网络设置</span>
            </div>
            <div 
              id="category-notification" 
              :class="[
                'flex items-center gap-2 p-3 rounded-md cursor-pointer',
                activeCategory === 'notification' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
              ]"
              @click="setActiveCategory('notification')"
            >
              <i class="fa-solid fa-bell"></i>
              <span>通知设置</span>
            </div>
          </div>
        </div>
        
        <!-- Settings Content -->
        <div id="settings-content" class="flex-1">
          <!-- Basic Settings Panel -->
          <div 
            id="basic-settings-panel" 
            v-show="activeCategory === 'basic'"
            class="bg-white rounded-lg shadow-sm p-6"
          >
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center gap-2">
                <i class="fa-solid fa-globe text-primary text-xl"></i>
                <h2 class="text-xl font-bold">基础设置</h2>
              </div>
              <button 
                class="text-primary hover:text-blue-600"
                @click="resetBasicSettings"
              >
                <i class="fa-solid fa-rotate-right"></i> 重置
              </button>
            </div>
            
            <div class="space-y-6">
              <!-- Language Setting -->
              <div id="language-setting" class="flex flex-col">
                <label class="text-sm font-medium mb-2">语言设置:</label>
                <div class="relative w-64">
                  <select 
                    v-model="basicSettings.language"
                    class="w-full p-2 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="zh-CN">中文(简体)</option>
                    <option value="en-US">English</option>
                    <option value="ja-JP">日本語</option>
                    <option value="ko-KR">한국어</option>
                  </select>
                  <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <i class="fa-solid fa-chevron-down text-gray-400"></i>
                  </div>
                </div>
              </div>
              
              <!-- Timezone Setting -->
              <div id="timezone-setting" class="flex flex-col">
                <label class="text-sm font-medium mb-2">时区设置:</label>
                <div class="relative w-64">
                  <select 
                    v-model="basicSettings.timezone"
                    class="w-full p-2 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="GMT+8">GMT+8:00 北京时间</option>
                    <option value="GMT+0">GMT+0:00 格林威治时间</option>
                    <option value="GMT-5">GMT-5:00 东部标准时间</option>
                    <option value="GMT-8">GMT-8:00 太平洋标准时间</option>
                  </select>
                  <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <i class="fa-solid fa-chevron-down text-gray-400"></i>
                  </div>
                </div>
              </div>
              
              <!-- Theme Setting -->
              <div id="theme-setting" class="flex flex-col">
                <label class="text-sm font-medium mb-2">界面主题:</label>
                <div class="flex gap-6">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input 
                      v-model="basicSettings.theme"
                      type="radio" 
                      value="light"
                      class="w-4 h-4 text-primary focus:ring-primary"
                    >
                    <i class="fa-regular fa-sun"></i>
                    <span>浅色</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input 
                      v-model="basicSettings.theme"
                      type="radio" 
                      value="dark"
                      class="w-4 h-4 text-primary focus:ring-primary"
                    >
                    <i class="fa-regular fa-moon"></i>
                    <span>深色</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input 
                      v-model="basicSettings.theme"
                      type="radio" 
                      value="auto"
                      class="w-4 h-4 text-primary focus:ring-primary"
                    >
                    <i class="fa-solid fa-circle-half-stroke"></i>
                    <span>自动</span>
                  </label>
                </div>
              </div>
              
              <!-- Auto Save Setting -->
              <div id="autosave-setting" class="flex flex-col">
                <label class="text-sm font-medium mb-2">自动保存:</label>
                <div class="flex items-center gap-4">
                  <label class="inline-flex items-center cursor-pointer">
                    <input 
                      v-model="basicSettings.autoSave.enabled"
                      type="checkbox" 
                      class="w-4 h-4 text-primary focus:ring-primary"
                    >
                    <span class="ml-2">启用</span>
                  </label>
                  <div class="flex items-center gap-2">
                    <span>间隔:</span>
                    <input 
                      v-model="basicSettings.autoSave.interval"
                      type="number" 
                      min="1" 
                      max="60" 
                      class="w-16 p-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                    <span>分钟</span>
                  </div>
                </div>
              </div>
              
              <!-- Auto Start Setting -->
              <div id="autostart-setting" class="flex flex-col">
                <label class="text-sm font-medium mb-2">开机自启:</label>
                <label class="inline-flex items-center cursor-pointer">
                  <input 
                    v-model="basicSettings.autoStart"
                    type="checkbox" 
                    class="w-4 h-4 text-primary focus:ring-primary"
                  >
                  <span class="ml-2">启用</span>
                </label>
              </div>
              
              <!-- Log Level Setting -->
              <div id="loglevel-setting" class="flex flex-col">
                <label class="text-sm font-medium mb-2">日志级别:</label>
                <div class="relative w-64">
                  <select 
                    v-model="basicSettings.logLevel"
                    class="w-full p-2 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARN">WARN</option>
                    <option value="ERROR">ERROR</option>
                  </select>
                  <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                    <i class="fa-solid fa-chevron-down text-gray-400"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Device Settings Panel -->
          <div 
            id="device-settings-panel" 
            v-show="activeCategory === 'device'"
            class="bg-white rounded-lg shadow-sm p-6"
          >
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center gap-2">
                <i class="fa-solid fa-robot text-primary text-xl"></i>
                <h2 class="text-xl font-bold">设备配置</h2>
              </div>
              <button 
                class="text-primary hover:text-blue-600"
                @click="resetDeviceSettings"
              >
                <i class="fa-solid fa-rotate-right"></i> 重置
              </button>
            </div>
            
            <div class="space-y-8">
              <!-- FR3 Robot Arm Settings -->
              <div id="robot-arm-settings" class="border border-gray-200 rounded-lg p-4">
                <h3 class="text-lg font-medium mb-4">FR3机械臂配置:</h3>
                <div class="grid grid-cols-2 gap-6">
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">最大速度 (m/s):</label>
                    <input 
                      v-model="deviceSettings.robotArm.maxSpeed"
                      type="number" 
                      min="0.1" 
                      max="5.0" 
                      step="0.1" 
                      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">最大加速度 (m/s²):</label>
                    <input 
                      v-model="deviceSettings.robotArm.maxAcceleration"
                      type="number" 
                      min="0.1" 
                      max="10.0" 
                      step="0.1" 
                      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">碰撞检测:</label>
                    <label class="inline-flex items-center cursor-pointer">
                      <input 
                        v-model="deviceSettings.robotArm.collisionDetection"
                        type="checkbox" 
                        class="w-4 h-4 text-primary focus:ring-primary"
                      >
                      <span class="ml-2">启用</span>
                    </label>
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">力控阈值 (N):</label>
                    <input 
                      v-model="deviceSettings.robotArm.forceThreshold"
                      type="number" 
                      min="1.0" 
                      max="50.0" 
                      step="0.5" 
                      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                  </div>
                </div>
              </div>
              
              <!-- Hermes Base Settings -->
              <div id="base-settings" class="border border-gray-200 rounded-lg p-4">
                <h3 class="text-lg font-medium mb-4">Hermes底盘配置:</h3>
                <div class="grid grid-cols-2 gap-6">
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">最大线速度 (m/s):</label>
                    <input 
                      v-model="deviceSettings.base.maxLinearSpeed"
                      type="number" 
                      min="0.1" 
                      max="3.0" 
                      step="0.1" 
                      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">最大角速度 (rad/s):</label>
                    <input 
                      v-model="deviceSettings.base.maxAngularSpeed"
                      type="number" 
                      min="0.1" 
                      max="3.0" 
                      step="0.1" 
                      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">安全距离 (m):</label>
                    <input 
                      v-model="deviceSettings.base.safetyDistance"
                      type="number" 
                      min="0.1" 
                      max="1.0" 
                      step="0.05" 
                      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">避障敏感度:</label>
                    <div class="relative">
                      <select 
                        v-model="deviceSettings.base.obstacleSensitivity"
                        class="w-full p-2 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="low">低</option>
                        <option value="medium">中等</option>
                        <option value="high">高</option>
                      </select>
                      <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                        <i class="fa-solid fa-chevron-down text-gray-400"></i>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Camera Settings -->
              <div id="camera-settings" class="border border-gray-200 rounded-lg p-4">
                <h3 class="text-lg font-medium mb-4">相机系统配置:</h3>
                <div class="grid grid-cols-2 gap-6">
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">2D相机分辨率:</label>
                    <div class="relative">
                      <select 
                        v-model="deviceSettings.camera.resolution"
                        class="w-full p-2 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="1280x720">1280x720</option>
                        <option value="1920x1080">1920x1080</option>
                        <option value="2560x1440">2560x1440</option>
                        <option value="3840x2160">3840x2160</option>
                      </select>
                      <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                        <i class="fa-solid fa-chevron-down text-gray-400"></i>
                      </div>
                    </div>
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">帧率 (fps):</label>
                    <input 
                      v-model="deviceSettings.camera.frameRate"
                      type="number" 
                      min="15" 
                      max="120" 
                      step="1" 
                      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">TOF相机深度范围 (m):</label>
                    <div class="flex items-center gap-2">
                      <input 
                        v-model="deviceSettings.camera.depthRange.min"
                        type="number" 
                        min="0.1" 
                        max="1.0" 
                        step="0.1" 
                        class="w-20 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                      <span>-</span>
                      <input 
                        v-model="deviceSettings.camera.depthRange.max"
                        type="number" 
                        min="1.0" 
                        max="20.0" 
                        step="0.5" 
                        class="w-20 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                    </div>
                  </div>
                  <div class="flex flex-col">
                    <label class="text-sm font-medium mb-2">精度:</label>
                    <div class="relative">
                      <select 
                        v-model="deviceSettings.camera.precision"
                        class="w-full p-2 border border-gray-300 rounded-md appearance-none focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="low">低</option>
                        <option value="medium">中</option>
                        <option value="high">高</option>
                      </select>
                      <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                        <i class="fa-solid fa-chevron-down text-gray-400"></i>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Other Settings Panels (placeholder for other categories) -->
          <div 
            v-show="activeCategory !== 'basic' && activeCategory !== 'device'"
            class="bg-white rounded-lg shadow-sm p-6 flex items-center justify-center h-96"
          >
            <div class="text-center text-gray-500">
              <i class="fa-solid fa-gear text-4xl mb-4"></i>
              <p class="text-lg font-medium">{{ getCategoryTitle(activeCategory) }}</p>
              <p class="text-sm">该设置面板正在开发中...</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div id="action-buttons" class="mt-6 grid grid-cols-6 gap-4">
        <button 
          class="flex items-center justify-center gap-2 bg-primary text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors"
          @click="applySettings"
        >
          <i class="fa-solid fa-check"></i> 应用设置
        </button>
        <button 
          class="flex items-center justify-center gap-2 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
          @click="restoreDefaults"
        >
          <i class="fa-solid fa-rotate-left"></i> 恢复默认
        </button>
        <button 
          class="flex items-center justify-center gap-2 bg-warning text-white py-2 px-4 rounded-md hover:bg-yellow-600 transition-colors"
          @click="restartSystem"
        >
          <i class="fa-solid fa-power-off"></i> 重启系统
        </button>
        <button 
          class="flex items-center justify-center gap-2 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
          @click="importConfig"
        >
          <i class="fa-solid fa-file-import"></i> 导入配置
        </button>
        <button 
          class="flex items-center justify-center gap-2 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
          @click="exportConfig"
        >
          <i class="fa-solid fa-file-export"></i> 导出配置
        </button>
        <button 
          class="flex items-center justify-center gap-2 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
          @click="backupSystem"
        >
          <i class="fa-solid fa-database"></i> 备份系统
        </button>
      </div>
      
      <!-- Status Indicators -->
      <div id="status-indicators" class="mt-4 flex items-center gap-6 text-sm text-gray-600">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-success"></span>
          <span>系统状态: {{ systemStatus.status }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-success"></span>
          <span>网络连接: {{ systemStatus.network }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-info"></span>
          <span>上次更新: {{ systemStatus.lastUpdate }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 活动分类
const activeCategory = ref('basic')

// 基础设置
const basicSettings = reactive({
  language: 'zh-CN',
  timezone: 'GMT+8',
  theme: 'light',
  autoSave: {
    enabled: true,
    interval: 5
  },
  autoStart: true,
  logLevel: 'INFO'
})

// 设备设置
const deviceSettings = reactive({
  robotArm: {
    maxSpeed: 2.0,
    maxAcceleration: 2.0,
    collisionDetection: true,
    forceThreshold: 10.0
  },
  base: {
    maxLinearSpeed: 1.0,
    maxAngularSpeed: 1.0,
    safetyDistance: 0.3,
    obstacleSensitivity: 'medium'
  },
  camera: {
    resolution: '1920x1080',
    frameRate: 30,
    depthRange: {
      min: 0.2,
      max: 10.0
    },
    precision: 'high'
  }
})

// 系统状态
const systemStatus = reactive({
  status: '正常',
  network: '已连接',
  lastUpdate: '2025-07-20 14:30:45'
})

// 分类标题映射
const categoryTitles: Record<string, string> = {
  basic: '基础设置',
  device: '设备配置',
  security: '安全设置',
  maintenance: '系统维护',
  performance: '性能调优',
  theme: '界面主题',
  network: '网络设置',
  notification: '通知设置'
}

// 设置活动分类
const setActiveCategory = (category: string) => {
  activeCategory.value = category
}

// 获取分类标题
const getCategoryTitle = (category: string) => {
  return categoryTitles[category] || '未知分类'
}

// 重置基础设置
const resetBasicSettings = async () => {
  try {
    await ElMessageBox.confirm('确定要重置基础设置吗？', '确认重置', {
      type: 'warning'
    })
    
    // 重置为默认值
    Object.assign(basicSettings, {
      language: 'zh-CN',
      timezone: 'GMT+8',
      theme: 'light',
      autoSave: { enabled: true, interval: 5 },
      autoStart: true,
      logLevel: 'INFO'
    })
    
    ElMessage.success('基础设置已重置为默认值')
  } catch {
    // 用户取消
  }
}

// 重置设备设置
const resetDeviceSettings = async () => {
  try {
    await ElMessageBox.confirm('确定要重置设备设置吗？', '确认重置', {
      type: 'warning'
    })
    
    // 重置为默认值
    Object.assign(deviceSettings, {
      robotArm: {
        maxSpeed: 2.0,
        maxAcceleration: 2.0,
        collisionDetection: true,
        forceThreshold: 10.0
      },
      base: {
        maxLinearSpeed: 1.0,
        maxAngularSpeed: 1.0,
        safetyDistance: 0.3,
        obstacleSensitivity: 'medium'
      },
      camera: {
        resolution: '1920x1080',
        frameRate: 30,
        depthRange: { min: 0.2, max: 10.0 },
        precision: 'high'
      }
    })
    
    ElMessage.success('设备设置已重置为默认值')
  } catch {
    // 用户取消
  }
}

// 应用设置
const applySettings = () => {
  ElMessage.success('设置已应用并保存')
  // 这里应该调用API保存设置
  console.log('Basic Settings:', basicSettings)
  console.log('Device Settings:', deviceSettings)
}

// 恢复默认设置
const restoreDefaults = async () => {
  try {
    await ElMessageBox.confirm('确定要恢复默认设置吗？这将覆盖所有当前配置。', '确认恢复', {
      type: 'warning'
    })
    
    resetBasicSettings()
    resetDeviceSettings()
    ElMessage.success('所有设置已恢复为默认值')
  } catch {
    // 用户取消
  }
}

// 重启系统
const restartSystem = async () => {
  try {
    await ElMessageBox.confirm('确定要重启系统吗？这将中断所有正在进行的操作。', '确认重启', {
      type: 'warning'
    })
    
    ElMessage.info('系统正在重启，请稍候...')
    // 这里应该调用API重启系统
  } catch {
    // 用户取消
  }
}

// 导入配置
const importConfig = () => {
  ElMessage.info('导入配置功能正在开发中')
  // 这里应该实现文件选择和配置导入
}

// 导出配置
const exportConfig = () => {
  ElMessage.success('配置已导出到下载目录')
  // 这里应该实现配置导出
}

// 备份系统
const backupSystem = () => {
  ElMessage.info('系统备份功能正在开发中')
  // 这里应该实现系统备份
}

// 更新系统状态
const updateSystemStatus = () => {
  const now = new Date()
  systemStatus.lastUpdate = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  console.log('系统设置页面已加载')
  // 定期更新系统状态
  setInterval(updateSystemStatus, 30000) // 每30秒更新一次
})
</script>

<style scoped>
/* 颜色变量 */
.text-secondary {
  color: #2c3e50;
}

.bg-light-bg {
  background-color: #F8F9FA;
}

.bg-info {
  background-color: #909399;
}

.bg-primary {
  background-color: #409EFF;
}

.bg-warning {
  background-color: #E6A23C;
}

.bg-success {
  background-color: #00A870;
}

.text-primary {
  color: #409EFF;
}

.hover\:text-blue-600:hover {
  color: #1E90FF;
}

.hover\:bg-blue-600:hover {
  background-color: #1E90FF;
}

.hover\:bg-yellow-600:hover {
  background-color: #D4A022;
}

.hover\:bg-gray-300:hover {
  background-color: #D1D5DB;
}

.focus\:ring-primary:focus {
  --tw-ring-color: #409EFF;
}

.focus\:ring-2:focus {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

/* 确保字体一致性 */
* {
  font-family: 'Inter', sans-serif;
}

/* 滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}

/* 选择框样式重置 */
select {
  background-image: none;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  #settings-container {
    flex-direction: column;
  }
  
  #settings-categories {
    width: 100%;
    margin-bottom: 1rem;
  }
  
  #action-buttons {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  #action-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>