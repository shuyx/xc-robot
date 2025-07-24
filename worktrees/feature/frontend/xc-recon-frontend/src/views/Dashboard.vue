<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>XC-RECON 控制台</h2>
      <p>系统状态总览</p>
    </div>

    <el-row :gutter="20" class="status-cards">
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon online"><Connection /></el-icon>
            <div>
              <h3>{{ onlineDevices }}</h3>
              <p>在线设备</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon running"><VideoPlay /></el-icon>
            <div>
              <h3>{{ runningTasks }}</h3>
              <p>运行任务</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon pending"><Clock /></el-icon>
            <div>
              <h3>{{ pendingTasks }}</h3>
              <p>待执行任务</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="status-card">
          <div class="status-item">
            <el-icon class="status-icon warning"><Warning /></el-icon>
            <div>
              <h3>{{ systemAlerts }}</h3>
              <p>系统警告</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="main-content">
      <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
        <el-card title="设备状态">
          <template #header>
            <div class="card-header">
              <span>设备状态</span>
              <el-button type="primary" size="small" @click="refreshDevices">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          
          <el-table :data="devices" style="width: 100%" size="small">
            <el-table-column prop="name" label="设备名称" min-width="120" />
            <el-table-column prop="type" label="类型" min-width="80" />
            <el-table-column prop="status" label="状态" min-width="80">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.status === 'online' ? 'success' : 'danger'"
                  size="small"
                >
                  {{ scope.row.status === 'online' ? '在线' : '离线' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_heartbeat" label="最后心跳" min-width="150" />
            <el-table-column label="操作" min-width="80">
              <template #default="scope">
                <el-button 
                  v-if="scope.row.status === 'offline'"
                  type="success" 
                  size="small"
                  @click="connectDevice(scope.row.id)"
                >
                  连接
                </el-button>
                <el-button 
                  v-else
                  type="danger" 
                  size="small"
                  @click="disconnectDevice(scope.row.id)"
                >
                  断开
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <el-card title="最近任务">
          <template #header>
            <div class="card-header">
              <span>最近任务</span>
              <el-button type="primary" size="small" @click="$router.push('/tasks')">
                查看全部
              </el-button>
            </div>
          </template>
          
          <div class="recent-tasks">
            <div 
              v-for="task in recentTasks" 
              :key="task.id" 
              class="task-item"
            >
              <div class="task-info">
                <h4>{{ task.name }}</h4>
                <p>{{ task.description }}</p>
              </div>
              <el-tag 
                :type="getTaskTagType(task.status)"
                size="small"
              >
                {{ getTaskStatusText(task.status) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Connection, 
  VideoPlay, 
  Clock, 
  Warning, 
  Refresh 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 类型定义
interface Device {
  id: string
  name: string
  type: string
  status: 'online' | 'offline'
  last_heartbeat: string
}

interface Task {
  id: string
  name: string
  description: string
  status: 'running' | 'completed' | 'pending' | 'failed'
}

// 模拟数据
const onlineDevices = ref(2)
const runningTasks = ref(1)
const pendingTasks = ref(3)
const systemAlerts = ref(0)

const devices = ref<Device[]>([
  {
    id: '1',
    name: 'FR3右臂',
    type: '机械臂',
    status: 'online',
    last_heartbeat: '2025-07-18 15:30:25'
  },
  {
    id: '2',
    name: 'Hermes底盘',
    type: '移动底盘',
    status: 'online',
    last_heartbeat: '2025-07-18 15:30:20'
  },
  {
    id: '3',
    name: 'FR3左臂',
    type: '机械臂',
    status: 'offline',
    last_heartbeat: '2025-07-18 14:25:10'
  }
])

const recentTasks = ref<Task[]>([
  {
    id: '1',
    name: '抓取任务A',
    description: '抓取目标物体至指定位置',
    status: 'running'
  },
  {
    id: '2',
    name: '导航任务B',
    description: '移动至目标点位',
    status: 'completed'
  },
  {
    id: '3',
    name: '复合任务C',
    description: '多设备协同作业',
    status: 'pending'
  }
])

const refreshDevices = () => {
  ElMessage.success('设备状态已刷新')
  // 这里将来连接真实API
}

const connectDevice = (deviceId: string) => {
  ElMessage.success(`正在连接设备 ${deviceId}`)
  // 这里将来连接真实API
}

const disconnectDevice = (deviceId: string) => {
  ElMessage.warning(`已断开设备 ${deviceId}`)
  // 这里将来连接真实API
}

const getTaskTagType = (status: Task['status']) => {
  switch (status) {
    case 'running': return 'warning'
    case 'completed': return 'success'
    case 'pending': return 'info'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getTaskStatusText = (status: Task['status']) => {
  switch (status) {
    case 'running': return '运行中'
    case 'completed': return '已完成'
    case 'pending': return '等待中'
    case 'failed': return '失败'
    default: return '未知'
  }
}

onMounted(() => {
  // 初始化数据加载
  refreshDevices()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.dashboard-header p {
  margin: 0;
  color: #909399;
}

.status-cards {
  margin-bottom: 30px;
}

.status-card {
  border-radius: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-icon {
  font-size: 32px;
  padding: 12px;
  border-radius: 50%;
  color: white;
  flex-shrink: 0;
}

.status-icon.online {
  background-color: #67c23a;
}

.status-icon.running {
  background-color: #409eff;
}

.status-icon.pending {
  background-color: #e6a23c;
}

.status-icon.warning {
  background-color: #f56c6c;
}

.status-item h3 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
}

.status-item p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.main-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.recent-tasks {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background-color: #fafafa;
  gap: 10px;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  word-wrap: break-word;
}

.task-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  word-wrap: break-word;
}

/* 平板端样式 */
@media (min-width: 768px) and (max-width: 1023px) {
  .dashboard {
    padding: 15px;
  }
  
  .dashboard-header h2 {
    font-size: 22px;
  }
  
  .status-icon {
    font-size: 28px;
    padding: 10px;
  }
  
  .status-item h3 {
    font-size: 20px;
  }
  
  .main-content {
    margin-top: 15px;
  }
}

/* 移动端样式 */
@media (max-width: 767px) {
  .dashboard {
    padding: 10px;
  }
  
  .dashboard-header {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .dashboard-header h2 {
    font-size: 20px;
  }
  
  .dashboard-header p {
    font-size: 14px;
  }
  
  .status-cards {
    margin-bottom: 20px;
  }
  
  .status-card {
    min-height: 80px;
  }
  
  .status-item {
    gap: 10px;
  }
  
  .status-icon {
    font-size: 24px;
    padding: 8px;
  }
  
  .status-item h3 {
    font-size: 18px;
  }
  
  .status-item p {
    font-size: 12px;
  }
  
  .main-content {
    margin-top: 15px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .task-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }
  
  .task-info h4 {
    font-size: 13px;
  }
  
  .task-info p {
    font-size: 11px;
  }
}

/* 超小屏幕样式 */
@media (max-width: 480px) {
  .dashboard {
    padding: 8px;
  }
  
  .dashboard-header h2 {
    font-size: 18px;
  }
  
  .dashboard-header p {
    font-size: 13px;
  }
  
  .status-item {
    gap: 8px;
  }
  
  .status-icon {
    font-size: 20px;
    padding: 6px;
  }
  
  .status-item h3 {
    font-size: 16px;
  }
  
  .status-item p {
    font-size: 11px;
  }
}
</style>