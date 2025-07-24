<template>
  <div class="tech-support-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="fa-solid fa-life-ring"></i>
          技术文档
        </h1>
        <p class="page-description">
          XC-RECON-V2项目技术文档资源中心，包含系统设计、硬件规格、开发指南等核心技术资料
        </p>
      </div>
    </div>

    <!-- 文档分类列表 -->
    <div class="doc-categories">
      <!-- 核心文档 -->
      <div class="doc-category">
        <h2 class="category-title">
          <i class="fa-solid fa-star"></i>
          核心文档
        </h2>
        <div class="doc-list">
          <div class="doc-item featured" @click="openDocument('system')">
            <div class="doc-icon">
              <i class="fa-solid fa-cogs"></i>
            </div>
            <div class="doc-content">
              <h3 class="doc-title">XC-RECON系统设计</h3>
              <p class="doc-description">双臂类人形机器人控制系统完整架构设计和技术规范</p>
              <span class="doc-size">1.8MB • MD文档</span>
            </div>
            <div class="doc-action">
              <i class="fa-solid fa-external-link-alt"></i>
            </div>
          </div>
          
          <div class="doc-item" @click="openDocument('docs-index')">
            <div class="doc-icon">
              <i class="fa-solid fa-book"></i>
            </div>
            <div class="doc-content">
              <h3 class="doc-title">项目文档索引</h3>
              <p class="doc-description">完整的项目文档结构和快速导航指南</p>
              <span class="doc-size">268行 • MD文档</span>
            </div>
            <div class="doc-action">
              <i class="fa-solid fa-external-link-alt"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 硬件文档 -->
      <div class="doc-category">
        <h2 class="category-title">
          <i class="fa-solid fa-microchip"></i>
          硬件文档
        </h2>
        <div class="doc-list">
          <div class="doc-item" v-for="doc in hardwareDocs" :key="doc.id" @click="openDocument(doc.id)">
            <div class="doc-icon">
              <i :class="doc.icon"></i>
            </div>
            <div class="doc-content">
              <h3 class="doc-title">{{ doc.title }}</h3>
              <p class="doc-description">{{ doc.description }}</p>
              <span class="doc-size">{{ doc.size }}</span>
            </div>
            <div class="doc-action">
              <i class="fa-solid fa-external-link-alt"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 开发文档 -->
      <div class="doc-category">
        <h2 class="category-title">
          <i class="fa-solid fa-code"></i>
          开发文档
        </h2>
        <div class="doc-list">
          <div class="doc-item" v-for="doc in developmentDocs" :key="doc.id" @click="openDocument(doc.id)">
            <div class="doc-icon">
              <i :class="doc.icon"></i>
            </div>
            <div class="doc-content">
              <h3 class="doc-title">{{ doc.title }}</h3>
              <p class="doc-description">{{ doc.description }}</p>
              <span class="doc-size">{{ doc.size }}</span>
            </div>
            <div class="doc-action">
              <i class="fa-solid fa-external-link-alt"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 测试文档 -->
      <div class="doc-category">
        <h2 class="category-title">
          <i class="fa-solid fa-vial"></i>
          测试文档
        </h2>
        <div class="doc-list">
          <div class="doc-item" v-for="doc in testingDocs" :key="doc.id" @click="openDocument(doc.id)">
            <div class="doc-icon">
              <i :class="doc.icon"></i>
            </div>
            <div class="doc-content">
              <h3 class="doc-title">{{ doc.title }}</h3>
              <p class="doc-description">{{ doc.description }}</p>
              <span class="doc-size">{{ doc.size }}</span>
            </div>
            <div class="doc-action">
              <i class="fa-solid fa-external-link-alt"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档查看器模态框 -->
    <div v-if="showDocViewer" class="doc-viewer-modal" @click="closeDocViewer">
      <div class="doc-viewer-content" @click.stop>
        <div class="doc-viewer-header">
          <h3>{{ currentDocTitle }}</h3>
          <button class="close-btn" @click="closeDocViewer">
            <i class="fa-solid fa-times"></i>
          </button>
        </div>
        <div class="doc-viewer-body">
          <div class="markdown-content" v-html="currentDocContent"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// 响应式数据
