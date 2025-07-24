<template>
  <!-- 动态选择使用 FontAwesome 还是 Element Plus 图标 -->
  <font-awesome-icon 
    v-if="isFontAwesome" 
    :icon="faIcon" 
    v-bind="$attrs"
  />
  <i 
    v-else 
    :class="icon" 
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon: string
}

const props = defineProps<Props>()

// 检查是否是 FontAwesome 图标
const isFontAwesome = computed(() => {
  return props.icon.includes('fa-')
})

// 转换为 FontAwesome 图标格式
const faIcon = computed(() => {
  if (!isFontAwesome.value) return null
  
  const iconClass = props.icon
  const parts = iconClass.split(' ')
  
  let prefix = 'fas' // 默认为 solid
  let iconName = ''
  
  for (const part of parts) {
    if (part === 'fa-solid' || part === 'fas') {
      prefix = 'fas'
    } else if (part === 'fa-regular' || part === 'far') {
      prefix = 'far'
    } else if (part === 'fa-brands' || part === 'fab') {
      prefix = 'fab'
    } else if (part.startsWith('fa-') && !['fa-solid', 'fa-regular', 'fa-brands'].includes(part)) {
      iconName = part.substring(3) // 移除 'fa-' 前缀
    }
  }
  
  return [prefix, iconName]
})
</script>

<style scoped>
/* 继承父组件样式 */
</style>