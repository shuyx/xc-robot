<template>
  <div class="fr3-control">
    <div class="page-header">
      <h2>FR3 机械臂控制</h2>
      <p>控制和监控 FR3 机械臂</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card title="控制面板">
          <div class="control-panel">
            <el-button type="success" size="large" @click="enableArm">
              <el-icon><VideoPlay /></el-icon>
              使能
            </el-button>
            <el-button type="warning" size="large" @click="disableArm">
              <el-icon><VideoPause /></el-icon>
              去使能
            </el-button>
            <el-button type="danger" size="large" @click="stopArm">
              <el-icon><CircleClose /></el-icon>
              急停
            </el-button>
          </div>
          
          <el-divider />
          
          <div class="movement-control">
            <h4>位置控制</h4>
            <el-form :model="targetPosition" label-width="60px">
              <el-form-item label="X轴">
                <el-input-number v-model="targetPosition.x" :precision="3" :step="0.01" size="small" />
              </el-form-item>
              <el-form-item label="Y轴">
                <el-input-number v-model="targetPosition.y" :precision="3" :step="0.01" size="small" />
              </el-form-item>
              <el-form-item label="Z轴">
                <el-input-number v-model="targetPosition.z" :precision="3" :step="0.01" size="small" />
              </el-form-item>
            </el-form>
            <el-button type="primary" @click="moveToPosition">移动到目标位置</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card title="状态监控">
          <div class="status-grid">
            <div class="status-item">
              <h4>连接状态</h4>
              <el-tag :type="armStatus.connected ? 'success' : 'danger'">
                {{ armStatus.connected ? '已连接' : '未连接' }}
              </el-tag>
            </div>
            <div class="status-item">
              <h4>使能状态</h4>
              <el-tag :type="armStatus.enabled ? 'success' : 'warning'">
                {{ armStatus.enabled ? '已使能' : '未使能' }}
              </el-tag>
            </div>
            <div class="status-item">
              <h4>工作模式</h4>
              <el-tag type="info">{{ armStatus.mode }}</el-tag>
            </div>
          </div>
          
          <el-divider />
          
          <div class="current-position">
            <h4>当前位置</h4>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="X轴">{{ armStatus.position.x.toFixed(3) }} m</el-descriptions-item>
              <el-descriptions-item label="Y轴">{{ armStatus.position.y.toFixed(3) }} m</el-descriptions-item>
              <el-descriptions-item label="Z轴">{{ armStatus.position.z.toFixed(3) }} m</el-descriptions-item>
              <el-descriptions-item label="RX">{{ armStatus.rotation.rx.toFixed(3) }} rad</el-descriptions-item>
              <el-descriptions-item label="RY">{{ armStatus.rotation.ry.toFixed(3) }} rad</el-descriptions-item>
              <el-descriptions-item label="RZ">{{ armStatus.rotation.rz.toFixed(3) }} rad</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { VideoPlay, VideoPause, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const targetPosition = reactive({
  x: 0.5,
  y: 0.2,
  z: 0.3
})

const armStatus = ref({
  connected: true,
  enabled: false,
  mode: '示教模式',
  position: { x: 0.512, y: 0.186, z: 0.324 },
  rotation: { rx: 3.142, ry: 0.001, rz: 0.785 }
})

const enableArm = () => {
  armStatus.value.enabled = true
  ElMessage.success('机械臂已使能')
}

const disableArm = () => {
  armStatus.value.enabled = false
  ElMessage.warning('机械臂已去使能')
}

const stopArm = () => {
  armStatus.value.enabled = false
  ElMessage.error('紧急停止已激活')
}

const moveToPosition = () => {
  if (!armStatus.value.enabled) {
    ElMessage.warning('请先使能机械臂')
    return
  }
  armStatus.value.position = { ...targetPosition }
  ElMessage.success('正在移动到目标位置')
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

.control-panel {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.movement-control h4 {
  margin: 0 0 15px 0;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.status-item h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.current-position h4 {
  margin: 0 0 15px 0;
}
</style>