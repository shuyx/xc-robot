<template>
  <div class="conversational-task-page">
    <el-row :gutter="20">
      <!-- 对话区域 -->
      <el-col :span="16">
        <el-card class="chat-card">
          <template #header>
            <div class="chat-header">
              <span class="header-icon">🎤</span>
              <span class="header-title">智能对话系统</span>
              <div class="chat-status">
                <el-tag :type="isListening ? 'success' : 'info'">
                  {{ isListening ? '正在聆听' : '待机中' }}
                </el-tag>
              </div>
            </div>
          </template>
          
          <!-- 对话消息列表 -->
          <div class="chat-messages" ref="chatContainer">
            <div 
              v-for="message in messages" 
              :key="message.id" 
              :class="['message', message.type]"
            >
              <div class="message-avatar">
                <el-avatar :size="36" :src="message.avatar">
                  {{ message.sender.charAt(0) }}
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-sender">{{ message.sender }}</span>
                  <span class="message-time">{{ message.timestamp }}</span>
                </div>
                <div class="message-text">{{ message.content }}</div>
                <div v-if="message.actions" class="message-actions">
                  <el-tag 
                    v-for="action in message.actions" 
                    :key="action"
                    size="small"
                    class="action-tag"
                  >
                    {{ action }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <!-- 正在输入指示器 -->
            <div v-if="isTyping" class="typing-indicator">
              <div class="typing-avatar">
                <el-avatar :size="36">🤖</el-avatar>
              </div>
              <div class="typing-content">
                <div class="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 输入区域 -->
          <div class="chat-input">
            <el-input
              v-model="currentMessage"
              placeholder="请输入指令或问题..."
              @keyup.enter="sendMessage"
              :disabled="isProcessing"
              size="large"
            >
              <template #prepend>
                <el-button 
                  :icon="isListening ? 'Microphone' : 'Microphone'"
                  :type="isListening ? 'success' : 'default'"
                  @click="toggleVoiceInput"
                >
                  {{ isListening ? '停止' : '语音' }}
                </el-button>
              </template>
              <template #append>
                <el-button 
                  type="primary" 
                  @click="sendMessage"
                  :loading="isProcessing"
                  :disabled="!currentMessage.trim()"
                >
                  发送
                </el-button>
              </template>
            </el-input>
          </div>
          
          <!-- 快捷指令 -->
          <div class="quick-commands">
            <span class="commands-label">快捷指令：</span>
            <el-button 
              v-for="command in quickCommands" 
              :key="command"
              size="small" 
              @click="selectQuickCommand(command)"
              class="command-btn"
            >
              {{ command }}
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <!-- 状态和控制面板 -->
      <el-col :span="8">
        <!-- 当前任务状态 -->
        <el-card class="status-card" shadow="never">
          <template #header>
            <span>🤖 当前任务</span>
          </template>
          
          <div class="current-task">
            <div class="task-name">{{ currentTask.name || '无执行任务' }}</div>
            <div class="task-description">{{ currentTask.description }}</div>
            <el-progress 
              v-if="currentTask.progress !== undefined"
              :percentage="currentTask.progress" 
              :status="currentTask.status"
            />
            <div class="task-actions" v-if="currentTask.name">
              <el-button size="small" type="warning" @click="pauseTask">暂停</el-button>
              <el-button size="small" type="danger" @click="cancelTask">取消</el-button>
            </div>
          </div>
        </el-card>
        
        <!-- 系统状态 -->
        <el-card class="system-status-card" shadow="never">
          <template #header>
            <span>📊 系统状态</span>
          </template>
          
          <div class="status-grid">
            <div class="status-item">
              <div class="status-label">语音识别</div>
              <el-tag :type="systemStatus.speech.type">{{ systemStatus.speech.status }}</el-tag>
            </div>
            <div class="status-item">
              <div class="status-label">自然语言理解</div>
              <el-tag :type="systemStatus.nlu.type">{{ systemStatus.nlu.status }}</el-tag>
            </div>
            <div class="status-item">
              <div class="status-label">任务执行引擎</div>
              <el-tag :type="systemStatus.execution.type">{{ systemStatus.execution.status }}</el-tag>
            </div>
            <div class="status-item">
              <div class="status-label">机器人连接</div>
              <el-tag :type="systemStatus.robot.type">{{ systemStatus.robot.status }}</el-tag>
            </div>
          </div>
        </el-card>
        
        <!-- 任务历史 -->
        <el-card class="history-card" shadow="never">
          <template #header>
            <span>📝 任务历史</span>
          </template>
          
          <el-timeline class="task-timeline">
            <el-timeline-item
              v-for="task in taskHistory"
              :key="task.id"
              :timestamp="task.timestamp"
              :type="task.type"
            >
              <div class="timeline-content">
                <div class="timeline-title">{{ task.title }}</div>
                <div class="timeline-description">{{ task.description }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 对话消息
const messages = ref([
  {
    id: 1,
    type: 'assistant',
    sender: '智能助手',
    content: '您好！我是XC-RECON机器人智能助手。我可以帮助您控制机器人、执行任务或回答问题。请告诉我您需要什么帮助？',
    timestamp: '15:30:00',
    avatar: '',
    actions: ['机械臂控制', '移动导航', '视觉识别']
  },
  {
    id: 2,
    type: 'user',
    sender: 'Kevin Yuan',
    content: '请移动机械臂到指定位置',
    timestamp: '15:30:15',
    avatar: ''
  },
  {
    id: 3,
    type: 'assistant',
    sender: '智能助手',
    content: '收到指令！我将为您规划机械臂运动路径。请指定目标位置坐标，或者您可以通过"示教模式"手动引导机械臂到目标位置。',
    timestamp: '15:30:18',
    avatar: '',
    actions: ['坐标输入', '示教模式', '预设位置']
  }
])

// 状态变量
const currentMessage = ref('')
const isListening = ref(false)
const isProcessing = ref(false)
const isTyping = ref(false)
const chatContainer = ref<HTMLElement>()

// 当前任务
const currentTask = ref({
  name: '机械臂位置调整',
  description: '正在规划从当前位置到目标位置的运动轨迹',
  progress: 75,
  status: 'success'
})

// 系统状态
const systemStatus = ref({
  speech: { status: '正常', type: 'success' },
  nlu: { status: '正常', type: 'success' },
  execution: { status: '运行中', type: 'warning' },
  robot: { status: '已连接', type: 'success' }
})

// 任务历史
const taskHistory = ref([
  {
    id: 1,
    title: '机械臂校准完成',
    description: '双臂机械臂校准成功，精度达标',
    timestamp: '15:25:00',
    type: 'success'
  },
  {
    id: 2,
    title: '抓取任务执行',
    description: '物体抓取任务执行完成，成功率98%',
    timestamp: '15:20:00',
    type: 'success'
  },
  {
    id: 3,
    title: '路径规划',
    description: '移动路径规划完成，避障算法优化',
    timestamp: '15:15:00',
    type: 'primary'
  },
  {
    id: 4,
    title: '系统初始化',
    description: '系统启动完成，所有模块正常运行',
    timestamp: '15:10:00',
    type: 'info'
  }
])

// 快捷指令
const quickCommands = ref([
  '移动机械臂',
  '开始导航',
  '拍照识别',
  '回到初始位置',
  '系统状态查询',
  '紧急停止'
])

// 发送消息
const sendMessage = async () => {
  if (!currentMessage.value.trim() || isProcessing.value) return
  
  const userMessage = {
    id: Date.now(),
    type: 'user',
    sender: 'Kevin Yuan',
    content: currentMessage.value,
    timestamp: new Date().toLocaleTimeString(),
    avatar: ''
  }
  
  messages.value.push(userMessage)
  const messageText = currentMessage.value
  currentMessage.value = ''
  isProcessing.value = true
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 显示正在输入指示器
  isTyping.value = true
  
  // 模拟AI处理和响应
  setTimeout(() => {
    isTyping.value = false
    const response = generateResponse(messageText)
    messages.value.push(response)
    isProcessing.value = false
    
    // 模拟任务更新
    updateCurrentTask(messageText)
    
    nextTick(() => {
      scrollToBottom()
    })
  }, 2000)
}

// 生成AI响应
const generateResponse = (userInput: string) => {
  const responses = {
    '移动机械臂': {
      content: '已接收机械臂控制指令。正在规划运动轨迹，请稍候...',
      actions: ['确认执行', '调整参数', '取消操作']
    },
    '导航': {
      content: '导航系统已激活。请选择目标位置或使用语音指定目的地。',
      actions: ['选择地点', '语音导航', '手动控制']
    },
    '拍照': {
      content: '相机系统已就绪。将进行物体识别和环境感知。',
      actions: ['开始拍照', '调整参数', '选择相机']
    },
    '状态': {
      content: '系统运行正常。所有硬件设备连接稳定，当前无异常报警。',
      actions: ['详细报告', '性能监控', '硬件检测']
    },
    '停止': {
      content: '收到紧急停止指令！所有运动已停止，系统进入安全模式。',
      actions: ['恢复运行', '系统检查', '重新初始化']
    }
  }
  
  // 简单的关键词匹配
  let responseData = responses['移动机械臂'] // 默认响应
  for (const [key, value] of Object.entries(responses)) {
    if (userInput.includes(key)) {
      responseData = value
      break
    }
  }
  
  return {
    id: Date.now(),
    type: 'assistant',
    sender: '智能助手',
    content: responseData.content,
    timestamp: new Date().toLocaleTimeString(),
    avatar: '',
    actions: responseData.actions
  }
}

// 更新当前任务
const updateCurrentTask = (userInput: string) => {
  if (userInput.includes('机械臂')) {
    currentTask.value = {
      name: '机械臂运动控制',
      description: '正在执行机械臂位置调整任务',
      progress: 0,
      status: 'success'
    }
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (currentTask.value.progress < 100) {
        currentTask.value.progress += 10
      } else {
        clearInterval(progressInterval)
        ElMessage.success('机械臂任务执行完成')
      }
    }, 500)
  }
}

