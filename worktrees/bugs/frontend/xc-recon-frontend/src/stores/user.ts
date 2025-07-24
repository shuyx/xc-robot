import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface User {
  id: string
  username: string
  email: string
  role: string
  created_at: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setUser(userData: User) {
    user.value = userData
  }

  function setToken(tokenValue: string) {
    token.value = tokenValue
    localStorage.setItem('access_token', tokenValue)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  // 模拟登录状态（开发阶段）
  function mockLogin() {
    const mockUser: User = {
      id: '1',
      username: 'admin',
      email: 'admin@xc-recon.com',
      role: 'admin',
      created_at: new Date().toISOString()
    }
    setUser(mockUser)
    setToken('mock-token-' + Date.now())
  }

  // 开发阶段自动模拟登录 (仅在开发环境)
  if (import.meta.env.DEV && !token.value) {
    mockLogin()
  }

  return { user, token, isAuthenticated, isAdmin, setUser, setToken, logout, mockLogin }
})