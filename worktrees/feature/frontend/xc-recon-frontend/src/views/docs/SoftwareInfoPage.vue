<template>
  <div class="software-info-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="fa-solid fa-info-circle"></i>
          软件信息
        </h1>
        <p class="page-description">
          XC-RECON-V2 双臂类人形机器人控制系统 - 现代化企业级机器人控制平台
        </p>
      </div>
    </div>

    <!-- 软件概览 -->
    <div class="software-overview">
      <div class="overview-grid">
        <div class="overview-card">
          <div class="card-icon">
            <i class="fa-solid fa-robot"></i>
          </div>
          <div class="card-content">
            <h3>系统名称</h3>
            <p>XC-RECON-V2</p>
            <span class="card-subtitle">双臂类人形机器人控制系统</span>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">
            <i class="fa-solid fa-code-branch"></i>
          </div>
          <div class="card-content">
            <h3>版本信息</h3>
            <p>v3.0.1 (Build {{ buildNumber }})</p>
            <span class="card-subtitle">基于FastAPI + Vue3重构版本</span>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">
            <i class="fa-solid fa-calendar"></i>
          </div>
          <div class="card-content">
            <h3>发布日期</h3>
            <p>2025年7月</p>
            <span class="card-subtitle">企业级重构完成</span>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">
            <i class="fa-solid fa-shield-alt"></i>
          </div>
          <div class="card-content">
            <h3>架构类型</h3>
            <p>微服务架构</p>
            <span class="card-subtitle">前后端分离、云原生</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 技术架构 -->
    <div class="architecture-section">
      <h2 class="section-title">
        <i class="fa-solid fa-sitemap"></i>
        技术架构
      </h2>
      
      <div class="architecture-grid">
        <!-- 前端技术栈 -->
        <div class="tech-stack-card">
          <h3 class="stack-title">
            <i class="fa-solid fa-desktop"></i>
            前端技术栈
          </h3>
          <div class="tech-list">
            <div class="tech-item">
              <span class="tech-name">Vue 3</span>
              <span class="tech-desc">现代化前端框架</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">TypeScript</span>
              <span class="tech-desc">类型安全开发</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Element Plus</span>
              <span class="tech-desc">企业级UI组件库</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Pinia</span>
              <span class="tech-desc">状态管理库</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Vite</span>
              <span class="tech-desc">高性能构建工具</span>
            </div>
          </div>
        </div>

        <!-- 后端技术栈 -->
        <div class="tech-stack-card">
          <h3 class="stack-title">
            <i class="fa-solid fa-server"></i>
            后端技术栈
          </h3>
          <div class="tech-list">
            <div class="tech-item">
              <span class="tech-name">FastAPI</span>
              <span class="tech-desc">高性能API框架</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Python 3.11</span>
              <span class="tech-desc">现代Python运行时</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">PostgreSQL</span>
              <span class="tech-desc">企业级数据库</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">SQLAlchemy</span>
              <span class="tech-desc">ORM数据访问层</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Pydantic</span>
              <span class="tech-desc">数据验证框架</span>
            </div>
          </div>
        </div>

        <!-- 硬件集成 -->
        <div class="tech-stack-card">
          <h3 class="stack-title">
            <i class="fa-solid fa-microchip"></i>
            硬件平台
          </h3>
          <div class="tech-list">
            <div class="tech-item">
              <span class="tech-name">FR3双机械臂</span>
              <span class="tech-desc">法奥意威协作机器人</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Hermes底盘</span>
              <span class="tech-desc">思岚科技移动平台</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Gemini335</span>
              <span class="tech-desc">TOF深度相机系统</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">工控主机</span>
              <span class="tech-desc">x86架构控制系统</span>
            </div>
          </div>
        </div>

        <!-- 开发工具 -->
        <div class="tech-stack-card">
          <h3 class="stack-title">
            <i class="fa-solid fa-tools"></i>
            开发工具
          </h3>
          <div class="tech-list">
            <div class="tech-item">
              <span class="tech-name">Docker</span>
              <span class="tech-desc">容器化部署</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">Git</span>
              <span class="tech-desc">版本控制系统</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">VS Code</span>
              <span class="tech-desc">集成开发环境</span>
            </div>
            <div class="tech-item">
              <span class="tech-name">pytest</span>
              <span class="tech-desc">Python测试框架</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统特性 -->
    <div class="features-section">
      <h2 class="section-title">
        <i class="fa-solid fa-star"></i>
        核心特性
      </h2>
      
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fa-solid fa-handshake"></i>
          </div>
          <h3>双臂协调控制</h3>
          <p>支持双机械臂同步、异步、协调运动控制，实现复杂的人机协作任务</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fa-solid fa-route"></i>
          </div>
          <h3>自主导航</h3>
          <p>基于SLAM算法的精确定位和路径规划，支持动态避障和任务规划</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fa-solid fa-eye"></i>
          </div>
          <h3>视觉感知</h3>
          <p>3D视觉系统集成，支持物体识别、姿态估计和环境三维重建</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fa-solid fa-brain"></i>
          </div>
          <h3>智能交互</h3>
          <p>人脸识别、语音对话、梯控系统，提供完整的人机交互解决方案</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fa-solid fa-cube"></i>
          </div>
          <h3>3D仿真</h3>
          <p>高保真机器人仿真环境，支持轨迹预览、碰撞检测和任务验证</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fa-solid fa-shield-check"></i>
          </div>
          <h3>安全保障</h3>
          <p>多层级安全机制，符合工业安全标准，保障人机协作安全</p>
        </div>
      </div>
    </div>

    <!-- 开发团队 -->
    <div class="team-section">
      <h2 class="section-title">
        <i class="fa-solid fa-users"></i>
        开发团队
      </h2>
      
      <div class="team-info">
        <div class="developer-card">
          <div class="developer-avatar">
            <i class="fa-solid fa-user-tie"></i>
          </div>
          <div class="developer-info">
            <h3>Kevin Yuan</h3>
            <p class="developer-title">项目负责人 & 首席架构师</p>
            <p class="developer-desc">
              专注于具身智能机器人、协作机械臂等安全关键系统的开发，
              在机器人控制、系统架构和AI集成方面拥有丰富经验。
            </p>
            
            <div class="contact-info">
              <div class="contact-item">
                <i class="fa-solid fa-envelope"></i>
                <a href="mailto:kevindreamfly@gmail.com">kevindreamfly@gmail.com</a>
              </div>
              <div class="contact-item">
                <i class="fa-brands fa-github"></i>
                <a href="https://github.com/shuyx" target="_blank">github.com/shuyx</a>
              </div>
            </div>
          </div>
        </div>
        
        <div class="project-stats">
          <h3>项目统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-number">50,000+</span>
              <span class="stat-label">代码行数</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">25+</span>
              <span class="stat-label">功能模块</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">6</span>
              <span class="stat-label">开发月数</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">100%</span>
              <span class="stat-label">完成度</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 技术文档链接 -->
    <div class="docs-section">
      <h2 class="section-title">
        <i class="fa-solid fa-book"></i>
        相关文档
      </h2>
      
      <div class="docs-links">
        <router-link to="/docs/technical-support" class="doc-link-card">
          <div class="doc-link-icon">
            <i class="fa-solid fa-life-ring"></i>
          </div>
          <div class="doc-link-content">
            <h3>技术文档</h3>
            <p>查看完整的技术文档、API参考和开发指南</p>
          </div>
          <div class="doc-link-arrow">
            <i class="fa-solid fa-arrow-right"></i>
          </div>
        </router-link>
        
        <a href="https://github.com/shuyx" target="_blank" class="doc-link-card">
          <div class="doc-link-icon">
            <i class="fa-brands fa-github"></i>
          </div>
          <div class="doc-link-content">
            <h3>开源项目</h3>
            <p>访问GitHub查看更多开源项目和技术分享</p>
          </div>
          <div class="doc-link-arrow">
            <i class="fa-solid fa-external-link-alt"></i>
          </div>
        </a>
      </div>
    </div>

    <!-- 版权信息 -->
    <div class="copyright-section">
      <div class="copyright-content">
        <p>© 2025 祥承 Technology. All rights reserved.</p>
        <p class="copyright-desc">
          XC-RECON-V2是一个专业的机器人控制系统，遵循工业安全标准，
          为企业级应用提供可靠、安全、高效的机器人控制解决方案。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 动态生成构建版本号