// 切换语音输入
const toggleVoiceInput = () => {
  isListening.value = !isListening.value
  
  if (isListening.value) {
    ElMessage.info('正在监听语音输入...')
    // 模拟语音识别
    setTimeout(() => {
      if (isListening.value) {
        currentMessage.value = '请移动机械臂到桌子上方'
        isListening.value = false
        ElMessage.success('语音识别完成')
      }
    }, 3000)
  } else {
    ElMessage.info('语音输入已停止')
  }
}

// 选择快捷指令
const selectQuickCommand = (command: string) => {
  currentMessage.value = command
}

// 暂停任务
const pauseTask = () => {
  ElMessage.warning('任务已暂停')
  currentTask.value.status = 'warning'
}

// 取消任务
const cancelTask = () => {
  ElMessage.error('任务已取消')
  currentTask.value = {
    name: '',
    description: '无执行任务',
    progress: undefined,
    status: 'info'
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.conversational-task-page {
  padding: 20px;
}

.chat-card {
  height: 600px;
  display: flex;
  flex-direction: column;
}

.chat-header {
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

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  max-height: 400px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  text-align: right;
  background: #409eff;
  color: white;
}

.message-content {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 70%;
  flex: 1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-sender {
  font-weight: 500;
  font-size: 13px;
  color: #606266;
}

.message.user .message-sender {
  color: rgba(255, 255, 255, 0.9);
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.message-text {
  line-height: 1.5;
  margin-bottom: 8px;
}

.message-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.action-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-tag:hover {
  transform: translateY(-1px);
}

.typing-indicator {
  display: flex;
  gap: 12px;
  align-items: center;
}

.typing-content {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 12px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  margin: 20px 0;
}

.quick-commands {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px 0;
  border-top: 1px solid #ebeef5;
}

.commands-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.command-btn {
  font-size: 12px;
}

.status-card, .system-status-card, .history-card {
  margin-bottom: 20px;
}

.current-task {
  text-align: center;
}

.task-name {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.task-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 15px;
  line-height: 1.4;
}

.task-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 15px;
}

.status-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.status-label {
  font-size: 13px;
  color: #606266;
}

.task-timeline {
  max-height: 300px;
  overflow-y: auto;
}

.timeline-content {
  padding-left: 10px;
}

.timeline-title {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 4px;
}

.timeline-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .conversational-task-page {
    padding: 10px;
  }
  
  .chat-card {
    height: auto;
    min-height: 500px;
  }
  
  .chat-messages {
    max-height: 300px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .quick-commands {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .command-btn {
    margin: 2px;
  }
}
</style>