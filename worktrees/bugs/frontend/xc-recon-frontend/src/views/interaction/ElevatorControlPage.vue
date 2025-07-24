<template>
  <div id="elevator-control-system" class="w-full h-[calc(100vh-100px)] bg-gray-50 p-4 overflow-auto">
    <!-- Page Header -->
    <div id="page-header" class="mb-4">
      <h1 class="text-2xl font-bold text-secondary">智能梯控系统</h1>
      <p class="text-gray-500">电梯智能控制与楼层导航</p>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Elevator Status Card -->
      <div id="elevator-status-card" class="bg-white rounded-lg shadow-sm">
        <div class="flex items-center justify-between border-b p-3">
          <div class="flex items-center">
            <i class="fa-solid fa-building text-primary mr-2"></i>
            <h2 class="font-semibold">电梯状态</h2>
          </div>
          <button 
            @click="refreshElevatorStatus"
            class="text-gray-400 hover:text-primary"
          >
            <i class="fa-solid fa-arrows-rotate"></i>
          </button>
        </div>
        <div class="p-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-3">
              <div class="flex items-center">
                <i class="fa-solid fa-location-dot text-primary w-6"></i>
                <span class="font-medium mr-2">当前楼层:</span>
                <span class="text-success font-bold">{{ elevatorStatus.currentFloor }}</span>
              </div>
              <div class="flex items-center">
                <i class="fa-solid fa-arrows-up-down text-primary w-6"></i>
                <span class="font-medium mr-2">运行状态:</span>
                <span :class="[
                  elevatorStatus.status === '静止' ? 'text-info' : 
                  elevatorStatus.status === '上行' ? 'text-primary' : 'text-warning'
                ]">{{ elevatorStatus.status }}</span>
              </div>
              <div class="flex items-center">
                <i class="fa-solid fa-door-open text-primary w-6"></i>
                <span class="font-medium mr-2">门状态:</span>
                <span>{{ elevatorStatus.doorStatus }}</span>
              </div>
              <div class="flex items-center">
                <i class="fa-solid fa-weight-scale text-primary w-6"></i>
                <span class="font-medium mr-2">载重:</span>
                <span>{{ elevatorStatus.weight }}/1000kg</span>
              </div>
              <div class="flex items-center">
                <i class="fa-regular fa-clock text-primary w-6"></i>
                <span class="font-medium mr-2">等待时间:</span>
                <span>{{ elevatorStatus.waitTime }}秒</span>
              </div>
            </div>
            
            <div id="elevator-status-graph" class="bg-gray-50 rounded-lg p-3 min-h-[300px]">
              <h3 class="text-sm font-medium mb-2">实时状态图</h3>
              <div class="flex items-stretch h-[250px]">
                <div class="w-16 border border-gray-200 rounded-lg bg-light relative">
                  <div class="absolute inset-0 flex flex-col justify-between py-2 items-center">
                    <div 
                      v-for="floor in floors" 
                      :key="floor.number"
                      :class="[
                        'w-8 h-5 rounded',
                        floor.number === elevatorStatus.currentFloor ? 'bg-success' : 'bg-gray-200'
                      ]"
                    ></div>
                  </div>
                </div>
                <div class="flex-1 flex flex-col justify-between py-2 ml-2 text-sm">
                  <div 
                    v-for="floor in floors" 
                    :key="floor.number"
                    :class="[
                      floor.number === elevatorStatus.currentFloor ? 'flex items-center font-bold text-success' : ''
                    ]"
                  >
                    {{ floor.label }}
                    <template v-if="floor.number === elevatorStatus.currentFloor">
                      <i class="fa-solid fa-arrow-left ml-1"></i> 
                      <span class="ml-1">当前</span>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Floor Selection Card -->
      <div id="floor-selection-card" class="bg-white rounded-lg shadow-sm">
        <div class="flex items-center justify-between border-b p-3">
          <div class="flex items-center">
            <i class="fa-solid fa-bullseye text-primary mr-2"></i>
            <h2 class="font-semibold">楼层选择</h2>
          </div>
        </div>
        <div class="p-4">
          <h3 class="font-medium mb-3 flex items-center">
            <i class="fa-solid fa-building-user mr-2 text-primary"></i>
            目标楼层选择
          </h3>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 gap-3">
            <button 
              v-for="floor in floorButtons" 
              :key="floor.number"
              @click="selectFloor(floor.number)"
              @dblclick="callElevator(floor.number)"
              :class="[
                'floor-btn p-3 rounded-lg flex items-center justify-center transition-colors',
                floor.number === elevatorStatus.currentFloor 
                  ? 'border-2 border-success bg-green-50 text-success font-medium'
                  : selectedFloor === floor.number
                  ? 'border-2 border-primary bg-blue-50 text-primary font-medium'
                  : 'border border-gray-300 text-gray-600 hover:border-primary'
              ]"
            >
              <span class="font-medium">{{ floor.label }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Control Operations Card -->
      <div id="control-operations-card" class="bg-white rounded-lg shadow-sm">
        <div class="flex items-center justify-between border-b p-3">
          <div class="flex items-center">
            <i class="fa-solid fa-gamepad text-primary mr-2"></i>
            <h2 class="font-semibold">控制操作</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex space-x-2">
              <button 
                @click="controlDoor('open')"
                class="flex-1 bg-light hover:bg-gray-200 text-secondary py-2 px-4 rounded-lg flex items-center justify-center transition-colors"
              >
                <i class="fa-solid fa-door-open mr-2"></i> 开门
              </button>
              <button 
                @click="controlDoor('close')"
                class="flex-1 bg-light hover:bg-gray-200 text-secondary py-2 px-4 rounded-lg flex items-center justify-center transition-colors"
              >
                <i class="fa-solid fa-door-closed mr-2"></i> 关门
              </button>
            </div>
            <div class="flex space-x-2">
              <button 
                @click="moveElevator('up')"
                class="flex-1 bg-light hover:bg-gray-200 text-secondary py-2 px-4 rounded-lg flex items-center justify-center transition-colors"
              >
                <i class="fa-solid fa-arrow-up mr-2"></i> 上行
              </button>
              <button 
                @click="moveElevator('down')"
                class="flex-1 bg-light hover:bg-gray-200 text-secondary py-2 px-4 rounded-lg flex items-center justify-center transition-colors"
              >
                <i class="fa-solid fa-arrow-down mr-2"></i> 下行
              </button>
            </div>
            <div class="flex space-x-2">
              <button 
                @click="callElevatorToFloor"
                class="flex-1 bg-primary hover:bg-blue-500 text-white py-2 px-4 rounded-lg flex items-center justify-center transition-colors"
              >
                <i class="fa-solid fa-bell mr-2"></i> 呼叫电梯
              </button>
            </div>
            <div class="flex space-x-2">
              <button 
                @click="cancelCall"
                class="flex-1 bg-light hover:bg-gray-200 text-secondary py-2 px-4 rounded-lg flex items-center justify-center transition-colors"
              >
                <i class="fa-solid fa-ban mr-2"></i> 取消呼叫
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Usage Statistics Card -->
      <div id="usage-statistics-card" class="bg-white rounded-lg shadow-sm">
        <div class="flex items-center justify-between border-b p-3">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-simple text-primary mr-2"></i>
            <h2 class="font-semibold">使用统计</h2>
          </div>
          <div class="flex space-x-2">
            <button 
              @click="changeStatsPeriod('today')"
              :class="[
                'text-xs px-2 py-1 rounded transition-colors',
                statsPeriod === 'today' ? 'bg-light hover:bg-gray-200' : 'text-gray-500 hover:bg-gray-100'
              ]"
            >今日</button>
            <button 
              @click="changeStatsPeriod('week')"
              :class="[
                'text-xs px-2 py-1 rounded transition-colors',
                statsPeriod === 'week' ? 'bg-light hover:bg-gray-200' : 'text-gray-500 hover:bg-gray-100'
              ]"
            >本周</button>
            <button 
              @click="changeStatsPeriod('month')"
              :class="[
                'text-xs px-2 py-1 rounded transition-colors',
                statsPeriod === 'month' ? 'bg-light hover:bg-gray-200' : 'text-gray-500 hover:bg-gray-100'
              ]"
            >本月</button>
          </div>
        </div>
        <div class="p-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-light rounded-lg p-3 flex items-center">
              <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                <i class="fa-solid fa-elevator text-primary text-xl"></i>
              </div>
              <div>
                <div class="text-sm text-gray-500">{{ statsPeriod === 'today' ? '今日使用' : statsPeriod === 'week' ? '本周使用' : '本月使用' }}</div>
                <div class="text-xl font-bold">{{ usageStats.totalUsage }}次</div>
              </div>
            </div>
            <div class="bg-light rounded-lg p-3 flex items-center">
              <div class="w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center mr-3">
                <i class="fa-regular fa-clock text-warning text-xl"></i>
              </div>
              <div>
                <div class="text-sm text-gray-500">平均等待</div>
                <div class="text-xl font-bold">{{ usageStats.averageWait }}秒</div>
              </div>
            </div>
            <div class="bg-light rounded-lg p-3 flex items-center">
              <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mr-3">
                <i class="fa-solid fa-triangle-exclamation text-danger text-xl"></i>
              </div>
              <div>
                <div class="text-sm text-gray-500">故障次数</div>
                <div class="text-xl font-bold">{{ usageStats.faultCount }}次</div>
              </div>
            </div>
            <div class="bg-light rounded-lg p-3 flex items-center">
              <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mr-3">
                <i class="fa-solid fa-screwdriver-wrench text-success text-xl"></i>
              </div>
              <div>
                <div class="text-sm text-gray-500">维护状态</div>
                <div class="text-xl font-bold flex items-center">
                  <span :class="[
                    'w-3 h-3 rounded-full mr-2',
                    usageStats.maintenanceStatus === '正常' ? 'bg-success' : 'bg-warning'
                  ]"></span>{{ usageStats.maintenanceStatus }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Operation Records Card -->
    <div id="operation-records-card" class="bg-white rounded-lg shadow-sm mt-4">
      <div class="flex items-center justify-between border-b p-3">
        <div class="flex items-center">
          <i class="fa-solid fa-clipboard-list text-primary mr-2"></i>
          <h2 class="font-semibold">操作记录</h2>
        </div>
        <button 
          @click="viewAllRecords"
          class="text-primary text-sm hover:underline"
        >
          查看全部
        </button>
      </div>
      <div class="p-4">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">楼层</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">方向</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">耗时</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="record in operationRecords" :key="record.id">
                <td class="px-3 py-3 whitespace-nowrap text-sm text-gray-500">{{ record.time }}</td>
                <td class="px-3 py-3 whitespace-nowrap text-sm font-medium">{{ record.floors }}</td>
                <td class="px-3 py-3 whitespace-nowrap text-sm">
                  <span :class="[
                    'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                    record.direction === '上行' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
                  ]">
                    <i :class="[
                      'mr-1',
                      record.direction === '上行' ? 'fa-solid fa-arrow-up' : 'fa-solid fa-arrow-down'
                    ]"></i> {{ record.direction }}
                  </span>
                </td>
                <td class="px-3 py-3 whitespace-nowrap text-sm text-gray-500">{{ record.duration }}</td>
                <td class="px-3 py-3 whitespace-nowrap text-sm">
                  <span class="inline-flex items-center">
                    <span :class="[
                      'w-2 h-2 rounded-full mr-1',
                      record.status === '完成' ? 'bg-success' : 'bg-warning'
                    ]"></span> {{ record.status }}
                  </span>
                </td>
                <td class="px-3 py-3 whitespace-nowrap text-right text-sm font-medium">
                  <span 
                    @click="viewRecordDetail(record.id)"
                    class="text-primary hover:text-blue-700 cursor-pointer"
                  >查看详情</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 电梯状态接口定义
