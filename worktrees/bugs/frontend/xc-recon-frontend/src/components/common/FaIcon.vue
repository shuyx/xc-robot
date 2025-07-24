<template>
  <FontAwesomeIcon :icon="iconArray" :class="className" :style="style" />
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon: string
  className?: string
  style?: any
}

const props = withDefaults(defineProps<Props>(), {
  className: '',
  style: undefined
})

// 将 CSS 类名转换为 FontAwesome 图标数组格式
const iconArray = computed(() => {
  const iconClass = props.icon
  
  // 解析图标类名：fa-solid fa-home -> ['fas', 'home']
  const parts = iconClass.split(' ')
  let prefix = 'fas' // 默认为 solid
  let iconName = ''
  
  for (const part of parts) {
    if (part.startsWith('fa-solid')) {
      prefix = 'fas'
    } else if (part.startsWith('fa-regular')) {
      prefix = 'far'
    } else if (part.startsWith('fa-brands')) {
      prefix = 'fab'
    } else if (part.startsWith('fa-') && part !== 'fa-solid' && part !== 'fa-regular' && part !== 'fa-brands') {
      iconName = part.substring(3) // 移除 'fa-' 前缀
    }
  }
  
  // 处理特殊情况的图标名称映射
  const iconNameMap: Record<string, string> = {
    'sync-alt': 'sync',
    'angle-up': 'angle-up',
    'angle-down': 'angle-down',
    'chevron-up': 'chevron-up',
    'chevron-down': 'chevron-down',
    'chevron-left': 'chevron-left',
    'chevron-right': 'chevron-right',
    'clipboard-list': 'clipboard-list',
    'chart-bar': 'chart-bar',
    'chart-pie': 'chart-pie',
    'chart-line': 'chart-line'
  }
  
  const finalIconName = iconNameMap[iconName] || iconName
  
  return [prefix, finalIconName]
})
</script>

<style scoped>
/* 保持与原有 FontAwesome CSS 的兼容性 */
:deep(.fa-icon) {
  display: inline-block;
  font-style: normal;
  font-variant: normal;
  text-rendering: auto;
  line-height: 1;
}
</style>