<template>
  <div class="cart">
    <div class="cart-container">
      <h2 class="cart-title">カート</h2>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <p>読み込み中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
      </div>
      
      <div v-else-if="cartItems.length === 0" class="empty-cart">
        <p>カートは空です</p>
        <router-link to="/" class="shop-now-button">ショッピングを始める</router-link>
      </div>
      
      <div v-else class="cart-content">
        <!-- 购物车商品列表 -->
        <div class="cart-items">
          <div class="cart-item" v-for="item in cartItems" :key="item.id">
            <div class="item-image">
              <img 
                :src="`/image/${item.year || '2025'}/${item.rank || 1}.${(item.rank === 4 && item.year === '2025') || (item.rank === 2 && item.year === '2021') ? 'webp' : 'jpg'}`" 
                :alt="item.name + 'のカバー'"
                class="item-image-src"
                @error="handleImageError($event, item)"
              />
            </div>
            
            <div class="item-details">
              <h3 class="item-name">{{ item.name }}</h3>
              <p class="item-author">{{ item.author }}</p>
              <p class="item-price">¥{{ item.price }}</p>
            </div>
            
            <div class="item-quantity">
              <button 
                class="quantity-button minus"
                @click="decreaseQuantity(item.id)"
                :disabled="item.quantity <= 1"
              >
                -
              </button>
              <span class="quantity">{{ item.quantity }}</span>
              <button 
                class="quantity-button plus"
                @click="increaseQuantity(item.id)"
              >
                +
              </button>
            </div>
            
            <div class="item-subtotal">
              ¥{{ (item.price * item.quantity).toFixed(2) }}
            </div>
            
            <button 
              class="remove-button"
              @click="removeItem(item.id)"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- 购物车摘要 -->
        <div class="cart-summary">
          <h3>カートの合計</h3>
          
          <div class="summary-item">
            <span>商品の合計</span>
            <span>¥{{ subtotal.toFixed(2) }}</span>
          </div>
          
          <div class="summary-item">
            <span>配送料</span>
            <span>¥{{ shipping.toFixed(2) }}</span>
          </div>
          
          <div class="summary-total">
            <span>合計</span>
            <span>¥{{ total.toFixed(2) }}</span>
          </div>
          
          <button class="checkout-button" @click="checkout">チェックアウト</button>
          
          <router-link to="/" class="continue-shopping">
            ショッピングを続ける
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// カートアイテムの型定義
interface CartItem {
  id: number
  name: string
  author: string
  price: number
  quantity: number
  rank?: number
  year?: string
}

// カートデータ
const cartItems = ref<CartItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// バックエンドからカートデータを取得
const fetchCartData = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await fetch('http://localhost:8000/api/cart/', {
      credentials: 'include' // セッションを保持するためにクレデンシャルを含める
    })
    if (!response.ok) {
      throw new Error('カートデータの取得に失敗しました')
    }
    const data = await response.json()
    // バックエンドからのデータを処理し、ネストされたnovel情報を正しく抽出し、priceを数値型に変換する
    cartItems.value = (data.items || []).map((item: any) => ({
      id: item.id,
      name: item.novel?.name || '未知の名前',
      author: item.novel?.author || '未知の作者',
      price: parseFloat(item.novel?.price) || 0,
      quantity: item.quantity || 1,
      rank: item.novel?.rank,
      year: item.novel?.year
    }))
  } catch (err) {
    error.value = err instanceof Error ? err.message : '未知のエラー'
    // 取得に失敗した場合は空の配列を使用
    cartItems.value = []
  } finally {
    loading.value = false
  }
}

// 商品の合計金額を計算
const subtotal = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
})

// 配送料（ここでは簡単なシミュレーション、注文金額が200円以上の場合配送料無料）
const shipping = computed(() => {
  return subtotal.value >= 200 ? 0 : 15
})

// 注文の合計金額を計算
const total = computed(() => {
  return subtotal.value + shipping.value
})

// 商品の数量を増やす
const increaseQuantity = async (id: number) => {
  try {
    const response = await fetch('http://localhost:8000/api/cart/update_item/', {
      method: 'PUT',
      credentials: 'include', // セッションを保持するためにクレデンシャルを含める
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        item_id: id,
        quantity: 1
      })
    })
    
    if (!response.ok) {
      throw new Error('数量の更新に失敗しました')
    }
    
    // 更新成功後、カートデータを再取得
    await fetchCartData()
    
    // カスタムイベントを送信して、App.vueにカートの数量の更新を通知
    window.dispatchEvent(new Event('cart-updated'))
  } catch (err) {
    console.error('数量の増加に失敗:', err)
    alert('数量の増加に失敗しました。後でもう一度お試しください。')
  }
}

// 画像の読み込みエラーを処理
const handleImageError = (event: Event, item: CartItem) => {
  // 画像の読み込みに失敗した場合、デフォルトのパスまたはプレースホルダーを使用します
  const img = event.target as HTMLImageElement
  // デフォルトの画像パスにダウングレード
  img.src = `/image/${item.year || '2025'}/1.jpg`
}

