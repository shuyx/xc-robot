<template>
  <div class="task-create">
    <div class="page-header">
      <h2>创建任务</h2>
      <p>配置并创建新的系统任务</p>
    </div>

    <el-card>
      <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef" label-width="120px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="taskForm.type" placeholder="请选择任务类型" style="width: 100%">
            <el-option label="机械臂操作" value="arm_operation" />
            <el-option label="底盘移动" value="chassis_movement" />
            <el-option label="多设备协同" value="multi_device" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="taskForm.description" type="textarea" rows="3" placeholder="请输入任务描述" />
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="taskForm.priority">
            <el-radio value="low">低</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="high">高</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="执行时间" prop="execution_time">
          <el-radio-group v-model="taskForm.execution_time">
            <el-radio value="immediate">立即执行</el-radio>
            <el-radio value="scheduled">定时执行</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="taskForm.execution_time === 'scheduled'" label="计划时间" prop="scheduled_time">
          <el-date-picker
            v-model="taskForm.scheduled_time"
            type="datetime"
            placeholder="选择执行时间"
            format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-divider content-position="left">任务配置</el-divider>
        
        <!-- 机械臂操作配置 -->
        <div v-if="taskForm.type === 'arm_operation'">
          <el-form-item label="操作类型">
            <el-select v-model="taskForm.config.operation" placeholder="选择操作类型">
              <el-option label="移动到位置" value="move_to_position" />
              <el-option label="抓取物体" value="grasp_object" />
              <el-option label="释放物体" value="release_object" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="目标位置" v-if="taskForm.config.operation === 'move_to_position'">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-input-number v-model="taskForm.config.position.x" placeholder="X" :precision="3" style="width: 100%" />
              </el-col>
              <el-col :span="8">
                <el-input-number v-model="taskForm.config.position.y" placeholder="Y" :precision="3" style="width: 100%" />
              </el-col>
              <el-col :span="8">
                <el-input-number v-model="taskForm.config.position.z" placeholder="Z" :precision="3" style="width: 100%" />
              </el-col>
            </el-row>
          </el-form-item>
        </div>
        
        <!-- 底盘移动配置 -->
        <div v-if="taskForm.type === 'chassis_movement'">
          <el-form-item label="移动类型">
            <el-select v-model="taskForm.config.movement" placeholder="选择移动类型">
              <el-option label="导航到位置" value="navigate_to_position" />
              <el-option label="相对移动" value="relative_move" />
              <el-option label="巡航路径" value="patrol_path" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="目标位置" v-if="taskForm.config.movement === 'navigate_to_position'">
            <el-row :gutter="10">
              <el-col :span="12">
                <el-input-number v-model="taskForm.config.target.x" placeholder="X坐标" :precision="2" style="width: 100%" />
              </el-col>
              <el-col :span="12">
                <el-input-number v-model="taskForm.config.target.y" placeholder="Y坐标" :precision="2" style="width: 100%" />
              </el-col>
            </el-row>
          </el-form-item>
        </div>
        
        <el-form-item>
          <el-button type="primary" @click="createTask" :loading="creating">创建任务</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="$router.push('/tasks')">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const creating = ref(false)
const taskFormRef = ref<FormInstance>()

const taskForm = reactive({
  name: '',
  type: '',
  description: '',
  priority: 'medium',
  execution_time: 'immediate',
  scheduled_time: null,
  config: {
    operation: '',
    position: { x: 0, y: 0, z: 0 },
    movement: '',
    target: { x: 0, y: 0 }
  }
})

const taskRules: FormRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入任务描述', trigger: 'blur' }
  ]
}

const createTask = async () => {
  if (!taskFormRef.value) return

  try {
    await taskFormRef.value.validate()
    creating.value = true
    
    // 模拟创建任务API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    ElMessage.success('任务创建成功')
    router.push('/tasks')
  } catch (error) {
    // 表单验证失败
  } finally {
    creating.value = false
  }
}

const resetForm = () => {
  if (taskFormRef.value) {
    taskFormRef.value.resetFields()
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
</style>