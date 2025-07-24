<template>
  <div class="placeholder-page">
    <div class="placeholder-content">
      <!-- 页面图标 -->
      <div class="page-icon">
        <i :class="pageIcon" class="icon"></i>
      </div>
      
      <!-- 页面标题 -->
      <h1 class="page-title">{{ pageTitle }}</h1>
      
      <!-- 页面描述 -->
      <p class="page-description">
        此页面正在开发中，即将上线...
      </p>
      
      <!-- 功能预览卡片 -->
      <div class="feature-cards">
        <div class="feature-card" v-for="feature in pageFeatures" :key="feature.title">
          <div class="feature-icon">
            <i :class="feature.icon"></i>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
        </div>
      </div>
      
      <!-- 返回按钮 -->
      <div class="actions">
        <el-button @click="goBack" type="primary">
          <i class="fa-solid fa-arrow-left"></i>
          返回上一页
        </el-button>
        <el-button @click="goHome">
          <i class="fa-solid fa-home"></i>
          返回主页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRouteMetaInfo } from '@/router/routes'

const route = useRoute()
const router = useRouter()

// 获取页面信息
const routeInfo = computed(() => {
  const info = getRouteMetaInfo(route.name as string)
  return info || {
    title: '页面开发中',
    icon: 'fa-solid fa-cog',
    menuGroupTitle: '系统功能'
  }
})

const pageTitle = computed(() => routeInfo.value.title)
const pageIcon = computed(() => routeInfo.value.icon)

// 根据页面类型生成功能预览
const pageFeatures = computed(() => {
  const menuGroup = routeInfo.value.menuGroup
  
  const featureMap: Record<string, Array<{title: string, icon: string, description: string}>> = {
    'quick-launch': [
      { title: '快速访问', icon: 'fa-solid fa-bolt', description: '一键启动常用功能模块' },
      { title: '收藏管理', icon: 'fa-solid fa-star', description: '自定义收藏功能列表' },
      { title: '历史记录', icon: 'fa-solid fa-clock', description: '查看最近使用的功能' }
    ],
    'device-connection': [
      { title: '设备管理', icon: 'fa-solid fa-plug', description: '统一管理所有连接设备' },
      { title: '网络配置', icon: 'fa-solid fa-globe', description: '配置设备网络连接参数' },
      { title: '连接测试', icon: 'fa-solid fa-flask', description: '测试设备连接状态和性能' }
    ],
    'robot-control': [
      { title: '机械臂控制', icon: 'fa-solid fa-robot', description: '精确控制双臂机械臂运动' },
      { title: '底盘控制', icon: 'fa-solid fa-bullseye', description: '控制机器人移动和导航' },
      { title: '联动控制', icon: 'fa-solid fa-sync', description: '协调多设备联合作业' }
    ],
    'intelligent-interaction': [
      { title: '人脸识别', icon: 'fa-solid fa-user', description: '智能人脸检测和识别' },
      { title: '智能对话', icon: 'fa-solid fa-comment', description: '自然语言交互对话' },
      { title: '梯控系统', icon: 'fa-solid fa-building', description: '电梯控制和楼层导航' }
    ],
    'scene-testing': [
      { title: '组件测试', icon: 'fa-solid fa-flask', description: '单元组件功能测试' },
      { title: '集成测试', icon: 'fa-solid fa-link', description: '多组件协同测试' },
      { title: '端到端测试', icon: 'fa-solid fa-bullseye', description: '完整业务流程测试' }
    ],
    'simulation-planning': [
      { title: '机器人仿真', icon: 'fa-solid fa-gamepad', description: '3D仿真环境测试' },
      { title: '路径规划', icon: 'fa-solid fa-map', description: '智能路径规划算法' },
      { title: '任务编排', icon: 'fa-solid fa-clipboard-list', description: '复杂任务自动编排' }
    ],
    'visual-perception': [
      { title: '视觉系统', icon: 'fa-solid fa-eye', description: '机器视觉处理和分析' },
      { title: '相机标定', icon: 'fa-solid fa-camera', description: '相机参数精确标定' },
      { title: '图像处理', icon: 'fa-solid fa-image', description: '实时图像处理和增强' }
    ],
    'data-monitoring': [
      { title: '系统监控', icon: 'fa-solid fa-chart-bar', description: '实时系统状态监控' },
      { title: '数据分析', icon: 'fa-solid fa-chart-pie', description: '数据统计和趋势分析' },
      { title: '性能统计', icon: 'fa-solid fa-chart-line', description: '性能指标跟踪统计' }
    ],
    'system-management': [
      { title: '系统设置', icon: 'fa-solid fa-cog', description: '系统参数配置管理' },
      { title: '参数配置', icon: 'fa-solid fa-sliders-h', description: '业务参数自定义配置' },
      { title: '维护管理', icon: 'fa-solid fa-tools', description: '系统维护和故障处理' }
    ]
  }
  
  return featureMap[menuGroup] || [
    { title: '核心功能', icon: 'fa-solid fa-star', description: '提供核心业务功能支持' },
    { title: '数据管理', icon: 'fa-solid fa-database', description: '数据存储和管理服务' },
    { title: '系统集成', icon: 'fa-solid fa-link', description: '与其他系统无缝集成' }
  ]
})

// 导航方法
const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.placeholder-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.placeholder-content {
  max-width: 800px;
  text-align: center;
  background: white;
  padding: 60px 40px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.page-icon {
  margin-bottom: 24px;
}

.page-icon .icon {
  font-size: 64px;
  color: var(--primary-color, #409EFF);
  opacity: 0.8;
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: var(--secondary-color, #2c3e50);
  margin: 0 0 16px 0;
}

.page-description {
  font-size: 18px;
  color: #666;
  margin: 0 0 40px 0;
  line-height: 1.6;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.feature-card {
  background: #f8f9fa;
  padding: 24px 20px;
  border-radius: 12px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  margin-bottom: 12px;
}

.feature-icon i {
  font-size: 32px;
  color: var(--primary-color, #409EFF);
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--secondary-color, #2c3e50);
  margin: 0 0 8px 0;
}

.feature-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.actions .el-button {
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 8px;
}

.actions .el-button i {
  margin-right: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .placeholder-content {
    padding: 40px 24px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .page-description {
    font-size: 16px;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .actions {
    flex-direction: column;
    align-items: center;
  }
  
  .actions .el-button {
    width: 200px;
  }
}
</style>