const showDocViewer = ref(false)
const currentDocTitle = ref('')
const currentDocContent = ref('')

// 硬件文档列表
const hardwareDocs = reactive([
  {
    id: 'fr3-analysis',
    title: 'FR3机械臂技术分析',
    description: '法奥意威FR3协作机器人运动学模型、DH参数和控制接口详细分析',
    icon: 'fa-solid fa-robot',
    size: '完整分析 • MD文档'
  },
  {
    id: 'hermes-control',
    title: 'Hermes底盘控制文档',
    description: '思岚科技Hermes移动底盘控制API和导航系统集成指南',
    icon: 'fa-solid fa-car',
    size: 'API文档 • HTML'
  },
  {
    id: 'gemini335-vision',
    title: 'Gemini335视觉系统',
    description: 'TOF深度相机技术规格、配置方法和视觉处理流程',
    icon: 'fa-solid fa-eye',
    size: '技术规格 • HTML'
  },
  {
    id: 'robot-config',
    title: '机器人配置参考',
    description: '硬件配置参数、网络设置和系统集成配置模板',
    icon: 'fa-solid fa-cog',
    size: 'JSON配置 • 参考文档'
  }
])

// 开发文档列表
const developmentDocs = reactive([
  {
    id: 'deployment-guide',
    title: '部署指南',
    description: '开发环境配置、生产部署和常见问题解决方案',
    icon: 'fa-solid fa-rocket',
    size: '部署指南 • MD文档'
  },
  {
    id: 'dual-arm-integration',
    title: '双臂集成指南',
    description: '双机械臂协调控制实现方法和同步机制设计',
    icon: 'fa-solid fa-handshake',
    size: '集成指南 • MD文档'
  },
  {
    id: 'cross-platform',
    title: '跨平台开发方案',
    description: 'Mac/Windows协作开发环境配置和兼容性解决方案',
    icon: 'fa-solid fa-laptop',
    size: '解决方案 • MD文档'
  }
])

// 测试文档列表
const testingDocs = reactive([
  {
    id: 'testing-plan',
    title: '综合测试规划',
    description: '系统测试策略、安全规范和质量保证流程',
    icon: 'fa-solid fa-clipboard-check',
    size: '测试规范 • MD文档'
  },
  {
    id: 'testing-programs',
    title: '测试程序指南',
    description: '测试代码编写规范、执行流程和结果评估标准',
    icon: 'fa-solid fa-code',
    size: '程序指南 • MD文档'
  }
])

// 打开文档
const openDocument = (docId: string) => {
  // 根据文档ID设置相应的标题和内容
  const docMap: Record<string, { title: string; content: string }> = {
    'system': {
      title: 'XC-RECON系统设计文档',
      content: generateSystemDocContent()
    },
    'docs-index': {
      title: '项目文档索引',
      content: generateDocsIndexContent()
    },
    'fr3-analysis': {
      title: 'FR3机械臂技术分析',
      content: generateFR3AnalysisContent()
    },
    'hermes-control': {
      title: 'Hermes底盘控制文档',
      content: generateHermesControlContent()
    },
    'gemini335-vision': {
      title: 'Gemini335视觉系统',
      content: generateGeminiVisionContent()
    },
    'robot-config': {
      title: '机器人配置参考',
      content: generateRobotConfigContent()
    },
    'deployment-guide': {
      title: '部署指南',
      content: generateDeploymentGuideContent()
    },
    'dual-arm-integration': {
      title: '双臂集成指南',
      content: generateDualArmIntegrationContent()
    },
    'cross-platform': {
      title: '跨平台开发方案',
      content: generateCrossPlatformContent()
    },
    'testing-plan': {
      title: '综合测试规划',
      content: generateTestingPlanContent()
    },
    'testing-programs': {
      title: '测试程序指南',
      content: generateTestingProgramsContent()
    }
  }

  const doc = docMap[docId]
  if (doc) {
    currentDocTitle.value = doc.title
    currentDocContent.value = doc.content
    showDocViewer.value = true
  }
}