// 商品の数量を減らす
const decreaseQuantity = async (id: number) => {
  try {
    const response = await fetch('http://localhost:8000/api/cart/update_item/', {
      method: 'PUT',
      credentials: 'include', // セッションを保持するためにクレデンシャルを含める
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        item_id: id,
        quantity: -1
      })
    })
    
    if (!response.ok) {
      throw new Error('数量の更新に失敗しました')
    }
    
    // 更新成功後、カートデータを再取得
    await fetchCartData()
    
    // カスタムイベントを送信して、App.vueにカートの数量の更新を通知
    window.dispatchEvent(new Event('cart-updated'))
  } catch (err) {
    console.error('数量を減らすのに失敗しました:', err)
    alert('数量を減らすのに失敗しました。後でもう一度お試しください。')
  }
}

// 商品を削除
const removeItem = async (id: number) => {
  try {
    const response = await fetch(`http://localhost:8000/api/cart/remove_item/?item_id=${id}`, {
      method: 'DELETE',
      credentials: 'include' // セッションを保持するためにクレデンシャルを含める
    })
    
    if (!response.ok) {
      throw new Error('商品の削除に失敗しました')
    }
    
    // 削除成功後、カートデータを再取得
    await fetchCartData()
    
    // カスタムイベントを送信して、App.vueにカートの数量の更新を通知
    window.dispatchEvent(new Event('cart-updated'))
  } catch (err) {
    console.error('商品の削除に失敗しました:', err)
    alert('商品の削除に失敗しました。後でもう一度お試しください。')
  }
}

// チェックアウトを処理
const checkout = async () => {
  try {
    // 購入成功の通知を表示（透明な白いボックスの通知を使用）
    (window as any).showNotification('購入成功しました', 'success');
    
    // APIを呼び出してカートを空にする
    const response = await fetch('http://localhost:8000/api/cart/clear/', {
      method: 'DELETE',
      credentials: 'include' // セッションを保持するためにクレデンシャルを含める
    })
    
    if (!response.ok) {
      throw new Error('カートのクリアに失敗しました')
    }
    
    // クリア成功後、カートデータを再取得して、ページが空であることを確認
    await fetchCartData()
    
    // カスタムイベントを送信して、App.vueにカートの数量の更新を通知
    window.dispatchEvent(new Event('cart-updated'))
  } catch (err) {
    console.error('チェックアウト中にエラーが発生しました:', err)
  }
}

// コンポーネントのマウント後にカートデータを取得
onMounted(() => {
  fetchCartData()
})
</script>

<style scoped>
.cart {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 2rem;
}

.cart-container {
  max-width: 1400px;
  margin: 0 auto;
}

.cart-title {
  font-size: 1.75rem;
  margin-bottom: 2rem;
  color: #333;
}

/* 加载状态样式 */
.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 1.2rem;
}

/* 错误状态样式 */
.error {
  text-align: center;
  padding: 2rem;
  color: #e74c3c;
  font-size: 1.2rem;
  background-color: #fadbd8;
  border-radius: 8px;
}

.empty-cart {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  text-align: center;
}

.empty-cart p {
  font-size: 1.25rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.shop-now-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: #fff;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.shop-now-button:hover {
  background-color: #2980b9;
}

.cart-content {
  display: flex;
  gap: 2rem;
}

.cart-items {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.cart-item {
  display: grid;
  grid-template-columns: 100px 1fr 150px 120px 40px;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
  gap: 1rem;
}

.item-image .cover-placeholder.small {
    width: 80px;
    height: 120px;
    background-color: #e0e0e0;
    border-radius: 4px;
  }

  .item-image .item-image-src {
    width: 80px;
    height: 120px;
    object-fit: cover;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

.item-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-name {
  font-size: 1rem;
  font-weight: 500;
  color: #333;
}

.item-author {
  font-size: 0.875rem;
  color: #666;
}

.item-price {
  font-size: 1rem;
  font-weight: bold;
  color: #e74c3c;
}

.item-quantity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-button {
  width: 30px;
  height: 30px;
  border: 1px solid #ddd;
  background-color: #f8f8f8;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: all 0.3s ease;
}

.quantity-button:hover:not(:disabled) {
  background-color: #e8e8e8;
}

.quantity-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity {
  min-width: 30px;
  text-align: center;
  font-weight: 500;
}

.item-subtotal {
  font-weight: bold;
  text-align: right;
  color: #333;
}

.remove-button {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.remove-button:hover {
  background-color: #f8f8f8;
}

.cart-summary {
  width: 350px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.cart-summary h3 {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  color: #333;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: #666;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  margin: 1.5rem 0;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  font-weight: bold;
  font-size: 1.25rem;
  color: #333;
}

.checkout-button {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #27ae60;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-bottom: 1rem;
}

.checkout-button:hover {
  background-color: #229954;
}

.continue-shopping {
  display: block;
  text-align: center;
  color: #3498db;
  text-decoration: none;
  font-size: 0.875rem;
}

.continue-shopping:hover {
  text-decoration: underline;
}

@media (max-width: 1024px) {
  .cart-content {
    flex-direction: column;
  }
  
  .cart-summary {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .cart {
    padding: 1rem;
  }
  
  .cart-item {
    grid-template-columns: 80px 1fr;
    grid-template-rows: auto auto;
    grid-template-areas:
      "image details details"
      "quantity subtotal remove";
    gap: 0.5rem;
  }
  
  .item-image {
    grid-area: image;
  }
  
  .item-details {
    grid-area: details;
  }
  
  .item-quantity {
    grid-area: quantity;
    justify-content: flex-start;
  }
  
  .item-subtotal {
    grid-area: subtotal;
    text-align: left;
  }
  
  .remove-button {
    grid-area: remove;
    justify-self: end;
  }
}
</style>