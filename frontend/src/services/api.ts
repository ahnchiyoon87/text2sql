import axios from 'axios'

// Gateway를 통한 접근: http://localhost:9090/api
const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface AskRequest {
  question: string
  limit?: number
  visual_pref?: string[]
}

export interface AskResponse {
  sql: string
  table: {
    columns: string[]
    rows: any[][]
    row_count: number
    execution_time_ms: number
  }
  charts: Chart[]
  provenance: {
    tables: string[]
    columns: string[]
    neo4j_paths: string[]
    vector_matches: Array<{ node: string; score: number }>
    prompt_snapshot_id: string
  }
  perf: {
    embedding_ms: number
    graph_search_ms: number
    llm_ms: number
    sql_ms: number
    total_ms: number
  }
}

export interface Chart {
  title: string
  type: string
  description: string
  vega_lite?: any
}

export interface TableInfo {
  name: string
  schema: string
  description: string
  column_count: number
}

export interface ColumnInfo {
  name: string
  table_name: string
  dtype: string
  nullable: boolean
  description: string
}

export interface FeedbackRequest {
  prompt_snapshot_id: string
  original_sql: string
  corrected_sql?: string
  rating: number
  notes?: string
  approved: boolean
}

export const apiService = {
  // 자연어 질의
  async ask(request: AskRequest): Promise<AskResponse> {
    const { data } = await api.post('/ask', request)
    return data
  },

  // 테이블 목록
  async getTables(search?: string, schema?: string, limit: number = 50): Promise<TableInfo[]> {
    const { data } = await api.get('/meta/tables', {
      params: { search, schema, limit }
    })
    return data
  },

  // 테이블 컬럼
  async getTableColumns(tableName: string, schema: string = 'public'): Promise<ColumnInfo[]> {
    const { data } = await api.get(`/meta/tables/${tableName}/columns`, {
      params: { schema }
    })
    return data
  },

  // 컬럼 검색
  async searchColumns(search: string, limit: number = 50): Promise<ColumnInfo[]> {
    const { data } = await api.get('/meta/columns', {
      params: { search, limit }
    })
    return data
  },

  // 피드백 제출
  async submitFeedback(feedback: FeedbackRequest): Promise<any> {
    const { data } = await api.post('/feedback', feedback)
    return data
  },

  // 피드백 통계
  async getFeedbackStats(): Promise<any> {
    const { data } = await api.get('/feedback/stats')
    return data
  },

  // 스키마 인제스천
  async ingestSchema(dbName: string, schema: string, clearExisting: boolean = false): Promise<any> {
    const { data } = await api.post('/ingest', {
      db_name: dbName,
      schema,
      clear_existing: clearExisting
    })
    return data
  },

  // 헬스체크
  async healthCheck(): Promise<any> {
    const { data } = await api.get('/health')
    return data
  }
}

// Export the axios instance for direct use
export { api }
export default apiService

