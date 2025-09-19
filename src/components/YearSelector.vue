<template>
  <div class="year-selector">
    <button 
      v-for="year in novelsStore.years" 
      :key="year"
      :class="['year-button', { active: novelsStore.selectedYear === year }]"
      @click="selectYear(year)"
    >
      {{ year }}年
    </button>
  </div>
</template>

<script setup lang="ts">
import { useNovelsStore } from '../stores/novels'
import { useRouter } from 'vue-router'

const novelsStore = useNovelsStore()
const router = useRouter()

// 年を選択してルートを更新
const selectYear = (year: string) => {
  novelsStore.setSelectedYear(year)
  // URLから特定の年のランキングに直接アクセスできるように、ルートパラメータを更新
  router.push({ query: { year } })
}
</script>

<style scoped>
.year-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.year-button {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background-color: #fff;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
}

.year-button:hover {
  background-color: #f8f8f8;
  border-color: #3498db;
}

.year-button.active {
  background-color: #3498db;
  color: #fff;
  border-color: #3498db;
}

/* レスポンシブデザイン */
@media (max-width: 768px) {
  .year-selector {
    gap: 0.25rem;
  }
  
  .year-button {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
  }
}
</style>