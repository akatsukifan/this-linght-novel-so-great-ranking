<template>
  <div class="home">
    <!-- メインコンテンツエリア -->
    <main class="main-content">
      <h2 class="year-title">{{ novelsStore.selectedYear }}年</h2>
      <!-- 年セレクター -->
      <YearSelector />
      

      <!-- ローディング状態 -->
      <div v-if="novelsStore.currentLoading" class="loading">
        <p>読み込み中...</p>
      </div>

      <!-- エラー状態 -->
      <div v-else-if="novelsStore.currentError" class="error">
        <p>{{ novelsStore.currentError }}</p>
      </div>

      <!-- コンテンツエリア -->
      <template v-else>
        <!-- 1位 -->
        <div class="first-place" v-if="novelsStore.firstPlace">
          <NovelCard 
            :id="novelsStore.firstPlace.id"
            :name="novelsStore.firstPlace.name"
            :author="novelsStore.firstPlace.author"
            :publisher="novelsStore.firstPlace.publisher"
            :rank="novelsStore.firstPlace.rank"
            :price="novelsStore.firstPlace.price"
            :year="novelsStore.selectedYear"
            :is-large="true"
          />
        </div>

        <!-- その他の4位 -->
        <div class="other-places">
          <NovelCard 
            v-for="novel in novelsStore.otherPlaces" 
            :key="novel.id"
            :id="novel.id"
            :name="novel.name"
            :author="novel.author"
            :publisher="novel.publisher"
            :rank="novel.rank"
            :price="novel.price"
            :year="novelsStore.selectedYear"
          />
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useNovelsStore } from '../stores/novels'
import YearSelector from '../components/YearSelector.vue'
import NovelCard from '../components/NovelCard.vue'

const route = useRoute()
const novelsStore = useNovelsStore()

// ルートパラメータから年を取得してselectedYearを設定
const updateYearFromRoute = () => {
  const yearParam = route.query.year as string
  if (yearParam && novelsStore.years.includes(yearParam)) {
    novelsStore.setSelectedYear(yearParam)
  }
}

// コンポーネントマウント時に年と小説データを取得
onMounted(() => {
  updateYearFromRoute()
  novelsStore.fetchNovels()
})

// ルートパラメータの変化を監視し、年を更新
watch(
  () => route.query.year,
  () => {
    updateYearFromRoute()
  }
)

// 選択された年の変化を監視し、データを再取得
watch(
  () => novelsStore.selectedYear,
  (newYear) => {
    novelsStore.fetchNovels(newYear)
  }
)
</script>

<style scoped>
/* メインコンテンツエリアのスタイル */
.main-content {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.year-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #333;
}

/* ローディング状態のスタイル */
.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 1.2rem;
}

/* エラー状態のスタイル */
.error {
  text-align: center;
  padding: 2rem;
  color: #e74c3c;
  font-size: 1.2rem;
  background-color: #fadbd8;
  border-radius: 8px;
}

/* 1位のスタイル */
.first-place {
  display: flex;
  justify-content: center;
  margin-bottom: 3rem;
}

/* その他の4位のスタイル */
.other-places {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  margin-top: 2rem;
}

/* すべての小説カードのサイズを一致させる */
.other-places .novel-card {
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 100%;
}

.other-places .novel-image {
  width: 180px;
  height: 270px;
}

.other-places .novel-name {
  font-size: 1rem;
}

@media (max-width: 1200px) {
  .other-places {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .other-places {
    grid-template-columns: 1fr;
  }
}
</style>