interface ElevatorStatus {
  currentFloor: string
  status: string
  doorStatus: string
  weight: number
  waitTime: number
}

interface FloorInfo {
  number: string
  label: string
}

interface UsageStats {
  totalUsage: number
  averageWait: number
  faultCount: number
  maintenanceStatus: string
}

interface OperationRecord {
  id: number
  time: string
  floors: string
  direction: string
  duration: string
  status: string
}

// 响应式数据
const selectedFloor = ref<string | null>(null)
const statsPeriod = ref('today')

// 电梯状态
const elevatorStatus = reactive<ElevatorStatus>({
  currentFloor: '3F',
  status: '静止',
  doorStatus: '关闭',
  weight: 150,
  waitTime: 0
})

// 楼层信息（倒序排列，用于状态图显示）
const floors = ref<FloorInfo[]>([
  { number: '10F', label: '10F' },
  { number: '9F', label: '9F' },
  { number: '8F', label: '8F' },
  { number: '7F', label: '7F' },
  { number: '6F', label: '6F' },
  { number: '5F', label: '5F' },
  { number: '4F', label: '4F' },
  { number: '3F', label: '3F' },
  { number: '2F', label: '2F' },
  { number: '1F', label: '1F' },
  { number: 'B1', label: 'B1' }
])

