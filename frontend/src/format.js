// 各户最近运行的合计摘要 → 一行短文本；无运行（空对象）时显示占位符
export function runSummaryText(summary) {
  if (!summary || !summary.kind) return '—'
  if (summary.kind === 'compare') return `峰 ¥${summary.peak_total} / 平 ¥${summary.plain_total}`
  return `合计 ¥${summary.total}`
}
