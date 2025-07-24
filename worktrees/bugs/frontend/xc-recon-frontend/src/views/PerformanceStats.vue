<template>
  <div class="w-full h-full p-4 overflow-auto">
    <!-- Header Section -->
    <div class="mb-4">
      <h1 class="text-2xl font-bold text-secondary">性能统计仪表板</h1>
      <p class="text-sm text-gray-500">系统全维度性能指标监控与分析</p>
    </div>

    <!-- Key Metrics Overview -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-semibold text-secondary flex items-center">
          <i class="fa-solid fa-bullseye mr-2 text-primary"></i>关键指标概览
        </h2>
        <div class="flex space-x-2">
          <button 
            class="text-sm px-3 py-1 bg-primary text-white rounded-md flex items-center hover:bg-blue-600 transition-colors"
            @click="handleRefreshMetrics"
          >
            <i class="fa-solid fa-rotate mr-1"></i>刷新
          </button>
          <button 
            class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md flex items-center hover:bg-gray-50 transition-colors"
            @click="handleSettings"
          >
            <i class="fa-solid fa-gear mr-1"></i>设置
          </button>
        </div>
      </div>
      
      <!-- System Metrics -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <!-- CPU Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-microchip text-primary text-lg mr-2"></i>
              <h3 class="font-medium">CPU</h3>
            </div>
            <span class="text-lg font-bold">{{ systemMetrics.cpu.usage }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-primary h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: systemMetrics.cpu.usage + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-success">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ systemMetrics.cpu.status }}
            </span>
            <span class="text-gray-500 text-xs">{{ systemMetrics.cpu.cores }}核心</span>
          </div>
        </div>

        <!-- Memory Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-memory text-primary text-lg mr-2"></i>
              <h3 class="font-medium">内存</h3>
            </div>
            <span class="text-lg font-bold">{{ systemMetrics.memory.used }}/{{ systemMetrics.memory.total }}GB</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-primary h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: systemMetrics.memory.percentage + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-success">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ systemMetrics.memory.status }}
            </span>
            <span class="text-gray-500 text-xs">{{ systemMetrics.memory.percentage }}% 已用</span>
          </div>
        </div>

        <!-- GPU Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-desktop text-primary text-lg mr-2"></i>
              <h3 class="font-medium">GPU</h3>
            </div>
            <span class="text-lg font-bold">{{ systemMetrics.gpu.usage }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-primary h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: systemMetrics.gpu.usage + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-success">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ systemMetrics.gpu.status }}
            </span>
            <span class="text-gray-500 text-xs">{{ systemMetrics.gpu.model }}</span>
          </div>
        </div>

        <!-- Network Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-network-wired text-primary text-lg mr-2"></i>
              <h3 class="font-medium">网络</h3>
            </div>
            <span class="text-lg font-bold">{{ systemMetrics.network.bandwidth }} Mbps</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-primary h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: systemMetrics.network.usage + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-success">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ systemMetrics.network.status }}
            </span>
            <span class="text-gray-500 text-xs">延迟: {{ systemMetrics.network.latency }}ms</span>
          </div>
        </div>
      </div>

      <!-- Robot Metrics -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- Task Completion Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-robot text-success text-lg mr-2"></i>
              <h3 class="font-medium">任务</h3>
            </div>
            <span class="text-lg font-bold">{{ robotMetrics.tasks.completion }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-success h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: robotMetrics.tasks.completion + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-excellent">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ robotMetrics.tasks.status }}
            </span>
            <span class="text-gray-500 text-xs">完成率</span>
          </div>
        </div>

        <!-- Response Time Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-bolt text-success text-lg mr-2"></i>
              <h3 class="font-medium">响应时间</h3>
            </div>
            <span class="text-lg font-bold">{{ robotMetrics.response.time }}ms</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-success h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: robotMetrics.response.percentage + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-success">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ robotMetrics.response.status }}
            </span>
            <span class="text-gray-500 text-xs">平均</span>
          </div>
        </div>

        <!-- Precision Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-bullseye text-success text-lg mr-2"></i>
              <h3 class="font-medium">精度</h3>
            </div>
            <span class="text-lg font-bold">{{ robotMetrics.precision.value }}mm</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-success h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: robotMetrics.precision.percentage + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-excellent">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ robotMetrics.precision.status }}
            </span>
            <span class="text-gray-500 text-xs">偏差</span>
          </div>
        </div>

        <!-- Stability Card -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
              <i class="fa-solid fa-rotate text-success text-lg mr-2"></i>
              <h3 class="font-medium">稳定性</h3>
            </div>
            <span class="text-lg font-bold">{{ robotMetrics.stability.uptime }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              class="bg-success h-2.5 rounded-full transition-all duration-500" 
              :style="{ width: robotMetrics.stability.uptime + '%' }"
            ></div>
          </div>
          <div class="flex justify-between items-center text-sm">
            <span class="flex items-center text-excellent">
              <i class="fa-solid fa-circle text-xs mr-1"></i>{{ robotMetrics.stability.status }}
            </span>
            <span class="text-gray-500 text-xs">运行时间</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Trends and Configuration Panel -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
      <!-- Performance Trends (3 columns) -->
      <div class="lg:col-span-3">
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200 h-full">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold text-secondary flex items-center">
              <i class="fa-solid fa-chart-line mr-2 text-primary"></i>性能趋势图表 (过去{{ getTimeRangeText(chartSettings.timeRange) }})
            </h2>
            <div class="flex space-x-2">
              <button 
                class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
                @click="handlePauseCharts"
              >
                <i class="fa-solid fa-pause"></i>
              </button>
              <button 
                class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
                @click="handleZoomCharts"
              >
                <i class="fa-solid fa-magnifying-glass-plus"></i>
              </button>
              <button 
                class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
                @click="handleDownloadCharts"
              >
                <i class="fa-solid fa-download"></i>
              </button>
            </div>
          </div>
          
          <!-- CPU Trend Chart -->
          <div class="h-56 mb-4 bg-gray-50 rounded-lg flex items-center justify-center">
            <div class="text-center text-gray-500">
              <i class="fa-solid fa-chart-line text-2xl mb-2"></i>
              <p class="text-sm">CPU使用率趋势图</p>
              <p class="text-xs">需要 Highcharts 库支持</p>
            </div>
          </div>
          
          <!-- Memory Trend Chart -->
          <div class="h-56 mb-4 bg-gray-50 rounded-lg flex items-center justify-center">
            <div class="text-center text-gray-500">
              <i class="fa-solid fa-chart-area text-2xl mb-2"></i>
              <p class="text-sm">内存使用趋势图</p>
              <p class="text-xs">需要 Highcharts 库支持</p>
            </div>
          </div>
          
          <!-- Robot Performance Trend Chart -->
          <div class="h-56 bg-gray-50 rounded-lg flex items-center justify-center">
            <div class="text-center text-gray-500">
              <i class="fa-solid fa-robot text-2xl mb-2"></i>
              <p class="text-sm">机器人性能趋势图</p>
              <p class="text-xs">需要 Highcharts 库支持</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Configuration Panel (1 column) -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200 mb-4">
          <h2 class="text-lg font-semibold text-secondary flex items-center mb-4">
            <i class="fa-solid fa-gear mr-2 text-primary"></i>配置面板
          </h2>
          
          <!-- Chart Settings -->
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2 flex items-center">
              <i class="fa-solid fa-chart-pie mr-1 text-primary"></i>图表设置:
            </h3>
            <div class="ml-2">
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="time-1h" 
                  v-model="chartSettings.timeRange" 
                  value="1h" 
                  class="mr-2"
                >
                <label for="time-1h" class="text-sm">1小时</label>
              </div>
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="time-24h" 
                  v-model="chartSettings.timeRange" 
                  value="24h" 
                  class="mr-2"
                >
                <label for="time-24h" class="text-sm">24小时</label>
              </div>
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="time-7d" 
                  v-model="chartSettings.timeRange" 
                  value="7d" 
                  class="mr-2"
                >
                <label for="time-7d" class="text-sm">7天</label>
              </div>
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="time-30d" 
                  v-model="chartSettings.timeRange" 
                  value="30d" 
                  class="mr-2"
                >
                <label for="time-30d" class="text-sm">30天</label>
              </div>
            </div>
          </div>
          
          <!-- Alert Settings -->
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2 flex items-center">
              <i class="fa-solid fa-bell mr-1 text-warning"></i>告警设置:
            </h3>
            <div class="grid grid-cols-2 gap-2 ml-2">
              <div class="text-sm">CPU:</div>
              <div class="flex items-center">
                <input 
                  type="text" 
                  v-model="alertSettings.cpu" 
                  class="w-12 h-6 text-xs border border-gray-300 rounded px-1"
                >
                <i class="fa-solid fa-chevron-down ml-1 text-gray-500 text-xs"></i>
              </div>
              
              <div class="text-sm">内存:</div>
              <div class="flex items-center">
                <input 
                  type="text" 
                  v-model="alertSettings.memory" 
                  class="w-12 h-6 text-xs border border-gray-300 rounded px-1"
                >
                <i class="fa-solid fa-chevron-down ml-1 text-gray-500 text-xs"></i>
              </div>
              
              <div class="text-sm">温度:</div>
              <div class="flex items-center">
                <input 
                  type="text" 
                  v-model="alertSettings.temperature" 
                  class="w-12 h-6 text-xs border border-gray-300 rounded px-1"
                >
                <i class="fa-solid fa-chevron-down ml-1 text-gray-500 text-xs"></i>
              </div>
              
              <div class="text-sm">响应:</div>
              <div class="flex items-center">
                <input 
                  type="text" 
                  v-model="alertSettings.response" 
                  class="w-12 h-6 text-xs border border-gray-300 rounded px-1"
                >
                <i class="fa-solid fa-chevron-down ml-1 text-gray-500 text-xs"></i>
              </div>
            </div>
          </div>
          
          <button 
            class="w-full bg-primary text-white py-2 rounded-md text-sm"
            @click="handleSaveSettings"
          >
            保存设置
          </button>
        </div>
        
        <!-- Statistics Report -->
        <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <h2 class="text-lg font-semibold text-secondary flex items-center mb-4">
            <i class="fa-solid fa-chart-pie mr-2 text-primary"></i>统计报告
          </h2>
          
          <!-- Report Options -->
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2 flex items-center">
              <i class="fa-regular fa-file-lines mr-1 text-primary"></i>性能报告:
            </h3>
            <div class="ml-2">
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="report-realtime" 
                  v-model="reportSettings.type" 
                  value="realtime" 
                  class="mr-2"
                >
                <label for="report-realtime" class="text-sm">实时报告</label>
              </div>
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="report-daily" 
                  v-model="reportSettings.type" 
                  value="daily" 
                  class="mr-2"
                >
                <label for="report-daily" class="text-sm">日报</label>
              </div>
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="report-weekly" 
                  v-model="reportSettings.type" 
                  value="weekly" 
                  class="mr-2"
                >
                <label for="report-weekly" class="text-sm">周报</label>
              </div>
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  id="report-monthly" 
                  v-model="reportSettings.type" 
                  value="monthly" 
                  class="mr-2"
                >
                <label for="report-monthly" class="text-sm">月报</label>
              </div>
            </div>
          </div>
          
          <!-- Email Setting -->
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2 flex items-center">
              <i class="fa-regular fa-envelope mr-1 text-primary"></i>推送邮箱:
            </h3>
            <input 
              type="email" 
              v-model="reportSettings.email" 
              class="w-full text-sm border border-gray-300 rounded-md px-2 py-1"
            >
          </div>
          
          <button 
            class="w-full bg-success text-white py-2 rounded-md text-sm"
            @click="handleGenerateReport"
          >
            生成报告
          </button>
        </div>
      </div>
    </div>

    <!-- Performance Details and Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-1 gap-6 mb-6">
      <!-- Performance Details -->
      <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-secondary flex items-center">
            <i class="fa-solid fa-clipboard-list mr-2 text-primary"></i>性能详细统计
          </h2>
          <div class="flex space-x-2">
            <button 
              class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
              @click="handleExportDetails"
            >
              导出详情
            </button>
            <button 
              class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
              @click="handlePerformanceTest"
            >
              性能测试
            </button>
            <button 
              class="text-sm px-3 py-1 bg-primary text-white rounded-md"
              @click="handleOptimizationSuggestions"
            >
              优化建议
            </button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- System Resource Details -->
          <div>
            <h3 class="text-md font-medium mb-3 flex items-center">
              <i class="fa-solid fa-microchip mr-1 text-primary"></i>系统资源详情:
            </h3>
            <div class="grid grid-cols-2 gap-2 mb-4">
              <div class="text-sm" v-for="(core, index) in systemDetails.cpuCores" :key="index">
                CPU {{ index }}: <span class="font-medium">{{ core }}%</span>
              </div>
            </div>
            <div class="text-sm mb-4">平均负载: <span class="font-medium">{{ systemDetails.loadAverage.join(', ') }}</span></div>
            
            <h3 class="text-md font-medium mb-3 flex items-center">
              <i class="fa-solid fa-memory mr-1 text-primary"></i>内存详情:
            </h3>
            <div class="text-sm mb-2">物理内存: <span class="font-medium">{{ systemDetails.memory.physical }}</span></div>
            <div class="text-sm mb-2">交换内存: <span class="font-medium">{{ systemDetails.memory.swap }}</span></div>
            <div class="text-sm mb-4">缓存: <span class="font-medium">{{ systemDetails.memory.cache }}</span></div>
          </div>
          
          <!-- Robot Performance Details -->
          <div>
            <h3 class="text-md font-medium mb-3 flex items-center">
              <i class="fa-solid fa-robot mr-1 text-success"></i>机器人性能详情:
            </h3>
            <div class="grid grid-cols-2 gap-2 mb-4">
              <div class="text-sm">左臂精度: <span class="font-medium">{{ robotDetails.precision.leftArm }}</span></div>
              <div class="text-sm">右臂精度: <span class="font-medium">{{ robotDetails.precision.rightArm }}</span></div>
              <div class="text-sm">底盘定位: <span class="font-medium">{{ robotDetails.precision.chassis }}</span></div>
              <div class="text-sm">视觉延迟: <span class="font-medium">{{ robotDetails.precision.vision }}</span></div>
            </div>
            <div class="text-sm mb-4">任务队列: <span class="font-medium">{{ robotDetails.taskQueue }}个待处理</span></div>
            
            <div class="bg-lightBg p-3 rounded-md text-sm">
              <p class="font-medium mb-1">性能优化建议:</p>
              <ul class="list-disc pl-5">
                <li v-for="suggestion in optimizationSuggestions" :key="suggestion.id">{{ suggestion.text }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Performance Alerts History -->
      <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-secondary flex items-center">
            <i class="fa-solid fa-triangle-exclamation mr-2 text-warning"></i>性能告警历史
          </h2>
          <div class="flex space-x-2">
            <button 
              class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
              @click="handleViewAllAlerts"
            >
              查看全部
            </button>
            <button 
              class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
              @click="handleClearHistory"
            >
              清空历史
            </button>
            <button 
              class="text-sm px-3 py-1 bg-white border border-gray-300 text-secondary rounded-md"
              @click="handleExportLogs"
            >
              导出日志
            </button>
          </div>
        </div>
        
        <div class="overflow-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">告警内容</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="alert in alertHistory" :key="alert.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <i :class="getAlertIcon(alert.status)"></i>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  {{ alert.time }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  {{ alert.message }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <button class="text-primary" @click="handleViewAlert(alert.id)">查看</button>
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
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 类型定义
interface SystemMetrics {
  cpu: {
    usage: number
    cores: number
    status: string
  }
  memory: {
    used: number
    total: number
    percentage: number
    status: string
  }
  gpu: {
    usage: number
    status: string
    model: string
  }
  network: {
    bandwidth: number
    usage: number
    status: string
    latency: number
  }
}

interface RobotMetrics {
  tasks: {
    completion: number
    status: string
  }
  response: {
    time: number
    percentage: number
    status: string
  }
  precision: {
    value: number
    percentage: number
    status: string
  }
  stability: {
    uptime: number
    status: string
  }
}

interface AlertItem {
  id: string
  status: 'warning' | 'success' | 'danger'
  time: string
  message: string
}

// 响应式数据
const systemMetrics = reactive<SystemMetrics>({
  cpu: {
    usage: 68.5,
    cores: 8,
    status: '正常'
  },
  memory: {
    used: 4.2,
    total: 16,
    percentage: 26.25,
    status: '正常'
  },
  gpu: {
    usage: 45.2,
    status: '正常',
    model: 'NVIDIA RTX'
  },
  network: {
    bandwidth: 125,
    usage: 62.5,
    status: '良好',
    latency: 5
  }
})

const robotMetrics = reactive<RobotMetrics>({
  tasks: {
    completion: 95.2,
    status: '优秀'
  },
  response: {
    time: 45,
    percentage: 45,
    status: '良好'
  },
  precision: {
    value: 0.05,
    percentage: 95,
    status: '优秀'
  },
  stability: {
    uptime: 99.8,
    status: '优秀'
  }
})

const chartSettings = reactive({
  timeRange: '24h'
})

const alertSettings = reactive({
  cpu: '80%',
  memory: '85%',
  temperature: '75°',
  response: '100ms'
})

const reportSettings = reactive({
  type: 'daily',
  email: 'ops@xc.com'
})

const systemDetails = reactive({
  cpuCores: [45.2, 67.8, 52.3, 71.5],
  loadAverage: [2.1, 2.5, 2.8],
  memory: {
    physical: '4.2GB / 16GB 使用',
    swap: '0.8GB / 8GB 使用',
    cache: '2.1GB'
  }
})

const robotDetails = reactive({
  precision: {
    leftArm: '0.03mm',
    rightArm: '0.05mm',
    chassis: '±2cm',
    vision: '12ms'
  },
  taskQueue: 3
})

const optimizationSuggestions = ref([
  { id: '1', text: 'CPU 1和CPU 3负载较高，建议优化任务分配' },
  { id: '2', text: '视觉处理模块可进一步优化，降低延迟' },
  { id: '3', text: '增加内存缓存可提高响应速度' }
])

const alertHistory = ref<AlertItem[]>([
  {
    id: '1',
    status: 'warning',
    time: '2025-07-19 14:23',
    message: 'CPU使用率超过80% (当前: 85.2%)'
  },
  {
    id: '2',
    status: 'success',
    time: '2025-07-19 14:25',
    message: 'CPU使用率恢复正常 (当前: 72.1%)'
  },
  {
    id: '3',
    status: 'warning',
    time: '2025-07-19 13:45',
    message: '机械臂响应延迟 (延迟: 156ms)'
  },
  {
    id: '4',
    status: 'danger',
    time: '2025-07-19 12:30',
    message: 'GPU温度过高 (温度: 78°C)'
  }
])

// DOM 引用
const cpuChart = ref<HTMLElement>()
const memoryChart = ref<HTMLElement>()
const robotChart = ref<HTMLElement>()

// 工具方法
const getAlertIcon = (status: string): string => {
  const iconMap: Record<string, string> = {
    'warning': 'fa-solid fa-triangle-exclamation text-warning',
    'success': 'fa-solid fa-check-circle text-success',
    'danger': 'fa-solid fa-fire text-danger'
  }
  return iconMap[status] || 'fa-solid fa-circle text-info'
}

// 事件处理方法
const handleRefreshMetrics = () => {
  // 模拟刷新指标数据
  systemMetrics.cpu.usage = Math.round(Math.random() * 30 + 50)
  systemMetrics.memory.used = Math.round((Math.random() * 4 + 3) * 10) / 10
  systemMetrics.memory.percentage = Math.round((systemMetrics.memory.used / systemMetrics.memory.total) * 100 * 100) / 100
  systemMetrics.gpu.usage = Math.round(Math.random() * 40 + 30)
  systemMetrics.network.bandwidth = Math.round(Math.random() * 50 + 100)
  
  robotMetrics.tasks.completion = Math.round(Math.random() * 10 + 90 * 10) / 10
  robotMetrics.response.time = Math.round(Math.random() * 30 + 30)
  robotMetrics.precision.value = Math.round(Math.random() * 0.05 + 0.03 * 100) / 100
  robotMetrics.stability.uptime = Math.round(Math.random() * 2 + 98 * 10) / 10
  
  ElMessage.success('指标数据已刷新')
}

const handleSettings = () => {
  ElMessage.info('打开设置面板')
}

const handlePauseCharts = () => {
  ElMessage.info('暂停图表更新')
}

const handleZoomCharts = () => {
  ElMessage.info('放大图表显示')
}

const handleDownloadCharts = () => {
  ElMessage.success('图表数据导出成功')
}

const handleSaveSettings = () => {
  ElMessage.success('配置设置已保存')
}

const handleGenerateReport = () => {
  ElMessage.success(`正在生成${reportSettings.type}报告，将发送至 ${reportSettings.email}`)
}

const handleExportDetails = () => {
  ElMessage.success('性能详情导出成功')
}

const handlePerformanceTest = () => {
  ElMessage.info('启动性能测试...')
}

const handleOptimizationSuggestions = () => {
  ElMessage.info('生成性能优化建议')
}

const handleViewAllAlerts = () => {
  ElMessage.info('查看全部告警历史')
}

const handleClearHistory = () => {
  ElMessage.warning('确认清空告警历史吗？')
}

const handleExportLogs = () => {
  ElMessage.success('告警日志导出成功')
}

const handleViewAlert = (alertId: string) => {
  ElMessage.info(`查看告警详情: ${alertId}`)
}

const getTimeRangeText = (range: string) => {
  const rangeMap: Record<string, string> = {
    '1h': '1小时',
    '24h': '24小时',
    '7d': '7天',
    '30d': '30天'
  }
  return rangeMap[range] || '24小时'
}

// 初始化图表
const initCharts = () => {
  if (typeof window !== 'undefined' && (window as any).Highcharts) {
    const Highcharts = (window as any).Highcharts
    
    // CPU使用率趋势图
    if (cpuChart.value) {
      Highcharts.chart(cpuChart.value, {
        chart: {
          type: 'spline',
          backgroundColor: 'transparent',
          style: {
            fontFamily: 'Inter, sans-serif'
          }
        },
        title: {
          text: 'CPU使用率趋势',
          style: {
            fontSize: '14px',
            fontWeight: '600',
            color: '#2c3e50'
          }
        },
        xAxis: {
          type: 'datetime',
          labels: {
            format: '{value:%H:%M}'
          },
          tickInterval: 3600 * 1000
        },
        yAxis: {
          title: {
            text: '使用率 (%)'
          },
          min: 0,
          max: 100,
          plotLines: [{
            value: 80,
            color: '#E6A23C',
            dashStyle: 'shortdash',
            width: 2,
            label: {
              text: '警告阈值'
            }
          }]
        },
        tooltip: {
          headerFormat: '<b>{series.name}</b><br>',
          pointFormat: '{point.x:%Y-%m-%d %H:%M:%S}<br>{point.y:.2f}%'
        },
        plotOptions: {
          spline: {
            marker: {
              enabled: false
            }
          }
        },
        series: [{
          name: 'CPU使用率',
          color: '#409EFF',
          data: (() => {
            const data = []
            const now = new Date().getTime()
            for (let i = 24; i > 0; i--) {
              data.push([
                now - i * 3600 * 1000,
                Math.round(Math.random() * 30 + 40)
              ])
            }
            return data
          })()
        }],
        credits: {
          enabled: false
        }
      })
    }
    
    // 内存使用趋势图
    if (memoryChart.value) {
      Highcharts.chart(memoryChart.value, {
        chart: {
          type: 'area',
          backgroundColor: 'transparent',
          style: {
            fontFamily: 'Inter, sans-serif'
          }
        },
        title: {
          text: '内存使用趋势',
          style: {
            fontSize: '14px',
            fontWeight: '600',
            color: '#2c3e50'
          }
        },
        xAxis: {
          type: 'datetime',
          labels: {
            format: '{value:%H:%M}'
          },
          tickInterval: 3600 * 1000
        },
        yAxis: {
          title: {
            text: '使用量 (GB)'
          },
          min: 0,
          max: 16
        },
        tooltip: {
          headerFormat: '<b>{series.name}</b><br>',
          pointFormat: '{point.x:%Y-%m-%d %H:%M:%S}<br>{point.y:.2f} GB'
        },
        plotOptions: {
          area: {
            marker: {
              enabled: false
            },
            fillOpacity: 0.3
          }
        },
        series: [{
          name: '内存使用量',
          color: '#409EFF',
          data: (() => {
            const data = []
            const now = new Date().getTime()
            for (let i = 24; i > 0; i--) {
              data.push([
                now - i * 3600 * 1000,
                Math.round((Math.random() * 2 + 3) * 10) / 10
              ])
            }
            return data
          })()
        }],
        credits: {
          enabled: false
        }
      })
    }
    
    // 机器人性能趋势图
    if (robotChart.value) {
      Highcharts.chart(robotChart.value, {
        chart: {
          type: 'line',
          backgroundColor: 'transparent',
          style: {
            fontFamily: 'Inter, sans-serif'
          }
        },
        title: {
          text: '机器人性能趋势',
          style: {
            fontSize: '14px',
            fontWeight: '600',
            color: '#2c3e50'
          }
        },
        xAxis: {
          type: 'datetime',
          labels: {
            format: '{value:%H:%M}'
          },
          tickInterval: 3600 * 1000
        },
        yAxis: [{
          title: {
            text: '完成率 (%)',
            style: {
              color: '#00A870'
            }
          },
          min: 0,
          max: 100,
          labels: {
            style: {
              color: '#00A870'
            }
          }
        }, {
          title: {
            text: '响应时间 (ms)',
            style: {
              color: '#E6A23C'
            }
          },
          min: 0,
          max: 200,
          opposite: true,
          labels: {
            style: {
              color: '#E6A23C'
            }
          }
        }],
        tooltip: {
          shared: true
        },
        plotOptions: {
          line: {
            marker: {
              enabled: false
            }
          }
        },
        series: [{
          name: '任务完成率',
          color: '#00A870',
          yAxis: 0,
          data: (() => {
            const data = []
            const now = new Date().getTime()
            for (let i = 24; i > 0; i--) {
              data.push([
                now - i * 3600 * 1000,
                Math.round(Math.random() * 10 + 85)
              ])
            }
            return data
          })()
        }, {
          name: '响应时间',
          color: '#E6A23C',
          yAxis: 1,
          data: (() => {
            const data = []
            const now = new Date().getTime()
            for (let i = 24; i > 0; i--) {
              data.push([
                now - i * 3600 * 1000,
                Math.round(Math.random() * 50 + 30)
              ])
            }
            return data
          })()
        }],
        credits: {
          enabled: false
        }
      })
    }
  }
}

// 生命周期
onMounted(() => {
  nextTick(() => {
    // 延迟初始化图表，确保Highcharts已加载
    setTimeout(initCharts, 100)
  })
})

onUnmounted(() => {
  // 清理工作
})
</script>

<style scoped>
/* 项目配色变量 */
.text-secondary {
  color: #2c3e50;
}

.text-primary {
  color: #409EFF;
}

.text-success {
  color: #67C23A;
}

.text-warning {
  color: #E6A23C;
}

.text-danger {
  color: #F56C6C;
}

.text-excellent {
  color: #67C23A;
}

.bg-primary {
  background-color: #409EFF;
}

.bg-success {
  background-color: #67C23A;
}

.bg-lightBg {
  background-color: #E6F4FF;
}

/* 确保字体一致性 */
* {
  font-family: 'Inter', sans-serif;
}

/* 悬停效果 */
button:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .lg\:col-span-3 {
    grid-column: span 1;
  }
  
  .lg\:col-span-1 {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .md\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}
</style>