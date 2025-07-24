import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import type { App } from 'vue'

// 自动导入所有图标 - 更简洁的方案
import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fab } from '@fortawesome/free-brands-svg-icons'

// 将整个图标库添加到FontAwesome
library.add(fas, far, fab)

export default {
  install(app: App) {
    app.component('FontAwesomeIcon', FontAwesomeIcon)
  }
}