// 楼层按钮（正序排列，用于选择区域）
const floorButtons = ref<FloorInfo[]>([
  { number: 'B1', label: 'B1' },
  { number: '1F', label: '1F' },
  { number: '2F', label: '2F' },
  { number: '3F', label: '3F' },
  { number: '4F', label: '4F' },
  { number: '5F', label: '5F' },
  { number: '6F', label: '6F' },
  { number: '7F', label: '7F' },
  { number: '8F', label: '8F' },
  { number: '9F', label: '9F' },
  { number: '10F', label: '10F' }
])

// 使用统计数据
const usageStatsData = {
  today: { totalUsage: 23, averageWait: 15, faultCount: 0, maintenanceStatus: '正常' },
  week: { totalUsage: 156, averageWait: 18, faultCount: 1, maintenanceStatus: '正常' },
  month: { totalUsage: 687, averageWait: 16, faultCount: 2, maintenanceStatus: '正常' }
}

const usageStats = reactive<UsageStats>(usageStatsData.today)

// 操作记录
const operationRecords = ref<OperationRecord[]>([
  {
    id: 1,
    time: '14:30',
    floors: '3F → 7F',
    direction: '上行',
    duration: '25秒',
    status: '完成'
  },
  {
    id: 2,
    time: '14:15',
    floors: '7F → 1F',
    direction: '下行',
    duration: '30秒',
    status: '完成'
  },
  {
    id: 3,
    time: '13:45',
    floors: '1F → 5F',
    direction: '上行',
    duration: '20秒',
    status: '完成'
  },
  {
    id: 4,
    time: '13:20',
    floors: '5F → 2F',
    direction: '下行',
    duration: '18秒',
    status: '完成'
  }
])