// 关闭文档查看器
const closeDocViewer = () => {
  showDocViewer.value = false
  currentDocTitle.value = ''
  currentDocContent.value = ''
}

// 生成文档内容的函数（简化版本，实际应该读取真实文档）
const generateSystemDocContent = () => {
  return `
    <h2>XC-RECON-V2 系统架构概述</h2>
    <p>XC-RECON-V2是一个现代化的双臂类人形机器人控制系统，采用前后端分离架构设计。</p>
    
    <h3>核心特性</h3>
    <ul>
      <li><strong>双臂协调控制</strong>：法奥意威FR3协作机器人双臂系统</li>
      <li><strong>移动平台</strong>：思岚科技Hermes自主导航底盘</li>
      <li><strong>视觉感知</strong>：Gemini335 TOF深度相机系统</li>
      <li><strong>智能交互</strong>：人脸识别、语音对话、梯控系统</li>
    </ul>
    
    <h3>技术栈</h3>
    <ul>
      <li><strong>前端</strong>：Vue 3 + TypeScript + Element Plus</li>
      <li><strong>后端</strong>：FastAPI + Python 3.11 + PostgreSQL</li>
      <li><strong>通信</strong>：WebSocket + RESTful API</li>
      <li><strong>部署</strong>：Docker + 跨平台支持</li>
    </ul>
    
    <h3>系统架构</h3>
    <p>系统采用分层架构设计，包括硬件抽象层、控制逻辑层、业务服务层和用户界面层。</p>
    
    <p><em>注：完整文档内容请参考项目根目录的 xc_recon_system.md 文件</em></p>
  `
}

const generateDocsIndexContent = () => {
  return `
    <h2>XC-RECON-V2 项目文档索引</h2>
    <p>本文档库包含项目重构所需的所有技术资料、设计规范和开发指南。</p>
    
    <h3>📁 技术文档 (technical/)</h3>
    <ul>
      <li><strong>xc_os_context.md</strong> - 项目核心背景和技术栈</li>
      <li><strong>PROJECT_TECHNICAL_OVERVIEW.md</strong> - 系统架构和模块功能</li>
      <li><strong>GUI_DESCRIPTION.md</strong> - 界面功能详细说明</li>
    </ul>
    
    <h3>📁 硬件文档 (hardware/)</h3>
    <ul>
      <li><strong>FR3_ROBOT_ANALYSIS.md</strong> - FR3机械臂分析</li>
      <li><strong>fr3_control_doc.md</strong> - 机械臂控制API</li>
      <li><strong>hermes_control_doc.md</strong> - Hermes底盘控制</li>
      <li><strong>gemini335_control_doc.md</strong> - 视觉系统文档</li>
    </ul>
    
    <h3>📁 设计文档 (design/)</h3>
    <ul>
      <li><strong>design_reference/</strong> - 完整设计参考</li>
      <li><strong>component_specs.md</strong> - 组件规范</li>
      <li><strong>style_guide.md</strong> - 样式指南</li>
      <li><strong>ui_mockups/</strong> - UI原型设计</li>
    </ul>
    
    <h3>📁 测试文档 (testing/)</h3>
    <ul>
      <li><strong>Testing_Plan.md</strong> - 综合测试规划</li>
      <li><strong>Testing_Programs_Guide.md</strong> - 测试程序指南</li>
    </ul>
    
    <p><em>完整文档结构请参考 docs/README.md 文件</em></p>
  `
}

