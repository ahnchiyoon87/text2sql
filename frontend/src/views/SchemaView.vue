<template>
  <div class="schema-view">
    <div class="header">
      <h1>📊 데이터베이스 스키마</h1>
      <div class="header-actions">
        <button @click="loadSchema" class="btn-refresh">새로고침</button>
      </div>
    </div>

    <div class="search-bar">
      <input 
        v-model="searchQuery"
        @input="handleSearch"
        type="text" 
        placeholder="테이블 검색..."
      />
    </div>

    <div v-if="schemaStore.loading" class="loading">
      <div class="spinner"></div>
      <p>스키마 로딩 중...</p>
    </div>

    <div v-else class="schema-content">
      <!-- 통합 편집 가능한 스키마 뷰 -->
      <div class="integrated-schema-view">
        <!-- 테이블 목록 (편집 가능) -->
        <div class="tables-list">
          <h3>테이블 ({{ schemaStore.tables.length }})</h3>
          <div class="table-item" 
            v-for="table in schemaStore.tables" 
            :key="table.name"
            @click="selectTable(table)"
            :class="{ active: schemaStore.selectedTable?.name === table.name }"
          >
            <div class="table-header">
              <div class="table-name">📋 {{ table.name }}</div>
              <button 
                @click.stop="toggleTableEdit(table.name)"
                class="edit-btn"
              >
                {{ editingTable === table.name ? '취소' : '편집' }}
              </button>
            </div>
            
            <div v-if="editingTable === table.name" class="edit-form">
              <textarea
                v-model="tableEditForm.description"
                placeholder="테이블 설명을 입력하세요..."
                rows="2"
              ></textarea>
              <div class="form-actions">
                <button @click="saveTableDescription(table)" class="save-btn">
                  저장
                </button>
                <button @click="cancelTableEdit" class="cancel-btn">
                  취소
                </button>
              </div>
            </div>
            
            <div v-else class="table-info">
              <span>{{ table.column_count }} columns</span>
              <span v-if="table.description" class="description">{{ table.description }}</span>
            </div>
          </div>
        </div>

        <!-- 선택된 테이블 상세 (편집 가능) -->
        <div class="table-details" v-if="schemaStore.selectedTable">
          <div class="table-details-header">
            <h3>{{ schemaStore.selectedTable.name }}</h3>
            <button @click="refreshTableColumns" class="btn-refresh-small">컬럼 새로고침</button>
          </div>
          <p v-if="schemaStore.selectedTable.description" class="description">
            {{ schemaStore.selectedTable.description }}
          </p>
          
          <table class="columns-table">
            <thead>
              <tr>
                <th>컬럼명</th>
                <th>타입</th>
                <th>Nullable</th>
                <th>설명</th>
                <th>편집</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="col in schemaStore.selectedTableColumns" :key="col.name">
                <td>
                  <strong>{{ col.name }}</strong>
                  <span v-if="col.name.toLowerCase().includes('id')" class="badge">🔑</span>
                </td>
                <td><code>{{ col.dtype }}</code></td>
                <td>
                  <span :class="col.nullable ? 'yes' : 'no'">
                    {{ col.nullable ? 'YES' : 'NO' }}
                  </span>
                </td>
                <td>
                  <div v-if="editingColumn === col.name" class="inline-edit">
                    <textarea
                      v-model="columnEditForm.description"
                      placeholder="컬럼 설명을 입력하세요..."
                      rows="1"
                    ></textarea>
                    <div class="inline-actions">
                      <button @click="saveColumnDescription(col)" class="save-btn-small">저장</button>
                      <button @click="cancelColumnEdit" class="cancel-btn-small">취소</button>
                    </div>
                  </div>
                  <span v-else class="column-description">
                    {{ col.description || '-' }}
                  </span>
                </td>
                <td>
                  <button 
                    v-if="editingColumn !== col.name"
                    @click="toggleColumnEdit(col.name)"
                    class="edit-btn-small"
                  >
                    편집
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 릴레이션 관리 -->
    <RelationshipManager :tables="schemaStore.tables" />

    <!-- ER Diagram -->
    <div class="er-section" v-if="schemaStore.tables.length > 0">
      <ERDiagram 
        :tables="schemaStore.tables" 
        :all-columns="allColumnsMap"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import ERDiagram from '../components/ERDiagram.vue'
import RelationshipManager from '../components/RelationshipManager.vue'
import type { ColumnInfo, TableInfo } from '../services/api'
import { api } from '../services/api'
import { useSchemaStore } from '../stores/schema'

const schemaStore = useSchemaStore()
const searchQuery = ref('')
const allColumnsMap = ref<Record<string, ColumnInfo[]>>({})

// 편집 상태
const editingTable = ref<string | null>(null)
const editingColumn = ref<string | null>(null)

// 편집 폼
const tableEditForm = reactive({
  description: ''
})

const columnEditForm = reactive({
  description: ''
})

onMounted(async () => {
  await loadSchema()
})

async function loadSchema() {
  await schemaStore.loadTables()
  
  // 모든 테이블의 컬럼 정보를 미리 로드 (ER Diagram용)
  for (const table of schemaStore.tables) {
    const columns = await schemaStore.loadTableColumns(table.name, table.schema)
    allColumnsMap.value[table.name] = schemaStore.selectedTableColumns
  }
}