// 刷新电梯状态
const refreshElevatorStatus = () => {
  ElMessage.success('电梯状态已刷新')
}

// 选择楼层
const selectFloor = (floor: string) => {
  if (floor !== elevatorStatus.currentFloor) {
    selectedFloor.value = floor
    ElMessage.info(`已选择目标楼层: ${floor}`)
  }
}

// 呼叫电梯到指定楼层
const callElevator = (floor: string) => {
  if (floor !== elevatorStatus.currentFloor) {
    ElMessage.success(`电梯呼叫已发送！目标楼层: ${floor}`)
    selectedFloor.value = floor
    // 模拟电梯移动
    simulateElevatorMovement(floor)
  } else {
    ElMessage.info('电梯已在当前楼层')
  }
}

// 呼叫电梯到选中楼层
const callElevatorToFloor = () => {
  if (selectedFloor.value && selectedFloor.value !== elevatorStatus.currentFloor) {
    callElevator(selectedFloor.value)
  } else if (!selectedFloor.value) {
    ElMessage.warning('请先选择目标楼层')
  } else {
    ElMessage.info('电梯已在当前楼层')
  }
}

// 取消呼叫
const cancelCall = () => {
  selectedFloor.value = null
  ElMessage.info('已取消电梯呼叫')
}

// 控制门
const controlDoor = (action: 'open' | 'close') => {
  if (action === 'open') {
    elevatorStatus.doorStatus = '开启'
    ElMessage.success('电梯门已开启')
  } else {
    elevatorStatus.doorStatus = '关闭'
    ElMessage.success('电梯门已关闭')
  }
}

