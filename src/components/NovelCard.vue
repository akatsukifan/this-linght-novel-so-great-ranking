<template>
  <div :class="['novel-card', { large: isLarge }]">
    <div :class="['novel-rank', { first: rank === 1 }]">{{ rank }}</div>
    <div class="novel-cover">
      <img 
        :src="imagePath" 
        :alt="name + 'のカバー'"
        class="novel-image"
      />
    </div>
    <div class="novel-info">
      <h3 class="novel-name">{{ name }}</h3>
      <p class="novel-author">{{ author }}</p>
      <p class="novel-publisher">{{ publisher }}</p>
      <p class="novel-price">¥{{ price }}</p>
    </div>
    <button 
      class="add-to-cart" 
      @click="addToCart" 
      :title="'カートに追加'"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        :width="isLarge ? 20 : 16"
        :height="isLarge ? 20 : 16"
        viewBox="0 0 24 24" fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="9" cy="21" r="1"></circle>
        <circle cx="20" cy="21" r="1"></circle>
        <path
          d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
        ></path>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useNovelsStore } from '../stores/novels'

// コンポーネントのPropsを定義
interface Props {
  id: number
  name: string
  author: string
  publisher: string
  rank: number
  price: number
  year: string
  isLarge?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLarge: false
})

const novelsStore = useNovelsStore()

// 画像パスを計算
const imagePath = computed(() => {
  // 2025年的第四名和2021年的第二名是webp格式
  if ((props.rank === 4 && props.year === '2025') || (props.rank === 2 && props.year === '2021')) {
    return `/image/${props.year}/${props.rank}.webp`
  }
  return `/image/${props.year}/${props.rank === 6 ? 6 : props.rank}.jpg`
})

// カートに追加するメソッド
const addToCart = () => {
  novelsStore.addToCart(props.id)
}
</script>

<style scoped>
/* 小説カードの基本スタイル */
.novel-card {
  display: flex;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.novel-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 大サイズカードのスタイル */
.novel-card.large {
  padding: 1.5rem;
  margin-bottom: 2rem;
}

/* ランクのスタイル */
.novel-rank {
  font-size: 1.5rem;
  font-weight: bold;
  color: #666;
  margin-right: 1rem;
  min-width: 30px;
  text-align: center;
}

.novel-rank.first {
  color: #e74c3c;
  font-size: 2rem;
}

/* 表紙のスタイル */
.novel-cover {
  flex-shrink: 0;
  margin-right: 1rem;
}

.novel-image {
  width: 200px;
  height: 300px;
  object-fit: cover;
  border-radius: 4px;
}

/* 情報のスタイル */
.novel-info {
  flex: 1;
}

.novel-name {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.novel-card.large .novel-name {
  font-size: 1.5rem;
}

.novel-author {
  color: #666;
  margin-bottom: 0.25rem;
}

.novel-publisher {
  color: #999;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.novel-price {
  font-size: 1.1rem;
  font-weight: bold;
  color: #e74c3c;
  margin-top: 0.5rem;
}

/* カートに追加ボタン */
.add-to-cart {
  background-color: #3498db;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.add-to-cart:hover {
  background-color: #2980b9;
}

.novel-card:not(.large) .add-to-cart {
  width: 32px;
  height: 32px;
}
</style>