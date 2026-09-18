<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getJSON } from '../api'

const QUALITIES = [
  { value: null, label: '全部' },
  { value: 'clean', label: '正常 clean' },
  { value: 'dirty', label: '偏高 dirty' },
]
const VALID = ['dirty', 'clean']
const STORAGE_KEY = 'account_quality_filter'
const norm = q => (VALID.includes(q) ? q : null)
const kindLabel = { bill: '阶梯测算', compare: '尖峰对比' }

const route = useRoute()
const router = useRouter()
const stats = ref(null)
const data = ref(null)
const quality = ref(null)
const loading = ref(false)
const error = ref('')

async function loadStats() {
  stats.value = await getJSON('/api/dashboard')
}

async function loadAccounts() {
  loading.value = true
  error.value = ''
  try {
    const qs = quality.value ? `?quality=${encodeURIComponent(quality.value)}` : ''
    data.value = await getJSON(`/api/accounts${qs}`)
  } catch (e) {
    error.value = String(e.message || e)
  } finally {
    loading.value = false
  }
}

async function selectQuality(q) {
  const next = norm(q)
  if (next === quality.value) return
  quality.value = next
  if (next) sessionStorage.setItem(STORAGE_KEY, next)
  else sessionStorage.removeItem(STORAGE_KEY)
  await router.replace(next ? { query: { quality: next } } : { query: {} })
  loadAccounts()
}

onMounted(() => {
  // URL query 优先；从详情/侧边栏返回且 URL 无 query 时，沿用上次选择。
  const fromQuery = norm(route.query.quality)
  const fromStore = norm(sessionStorage.getItem(STORAGE_KEY))
  quality.value = fromQuery ?? fromStore ?? null
  if (quality.value && !fromQuery) {
    router.replace({ query: { quality: quality.value } })
  }
  loadStats()
  loadAccounts()
})

// 浏览器前进 / 后退
watch(
  () => route.query.quality,
  q => {
    const next = norm(q)
    if (next !== quality.value) {
      quality.value = next
      if (next) sessionStorage.setItem(STORAGE_KEY, next)
      else sessionStorage.removeItem(STORAGE_KEY)
      loadAccounts()
    }
  }
)
</script>
<template>
  <div class="page dash">
    <header><h1>用电总览</h1><p class="muted">阶梯累进 + 尖峰系数对照</p></header>
    <div class="tiles" v-if="stats">
      <div class="tile"><div class="hero-num">{{ stats.account_count }}</div><div class="muted">户号</div></div>
      <div class="tile"><div class="hero-num">{{ stats.reading_count }}</div><div class="muted">抄表</div></div>
      <div class="tile ok"><div class="hero-num">{{ stats.clean_accounts }}</div><div class="muted">正常对照</div></div>
      <div class="tile warn"><div class="hero-num">{{ stats.dirty_accounts }}</div><div class="muted">偏高种子</div></div>
    </div>

    <div class="panel filter-bar">
      <div class="seg" role="group" aria-label="按质量过滤户号">
        <button
          v-for="opt in QUALITIES" :key="opt.label"
          class="seg-btn" :class="{ active: quality === opt.value }"
          @click="selectQuality(opt.value)"
        >{{ opt.label }}</button>
      </div>
      <div class="count-line" v-if="data">
        当前 <strong class="hero-num" style="font-size:1.4rem">{{ data.filtered_count }}</strong> 户
        <span class="muted">/ 共 {{ data.total_count }} 户</span>
      </div>
    </div>

    <p v-if="error" class="warn-text">加载失败：{{ error }}</p>
    <table v-else-if="data">
      <thead><tr><th>名称</th><th>表号</th><th>备注</th><th>最近运行合计</th><th></th></tr></thead>
      <tbody>
        <tr v-for="a in data.items" :key="a.id">
          <td>{{ a.name }}</td>
          <td>{{ a.meter_no }}</td>
          <td class="muted">{{ a.note }}</td>
          <td>
            <template v-if="a.latest_run && a.latest_run.total != null">
              <strong>¥{{ a.latest_run.total }}</strong>
              <span class="muted run-kind">（{{ kindLabel[a.latest_run.kind] || a.latest_run.kind }}）</span>
            </template>
            <span v-else class="muted">—</span>
          </td>
          <td><router-link :to="{ path: `/accounts/${a.id}`, query: quality ? { quality } : {} }">详情</router-link></td>
        </tr>
      </tbody>
    </table>
    <p v-if="data && data.filtered_count !== data.items.length" class="warn-text">
      名单条数（{{ data.items.length }}）与计数（{{ data.filtered_count }}）不一致
    </p>
    <p v-if="data && !loading && data.items.length === 0" class="muted">该过滤条件下暂无户号。</p>

    <router-link to="/compare">去看尖峰对比 →</router-link>
  </div>
</template>
<style scoped>
.dash header { margin-bottom: 1rem; }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 1rem; }
.tile { background: var(--panel); padding: 1rem; border-radius: 12px; }
.tile.warn { border: 1px solid #e6a817; }
.tile.ok { border: 1px solid var(--accent); }
.filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.seg { display: inline-flex; gap: 0.4rem; }
.seg-btn { background: transparent; color: var(--text); border: 1px solid var(--muted); padding: 0.4rem 0.85rem; border-radius: 8px; cursor: pointer; font-weight: 600; }
.seg-btn.active { background: var(--accent); color: #111; border-color: var(--accent); }
.count-line { display: flex; align-items: baseline; gap: 0.35rem; }
.run-kind { font-size: 0.85rem; }
.warn-text { color: #e6a817; }
</style>
