<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">
          🤖 Graph-based Metadata-augmented Text2SQL
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">질의</router-link>
          <router-link to="/schema" class="nav-link">스키마</router-link>
          <div class="health-indicator" :class="healthStatus">
            <span class="dot"></span>
            {{ healthStatus === 'healthy' ? '정상' : '확인 중' }}
          </div>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>Graph-based Metadata-augmented Text2SQL - RAG 기반 자연어 SQL 생성 시스템</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiService } from './services/api'

const healthStatus = ref<'healthy' | 'checking'>('checking')

onMounted(async () => {
  try {
    await apiService.healthCheck()
    healthStatus.value = 'healthy'
  } catch {
    healthStatus.value = 'checking'
  }
})
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f7fa;
  color: #333;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-link {
  color: #666;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #4CAF50;
  background: #f0f0f0;
}

.nav-link.router-link-active {
  color: #4CAF50;
  background: #e8f5e9;
}

.health-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.health-indicator.healthy {
  background: #e8f5e9;
  color: #4CAF50;
}

.health-indicator.checking {
  background: #fff3e0;
  color: #ff9800;
}

.health-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.main-content {
  flex: 1;
}

.footer {
  background: white;
  border-top: 1px solid #e0e0e0;
  padding: 2rem;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}
</style>