const generateFR3AnalysisContent = () => {
  return `
    <h2>FR3机械臂技术分析</h2>
    <p>法奥意威FR3协作机器人是一款6自由度轻量化协作机械臂，专为人机协作场景设计。</p>
    
    <h3>技术参数</h3>
    <ul>
      <li><strong>自由度</strong>：6轴</li>
      <li><strong>最大负载</strong>：3kg</li>
      <li><strong>工作半径</strong>：850mm</li>
      <li><strong>重复定位精度</strong>：±0.1mm</li>
      <li><strong>通信接口</strong>：Ethernet TCP/IP</li>
    </ul>
    
    <h3>DH参数</h3>
    <p>基于标准DH参数模型建立的运动学方程，支持正逆运动学求解。</p>
    
    <h3>控制接口</h3>
    <ul>
      <li><strong>Python SDK</strong>：完整的Python控制库</li>
      <li><strong>实时控制</strong>：支持位置、速度、力控制模式</li>
      <li><strong>安全机制</strong>：碰撞检测、紧急停止、安全边界</li>
    </ul>
    
    <p><em>详细技术分析请参考 docs/hardware/FR3_ROBOT_ANALYSIS.md</em></p>
  `
}

const generateHermesControlContent = () => {
  return `
    <h2>Hermes底盘控制文档</h2>
    <p>思岚科技Hermes是一款自主导航移动底盘，集成SLAM算法和路径规划功能。</p>
    
    <h3>核心功能</h3>
    <ul>
      <li><strong>自主导航</strong>：基于激光SLAM的精确定位</li>
      <li><strong>路径规划</strong>：动态避障和最优路径计算</li>
      <li><strong>远程控制</strong>：RESTful API接口</li>
      <li><strong>状态监控</strong>：实时位置、速度、电量信息</li>
    </ul>
    
    <h3>API接口</h3>
    <ul>
      <li><strong>运动控制</strong>：/api/v1/move</li>
      <li><strong>位置信息</strong>：/api/v1/location</li>
      <li><strong>地图管理</strong>：/api/v1/map</li>
      <li><strong>导航任务</strong>：/api/v1/navigation</li>
    </ul>
    
    <h3>网络配置</h3>
    <p>默认IP地址：192.168.58.2，HTTP端口：1448</p>
    
    <p><em>完整API文档请参考 docs/hardware/hermes_api/ 目录</em></p>
  `
}

const generateGeminiVisionContent = () => {
  return `
    <h2>Gemini335视觉系统</h2>
    <p>Gemini335是一款高精度TOF深度相机，提供彩色图像和深度信息。</p>
    
    <h3>技术规格</h3>
    <ul>
      <li><strong>深度范围</strong>：0.3-5m</li>
      <li><strong>深度精度</strong>：±2mm@1m</li>
      <li><strong>RGB分辨率</strong>：1920×1080@30fps</li>
      <li><strong>深度分辨率</strong>：640×480@30fps</li>
      <li><strong>接口</strong>：USB 3.0</li>
    </ul>
    
    <h3>SDK支持</h3>
    <ul>
      <li><strong>OpenNI2</strong>：标准3D视觉接口</li>
      <li><strong>Python API</strong>：简化的Python控制库</li>
      <li><strong>PCL集成</strong>：点云处理支持</li>
    </ul>
    
    <h3>应用场景</h3>
    <ul>
      <li>3D物体检测与识别</li>
      <li>机械臂视觉引导</li>
      <li>环境三维重建</li>
      <li>人体姿态检测</li>
    </ul>
    
    <p><em>详细配置指南请参考 docs/hardware/gemini335/ 目录</em></p>
  `
}

const generateRobotConfigContent = () => {
  return `
    <h2>机器人配置参考</h2>
    <p>系统配置文件模板和网络设置指南。</p>
    
    <h3>网络配置</h3>
    <pre><code>{
  "fr3_left": {
    "ip": "192.168.58.2",
    "port": 20003
  },
  "fr3_right": {
    "ip": "192.168.58.3", 
    "port": 20003
  },
  "hermes_chassis": {
    "ip": "192.168.58.4",
    "port": 1448
  }
}</code></pre>
    
    <h3>系统参数</h3>
    <ul>
      <li><strong>控制频率</strong>：100Hz</li>
      <li><strong>通信超时</strong>：3000ms</li>
      <li><strong>安全限位</strong>：已启用</li>
    </ul>
    
    <p><em>完整配置文件请参考 docs/hardware/robot_config_reference.json</em></p>
  `
}