const buildNumber = ref('')

onMounted(() => {
  // 生成基于时间的构建号
  const now = new Date()
  const year = now.getFullYear().toString().slice(-2)
  const month = (now.getMonth() + 1).toString().padStart(2, '0')
  const day = now.getDate().toString().padStart(2, '0')
  buildNumber.value = `${year}${month}${day}`
})
</script>

<style scoped>
.software-info-page {
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

/* 软件概览 */
.software-overview {
  max-width: 1200px;
  margin: 0 auto 24px auto;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.overview-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409EFF, #66B3FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.card-icon i {
  font-size: 20px;
}

.card-content h3 {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
  font-weight: normal;
}

.card-content p {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
}

.card-subtitle {
  font-size: 12px;
  color: #999;
}

/* 通用段落样式 */
.section-title {
  font-size: 22px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  color: #409EFF;
}

/* 技术架构 */
.architecture-section {
  max-width: 1200px;
  margin: 0 auto 32px auto;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.architecture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.tech-stack-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.stack-title {
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stack-title i {
  color: #409EFF;
}

.tech-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tech-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tech-name {
  font-size: 14px;
  font-weight: bold;
  color: #2c3e50;
}

.tech-desc {
  font-size: 12px;
  color: #666;
}

/* 系统特性 */
.features-section {
  max-width: 1200px;
  margin: 0 auto 32px auto;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.feature-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 1px solid #e4e7ed;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  border-color: #409EFF;
}

.feature-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409EFF, #66B3FF);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px auto;
  color: white;
}

.feature-icon i {
  font-size: 24px;
}

.feature-card h3 {
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 8px;
}

.feature-card p {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

/* 开发团队 */
.team-section {
  max-width: 1200px;
  margin: 0 auto 32px auto;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.team-info {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
}

.developer-card {
  display: flex;
  gap: 20px;
}

.developer-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409EFF, #66B3FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.developer-avatar i {
  font-size: 32px;
}

.developer-info h3 {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
}

.developer-title {
  font-size: 14px;
  color: #409EFF;
  font-weight: bold;
  margin-bottom: 12px;
}

.developer-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.contact-item i {
  color: #409EFF;
  width: 16px;
}

.contact-item a {
  color: #409EFF;
  text-decoration: none;
}

.contact-item a:hover {
  text-decoration: underline;
}

.project-stats h3 {
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.stat-number {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

/* 技术文档链接 */
.docs-section {
  max-width: 1200px;
  margin: 0 auto 32px auto;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.docs-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.doc-link-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.doc-link-card:hover {
  border-color: #409EFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.1);
}

.doc-link-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409EFF, #66B3FF);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.doc-link-icon i {
  font-size: 20px;
}

.doc-link-content {
  flex: 1;
}

.doc-link-content h3 {
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
}

.doc-link-content p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.doc-link-arrow {
  color: #409EFF;
  flex-shrink: 0;
}

/* 版权信息 */
.copyright-section {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.copyright-content p {
  color: #666;
  margin-bottom: 8px;
}

.copyright-desc {
  font-size: 14px;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .software-info-page {
    padding: 12px;
  }
  
  .page-header,
  .architecture-section,
  .features-section,
  .team-section,
  .docs-section,
  .copyright-section {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .overview-grid,
  .architecture-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .team-info {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .developer-card {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .docs-links {
    grid-template-columns: 1fr;
  }
}
</style>