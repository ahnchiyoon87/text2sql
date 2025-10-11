<template>
  <div class="result-table">
    <div class="table-header">
      <h3>결과 ({{ data.row_count }}행)</h3>
      <span class="execution-time">실행 시간: {{ data.execution_time_ms }}ms</span>
    </div>
    
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th v-for="col in data.columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in data.rows" :key="idx">
            <td v-for="(cell, cidx) in row" :key="cidx">
              {{ formatCell(cell) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  data: {
    columns: string[]
    rows: any[][]
    row_count: number
    execution_time_ms: number
  }
}>()

function formatCell(value: any): string {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return String(value)
}
</script>

<style scoped>
.result-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.table-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.execution-time {
  font-size: 0.9rem;
  color: #666;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
  position: sticky;
  top: 0;
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f0f0f0;
}

tbody tr:hover {
  background: #f8f9fa;
}
</style>