const generateDeploymentGuideContent = () => {
  return `
    <h2>部署指南</h2>
    <p>XC-RECON-V2系统的完整部署和配置流程。</p>
    
    <h3>环境要求</h3>
    <ul>
      <li><strong>操作系统</strong>：Windows 11 / macOS 12+ / Ubuntu 20.04+</li>
      <li><strong>Python</strong>：3.11.10</li>
      <li><strong>Node.js</strong>：18+</li>
      <li><strong>数据库</strong>：PostgreSQL 14+</li>
    </ul>
    
    <h3>安装步骤</h3>
    <ol>
      <li>克隆项目代码</li>
      <li>配置Python虚拟环境</li>
      <li>安装后端依赖</li>
      <li>配置数据库</li>
      <li>安装前端依赖</li>
      <li>配置硬件连接</li>
    </ol>
    
    <h3>常见问题</h3>
    <ul>
      <li>硬件连接超时 → 检查网络配置</li>
      <li>依赖安装失败 → 使用镜像源</li>
      <li>权限问题 → 以管理员身份运行</li>
    </ul>
    
    <p><em>详细部署指南请参考 docs/development/DEPLOYMENT_GUIDE.md</em></p>
  `
}

const generateDualArmIntegrationContent = () => {
  return `
    <h2>双臂集成指南</h2>
    <p>双机械臂协调控制的实现方法和同步机制设计。</p>
    
    <h3>协调控制架构</h3>
    <ul>
      <li><strong>主从模式</strong>：一主一从协调运动</li>
      <li><strong>对称模式</strong>：双臂镜像对称运动</li>
      <li><strong>独立模式</strong>：双臂独立并行任务</li>
    </ul>
    
    <h3>同步机制</h3>
    <ul>
      <li><strong>时间同步</strong>：统一时间基准</li>
      <li><strong>运动同步</strong>：轨迹协调规划</li>
      <li><strong>状态同步</strong>：实时状态共享</li>
    </ul>
    
    <h3>安全机制</h3>
    <ul>
      <li>碰撞检测与避免</li>
      <li>工作空间限制</li>
      <li>紧急停止协议</li>
    </ul>
    
    <p><em>完整集成指南请参考 docs/development/dual_arm_integration_guide.md</em></p>
  `
}

const generateCrossPlatformContent = () => {
  return `
    <h2>跨平台开发方案</h2>
    <p>Mac/Windows协作开发环境配置和兼容性解决方案。</p>
    
    <h3>开发环境</h3>
    <ul>
      <li><strong>Mac环境</strong>：前端开发、UI设计</li>
      <li><strong>Windows环境</strong>：硬件测试、集成验证</li>
    </ul>
    
    <h3>兼容性处理</h3>
    <ul>
      <li><strong>路径处理</strong>：统一使用POSIX路径</li>
      <li><strong>编码问题</strong>：UTF-8编码标准化</li>
      <li><strong>依赖管理</strong>：使用虚拟环境</li>
    </ul>
    
    <h3>代码同步</h3>
    <ul>
      <li>Git工作流规范</li>
      <li>跨平台CI/CD配置</li>
      <li>环境变量管理</li>
    </ul>
    
    <p><em>详细方案请参考 docs/development/CROSS_PLATFORM_SOLUTION.md</em></p>
  `
}

