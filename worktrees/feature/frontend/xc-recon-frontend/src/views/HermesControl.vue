<template>
  <div class="hermes-control">
    <div class="page-header">
      <h2>Hermes 底盘控制</h2>
      <p>控制和监控 Hermes 移动底盘</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card title="移动控制">
          <div class="joystick-container">
            <div class="joystick">
              <div class="joystick-center">摇杆控制</div>
            </div>
          </div>
          
          <el-divider />
          
          <div class="speed-control">
            <h4>速度设置</h4>
            <el-form label-width="80px">
              <el-form-item label="线速度">
                <el-slider v-model="speedSettings.linear" :max="2" :step="0.1" show-input />
              </el-form-item>
              <el-form-item label="角速度">
                <el-slider v-model="speedSettings.angular" :max="2" :step="0.1" show-input />
              </el-form-item>
            </el-form>
          </div>
          
          <el-divider />
          
          <div class="direction-control">
            <h4>方向控制</h4>
            <div class="direction-buttons">
              <el-button @click="move('forward')">前进</el-button>
              <el-button @click="move('backward')">后退</el-button>
              <el-button @click="move('left')">左转</el-button>
              <el-button @click="move('right')">右转</el-button>
              <el-button type="danger" @click="stop()">停止</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card title="状态监控">
          <div class="status-grid">
            <div class="status-item">
              <h4>连接状态</h4>
              <el-tag :type="chassisStatus.connected ? 'success' : 'danger'">
                {{ chassisStatus.connected ? '已连接' : '未连接' }}
              </el-tag>
            </div>
            <div class="status-item">
              <h4>电池电量</h4>
              <el-progress :percentage="chassisStatus.battery" :color="getBatteryColor()" />
            </div>
            <div class="status-item">
              <h4>移动状态</h4>
              <el-tag :type="chassisStatus.moving ? 'warning' : 'success'">
                {{ chassisStatus.moving ? '移动中' : '静止' }}
              </el-tag>
            </div>
          </div>
          
          <el-divider />
          
          <div class="position-info">
            <h4>位置信息</h4>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="X坐标">{{ chassisStatus.position.x.toFixed(3) }} m</el-descriptions-item>
              <el-descriptions-item label="Y坐标">{{ chassisStatus.position.y.toFixed(3) }} m</el-descriptions-item>
              <el-descriptions-item label="朝向角度">{{ chassisStatus.position.theta.toFixed(3) }} rad</el-descriptions-item>
              <el-descriptions-item label="线速度">{{ chassisStatus.velocity.linear.toFixed(3) }} m/s</el-descriptions-item>
              <el-descriptions-item label="角速度">{{ chassisStatus.velocity.angular.toFixed(3) }} rad/s</el-descriptions-item>
            </el-descriptions>
          </div>
          
          <el-divider />
          
          <div class="navigation-control">
            <h4>导航控制</h4>
            <el-form :model="targetGoal" label-width="80px" inline>
              <el-form-item label="目标X">
                <el-input-number v-model="targetGoal.x" :precision="2" :step="0.1" size="small" />
              </el-form-item>
              <el-form-item label="目标Y">
                <el-input-number v-model="targetGoal.y" :precision="2" :step="0.1" size="small" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="navigateToGoal">导航到目标</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const speedSettings = reactive({
  linear: 0.5,
  angular: 0.5
})

const targetGoal = reactive({
  x: 1.0,
  y: 1.0
})

const chassisStatus = ref({
  connected: true,
  battery: 85,
  moving: false,
  position: { x: 0.0, y: 0.0, theta: 0.0 },
  velocity: { linear: 0.0, angular: 0.0 }
})

const getBatteryColor = () => {
  const battery = chassisStatus.value.battery
  if (battery > 60) return '#67c23a'
  if (battery > 30) return '#e6a23c'
  return '#f56c6c'
}

const move = (direction: string) => {
  chassisStatus.value.moving = true
  
  switch (direction) {
    case 'forward':
      chassisStatus.value.velocity.linear = speedSettings.linear
      chassisStatus.value.velocity.angular = 0
      break
    case 'backward':
      chassisStatus.value.velocity.linear = -speedSettings.linear
      chassisStatus.value.velocity.angular = 0
      break
    case 'left':
      chassisStatus.value.velocity.linear = 0
      chassisStatus.value.velocity.angular = speedSettings.angular
      break
    case 'right':
      chassisStatus.value.velocity.linear = 0
      chassisStatus.value.velocity.angular = -speedSettings.angular
      break
  }
  
  ElMessage.success(`开始${direction === 'forward' ? '前进' : direction === 'backward' ? '后退' : direction === 'left' ? '左转' : '右转'}`)
  
  // 模拟移动后停止
  setTimeout(() => {
    stop()
  }, 2000)
}

const stop = () => {
  chassisStatus.value.moving = false
  chassisStatus.value.velocity.linear = 0
  chassisStatus.value.velocity.angular = 0
  ElMessage.info('已停止移动')
}

const navigateToGoal = () => {
  if (!chassisStatus.value.connected) {
    ElMessage.warning('底盘未连接')
    return
  }
  
  chassisStatus.value.moving = true
  ElMessage.success(`开始导航到目标位置 (${targetGoal.x}, ${targetGoal.y})`)
  
  // 模拟导航过程
  setTimeout(() => {
    chassisStatus.value.position.x = targetGoal.x
    chassisStatus.value.position.y = targetGoal.y
    chassisStatus.value.moving = false
    ElMessage.success('导航完成，已到达目标位置')
  }, 3000)
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

.joystick-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.joystick {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 3px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  cursor: pointer;
  user-select: none;
}

.joystick-center {
  font-size: 12px;
  color: #666;
}

.speed-control h4,
.direction-control h4 {
  margin: 0 0 15px 0;
}

.direction-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.direction-buttons .el-button:nth-child(1) {
  grid-column: 2;
}

.direction-buttons .el-button:nth-child(2) {
  grid-column: 2;
}

.direction-buttons .el-button:nth-child(3) {
  grid-column: 1;
  grid-row: 2;
}

.direction-buttons .el-button:nth-child(4) {
  grid-column: 3;
  grid-row: 2;
}

.direction-buttons .el-button:nth-child(5) {
  grid-column: 1 / 4;
  grid-row: 3;
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

.position-info h4,
.navigation-control h4 {
  margin: 0 0 15px 0;
}
</style>