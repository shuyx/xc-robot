import fs from 'fs'
import path from 'path'

// 要处理的文件列表
const files = [
  'src/components/layout/Sidebar.vue',
  'src/components/layout/Header.vue',
  'src/views/IconTest.vue'
]

// 替换规则
function replaceIcons(content) {
  // 替换基本的 FontAwesome 图标
  // 匹配模式：<i class="fa-solid fa-xxx"></i> 或 <i class="fa-solid fa-xxx" other-attrs></i>
  content = content.replace(
    /<i\s+class="(fa-[^"]+)"([^>]*)><\/i>/g,
    '<FaIcon icon="$1"$2 />'
  )
  
  // 替换带有其他属性的图标
  content = content.replace(
    /<i\s+([^>]*class="[^"]*fa-[^"]*"[^>]*)><\/i>/g,
    (match, attrs) => {
      // 提取 class 属性中的 FontAwesome 类
      const classMatch = attrs.match(/class="([^"]*)"/)
      if (classMatch) {
        const classes = classMatch[1]
        const faClasses = classes.split(' ').filter(c => c.startsWith('fa-')).join(' ')
        const otherClasses = classes.split(' ').filter(c => !c.startsWith('fa-')).join(' ')
        
        // 重构属性
        let newAttrs = attrs.replace(/class="[^"]*"/, '')
        if (otherClasses) {
          newAttrs += ` class="${otherClasses}"`
        }
        
        return `<FaIcon icon="fa-solid ${faClasses}" ${newAttrs} />`
      }
      return match
    }
  )
  
  // 处理动态绑定的图标
  content = content.replace(
    /<i\s+:class="([^"]+)"([^>]*)><\/i>/g,
    '<FaIcon :icon="$1" $2 />'
  )
  
  return content
}

// 处理文件
files.forEach(filePath => {
  const fullPath = path.resolve(filePath)
  if (fs.existsSync(fullPath)) {
    let content = fs.readFileSync(fullPath, 'utf8')
    
    // 检查是否已经导入了 FaIcon
    if (!content.includes('import FaIcon')) {
      // 查找 script setup 部分并添加导入
      content = content.replace(
        /(<script setup[^>]*>[\s\S]*?)(import.*from.*vue.*\n)/,
        '$1$2import FaIcon from \'@/components/common/FaIcon.vue\'\n'
      )
    }
    
    // 替换图标
    const newContent = replaceIcons(content)
    
    if (newContent !== content) {
      fs.writeFileSync(fullPath, newContent, 'utf8')
      console.log(`Updated: ${filePath}`)
    } else {
      console.log(`No changes needed: ${filePath}`)
    }
  } else {
    console.log(`File not found: ${filePath}`)
  }
})

console.log('Icon replacement completed!')