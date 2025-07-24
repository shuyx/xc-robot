<template>
  <div class="icon-test-page">
    <h2>图标测试页面</h2>
    
    <div class="test-section">
      <h3>菜单图标测试</h3>
      <div class="icon-grid">
        <!-- 一级菜单图标 -->
        <div class="icon-item">
          <i class="fa-solid fa-bolt"></i>
          <span>fa-bolt (快速启动)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-plug"></i>
          <span>fa-plug (设备连接)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-robot"></i>
          <span>fa-robot (机器人控制)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-comments"></i>
          <span>fa-comments (智能交互)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-flask"></i>
          <span>fa-flask (场景测试)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-bullseye"></i>
          <span>fa-bullseye (仿真规划)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-eye"></i>
          <span>fa-eye (视觉感知)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-chart-bar"></i>
          <span>fa-chart-bar (数据监控)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-gear"></i>
          <span>fa-gear (系统管理)</span>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h3>折叠/展开图标测试</h3>
      <div class="icon-grid">
        <div class="icon-item">
          <i class="fa-solid fa-angle-down"></i>
          <span>fa-angle-down (展开)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-angle-up"></i>
          <span>fa-angle-up (折叠)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-chevron-down"></i>
          <span>fa-chevron-down (备选1)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-chevron-up"></i>
          <span>fa-chevron-up (备选2)</span>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h3>二级菜单图标测试</h3>
      <div class="icon-grid">
        <div class="icon-item">
          <i class="fa-solid fa-clipboard-list"></i>
          <span>fa-clipboard-list (主界面)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-star"></i>
          <span>fa-star (收藏功能)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-clock"></i>
          <span>fa-clock (最近使用)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-user"></i>
          <span>fa-user (人脸识别)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-comment"></i>
          <span>fa-comment (智能对话)</span>
        </div>
        <div class="icon-item">
          <i class="fa-solid fa-building"></i>
          <span>fa-building (梯控系统)</span>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h3>Element Plus 图标测试</h3>
      <div class="icon-grid">
        <div class="icon-item">
          <el-icon><House /></el-icon>
          <span>House</span>
        </div>
        <div class="icon-item">
          <el-icon><User /></el-icon>
          <span>User</span>
        </div>
        <div class="icon-item">
          <el-icon><Setting /></el-icon>
          <span>Setting</span>
        </div>
        <div class="icon-item">
          <el-icon><Connection /></el-icon>
          <span>Connection</span>
        </div>
      </div>
    </div>

    <div class="test-section">
      <h3>CSS 检查</h3>
      <div class="css-info">
        <p>FontAwesome CSS 是否加载：<span id="fa-check">检查中...</span></p>
        <p>字体文件是否加载：<span id="font-check">检查中...</span></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { House, User, Setting, Connection } from '@element-plus/icons-vue'

// 检查FontAwesome是否正确加载
onMounted(() => {
  // 检查CSS是否加载
  const checkFontAwesome = () => {
    const faCheck = document.getElementById('fa-check')
    const fontCheck = document.getElementById('font-check')
    
    if (faCheck && fontCheck) {
      // 检查是否有FontAwesome样式
      const testEl = document.createElement('i')
      testEl.className = 'fa-solid fa-home'
      testEl.style.opacity = '0'
      testEl.style.position = 'absolute'
      document.body.appendChild(testEl)
      
      const styles = window.getComputedStyle(testEl)
      const fontFamily = styles.fontFamily
      
      document.body.removeChild(testEl)
      
      if (fontFamily.includes('Font Awesome')) {
        faCheck.textContent = '✅ 已加载'
        faCheck.style.color = 'green'
        fontCheck.textContent = '✅ 字体已加载'
        fontCheck.style.color = 'green'
      } else {
        faCheck.textContent = '❌ 未加载'
        faCheck.style.color = 'red'
        fontCheck.textContent = '❌ 字体未加载'
        fontCheck.style.color = 'red'
      }
    }
  }
  
  // 延迟检查以确保CSS完全加载
  setTimeout(checkFontAwesome, 500)
})
</script>

<style scoped>
.icon-test-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: white;
}

.test-section h3 {
  margin-top: 0;
  color: #409EFF;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 10px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #f9f9f9;
}

.icon-item i,
.icon-item .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
  color: #409EFF;
}

.icon-item span {
  font-size: 12px;
  color: #666;
  text-align: center;
}

.css-info {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 6px;
}

.css-info p {
  margin: 8px 0;
  font-family: monospace;
}
</style>