<template>
  <div class="smart-interaction-page">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="header-icon">🤝</span>
          <span class="header-title">智能交互系统</span>
          <el-button type="primary" size="small">系统状态</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8" v-for="module in interactionModules" :key="module.id">
          <el-card class="module-card" shadow="hover" @click="navigateToModule(module.path)">
            <div class="module-content">
              <div class="module-icon">{{ module.icon }}</div>
              <h3 class="module-title">{{ module.title }}</h3>
              <p class="module-description">{{ module.description }}</p>
              <div class="module-status">
                <el-tag :type="module.status.type">{{ module.status.text }}</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6" v-for="stat in systemStats" :key="stat.label">
          <div class="stat-item">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 智能交互模块配置
const interactionModules = ref([
  {
    id: 'face-recognition',
    icon: '👤',
    title: '人脸识别',
    description: '基于深度学习的人脸识别系统，支持实时检测和身份验证',
    path: '/interaction/face',
    status: { type: 'success', text: '运行中' }
  },
  {
    id: 'conversational-task',
    icon: '🎤',
    title: '智能对话',
    description: '自然语言理解和任务执行，支持语音交互和指令识别',
    path: '/interaction/chat',
    status: { type: 'success', text: '就绪' }
  },
  {
    id: 'elevator-control',
    icon: '🏢',
    title: '梯控系统',
    description: '智能电梯控制系统，支持楼层调度和智能导航',
    path: '/interaction/elevator',
    status: { type: 'warning', text: '待连接' }
  }
])

// 系统统计数据
const systemStats = ref([
  { label: '识别准确率', value: '95.8%' },
  { label: '响应时间', value: '0.3s' },
  { label: '今日交互次数', value: '156' },
  { label: '系统正常运行时间', value: '99.2%' }
])

const navigateToModule = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.smart-interaction-page {
  padding: 20px;
}

.main-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.module-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 10px;
  margin-bottom: 20px;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.module-content {
  text-align: center;
  padding: 20px 10px;
}

.module-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.module-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.module-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 15px;
  min-height: 42px;
}

.module-status {
  margin-top: 10px;
}

.stats-row {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.stat-item {
  text-align: center;
  padding: 15px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .smart-interaction-page {
    padding: 10px;
  }
  
  .module-content {
    padding: 15px 5px;
  }
  
  .module-icon {
    font-size: 36px;
  }
  
  .module-title {
    font-size: 16px;
  }
  
  .module-description {
    font-size: 13px;
    min-height: 39px;
  }
  
  .stat-value {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .stat-item {
    padding: 10px 5px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 11px;
  }
}
</style>