<template>
  <div id="main-content" class="w-full h-[calc(100vh-100px)] overflow-hidden flex flex-col">
    <!-- Header Section -->
    <div id="page-header" class="px-6 py-4">
      <div class="flex items-center">
        <div class="bg-primary/10 p-2 rounded-lg mr-3">
          <i class="fa-solid fa-comments text-primary text-xl"></i>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-secondary">智能对话任务系统</h1>
          <p class="text-gray-600 text-sm">自然语言交互的任务理解与执行</p>
        </div>
      </div>
    </div>

    <!-- Chat Section -->
    <div id="chat-container" class="flex-1 flex flex-col p-4 gap-4 overflow-hidden">
      <!-- Chat History Area -->
      <div id="chat-history" ref="chatHistory" class="flex-1 bg-chatBg rounded-xl p-4 overflow-y-auto">
        <!-- Initial Bot Messages -->
        <div 
          v-for="message in chatMessages" 
          :key="message.id"
          class="mb-6"
        >
          <!-- Bot Message -->
          <div v-if="message.type === 'bot'" class="flex items-start">
            <div class="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center mr-2 flex-shrink-0">
              <i class="fa-solid fa-robot"></i>
            </div>
            <div class="flex-1">
              <div class="bg-botBubble p-3 rounded-lg rounded-tl-none mb-1">
                <p class="text-secondary" v-if="!message.taskInfo">{{ message.content }}</p>
                <div v-if="message.taskInfo">
                  <p class="text-secondary mb-3">{{ message.content }}</p>
                  <div class="border-t border-gray-200 pt-2">
                    <div class="flex items-center text-sm mb-1">
                      <i class="fa-solid fa-bullseye text-primary mr-2"></i>
                      <span class="font-medium">执行任务: {{ message.taskInfo.title }}</span>
                    </div>
                    <div class="flex items-center text-sm mb-1">
                      <i class="fa-solid fa-chart-line text-warning mr-2"></i>
                      <span>当前状态: {{ message.taskInfo.status }}</span>
                    </div>
                    <div class="flex items-center text-sm">
                      <i class="fa-solid fa-check-circle text-success mr-2"></i>
                      <span>任务完成: {{ message.taskInfo.result }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="message.fileInfo">
                  <p class="text-secondary mb-3">{{ message.content }}</p>
                  <div class="border-t border-gray-200 pt-2">
                    <div class="flex items-center text-sm">
                      <i class="fa-solid fa-camera text-success mr-2"></i>
                      <span>{{ message.fileInfo.message }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="flex justify-end text-xs text-gray-500">
                <span class="mr-2">{{ message.time }}</span>
                <button 
                  @click="toggleFavorite(message.id)"
                  :class="[
                    'hover:text-primary',
                    message.isFavorite ? 'text-primary' : 'text-gray-400'
                  ]"
                >
                  <i :class="message.isFavorite ? 'fa-solid fa-star' : 'fa-regular fa-star'"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- User Message -->
          <div v-else class="flex justify-end">
            <div class="max-w-[80%]">
              <div class="bg-userBubble p-3 rounded-lg rounded-tr-none mb-1">
                <p class="text-secondary">{{ message.content }}</p>
              </div>
              <div class="text-xs text-gray-500 text-right">{{ message.time }}</div>
            </div>
            <div class="bg-secondary text-white rounded-full w-8 h-8 flex items-center justify-center ml-2 flex-shrink-0">
              <i class="fa-solid fa-user"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div id="input-area" class="bg-white rounded-xl border border-gray-200 p-3">
        <div class="flex items-center">
          <input 
            v-model="inputMessage"
            @keypress.enter="sendMessage"
            type="text" 
            class="flex-1 border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" 
            :placeholder="isListening ? '正在听您说话...' : '请输入您的指令...'"
          >
          <button 
            @click="toggleVoiceRecognition"
            :class="[
              'ml-2 rounded-full w-10 h-10 flex items-center justify-center transition-colors',
              isListening ? 'bg-primary text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
            ]"
          >
            <i class="fa-solid fa-microphone"></i>
          </button>
          <button 
            @click="sendMessage"
            class="ml-2 bg-primary hover:bg-primary/90 text-white rounded-lg px-4 py-2 flex items-center justify-center transition-colors"
          >
            <i class="fa-solid fa-paper-plane mr-1"></i>
            发送
          </button>
        </div>
      </div>

      <!-- Quick Commands and Status -->
      <div id="commands-status" class="grid grid-cols-5 gap-4">
        <div id="quick-commands" class="col-span-4">
          <div class="mb-2">
            <h3 class="text-sm font-medium flex items-center">
              <i class="fa-solid fa-bullseye text-primary mr-1"></i>
              快捷指令
            </h3>
          </div>
          <div class="grid grid-cols-3 gap-2 md:grid-cols-6">
            <button 
              v-for="command in quickCommands" 
              :key="command.id"
              @click="executeQuickCommand(command.text)"
              class="bg-gray-100 hover:bg-gray-200 text-secondary rounded-lg py-2 px-3 text-sm flex items-center justify-center transition-colors"
            >
              <i :class="command.icon + ' text-primary mr-1'"></i>
              {{ command.text }}
            </button>
          </div>
        </div>
        
        <div id="status-panel" class="col-span-1">
          <div class="mb-2">
            <h3 class="text-sm font-medium flex items-center">
              <i class="fa-solid fa-chart-line text-primary mr-1"></i>
              对话状态
            </h3>
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-2">
            <div class="flex items-center mb-1 text-sm">
              <div :class="[
                'w-3 h-3 rounded-full mr-2',
                systemStatus.online ? 'bg-success' : 'bg-danger'
              ]"></div>
              <span>{{ systemStatus.online ? '在线' : '离线' }}</span>
            </div>
            <div class="flex items-center mb-1 text-sm">
              <i :class="[
                'fa-solid fa-microphone mr-2 w-3',
                systemStatus.listening ? 'text-primary' : 'text-gray-400'
              ]"></i>
              <span>{{ systemStatus.listening ? '监听中' : '未监听' }}</span>
            </div>
            <div class="flex items-center text-sm">
              <i :class="[
                'fa-solid fa-comment-dots mr-2 w-3',
                systemStatus.processing ? 'text-warning' : 'text-primary'
              ]"></i>
              <span>{{ systemStatus.processing ? '处理中' : '等待指令' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 消息类型定义
interface ChatMessage {
  id: number
  type: 'user' | 'bot'
  content: string
  time: string
  isFavorite: boolean
  taskInfo?: {
    title: string
    status: string
    result: string
  }
  fileInfo?: {
    message: string
  }
}

interface QuickCommand {
  id: number
  text: string
  icon: string
}

interface SystemStatus {
  online: boolean
  listening: boolean
  processing: boolean
}

// 响应式数据
const inputMessage = ref('')
const isListening = ref(false)
const chatHistory = ref<HTMLElement | null>(null)

// 快捷指令配置
const quickCommands = ref<QuickCommand[]>([
  { id: 1, text: '机械臂回零', icon: 'fa-solid fa-rotate-left' },
  { id: 2, text: '拍照保存', icon: 'fa-solid fa-camera' },
  { id: 3, text: '状态查询', icon: 'fa-solid fa-info-circle' },
  { id: 4, text: '底盘移动', icon: 'fa-solid fa-truck' },
  { id: 5, text: '人脸识别', icon: 'fa-solid fa-user-check' },
  { id: 6, text: '系统复位', icon: 'fa-solid fa-arrows-rotate' }
])

// 系统状态
const systemStatus = reactive<SystemStatus>({
  online: true,
  listening: true,
  processing: false
})

// 聊天消息数据
const chatMessages = ref<ChatMessage[]>([
  {
    id: 1,
    type: 'bot',
    content: '您好！我是XC机器人助手，请问需要什么帮助？',
    time: '14:30',
    isFavorite: false
  },
  {
    id: 2,
    type: 'user',
    content: '请帮我控制右臂移动到桌子上方',
    time: '14:31',
    isFavorite: false
  },
  {
    id: 3,
    type: 'bot',
    content: '好的，我将控制右臂移动到桌子上方位置。',
    time: '14:32',
    isFavorite: false,
    taskInfo: {
      title: '机械臂移动',
      status: '执行中...',
      result: '右臂已移动到目标位置'
    }
  },
  {
    id: 4,
    type: 'user',
    content: '拍一张照片',
    time: '14:33',
    isFavorite: false
  },
  {
    id: 5,
    type: 'bot',
    content: '正在为您拍照...',
    time: '14:33',
    isFavorite: false,
    fileInfo: {
      message: '照片已保存: photo_20250719_1433.jpg'
    }
  }
])

// 获取当前时间
const getCurrentTime = (): string => {
  const now = new Date()
  return now.getHours().toString().padStart(2, '0') + ':' + 
         now.getMinutes().toString().padStart(2, '0')
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatHistory.value) {
    chatHistory.value.scrollTop = chatHistory.value.scrollHeight
  }
}

// 切换收藏状态
const toggleFavorite = (messageId: number) => {
  const message = chatMessages.value.find(msg => msg.id === messageId)
  if (message) {
    message.isFavorite = !message.isFavorite
    ElMessage.success(message.isFavorite ? '已添加到收藏' : '已取消收藏')
  }
}

// 语音识别切换
const toggleVoiceRecognition = () => {
  isListening.value = !isListening.value
  systemStatus.listening = isListening.value
  
  if (isListening.value) {
    ElMessage.info('开始语音识别...')
    // 模拟语音识别 3秒后自动填入文本
    setTimeout(() => {
      if (isListening.value) {
        inputMessage.value = '请打开机械臂摄像头'
        isListening.value = false
        systemStatus.listening = false
        ElMessage.success('语音识别完成')
      }
    }, 3000)
  } else {
    ElMessage.info('停止语音识别')
  }
}

// 快捷指令执行
const executeQuickCommand = (commandText: string) => {
  inputMessage.value = commandText
  ElMessage.success(`已选择快捷指令: ${commandText}`)
}

// 发送消息
const sendMessage = () => {
  const message = inputMessage.value.trim()
  if (!message) return

  // 添加用户消息
  const userMessage: ChatMessage = {
    id: Date.now(),
    type: 'user',
    content: message,
    time: getCurrentTime(),
    isFavorite: false
  }
  
  chatMessages.value.push(userMessage)
  inputMessage.value = ''
  
  // 设置处理状态
  systemStatus.processing = true
  
  // 模拟机器人回复延迟
  setTimeout(() => {
    addBotResponse(message)
    systemStatus.processing = false
  }, 1000)
  
  scrollToBottom()
}

// 生成机器人回复
const addBotResponse = (userMessage: string) => {
  const botMessage: ChatMessage = {
    id: Date.now() + 1,
    type: 'bot',
    content: '',
    time: getCurrentTime(),
    isFavorite: false
  }

  // 根据用户消息生成不同类型的回复
  if (userMessage.includes('机械臂') || userMessage.includes('移动')) {
    botMessage.content = '正在处理您的机械臂控制请求...'
    botMessage.taskInfo = {
      title: '机械臂控制',
      status: '执行中...',
      result: '机械臂已按指令移动'
    }
  } else if (userMessage.includes('拍照') || userMessage.includes('照片') || userMessage.includes('摄像头')) {
    botMessage.content = '正在打开摄像头准备拍照...'
    const now = new Date()
    const dateStr = now.getFullYear() + 
                   (now.getMonth() + 1).toString().padStart(2, '0') + 
                   now.getDate().toString().padStart(2, '0')
    const timeStr = getCurrentTime().replace(':', '')
    botMessage.fileInfo = {
      message: `照片已保存: photo_${dateStr}_${timeStr}.jpg`
    }
  } else if (userMessage.includes('状态') || userMessage.includes('查询')) {
    botMessage.content = '系统状态查询结果如下：'
    botMessage.taskInfo = {
      title: '系统状态查询',
      status: '已完成',
      result: '电池电量87%，网络连接稳定，系统负载32%'
    }
  } else {
    botMessage.content = `我已收到您的指令"${userMessage}"，正在处理中。请问您需要进一步的帮助吗？`
  }
  
  chatMessages.value.push(botMessage)
  scrollToBottom()
}

onMounted(() => {
  console.log('智能对话页面已加载')
  scrollToBottom()
})
</script>

<style scoped>
/* 聊天背景颜色 */
.bg-chatBg {
  background-color: #F0F9FF;
}

.bg-userBubble {
  background-color: #E8F4FD;
}

.bg-botBubble {
  background-color: #F5F7FA;
}

/* 颜色系统 */
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

/* 滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  #commands-status {
    grid-template-columns: 1fr;
  }
  
  #quick-commands {
    grid-column: span 1;
  }
  
  #status-panel {
    grid-column: span 1;
  }
  
  .grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>