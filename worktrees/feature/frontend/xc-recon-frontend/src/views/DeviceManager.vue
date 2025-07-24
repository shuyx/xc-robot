<template>
  <div class="device-manager">
    <div class="page-header">
      <h2>设备管理</h2>
      <p>管理和监控所有连接的设备</p>
    </div>

    <el-card class="device-list">
      <template #header>
        <div class="card-header">
          <span>设备列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="refreshDevices">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="success" @click="showAddDevice = true">
              <el-icon><Plus /></el-icon>
              添加设备
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="devices" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="设备名称" width="180" />
        <el-table-column prop="type" label="设备类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === '机械臂' ? 'primary' : 'warning'">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP地址" width="150" />
        <el-table-column prop="port" label="端口" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag 
              :type="getStatusType(scope.row.status)"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_heartbeat" label="最后心跳" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'offline'"
              type="success" 
              size="small"
              @click="connectDevice(scope.row.id)"
              :loading="scope.row.connecting"
            >
              连接
            </el-button>
            <el-button 
              v-else
              type="danger" 
              size="small"
              @click="disconnectDevice(scope.row.id)"
              :loading="scope.row.disconnecting"
            >
              断开
            </el-button>
            <el-button 
              type="primary" 
              size="small"
              @click="openDeviceControl(scope.row)"
            >
              控制
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加设备对话框 -->
    <el-dialog
      v-model="showAddDevice"
      title="添加设备"
      width="500px"
    >
      <el-form :model="newDevice" :rules="deviceRules" ref="deviceForm" label-width="100px">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="newDevice.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型" prop="type">
          <el-select v-model="newDevice.type" placeholder="请选择设备类型" style="width: 100%">
            <el-option label="机械臂" value="robotic_arm" />
            <el-option label="移动底盘" value="mobile_base" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP地址" prop="ip">
          <el-input v-model="newDevice.ip" placeholder="请输入IP地址" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="newDevice.port" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="newDevice.description" type="textarea" placeholder="设备描述（可选）" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDevice = false">取消</el-button>
        <el-button type="primary" @click="addDevice" :loading="adding">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Refresh, 
  Plus 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()

const loading = ref(false)
const showAddDevice = ref(false)
const adding = ref(false)
const deviceForm = ref<FormInstance>()

// 模拟设备数据
const devices = ref([
  {
    id: '1',
    name: 'FR3右臂',
    type: '机械臂',
    ip: '192.168.58.2',
    port: 20003,
    status: 'online',
    last_heartbeat: '2025-07-18 15:30:25',
    connecting: false,
    disconnecting: false
  },
  {
    id: '2',
    name: 'Hermes底盘',
    type: '移动底盘',
    ip: '192.168.31.211',
    port: 1448,
    status: 'online',
    last_heartbeat: '2025-07-18 15:30:20',
    connecting: false,
    disconnecting: false
  },
  {
    id: '3',
    name: 'FR3左臂',
    type: '机械臂',
    ip: '192.168.58.3',
    port: 20003,
    status: 'offline',
    last_heartbeat: '2025-07-18 14:25:10',
    connecting: false,
    disconnecting: false
  }
])

const newDevice = reactive({
  name: '',
  type: '',
  ip: '',
  port: 20003,
  description: ''
})

const deviceRules: FormRules = {
  name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择设备类型', trigger: 'change' }
  ],
  ip: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: 'IP地址格式不正确', trigger: 'blur' }
  ],
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' }
  ]
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'online': return 'success'
    case 'offline': return 'danger'
    case 'connecting': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'online': return '在线'
    case 'offline': return '离线'
    case 'connecting': return '连接中'
    default: return '未知'
  }
}

const refreshDevices = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('设备状态已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const connectDevice = async (deviceId: string) => {
  const device = devices.value.find(d => d.id === deviceId)
  if (!device) return

  device.connecting = true
  try {
    // 模拟连接API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    device.status = 'online'
    device.last_heartbeat = new Date().toLocaleString()
    ElMessage.success(`设备 ${device.name} 连接成功`)
  } catch (error) {
    ElMessage.error(`设备 ${device.name} 连接失败`)
  } finally {
    device.connecting = false
  }
}

const disconnectDevice = async (deviceId: string) => {
  const device = devices.value.find(d => d.id === deviceId)
  if (!device) return

  try {
    await ElMessageBox.confirm(
      `确定要断开设备 ${device.name} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    device.disconnecting = true
    // 模拟断开API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    device.status = 'offline'
    ElMessage.success(`设备 ${device.name} 已断开`)
  } catch {
    // 用户取消操作
  } finally {
    device.disconnecting = false
  }
}

const openDeviceControl = (device: any) => {
  if (device.type === '机械臂') {
    router.push('/devices/fr3')
  } else if (device.type === '移动底盘') {
    router.push('/devices/hermes')
  }
  ElMessage.info(`正在打开 ${device.name} 控制界面`)
}

const addDevice = async () => {
  if (!deviceForm.value) return

  try {
    await deviceForm.value.validate()
    adding.value = true
    
    // 模拟添加设备API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const id = (devices.value.length + 1).toString()
    devices.value.push({
      id,
      name: newDevice.name,
      type: newDevice.type === 'robotic_arm' ? '机械臂' : '移动底盘',
      ip: newDevice.ip,
      port: newDevice.port,
      status: 'offline',
      last_heartbeat: '从未连接',
      connecting: false,
      disconnecting: false
    })

    ElMessage.success('设备添加成功')
    showAddDevice.value = false
    
    // 重置表单
    Object.assign(newDevice, {
      name: '',
      type: '',
      ip: '',
      port: 20003,
      description: ''
    })
  } catch (error) {
    // 表单验证失败或其他错误
  } finally {
    adding.value = false
  }
}

onMounted(() => {
  refreshDevices()
})
</script>

<style scoped>
.device-manager {
  padding: 20px;
}

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

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 平板端样式 */
@media (min-width: 768px) and (max-width: 1023px) {
  .device-manager {
    padding: 15px;
  }
  
  .page-header h2 {
    font-size: 22px;
  }
  
  .header-actions {
    gap: 8px;
  }
}

/* 移动端样式 */
@media (max-width: 767px) {
  .device-manager {
    padding: 10px;
  }
  
  .page-header {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .page-header h2 {
    font-size: 20px;
  }
  
  .page-header p {
    font-size: 14px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
    gap: 8px;
  }
  
  /* 表格在移动端的优化 */
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-table .cell) {
    padding: 8px 4px;
    word-break: break-word;
  }
  
  :deep(.el-button--small) {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  :deep(.el-tag--small) {
    padding: 2px 6px;
    font-size: 10px;
  }
}

/* 超小屏幕样式 */
@media (max-width: 480px) {
  .device-manager {
    padding: 8px;
  }
  
  .page-header h2 {
    font-size: 18px;
  }
  
  .page-header p {
    font-size: 13px;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .header-actions .el-button {
    width: 100%;
    justify-content: center;
  }
  
  /* 隐藏一些不重要的列以节省空间 */
  :deep(.el-table__header-wrapper),
  :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
}
</style>