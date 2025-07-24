import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import fontawesome from './plugins/fontawesome'
import AppIcon from './components/common/AppIcon.vue'

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册全局图标组件
app.component('AppIcon', AppIcon)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.use(fontawesome)

app.mount('#app')
