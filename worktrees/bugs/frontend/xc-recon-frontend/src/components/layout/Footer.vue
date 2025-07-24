<template>
  <footer class="footer-container">
    <div class="footer-content">
      <!-- Left Side - Copyright Info -->
      <div class="footer-left">
        <div class="footer-brand">
          <!-- 移除XC_OS System文字，只保留版权信息 -->
        </div>
        <div class="footer-copyright">
          © 2025 祥承 Technology. All rights reserved.
        </div>
      </div>

      <!-- Center - Quick Links -->
      <div class="footer-center">
        <div class="footer-links">
          <router-link to="/docs/technical-support" class="footer-link">
            <i class="fa-solid fa-life-ring"></i>
            技术文档
          </router-link>
          <router-link to="/docs/software-info" class="footer-link">
            <i class="fa-solid fa-info-circle"></i>
            软件信息
          </router-link>
        </div>
      </div>

      <!-- Right Side - System Status -->
      <div class="footer-right">
        <div class="system-status">
          <div class="status-item">
            <i class="fa-solid fa-circle status-indicator online"></i>
            <span class="status-text">Author: Kevin Yuan</span>
          </div>
          <div class="footer-version">
            <span class="version-label">构建版本:</span>
            <span class="version-number">v3.0.1</span>
          </div>
        </div>
      </div>
    </div>
  </footer>
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
.footer-container {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-top: 1px solid #e4e7ed;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  box-shadow: 0 -2px 4px rgba(0,0,0,0.05);
  pointer-events: none;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 20px;
  max-width: 100%;
  pointer-events: auto;
}

/* Left Side */
.footer-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 6px;
}

.footer-icon {
  color: var(--primary-color, #409EFF);
  font-size: 14px;
}

.footer-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--secondary-color, #2c3e50);
}

.footer-copyright {
  font-size: 12px;
  color: #909399;
}

/* Center */
.footer-center {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 400px;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: var(--primary-color, #409EFF);
}

.footer-link i {
  font-size: 12px;
}

/* Right Side */
.footer-right {
  display: flex;
  align-items: center;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  font-size: 8px;
  animation: pulse 2s infinite;
}

.status-indicator.online {
  color: var(--success-color, #00A870);
}

.status-text {
  font-size: 12px;
  color: #606266;
}

.footer-version {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.version-label {
  color: #909399;
}

.version-number {
  color: var(--primary-color, #409EFF);
  font-weight: 500;
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .footer-content {
    padding: 0 12px;
  }
  
  .footer-center {
    display: none;
  }
  
  .footer-left {
    gap: 12px;
  }
  
  .footer-copyright {
    display: none;
  }
  
  .footer-links {
    gap: 16px;
  }
  
  .footer-link {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .footer-left .footer-brand {
    gap: 4px;
  }
  
  .footer-text {
    font-size: 12px;
  }
  
  .system-status {
    gap: 8px;
  }
  
  .version-label {
    display: none;
  }
}
</style>