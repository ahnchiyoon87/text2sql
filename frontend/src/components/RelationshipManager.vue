<template>
  <div class="relationship-manager">
    <div class="manager-header">
      <h3>🔗 릴레이션 관리</h3>
      <button @click="loadUserRelationships" class="btn-refresh">새로고침</button>
    </div>
    
    <!-- 기존 릴레이션 목록 -->
    <div class="existing-relationships">
      <h4>현재 사용자 추가 릴레이션</h4>
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
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { api } from '../services/api';
import { useSchemaStore } from '../stores/schema';

const schemaStore = useSchemaStore()

// Props
const props = defineProps<{
  tables: any[]
}>()

// Data
const userRelationships = ref<any[]>([])

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
  loadUserRelationships()
})
</script>

<style scoped>
.relationship-manager {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
  margin-top: 2rem;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.manager-header h3 {
  margin: 0;
  color: #333;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-refresh:hover {
  background: #45a049;
}

.existing-relationships {
  margin-bottom: 2rem;
}

.existing-relationships h4 {
  margin: 0 0 1rem 0;
  color: #333;
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

.remove-btn:hover {
  background: #d32f2f;
}

.add-relationship {
  border-top: 2px solid #e0e0e0;
  padding-top: 1.5rem;
}

.add-relationship h4 {
  margin: 0 0 1rem 0;
  color: #333;
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
