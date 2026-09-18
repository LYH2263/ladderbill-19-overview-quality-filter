<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON } from '../api'
import { quality } from '../stores/qualityFilter'
import { runSummaryText } from '../format'
import QualityFilter from '../components/QualityFilter.vue'

const items = ref([])
const total = ref(0)
const load = async () => {
  const data = await getJSON(`/api/accounts?quality=${quality.value}`)
  items.value = data.items
  total.value = data.total
}
onMounted(load)
watch(quality, load)
</script>

<template>
  <div class="page">
    <h1>户号列表</h1>
    <div class="panel">
      <div class="filter-row">
        <QualityFilter />
        <span class="muted">共 <strong>{{ total }}</strong> 户</span>
      </div>
      <table>
        <thead><tr><th>名称</th><th>表号</th><th>备注</th><th>最近运行合计</th><th></th></tr></thead>
        <tbody>
          <tr v-for="a in items" :key="a.id">
            <td>{{ a.name }}</td>
            <td>{{ a.meter_no }}</td>
            <td class="muted">{{ a.note }}</td>
            <td class="muted">{{ runSummaryText(a.run_summary) }}</td>
            <td><router-link :to="`/accounts/${a.id}`">详情</router-link></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.filter-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
strong { color: var(--accent); }
</style>
