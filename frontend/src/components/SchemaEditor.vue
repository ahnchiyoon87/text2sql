<template>
  <div class="schema-editor">
    <div class="editor-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="tab-content">
      <!-- 테이블 설명 편집 -->
      <div v-if="activeTab === 'tables'" class="table-editor">
        <h3>테이블 설명 편집</h3>
        <div class="table-list">
          <div 
            v-for="table in tables" 
            :key="table.name"
            class="table-item"
          >
            <div class="table-header">
              <h4>{{ table.name }}</h4>
              <button 
                @click="toggleTableEdit(table.name)"
                class="edit-btn"
              >
                {{ editingTable === table.name ? '취소' : '편집' }}
              </button>
            </div>
            
            <div v-if="editingTable === table.name" class="edit-form">
              <textarea
                v-model="tableEditForm.description"
                placeholder="테이블 설명을 입력하세요..."
                rows="3"
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
            
            <div v-else class="table-description">
              {{ table.description || '설명이 없습니다.' }}
            </div>
          </div>
        </div>
      </div>

      <!-- 컬럼 설명 편집 -->
      <div v-if="activeTab === 'columns'" class="column-editor">
        <h3>컬럼 설명 편집</h3>
        <div class="table-selector">
          <label>테이블 선택:</label>
          <select v-model="selectedTable" @change="loadTableColumns">
            <option value="">테이블을 선택하세요</option>
            <option v-for="table in tables" :key="table.name" :value="table.name">
              {{ table.name }}
            </option>
          </select>
        </div>

        <div v-if="selectedTable && tableColumns.length > 0" class="columns-list">
          <div 
            v-for="column in tableColumns" 
            :key="column.name"
            class="column-item"
          >
            <div class="column-header">
              <span class="column-name">{{ column.name }}</span>
              <span class="column-type">{{ column.dtype }}</span>
              <button 
                @click="toggleColumnEdit(column.name)"
                class="edit-btn"
              >
                {{ editingColumn === column.name ? '취소' : '편집' }}
              </button>
            </div>
            
            <div v-if="editingColumn === column.name" class="edit-form">
              <textarea
                v-model="columnEditForm.description"
                placeholder="컬럼 설명을 입력하세요..."
                rows="2"
              ></textarea>
              <div class="form-actions">
                <button @click="saveColumnDescription(column)" class="save-btn">
                  저장
                </button>
                <button @click="cancelColumnEdit" class="cancel-btn">
                  취소
                </button>
              </div>
            </div>
            
            <div v-else class="column-description">
              {{ column.description || '설명이 없습니다.' }}
            </div>
          </div>
        </div>
      </div>

      <!-- 릴레이션 관리 -->
      <div v-if="activeTab === 'relationships'" class="relationship-editor">
        <h3>릴레이션 관리</h3>
        
        <!-- 기존 릴레이션 목록 -->
        <div class="existing-relationships">
          <h4>현재 릴레이션</h4>
          <div v-if="userRelationships.length === 0" class="no-data">
            사용자가 추가한 릴레이션이 없습니다.
          </div>
          <div v-else>
            <div 
              v-for="rel in userRelationships" 
              :key="`${rel.from_table}-${rel.from_column}-${rel.to_table}-${rel.to_column}`"
              class="relationship-item"
            >
              <div class="relationship-info">
                <span class="from">{{ rel.from_table }}.{{ rel.from_column }}</span>
                <span class="arrow">→</span>
                <span class="to">{{ rel.to_table }}.{{ rel.to_column }}</span>
                <span v-if="rel.description" class="description">({{ rel.description }})</span>
              </div>
              <button 
                @click="removeRelationship(rel)"
                class="remove-btn"
              >
                삭제
              </button>
            </div>
          </div>
        </div>

        <!-- 새 릴레이션 추가 -->
        <div class="add-relationship">
          <h4>새 릴레이션 추가</h4>
          <form @submit.prevent="addRelationship" class="relationship-form">
            <div class="form-row">
              <div class="form-group">
                <label>From 테이블:</label>
                <select v-model="newRelationship.from_table" required>
                  <option value="">선택하세요</option>
                  <option v-for="table in tables" :key="table.name" :value="table.name">
                    {{ table.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>From 컬럼:</label>
                <select v-model="newRelationship.from_column" required>
                  <option value="">선택하세요</option>
                  <option v-for="col in getTableColumns(newRelationship.from_table)" :key="col.name" :value="col.name">
                    {{ col.name }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>To 테이블:</label>
                <select v-model="newRelationship.to_table" required>
                  <option value="">선택하세요</option>
                  <option v-for="table in tables" :key="table.name" :value="table.name">
                    {{ table.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>To 컬럼:</label>
                <select v-model="newRelationship.to_column" required>
                  <option value="">선택하세요</option>
                  <option v-for="col in getTableColumns(newRelationship.to_table)" :key="col.name" :value="col.name">
                    {{ col.name }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label>설명 (선택사항):</label>
              <input 
                v-model="newRelationship.description"
                type="text"
                placeholder="릴레이션 설명"
              />
            </div>
            
            <button type="submit" class="add-btn" :disabled="!isRelationshipFormValid">
              릴레이션 추가
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { api } from '../services/api'
import { useSchemaStore } from '../stores/schema'

const schemaStore = useSchemaStore()

// Tab management
const tabs = [
  { id: 'tables', label: '테이블 설명' },
  { id: 'columns', label: '컬럼 설명' },
  { id: 'relationships', label: '릴레이션' }
]
const activeTab = ref('tables')

// Data
const tables = ref<any[]>([])
const tableColumns = ref<any[]>([])
const userRelationships = ref<any[]>([])

// Table editing
const editingTable = ref<string | null>(null)
const tableEditForm = reactive({
  description: ''
})

// Column editing
const selectedTable = ref('')
const editingColumn = ref<string | null>(null)
const columnEditForm = reactive({
  description: ''
})

// Relationship management
const newRelationship = reactive({
  from_table: '',
  from_column: '',
  to_table: '',
  to_column: '',
  description: ''
})

// Computed
const isRelationshipFormValid = computed(() => {
  return newRelationship.from_table && 
         newRelationship.from_column && 
         newRelationship.to_table && 
         newRelationship.to_column &&
         newRelationship.from_table !== newRelationship.to_table
})

// Methods
const loadData = async () => {
  await schemaStore.loadTables()
  tables.value = schemaStore.tables
  await loadUserRelationships()
}

const loadTableColumns = async () => {
  if (!selectedTable.value) {
    tableColumns.value = []
    return
  }
  
  await schemaStore.loadTableColumns(selectedTable.value)
  tableColumns.value = schemaStore.getTableColumns(selectedTable.value)
}

const loadUserRelationships = async () => {
  try {
    const response = await api.get('/schema-edit/relationships/user-added')
    userRelationships.value = response.data.relationships
  } catch (error) {
    console.error('Failed to load user relationships:', error)
  }
}

const getTableColumns = (tableName: string) => {
  if (!tableName) return []
  return schemaStore.getTableColumns(tableName)
}

// Table editing methods
const toggleTableEdit = (tableName: string) => {
  if (editingTable.value === tableName) {
    cancelTableEdit()
  } else {
    editingTable.value = tableName
    const table = tables.value.find(t => t.name === tableName)
    tableEditForm.description = table?.description || ''
  }
}

const cancelTableEdit = () => {
  editingTable.value = null
  tableEditForm.description = ''
}

const saveTableDescription = async (table: any) => {
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

// Column editing methods
const toggleColumnEdit = (columnName: string) => {
  if (editingColumn.value === columnName) {
    cancelColumnEdit()
  } else {
    editingColumn.value = columnName
    const column = tableColumns.value.find(c => c.name === columnName)
    columnEditForm.description = column?.description || ''
  }
}

const cancelColumnEdit = () => {
  editingColumn.value = null
  columnEditForm.description = ''
}

const saveColumnDescription = async (column: any) => {
  try {
    await api.put(`/schema-edit/tables/${selectedTable.value}/columns/${column.name}/description`, {
      table_name: selectedTable.value,
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

// Relationship methods
const addRelationship = async () => {
  try {
    await api.post('/schema-edit/relationships', {
      from_table: newRelationship.from_table,
      from_schema: 'public',
      from_column: newRelationship.from_column,
      to_table: newRelationship.to_table,
      to_schema: 'public',
      to_column: newRelationship.to_column,
      relationship_type: 'FK_TO_TABLE',
      description: newRelationship.description
    })
    
    // Reset form
    Object.assign(newRelationship, {
      from_table: '',
      from_column: '',
      to_table: '',
      to_column: '',
      description: ''
    })
    
    // Reload relationships
    await loadUserRelationships()
  } catch (error) {
    console.error('Failed to add relationship:', error)
    alert('릴레이션 추가에 실패했습니다.')
  }
}

const removeRelationship = async (rel: any) => {
  if (!confirm('이 릴레이션을 삭제하시겠습니까?')) return
  
  try {
    await api.delete('/schema-edit/relationships', {
      params: {
        from_table: rel.from_table,
        from_schema: rel.from_schema,
        from_column: rel.from_column,
        to_table: rel.to_table,
        to_schema: rel.to_schema,
        to_column: rel.to_column
      }
    })
    
    await loadUserRelationships()
  } catch (error) {
    console.error('Failed to remove relationship:', error)
    alert('릴레이션 삭제에 실패했습니다.')
  }
}

// Watch for table changes to reload columns
watch(() => newRelationship.from_table, () => {
  newRelationship.from_column = ''
})

watch(() => newRelationship.to_table, () => {
  newRelationship.to_column = ''
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.schema-editor {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.editor-tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-button.active {
  border-bottom-color: #4CAF50;
  color: #4CAF50;
  font-weight: 600;
}

.tab-content {
  min-height: 400px;
}

/* Table Editor */
.table-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.table-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.table-header h4 {
  margin: 0;
  color: #333;
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

.save-btn {
  padding: 0.5rem 1rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  padding: 0.5rem 1rem;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.table-description {
  color: #666;
  font-style: italic;
}

/* Column Editor */
.table-selector {
  margin-bottom: 1.5rem;
}

.table-selector label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.table-selector select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.columns-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.column-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.column-name {
  font-weight: 600;
  color: #333;
}

.column-type {
  color: #666;
  font-size: 0.9rem;
  margin-left: 1rem;
}

.column-description {
  color: #666;
  font-style: italic;
}

/* Relationship Editor */
.existing-relationships {
  margin-bottom: 2rem;
}

.relationship-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.relationship-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.from, .to {
  font-weight: 600;
  color: #333;
}

.arrow {
  color: #666;
}

.description {
  color: #666;
  font-size: 0.9rem;
}

.remove-btn {
  padding: 0.25rem 0.75rem;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.add-relationship {
  border-top: 2px solid #e0e0e0;
  padding-top: 1.5rem;
}

.relationship-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-btn {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  align-self: flex-start;
}

.add-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.no-data {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 2rem;
}
</style>