// 移动电梯
const moveElevator = (direction: 'up' | 'down') => {
  const currentIndex = floors.value.findIndex(f => f.number === elevatorStatus.currentFloor)
  let newIndex = currentIndex
  
  if (direction === 'up' && currentIndex > 0) {
    newIndex = currentIndex - 1
    elevatorStatus.status = '上行'
  } else if (direction === 'down' && currentIndex < floors.value.length - 1) {
    newIndex = currentIndex + 1
    elevatorStatus.status = '下行'
  } else {
    ElMessage.warning(`无法${direction === 'up' ? '上行' : '下行'}，已到达${direction === 'up' ? '最高' : '最低'}楼层`)
    return
  }
  
  ElMessage.info(`电梯开始${direction === 'up' ? '上行' : '下行'}`)
  
  // 模拟移动延迟
  setTimeout(() => {
    elevatorStatus.currentFloor = floors.value[newIndex].number
    elevatorStatus.status = '静止'
    ElMessage.success(`电梯已到达 ${elevatorStatus.currentFloor}`)
    addOperationRecord(direction === 'up' ? '上行' : '下行')
  }, 2000)
}

// 模拟电梯移动
const simulateElevatorMovement = (targetFloor: string) => {
  const currentIndex = floors.value.findIndex(f => f.number === elevatorStatus.currentFloor)
  const targetIndex = floors.value.findIndex(f => f.number === targetFloor)
  
  if (currentIndex === targetIndex) return
  
  const direction = currentIndex > targetIndex ? '上行' : '下行'
  elevatorStatus.status = direction
  
  // 模拟移动时间（根据楼层距离计算）
  const distance = Math.abs(currentIndex - targetIndex)
  const moveTime = distance * 1000 + 1000 // 每层1秒 + 1秒基础时间
  
  setTimeout(() => {
    elevatorStatus.currentFloor = targetFloor
    elevatorStatus.status = '静止'
    selectedFloor.value = null
    ElMessage.success(`电梯已到达目标楼层 ${targetFloor}`)
    addOperationRecord(direction)
  }, moveTime)
}

// 添加操作记录
const addOperationRecord = (direction: string) => {
  const now = new Date()
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  const duration = `${Math.floor(Math.random() * 15) + 15}秒` // 15-30秒随机
  
  const newRecord: OperationRecord = {
    id: operationRecords.value.length + 1,
    time: timeStr,
    floors: `${operationRecords.value[0]?.floors.split(' ')[0] || '1F'} → ${elevatorStatus.currentFloor}`,
    direction,
    duration,
    status: '完成'
  }
  
  operationRecords.value.unshift(newRecord)
  if (operationRecords.value.length > 10) {
    operationRecords.value.pop()
  }
}

// 切换统计周期
const changeStatsPeriod = (period: 'today' | 'week' | 'month') => {
  statsPeriod.value = period
  Object.assign(usageStats, usageStatsData[period])
}

// 查看所有记录
const viewAllRecords = () => {
  ElMessage.info('查看全部操作记录')
}

// 查看记录详情
const viewRecordDetail = (recordId: number) => {
  ElMessage.info(`查看记录详情 #${recordId}`)
}

onMounted(() => {
  console.log('电梯控制页面已加载')
})
</script>

<style scoped>
/* 项目配色系统 */
.text-primary {
  color: #409EFF;
}

.text-secondary {
  color: #2c3e50;
}

.text-success {
  color: #00A870;
}

.text-warning {
  color: #E6A23C;
}

.text-danger {
  color: #F56C6C;
}

.text-info {
  color: #909399;
}

.bg-primary {
  background-color: #409EFF;
}

.bg-secondary {
  background-color: #2c3e50;
}

.bg-success {
  background-color: #00A870;
}

.bg-warning {
  background-color: #E6A23C;
}

.bg-danger {
  background-color: #F56C6C;
}

.bg-light {
  background-color: #F8F9FA;
}

.border-primary {
  border-color: #409EFF;
}

.border-success {
  border-color: #00A870;
}

/* 楼层按钮悬停效果 */
.floor-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid.lg\\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  #elevator-status-graph {
    min-height: 200px;
  }
  
  .grid.grid-cols-2.sm\\:grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>