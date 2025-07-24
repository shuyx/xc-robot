<template>
  <div id="main-content" class="p-6 w-full h-[calc(100vh-100px)] overflow-y-auto">
    <!-- Page Header -->
    <div id="page-header" class="mb-6">
      <h1 class="text-2xl font-semibold text-textPrimary">快速启动中心</h1>
      <p class="text-textSecondary mt-1">快速访问常用功能和最近操作</p>
    </div>
    
    <!-- Favorites Section -->
    <div id="favorites-section" class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center">
          <i class="fa-solid fa-thumbtack text-primary mr-2"></i>
          <h2 class="text-lg font-medium">收藏功能</h2>
        </div>
        <button 
          class="text-primary hover:text-blue-600 text-sm flex items-center"
          @click="manageFavorites"
        >
          <i class="fa-solid fa-gear mr-1"></i>
          管理收藏
        </button>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Favorite Card 1 -->
        <div 
          id="favorite-card-1" 
          class="bg-white rounded-lg border border-gray-200 hover:border-primary hover:shadow-md transition-all duration-200 relative group cursor-pointer"
          @click="navigateToModule('arm-control')"
        >
          <div class="absolute top-2 right-2">
            <button 
              class="text-yellow-400 hover:text-yellow-500"
              @click.stop="toggleFavorite('arm-control')"
            >
              <i class="fa-solid fa-star"></i>
            </button>
          </div>
          <div class="p-5">
            <div class="flex items-center mb-3">
              <div class="w-10 h-10 rounded-lg bg-light flex items-center justify-center text-primary">
                <i class="fa-solid fa-robot text-xl"></i>
              </div>
              <div class="ml-3">
                <h3 class="font-medium">机械臂控制</h3>
                <p class="text-xs text-textSecondary">工业自动化</p>
              </div>
            </div>
            <p class="text-sm text-textSecondary mb-4 hidden group-hover:block">控制工业机械臂执行精准操作</p>
            <div class="flex justify-end">
              <button class="text-primary text-sm hover:text-blue-700 flex items-center">
                <span>进入</span>
                <i class="fa-solid fa-arrow-right ml-1"></i>
              </button>
            </div>
          </div>
          <div class="absolute bottom-0 left-0 w-full h-1 bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </div>
        
        <!-- Favorite Card 2 -->
        <div 
          id="favorite-card-2" 
          class="bg-white rounded-lg border border-gray-200 hover:border-primary hover:shadow-md transition-all duration-200 relative group cursor-pointer"
          @click="navigateToModule('face-recognition')"
        >
          <div class="absolute top-2 right-2">
            <button 
              class="text-yellow-400 hover:text-yellow-500"
              @click.stop="toggleFavorite('face-recognition')"
            >
              <i class="fa-solid fa-star"></i>
            </button>
          </div>
          <div class="p-5">
            <div class="flex items-center mb-3">
              <div class="w-10 h-10 rounded-lg bg-light flex items-center justify-center text-primary">
                <i class="fa-solid fa-eye text-xl"></i>
              </div>
              <div class="ml-3">
                <h3 class="font-medium">人脸识别系统</h3>
                <p class="text-xs text-textSecondary">计算机视觉</p>
              </div>
            </div>
            <p class="text-sm text-textSecondary mb-4 hidden group-hover:block">实时人脸检测与身份识别系统</p>
            <div class="flex justify-end">
              <button class="text-primary text-sm hover:text-blue-700 flex items-center">
                <span>进入</span>
                <i class="fa-solid fa-arrow-right ml-1"></i>
              </button>
            </div>
          </div>
          <div class="absolute bottom-0 left-0 w-full h-1 bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </div>
        
        <!-- Favorite Card 3 -->
        <div 
          id="favorite-card-3" 
          class="bg-white rounded-lg border border-gray-200 hover:border-primary hover:shadow-md transition-all duration-200 relative group cursor-pointer"
          @click="navigateToModule('path-planning')"
        >
          <div class="absolute top-2 right-2">
            <button 
              class="text-yellow-400 hover:text-yellow-500"
              @click.stop="toggleFavorite('path-planning')"
            >
              <i class="fa-solid fa-star"></i>
            </button>
          </div>
          <div class="p-5">
            <div class="flex items-center mb-3">
              <div class="w-10 h-10 rounded-lg bg-light flex items-center justify-center text-primary">
                <i class="fa-solid fa-bullseye text-xl"></i>
              </div>
              <div class="ml-3">
                <h3 class="font-medium">路径规划</h3>
                <p class="text-xs text-textSecondary">导航算法</p>
              </div>
            </div>
            <p class="text-sm text-textSecondary mb-4 hidden group-hover:block">智能路径规划与优化系统</p>
            <div class="flex justify-end">
              <button class="text-primary text-sm hover:text-blue-700 flex items-center">
                <span>进入</span>
                <i class="fa-solid fa-arrow-right ml-1"></i>
              </button>
            </div>
          </div>
          <div class="absolute bottom-0 left-0 w-full h-1 bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </div>
        
        <!-- Favorite Card 4 -->
        <div 
          id="favorite-card-4" 
          class="bg-white rounded-lg border border-gray-200 hover:border-primary hover:shadow-md transition-all duration-200 relative group cursor-pointer"
          @click="navigateToModule('data-monitoring')"
        >
          <div class="absolute top-2 right-2">
            <button 
              class="text-yellow-400 hover:text-yellow-500"
              @click.stop="toggleFavorite('data-monitoring')"
            >
              <i class="fa-solid fa-star"></i>
            </button>
          </div>
          <div class="p-5">
            <div class="flex items-center mb-3">
              <div class="w-10 h-10 rounded-lg bg-light flex items-center justify-center text-primary">
                <i class="fa-solid fa-chart-line text-xl"></i>
              </div>
              <div class="ml-3">
                <h3 class="font-medium">数据监控</h3>
                <p class="text-xs text-textSecondary">实时分析</p>
              </div>
            </div>
            <p class="text-sm text-textSecondary mb-4 hidden group-hover:block">实时数据监控与趋势分析</p>
            <div class="flex justify-end">
              <button class="text-primary text-sm hover:text-blue-700 flex items-center">
                <span>进入</span>
                <i class="fa-solid fa-arrow-right ml-1"></i>
              </button>
            </div>
          </div>
          <div class="absolute bottom-0 left-0 w-full h-1 bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </div>
      </div>
    </div>
    
    <!-- Recent Activities Section -->
    <div id="recent-section" class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center">
          <i class="fa-regular fa-clock text-primary mr-2"></i>
          <h2 class="text-lg font-medium">最近使用</h2>
        </div>
        <div class="relative">
          <input 
            v-model="recentSearchQuery"
            type="text" 
            placeholder="搜索最近使用" 
            class="pl-8 pr-4 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
            @input="filterRecentItems"
          >
          <i class="fa-solid fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"></i>
        </div>
      </div>
      
      <div class="bg-white rounded-lg border border-gray-200">
        <!-- Recent Activity 1 -->
        <div 
          id="recent-item-1" 
          class="p-4 border-b border-gray-100 hover:bg-light transition-colors cursor-pointer"
          @click="navigateToModule('smart-chat')"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-8 h-8 rounded-lg bg-light flex items-center justify-center text-primary mr-3">
                <i class="fa-solid fa-comments"></i>
              </div>
              <div>
                <h3 class="font-medium">智能对话系统</h3>
                <p class="text-xs text-textSecondary">{{ recentActivities[0]?.timestamp || '2025-07-19 14:30' }}</p>
              </div>
            </div>
            <button class="px-3 py-1 text-sm text-primary border border-primary rounded-md hover:bg-primary hover:text-white transition-colors">
              快速进入
            </button>
          </div>
        </div>
        
        <!-- Recent Activity 2 -->
        <div 
          id="recent-item-2" 
          class="p-4 border-b border-gray-100 hover:bg-light transition-colors cursor-pointer"
          @click="navigateToModule('device-test')"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-8 h-8 rounded-lg bg-light flex items-center justify-center text-primary mr-3">
                <i class="fa-solid fa-plug"></i>
              </div>
              <div>
                <h3 class="font-medium">设备连接测试</h3>
                <p class="text-xs text-textSecondary">{{ recentActivities[1]?.timestamp || '2025-07-19 14:15' }}</p>
              </div>
            </div>
            <button class="px-3 py-1 text-sm text-primary border border-primary rounded-md hover:bg-primary hover:text-white transition-colors">
              快速进入
            </button>
          </div>
        </div>
        
        <!-- Recent Activity 3 -->
        <div 
          id="recent-item-3" 
          class="p-4 hover:bg-light transition-colors cursor-pointer"
          @click="navigateToModule('arm-control')"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-8 h-8 rounded-lg bg-light flex items-center justify-center text-primary mr-3">
                <i class="fa-solid fa-robot"></i>
              </div>
              <div>
                <h3 class="font-medium">机械臂控制</h3>
                <p class="text-xs text-textSecondary">{{ recentActivities[2]?.timestamp || '2025-07-19 13:45' }}</p>
              </div>
            </div>
            <button class="px-3 py-1 text-sm text-primary border border-primary rounded-md hover:bg-primary hover:text-white transition-colors">
              快速进入
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- System Status Section -->
    <div id="status-section">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center">
          <i class="fa-solid fa-chart-pie text-primary mr-2"></i>
          <h2 class="text-lg font-medium">系统状态</h2>
        </div>
        <button 
          class="text-primary hover:text-blue-600 text-sm flex items-center"
          @click="refreshSystemStatus"
        >
          <i class="fa-solid fa-refresh mr-1"></i>
          刷新
        </button>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Status Card 1 -->
        <div id="status-card-1" class="bg-white rounded-lg border border-gray-200 p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-medium">设备状态</h3>
            <span class="w-4 h-4 rounded-full bg-success"></span>
          </div>
          <div class="flex items-center justify-between">
            <div class="text-3xl font-semibold">{{ systemStatus.devices.online }}/{{ systemStatus.devices.total }}</div>
            <div ref="deviceChartRef" class="w-16 h-16"></div>
          </div>
          <p class="text-xs text-textSecondary mt-2">{{ Math.round((systemStatus.devices.online / systemStatus.devices.total) * 100) }}% 设备在线运行中</p>
        </div>
        
        <!-- Status Card 2 -->
        <div id="status-card-2" class="bg-white rounded-lg border border-gray-200 p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-medium">任务状态</h3>
            <span class="w-4 h-4 rounded-full bg-warning"></span>
          </div>
          <div class="flex items-center justify-between">
            <div class="text-3xl font-semibold">{{ systemStatus.tasks.status }}</div>
            <div ref="taskChartRef" class="w-16 h-16"></div>
          </div>
          <p class="text-xs text-textSecondary mt-2">{{ systemStatus.tasks.running }}个任务正在执行，{{ systemStatus.tasks.waiting }}个等待中</p>
        </div>
        
        <!-- Status Card 3 -->
        <div id="status-card-3" class="bg-white rounded-lg border border-gray-200 p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-medium">系统负载</h3>
            <span class="w-4 h-4 rounded-full bg-success"></span>
          </div>
          <div class="flex items-center justify-between">
            <div class="text-3xl font-semibold">{{ systemStatus.system.cpu }}%</div>
            <div ref="loadChartRef" class="w-16 h-16"></div>
          </div>
          <p class="text-xs text-textSecondary mt-2">CPU: {{ systemStatus.system.cpu }}% | 内存: {{ systemStatus.system.memory }}% | 存储: {{ systemStatus.system.storage }}%</p>
        </div>
        
        <!-- Status Card 4 -->
        <div id="status-card-4" class="bg-white rounded-lg border border-gray-200 p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-medium">网络状态</h3>
            <span class="w-4 h-4 rounded-full bg-success"></span>
          </div>
          <div class="flex items-center justify-between">
            <div class="text-3xl font-semibold">{{ systemStatus.network.status }}</div>
            <div ref="networkChartRef" class="w-16 h-16"></div>
          </div>
          <p class="text-xs text-textSecondary mt-2">延迟: {{ systemStatus.network.latency }}ms | 丢包率: {{ systemStatus.network.packetLoss }}%</p>
        </div>
      </div>
    </div>
    
    <!-- Keyboard Shortcuts Info -->
    <div id="shortcuts-info" class="mt-6 text-center">
      <p class="text-xs text-textSecondary">
        <i class="fa-solid fa-keyboard mr-1"></i>
        快捷键提示: 按数字键 1-8 快速访问收藏功能
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 导入Highcharts (注意：在实际项目中可能需要安装 highcharts 包)
// import Highcharts from 'highcharts'

