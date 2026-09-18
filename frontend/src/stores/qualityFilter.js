import { ref } from 'vue'

// 模块级共享状态：路由切换不重置，从详情返回总览/户列表时过滤条件保持离开前的选择
export const quality = ref('all')

export const QUALITY_OPTIONS = [
  { value: 'all', label: '全部' },
  { value: 'clean', label: '正常对照' },
  { value: 'dirty', label: '偏高种子' },
]
