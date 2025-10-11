import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { apiService, type AskResponse } from '../services/api'

export const useQueryStore = defineStore('query', () => {
  const currentQuestion = ref('')
  const currentResponse = ref<AskResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const history = ref<Array<{ question: string; response: AskResponse; timestamp: Date }>>([])

  const hasResult = computed(() => currentResponse.value !== null)

  async function ask(question: string, limit: number = 100) {
    loading.value = true
    error.value = null
    currentQuestion.value = question

    try {
      const response = await apiService.ask({ question, limit })
      currentResponse.value = response
      
      // 히스토리에 추가
      history.value.unshift({
        question,
        response,
        timestamp: new Date()
      })
      
      // 최대 20개까지만 보관
      if (history.value.length > 20) {
        history.value = history.value.slice(0, 20)
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearResult() {
    currentResponse.value = null
    currentQuestion.value = ''
    error.value = null
  }

  return {
    currentQuestion,
    currentResponse,
    loading,
    error,
    history,
    hasResult,
    ask,
    clearResult
  }
})