const router = useRouter()

// 搜索查询
const recentSearchQuery = ref('')

// 最近活动数据 (集成Mock数据)
const recentActivities = ref([
  { id: 1, module: 'smart-chat', title: '智能对话系统', icon: 'fa-solid fa-comments', timestamp: '2025-07-19 14:30' },
  { id: 2, module: 'device-test', title: '设备连接测试', icon: 'fa-solid fa-plug', timestamp: '2025-07-19 14:15' },
  { id: 3, module: 'arm-control', title: '机械臂控制', icon: 'fa-solid fa-robot', timestamp: '2025-07-19 13:45' }
])

// 系统状态数据 (集成Mock数据)
const systemStatus = ref({
  devices: { online: 5, total: 6 },
  tasks: { status: '运行中', running: 3, waiting: 1 },
  system: { cpu: 65, memory: 48, storage: 32 },
  network: { status: '良好', latency: 23, packetLoss: 0.01 }
})

// 图表元素引用
const deviceChartRef = ref<HTMLElement>()
const taskChartRef = ref<HTMLElement>()
const loadChartRef = ref<HTMLElement>()
const networkChartRef = ref<HTMLElement>()

// 模块导航
const navigateToModule = (module: string) => {
  const moduleRoutes: Record<string, string> = {
    'arm-control': '/robot-control/arm',
    'face-recognition': '/intelligent-interaction/face',
    'path-planning': '/simulation-planning/path',
    'data-monitoring': '/data-monitoring/system',
    'smart-chat': '/intelligent-interaction/chat',
    'device-test': '/device-connection/test'
  }
  
  const route = moduleRoutes[module]
  if (route) {
    router.push(route)
  } else {
    ElMessage.info(`正在开发中: ${module}`)
  }
}

