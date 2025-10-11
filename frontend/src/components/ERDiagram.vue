<template>
  <div class="er-diagram">
    <div class="toolbar">
      <h3>ER Diagram</h3>
      <div class="toolbar-controls">
        <div class="search-controls">
          <input 
            v-model="searchQuery"
            @input="handleSearch"
            type="text" 
            placeholder="테이블 검색..."
            class="search-input"
          />
          <button @click="clearSearch" class="btn-clear">지우기</button>
        </div>
        <div class="filter-controls">
          <label class="filter-label">
            <input 
              type="checkbox" 
              v-model="showConnectedOnly"
              @change="updateDiagram"
            />
            연결된 테이블만 표시
          </label>
          <span class="table-count">{{ filteredTables.length }}개 테이블</span>
        </div>
        <button @click="refreshDiagram" class="btn-refresh">
          새로고침
        </button>
      </div>
    </div>
    <div ref="diagramEl" class="diagram-container"></div>
  </div>
</template>

<script setup lang="ts">
import mermaid from 'mermaid';
import { computed, onMounted, ref, watch } from 'vue';
import type { ColumnInfo, TableInfo } from '../services/api';

const props = defineProps<{
  tables: TableInfo[]
  allColumns: Record<string, ColumnInfo[]>
}>()

const diagramEl = ref<HTMLElement | null>(null)
const searchQuery = ref('')
const showConnectedOnly = ref(true)

// Computed properties
const filteredTables = computed(() => {
  let tables = props.tables
  
  // 검색어가 있으면 필터링
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    tables = tables.filter(table => 
      table.name.toLowerCase().includes(query) ||
      (table.description && table.description.toLowerCase().includes(query))
    )
  }
  
  // 연결된 테이블만 표시 옵션이 활성화되어 있고 검색 결과가 있으면
  if (showConnectedOnly.value && tables.length > 0) {
    const connectedTables = getConnectedTables(tables)
    return connectedTables
  }
  
  // 기본적으로 최대 20개 테이블만 표시 (대규모 스키마 대응)
  return tables.slice(0, 20)
})

onMounted(() => {
  mermaid.initialize({ 
    startOnLoad: false,
    theme: 'default',
    er: {
      layoutDirection: 'TB'
    }
  })
  renderDiagram()
})

watch(() => [filteredTables.value, props.allColumns], () => {
  renderDiagram()
}, { deep: true })

async function renderDiagram() {
  if (!diagramEl.value || filteredTables.value.length === 0) {
    if (diagramEl.value) {
      diagramEl.value.innerHTML = '<div class="no-data">표시할 테이블이 없습니다.</div>'
    }
    return
  }
  
  const mermaidCode = generateMermaidER()
  
  try {
    diagramEl.value.innerHTML = ''
    const { svg } = await mermaid.render('er-diagram', mermaidCode)
    diagramEl.value.innerHTML = svg
  } catch (err) {
    console.error('Mermaid render error:', err)
    diagramEl.value.innerHTML = `<pre style="color: red; padding: 1rem;">${err}</pre>`
  }
}

// 연결된 테이블 찾기 함수
function getConnectedTables(searchTables: TableInfo[]): TableInfo[] {
  const connectedTables = new Set<string>()
  const allTables = props.tables
  
  // 검색된 테이블들을 시작점으로 추가
  searchTables.forEach(table => connectedTables.add(table.name))
  
  // 각 검색된 테이블에 대해 1차 연결된 테이블 찾기
  searchTables.forEach(table => {
    const columns = props.allColumns[table.name] || []
    
    columns.forEach(col => {
      // FK 패턴 감지
      if (col.name.endsWith('_id') && col.name !== 'id') {
        const baseName = col.name.replace(/_id$/, '')
        
        // 가능한 참조 테이블 찾기
        const possibleRefs = [
          baseName + 's',  // 복수형
          baseName,        // 단수형
          baseName.replace(/s$/, '')  // 복수형에서 s 제거
        ]
        
        const refTable = allTables.find(t => possibleRefs.includes(t.name))
        if (refTable) {
          connectedTables.add(refTable.name)
        }
      }
    })
    
    // 역방향 관계도 찾기 (다른 테이블이 이 테이블을 참조하는 경우)
    allTables.forEach(otherTable => {
      if (otherTable.name === table.name) return
      
      const otherColumns = props.allColumns[otherTable.name] || []
      otherColumns.forEach(col => {
        if (col.name.endsWith('_id') && col.name !== 'id') {
          const baseName = col.name.replace(/_id$/, '')
          const possibleRefs = [
            baseName + 's',
            baseName,
            baseName.replace(/s$/, '')
          ]
          
          if (possibleRefs.includes(table.name)) {
            connectedTables.add(otherTable.name)
          }
        }
      })
    })
  })
  
  // 연결된 테이블들을 반환 (최대 15개로 제한)
  return Array.from(connectedTables)
    .map(tableName => allTables.find(t => t.name === tableName))
    .filter(Boolean)
    .slice(0, 15) as TableInfo[]
}

