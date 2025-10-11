import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService, type ColumnInfo, type TableInfo } from '../services/api'

export const useSchemaStore = defineStore('schema', () => {
  const tables = ref<TableInfo[]>([])
  const selectedTable = ref<TableInfo | null>(null)
  const selectedTableColumns = ref<ColumnInfo[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadTables(search?: string, schema?: string) {
    loading.value = true
    error.value = null

    try {
      tables.value = await apiService.getTables(search, schema)
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadTableColumns(tableName: string, schema: string = 'public') {
    loading.value = true
    error.value = null

    try {
      selectedTableColumns.value = await apiService.getTableColumns(tableName, schema)
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function selectTable(table: TableInfo) {
    selectedTable.value = table
    loadTableColumns(table.name, table.schema)
  }

  return {
    tables,
    selectedTable,
    selectedTableColumns,
    loading,
    error,
    loadTables,
    loadTableColumns,
    selectTable
  }
})