// 收藏管理
const manageFavorites = () => {
  ElMessage.info('收藏管理功能正在开发中')
}

const toggleFavorite = (module: string) => {
  ElMessage.success(`已更新 ${module} 的收藏状态`)
}

// 搜索过滤
const filterRecentItems = () => {
  // 实现搜索过滤逻辑
  console.log('搜索关键词:', recentSearchQuery.value)
}

// 刷新系统状态
const refreshSystemStatus = () => {
  ElMessage.success('系统状态已刷新')
  // 这里可以调用Mock数据API更新数据
}

// 初始化图表 (模拟Highcharts - 在实际项目中需要安装并正确导入Highcharts)
const initializeCharts = () => {
  // 由于我们使用Vue3 + TypeScript，这里需要模拟Highcharts的初始化
  // 在实际项目中，您需要：
  // 1. npm install highcharts
  // 2. import Highcharts from 'highcharts'
  // 3. 使用真正的Highcharts API
  
  console.log('图表初始化 - 设备状态图表')
  console.log('图表初始化 - 任务状态图表')
  console.log('图表初始化 - 系统负载图表')
  console.log('图表初始化 - 网络状态图表')
  
  // 这里应该使用真正的Highcharts初始化代码
  // 示例(需要安装Highcharts后使用):
  /*
  if (deviceChartRef.value) {
    Highcharts.chart(deviceChartRef.value, {
      chart: { type: 'pie', height: 80, width: 80, backgroundColor: 'transparent' },
      title: null,
      credits: { enabled: false },
      tooltip: { enabled: false },
      plotOptions: {
        pie: {
          dataLabels: { enabled: false },
          borderWidth: 0,
          innerSize: '70%',
          size: '100%'
        }
      },
      series: [{
        data: [
          { y: systemStatus.value.devices.online, color: '#67C23A' },
          { y: systemStatus.value.devices.total - systemStatus.value.devices.online, color: '#E4E7ED' }
        ]
      }]
    })
  }
  */
}