function generateMermaidER(): string {
  let code = 'erDiagram\n'
  
  // 필터링된 테이블들만 사용
  const tablesToRender = filteredTables.value
  
  // 각 테이블의 컬럼 정의 (매우 간단하고 안전한 방식)
  tablesToRender.forEach(table => {
    const columns = props.allColumns[table.name] || []
    
    code += `    ${table.name} {\n`
    
    // 최대 5개의 주요 컬럼만 표시 (대규모 스키마 최적화)
    const displayColumns = columns.slice(0, 5)
    
    displayColumns.forEach(col => {
      // 매우 안전한 데이터 타입 매핑
      let safeType = 'string'
      const dtype = col.dtype.toLowerCase()
      if (dtype.includes('int') || dtype.includes('serial')) {
        safeType = 'int'
      } else if (dtype.includes('decimal') || dtype.includes('numeric') || dtype.includes('float')) {
        safeType = 'float'
      } else if (dtype.includes('date') || dtype.includes('time')) {
        safeType = 'datetime'
      } else if (dtype.includes('bool')) {
        safeType = 'boolean'
      }
      
      // 컬럼명을 매우 안전하게 처리
      const safeName = col.name
        .replace(/[^a-zA-Z0-9]/g, '_')  // 특수문자 제거
        .toLowerCase()
        .substring(0, 15)  // 길이 제한 (더 짧게)
      
      code += `        ${safeType} ${safeName}\n`
    })
    
    // 더 많은 컬럼이 있음을 표시
    if (columns.length > 5) {
      code += `        string more_columns\n`
    }
    
    code += `    }\n`
  })
  
  // 관계 정의 (필터링된 테이블들 간의 관계만)
  const relationships: string[] = []
  
  tablesToRender.forEach(table => {
    const columns = props.allColumns[table.name] || []
    
    columns.forEach(col => {
      // 간단한 FK 패턴: *_id
      if (col.name.endsWith('_id') && col.name !== 'id') {
        const baseName = col.name.replace(/_id$/, '')
        
        // 필터링된 테이블들 중에서 참조 테이블 찾기
        const possibleRefs = [
          baseName + 's',  // 복수형
          baseName,        // 단수형
          baseName.replace(/s$/, '')  // 복수형에서 s 제거
        ]
        
        const refTable = tablesToRender.find(t => possibleRefs.includes(t.name))
        if (refTable) {
          const relString = `    ${refTable.name} ||--o{ ${table.name} : "${baseName}"`
          if (!relationships.includes(relString)) {
            relationships.push(relString)
          }
        }
      }
    })
  })
  
  // 관계 추가 (최대 8개로 제한)
  relationships.slice(0, 8).forEach(rel => {
    code += rel + '\n'
  })
  
  return code
}

function refreshDiagram() {
  renderDiagram()
}

function handleSearch() {
  // 검색어가 변경되면 자동으로 다이어그램 업데이트
  renderDiagram()
}

function clearSearch() {
  searchQuery.value = ''
  renderDiagram()
}

function updateDiagram() {
  renderDiagram()
}
</script>

<style scoped>
.er-diagram {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1.5rem;
}

.toolbar {
  margin-bottom: 1.5rem;
}

.toolbar h3 {
  margin: 0 0 1rem 0;
  color: #333;
}

.toolbar-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.btn-clear {
  padding: 0.5rem 1rem;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-clear:hover {
  background: #d32f2f;
}

.filter-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  cursor: pointer;
}

.filter-label input[type="checkbox"] {
  margin: 0;
}

.table-count {
  font-size: 0.9rem;
  color: #666;
  font-weight: 600;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  align-self: flex-end;
}

.btn-refresh:hover {
  background: #45a049;
}

.diagram-container {
  overflow-x: auto;
  min-height: 400px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1rem;
  background: #fafafa;
}

.diagram-container :deep(svg) {
  max-width: 100%;
  height: auto;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #666;
  font-style: italic;
  background: #f9f9f9;
  border-radius: 4px;
  margin: 1rem 0;
}

/* 반응형 디자인 */
@media (min-width: 768px) {
  .toolbar-controls {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .search-controls {
    flex: 1;
    max-width: 300px;
  }
  
  .filter-controls {
    gap: 1rem;
  }
}
</style>

