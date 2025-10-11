<template>
  <div class="chart-viewer">
    <div class="chart-selector" v-if="charts.length > 1">
      <button 
        v-for="(chart, idx) in charts" 
        :key="idx"
        @click="selectedIndex = idx"
        :class="{ active: selectedIndex === idx }"
      >
        {{ chart.title }}
      </button>
    </div>
    
    <div class="chart-container" v-if="selectedChart">
      <h4>{{ selectedChart.title }}</h4>
      <p class="chart-description">{{ selectedChart.description }}</p>
      <div ref="chartEl" class="chart"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import embed from 'vega-embed';
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import type { Chart } from '../services/api';

const props = defineProps<{
  charts: Chart[]
  tableData: { columns: string[], rows: any[][] }
}>()

const selectedIndex = ref(0)
const chartEl = ref<HTMLElement | null>(null)

const selectedChart = computed(() => props.charts[selectedIndex.value])

async function renderChart() {
  await nextTick()
  if (!chartEl.value || !selectedChart.value?.vega_lite) return
  
  try {
    const spec = {
      ...selectedChart.value.vega_lite,
      data: { 
        values: props.tableData.rows.map(row => {
          const obj: any = {}
          props.tableData.columns.forEach((col, idx) => {
            obj[col] = row[idx]
          })
          return obj
        })
      }
    }
    
    await embed(chartEl.value, spec, {
      actions: {
        export: true,
        source: false,
        compiled: false,
        editor: false
      }
    })
  } catch (err) {
    console.error('Chart rendering error:', err)
  }
}

watch(() => [selectedIndex.value, props.charts], () => {
  renderChart()
}, { deep: true })

onMounted(() => {
  renderChart()
})
</script>

<style scoped>
.chart-viewer {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.chart-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.5rem;
}

.chart-selector button {
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  transition: all 0.2s;
}

.chart-selector button:hover {
  color: #333;
}

.chart-selector button.active {
  color: #4CAF50;
  border-bottom-color: #4CAF50;
  font-weight: 600;
}

.chart-container h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.chart-description {
  color: #666;
  font-size: 0.9rem;
  margin: 0 0 1rem 0;
}

.chart {
  min-height: 400px;
}
</style>