// 键盘快捷键
const handleKeyboardShortcuts = (e: KeyboardEvent) => {
  // 检查按键是否为数字1-8
  if (e.key >= '1' && e.key <= '8') {
    const index = parseInt(e.key) - 1
    const favoriteCards = document.querySelectorAll('#favorites-section .grid > div')
    if (index < favoriteCards.length) {
      const card = favoriteCards[index] as HTMLElement
      card.click()
    }
  }
}

onMounted(async () => {
  // 等待DOM更新完成后初始化图表
  await nextTick()
  initializeCharts()
  
  // 添加键盘快捷键监听
  document.addEventListener('keydown', handleKeyboardShortcuts)
  
  console.log('快速启动页面已加载')
})

onUnmounted(() => {
  // 清理键盘监听器
  document.removeEventListener('keydown', handleKeyboardShortcuts)
})
</script>

<style scoped>
/* 基础颜色变量 */
.text-textPrimary {
  color: #2c3e50;
}

.text-textSecondary {
  color: #606266;
}

.text-primary {
  color: #409EFF;
}

.bg-light {
  background-color: #E6F4FF;
}

.bg-success {
  background-color: #67C23A;
}

.bg-warning {
  background-color: #E6A23C;
}

.border-primary {
  border-color: #409EFF;
}

.hover\:border-primary:hover {
  border-color: #409EFF;
}

.hover\:text-blue-600:hover {
  color: #1E90FF;
}

.hover\:text-blue-700:hover {
  color: #1976D2;
}

.hover\:text-yellow-500:hover {
  color: #FFC107;
}

.hover\:bg-light:hover {
  background-color: #E6F4FF;
}

.hover\:bg-primary:hover {
  background-color: #409EFF;
}

.ring-primary {
  --tw-ring-color: #409EFF;
}

/* 确保字体一致性 */
* {
  font-family: 'Inter', sans-serif;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .grid-cols-1.md\:grid-cols-2.lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

@media (min-width: 768px) {
  .grid-cols-1.md\:grid-cols-2.lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .grid-cols-1.md\:grid-cols-2.lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>