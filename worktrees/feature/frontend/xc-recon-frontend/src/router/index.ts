import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'
import { generateChildRoutes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      redirect: '/dashboard',
      children: [
        // 动态生成的子路由
        ...generateChildRoutes(),
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: {
        title: '用户登录',
        requiresAuth: false
      }
    },
    {
      path: '/404',
      name: '404',
      component: () => import('@/views/common/PlaceholderPage.vue'),
      meta: {
        title: '页面未找到'
      }
    },
    // 捕获所有未匹配的路由
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - XC-OS v3.0`
  } else {
    document.title = 'XC-OS v3.0 - 双臂类人形机器人控制系统'
  }
  
  // 身份验证检查
  const isAuthenticated = localStorage.getItem('access_token')
  
  if (to.path === '/login') {
    // 如果已登录用户访问登录页，重定向到主页
    if (isAuthenticated) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    // 需要认证的页面
    if (to.meta?.requiresAuth !== false && !isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  }
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  // 可以在这里添加错误日志上报
})

export default router