const generateTestingPlanContent = () => {
  return `
    <h2>综合测试规划</h2>
    <p>系统测试策略、安全规范和质量保证流程。</p>
    
    <h3>测试层级</h3>
    <ul>
      <li><strong>单元测试</strong>：覆盖率 > 80%</li>
      <li><strong>集成测试</strong>：模块间接口测试</li>
      <li><strong>系统测试</strong>：端到端功能验证</li>
      <li><strong>安全测试</strong>：硬件安全验证</li>
    </ul>
    
    <h3>测试工具</h3>
    <ul>
      <li><strong>前端</strong>：Vitest + Cypress</li>
      <li><strong>后端</strong>：pytest + FastAPI TestClient</li>
      <li><strong>硬件</strong>：自定义测试框架</li>
    </ul>
    
    <h3>安全标准</h3>
    <ul>
      <li>IEC 61508 功能安全标准</li>
      <li>ISO 13849 机械安全标准</li>
      <li>碰撞检测验证</li>
      <li>紧急停止测试</li>
    </ul>
    
    <p><em>详细测试计划请参考 docs/testing/Testing_Plan.md</em></p>
  `
}

const generateTestingProgramsContent = () => {
  return `
    <h2>测试程序指南</h2>
    <p>测试代码编写规范、执行流程和结果评估标准。</p>
    
    <h3>测试代码规范</h3>
    <ul>
      <li><strong>命名规范</strong>：test_功能_场景_期望结果</li>
      <li><strong>结构规范</strong>：Arrange-Act-Assert模式</li>
      <li><strong>数据驱动</strong>：参数化测试用例</li>
    </ul>
    
    <h3>测试执行</h3>
    <ul>
      <li><strong>自动化执行</strong>：CI/CD集成</li>
      <li><strong>手动测试</strong>：硬件验证场景</li>
      <li><strong>回归测试</strong>：版本发布验证</li>
    </ul>
    
    <h3>结果评估</h3>
    <ul>
      <li>测试覆盖率分析</li>
      <li>性能基准对比</li>
      <li>安全合规检查</li>
      <li>缺陷趋势分析</li>
    </ul>
    
    <p><em>详细指南请参考 docs/testing/Testing_Programs_Guide.md</em></p>
  `
}
</script>

<style scoped>
.tech-support-page {
  min-height: 100vh;
  background: #f8f9fa;
  padding: 20px;
}

/* 页面标题 */
.page-header {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title i {
  color: #409EFF;
}

.page-description {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 文档分类 */
.doc-categories {
  max-width: 1200px;
  margin: 0 auto;
}

.doc-category {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.category-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-title i {
  color: #409EFF;
}

/* 文档列表 */
.doc-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.doc-item:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.doc-item.featured {
  border-color: #409EFF;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f3ff 100%);
}

.doc-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409EFF;
  color: white;
  flex-shrink: 0;
}

.doc-icon i {
  font-size: 20px;
}

.doc-content {
  flex: 1;
  min-width: 0;
}

.doc-title {
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
}

.doc-description {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 8px;
}

.doc-size {
  font-size: 12px;
  color: #999;
}

.doc-action {
  color: #409EFF;
  flex-shrink: 0;
}

.doc-action i {
  font-size: 16px;
}

/* 文档查看器模态框 */
.doc-viewer-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.doc-viewer-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 900px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.doc-viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.doc-viewer-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.doc-viewer-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.markdown-content {
  line-height: 1.6;
  color: #333;
}

.markdown-content h2 {
  color: #2c3e50;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 8px;
  margin-bottom: 16px;
}

.markdown-content h3 {
  color: #2c3e50;
  margin-top: 24px;
  margin-bottom: 12px;
}

.markdown-content ul, .markdown-content ol {
  margin-bottom: 16px;
  padding-left: 24px;
}

.markdown-content li {
  margin-bottom: 8px;
}

.markdown-content strong {
  color: #2c3e50;
}

.markdown-content pre {
  background: #f5f5f5;
  border-radius: 4px;
  padding: 16px;
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-content code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
}

.markdown-content em {
  color: #666;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tech-support-page {
    padding: 12px;
  }
  
  .page-header {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .doc-category {
    padding: 16px;
  }
  
  .doc-list {
    grid-template-columns: 1fr;
  }
  
  .doc-item {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .doc-viewer-modal {
    padding: 12px;
  }
  
  .doc-viewer-header {
    padding: 16px;
  }
  
  .doc-viewer-body {
    padding: 16px;
  }
}
</style>