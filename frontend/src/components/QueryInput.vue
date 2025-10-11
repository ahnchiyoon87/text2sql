<template>
  <div class="query-input">
    <div class="input-container">
      <textarea
        v-model="question"
        @keydown.ctrl.enter="handleSubmit"
        placeholder="자연어로 질문하세요... 예: '카테고리별 상품 개수를 보여줘'"
        rows="3"
        :disabled="loading"
      ></textarea>
      <button @click="handleSubmit" :disabled="!question.trim() || loading" class="btn-primary">
        {{ loading ? '처리 중...' : '질문하기' }}
      </button>
    </div>
    
    <div class="examples">
      <span>예시:</span>
      <button @click="setExample(ex)" v-for="ex in examples" :key="ex" class="btn-example">
        {{ ex }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const emit = defineEmits<{
  submit: [question: string]
}>()

const props = defineProps<{
  loading?: boolean
}>()

const question = ref('')

const examples = [
  '카테고리별 상품 개수',
  '프리미엄 회원 목록',
  '가장 비싼 상품 Top 5',
  '국가별 고객 수',
  '최근 주문 10건'
]

function setExample(example: string) {
  question.value = example
}

function handleSubmit() {
  if (question.value.trim() && !props.loading) {
    emit('submit', question.value.trim())
  }
}
</script>

<style scoped>
.query-input {
  margin-bottom: 2rem;
}

.input-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

textarea {
  flex: 1;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s;
}

textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.btn-primary {
  padding: 1rem 2rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.examples {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
  color: #666;
  font-size: 0.9rem;
}

.btn-example {
  padding: 0.5rem 1rem;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-example:hover {
  background: #e0e0e0;
  border-color: #4CAF50;
}
</style>

