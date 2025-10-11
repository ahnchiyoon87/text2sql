import { createRouter, createWebHistory } from 'vue-router'
import QueryView from '../views/QueryView.vue'
import SchemaView from '../views/SchemaView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'query',
      component: QueryView
    },
    {
      path: '/schema',
      name: 'schema',
      component: SchemaView
    }
  ]
})

export default router

