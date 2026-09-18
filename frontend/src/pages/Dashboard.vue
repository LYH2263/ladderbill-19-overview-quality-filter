<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON } from '../api'
import { quality } from '../stores/qualityFilter'
import { runSummaryText } from '../format'
import QualityFilter from '../components/QualityFilter.vue'

const stats = ref(null)
const accounts = ref({ total: 0, items: [] })

const loadAccounts = async () => {
  accounts.value = await getJSON(`/api/accounts?quality=${quality.value}`)
}
onMounted(async () => {
  stats.value = await getJSON('/api/dashboard')
  loadAccounts()
})
watch(quality, loadAccounts)
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
    <div class="panel">
      <div class="filter-row">
        <QualityFilter />
        <span class="count muted">当前 <strong>{{ accounts.total }}</strong> 户</span>
      </div>
      <table>
        <thead><tr><th>名称</th><th>表号</th><th>最近运行合计</th><th></th></tr></thead>
        <tbody>
          <tr v-for="a in accounts.items" :key="a.id">
            <td>{{ a.name }}</td>
            <td>{{ a.meter_no }}</td>
            <td class="muted">{{ runSummaryText(a.run_summary) }}</td>
            <td><router-link :to="`/accounts/${a.id}`">详情</router-link></td>
          </tr>
        </tbody>
      </table>
    </div>
    <router-link to="/compare">去看尖峰对比 →</router-link>
  </div>
</template>

<style scoped>
.dash header { margin-bottom: 1rem; }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 1rem; }
.tile { background: var(--panel); padding: 1rem; border-radius: 12px; }
.tile.warn { border: 1px solid #e6a817; }
.tile.ok { border: 1px solid var(--accent); }
.filter-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.count strong { color: var(--accent); font-size: 1.25rem; }
</style>