function handleSearch() {
  schemaStore.loadTables(searchQuery.value)
}

function selectTable(table: TableInfo) {
  schemaStore.selectTable(table)
}

// 테이블 편집 관련 함수들
function toggleTableEdit(tableName: string) {
  if (editingTable.value === tableName) {
    cancelTableEdit()
  } else {
    editingTable.value = tableName
    const table = schemaStore.tables.find(t => t.name === tableName)
    tableEditForm.description = table?.description || ''
  }
}

function cancelTableEdit() {
  editingTable.value = null
  tableEditForm.description = ''
}

async function saveTableDescription(table: any) {
  try {
    await api.put(`/schema-edit/tables/${table.name}/description`, {
      name: table.name,
      schema: table.schema || 'public',
      description: tableEditForm.description
    })
    
    // Update local data
    table.description = tableEditForm.description
    cancelTableEdit()
  } catch (error) {
    console.error('Failed to save table description:', error)
    alert('테이블 설명 저장에 실패했습니다.')
  }
}

// 컬럼 편집 관련 함수들
function toggleColumnEdit(columnName: string) {
  if (editingColumn.value === columnName) {
    cancelColumnEdit()
  } else {
    editingColumn.value = columnName
    const column = schemaStore.selectedTableColumns.find(c => c.name === columnName)
    columnEditForm.description = column?.description || ''
  }
}

function cancelColumnEdit() {
  editingColumn.value = null
  columnEditForm.description = ''
}

async function saveColumnDescription(column: any) {
  try {
    await api.put(`/schema-edit/tables/${schemaStore.selectedTable?.name}/columns/${column.name}/description`, {
      table_name: schemaStore.selectedTable?.name,
      table_schema: 'public',
      column_name: column.name,
      description: columnEditForm.description
    })
    
    // Update local data
    column.description = columnEditForm.description
    cancelColumnEdit()
  } catch (error) {
    console.error('Failed to save column description:', error)
    alert('컬럼 설명 저장에 실패했습니다.')
  }
}

async function refreshTableColumns() {
  if (schemaStore.selectedTable) {
    await schemaStore.loadTableColumns(schemaStore.selectedTable.name, schemaStore.selectedTable.schema)
  }
}
</script>

<style scoped>
.schema-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.header h1 {
  margin: 0;
  color: #333;
}

.btn-edit {
  padding: 0.75rem 1.5rem;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #1976D2;
}

.btn-edit.active {
  background: #FF9800;
}

.btn-edit.active:hover {
  background: #F57C00;
}

.btn-refresh {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
}

.btn-refresh:hover {
  background: #45a049;
}

.search-bar {
  margin-bottom: 2rem;
}

.search-bar input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
}

.search-bar input:focus {
  outline: none;
  border-color: #4CAF50;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.schema-content {
  margin-bottom: 2rem;
}

.integrated-schema-view {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 2rem;
}

.tables-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
  max-height: 600px;
  overflow-y: auto;
}

.tables-list h3 {
  margin: 0 0 1rem 0;
  color: #333;
}

.table-item {
  padding: 1rem;
  margin-bottom: 0.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.table-item:hover {
  border-color: #4CAF50;
  background: #f8f9fa;
}

.table-item.active {
  border-color: #4CAF50;
  background: #e8f5e9;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.table-name {
  font-weight: 600;
  color: #333;
}

.table-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #666;
}

.edit-form {
  margin-top: 0.5rem;
}

.edit-form textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  margin-bottom: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.save-btn, .cancel-btn {
  padding: 0.25rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.save-btn {
  background: #4CAF50;
  color: white;
}

.cancel-btn {
  background: #f44336;
  color: white;
}

.edit-btn {
  padding: 0.25rem 0.75rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.edit-btn:hover {
  background: #45a049;
}

.table-details {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.table-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.table-details h3 {
  margin: 0;
  color: #333;
}

.table-details .description {
  color: #666;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.btn-refresh-small {
  padding: 0.5rem 1rem;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-refresh-small:hover {
  background: #1976D2;
}

.columns-table {
  width: 100%;
  border-collapse: collapse;
}

.columns-table th {
  background: #f8f9fa;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e0e0e0;
}

.columns-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
}

.columns-table code {
  background: #f5f5f5;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-size: 0.9rem;
}

.badge {
  font-size: 0.8rem;
  margin-left: 0.5rem;
}

.yes {
  color: #4CAF50;
}

.no {
  color: #f44336;
  font-weight: 600;
}

/* 인라인 편집 스타일 */
.inline-edit {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.inline-edit textarea {
  width: 100%;
  padding: 0.25rem;
  border: 1px solid #ddd;
  border-radius: 3px;
  resize: vertical;
  font-size: 0.9rem;
}

.inline-actions {
  display: flex;
  gap: 0.25rem;
}

.save-btn-small, .cancel-btn-small {
  padding: 0.2rem 0.5rem;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.8rem;
}

.save-btn-small {
  background: #4CAF50;
  color: white;
}

.cancel-btn-small {
  background: #f44336;
  color: white;
}

.edit-btn-small {
  padding: 0.2rem 0.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.8rem;
}

.edit-btn-small:hover {
  background: #45a049;
}

.column-description {
  color: #666;
}

.er-section {
  margin-top: 2rem;
}
</style>

