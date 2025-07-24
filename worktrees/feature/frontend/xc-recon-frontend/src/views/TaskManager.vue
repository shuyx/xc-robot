<template>
  <div class="task-manager">
    <div class="page-header">
      <h2>任务管理</h2>
      <p>创建、管理和监控系统任务</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <el-button type="primary" @click="$router.push('/tasks/create')">
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </div>
      </template>
      
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="name" label="任务名称" width="200" />
        <el-table-column prop="type" label="任务类型" width="150">
          <template #default="scope">
            <el-tag :type="getTaskTypeColor(scope.row.type)">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" :status="getProgressStatus(scope.row.status)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'pending'"
              type="success" 
              size="small"
              @click="startTask(scope.row.id)"
            >
              启动
            </el-button>
            <el-button 
              v-if="scope.row.status === 'running'"
              type="warning" 
              size="small"
              @click="pauseTask(scope.row.id)"
            >
              暂停
            </el-button>
            <el-button 
              type="danger" 
              size="small"
              @click="deleteTask(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const tasks = ref([
  {
    id: '1',
    name: '抓取任务A',
    type: '机械臂操作',
    status: 'running',
    progress: 65,
    created_at: '2025-07-18 14:30:00'
  },
  {
    id: '2',
    name: '导航任务B',
    type: '底盘移动',
    status: 'completed',
    progress: 100,
    created_at: '2025-07-18 13:15:00'
  },
  {
    id: '3',
    name: '复合任务C',
    type: '多设备协同',
    status: 'pending',
    progress: 0,
    created_at: '2025-07-18 15:00:00'
  }
])

const getTaskTypeColor = (type: string) => {
  switch (type) {
    case '机械臂操作': return 'primary'
    case '底盘移动': return 'warning'
    case '多设备协同': return 'success'
    default: return 'info'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'running': return 'warning'
    case 'completed': return 'success'
    case 'pending': return 'info'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'running': return '运行中'
    case 'completed': return '已完成'
    case 'pending': return '等待中'
    case 'failed': return '失败'
    default: return '未知'
  }
}

const getProgressStatus = (status: string) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

const startTask = (taskId: string) => {
  const task = tasks.value.find(t => t.id === taskId)
  if (task) {
    task.status = 'running'
    ElMessage.success(`任务 ${task.name} 已启动`)
  }
}

const pauseTask = (taskId: string) => {
  const task = tasks.value.find(t => t.id === taskId)
  if (task) {
    task.status = 'pending'
    ElMessage.warning(`任务 ${task.name} 已暂停`)
  }
}

const deleteTask = (taskId: string) => {
  const index = tasks.value.findIndex(t => t.id === taskId)
  if (index > -1) {
    const taskName = tasks.value[index].name
    tasks.value.splice(index, 1)
    ElMessage.error(`任务 ${taskName} 已删除`)
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>