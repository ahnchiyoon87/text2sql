import { createRouter, createWebHistory } from 'vue-router'
import QueryView from '../views/QueryView.vue'
import ReactView from '../views/ReactView.vue'
import SchemaView from '../views/SchemaView.vue'

type ImportMetaWithEnv = ImportMeta & {
  env?: Record<string, string | undefined>
}

const env = ((import.meta as ImportMetaWithEnv).env ?? {}) as Record<string, string | undefined>
const baseUrl = env.BASE_URL || '/'

const router = createRouter({
  history: createWebHistory(baseUrl),
  routes: [
    {
      path: '/',
      name: 'query',
      component: QueryView
    },
    {
      path: '/react',
      name: 'react',
      component: ReactView
    },
    {
      path: '/schema',
      name: 'schema',
      component: SchemaView
    }
  ]
})

export default router

