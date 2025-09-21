<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getApiUrl, env } from './config/env'

const router = useRouter()

// ユーザー状態
const currentUser = ref<any>(null)

// カートの商品数、初期は0
const cartItemCount = ref<number>(0)

// バックエンドからカートの実際の商品数を取得
const fetchCartItemCount = async () => {
  try {
    const cartUrl = getApiUrl(env.CART_URL)
    const response = await fetch(cartUrl, {
      credentials: 'include' // セッションを維持するためにクレデンシャルを含める
    })
    
    if (response.ok) {
      const data = await response.json()
      // バックエンドから返されたtotal_itemsフィールドを直接使用
      cartItemCount.value = data.total_items || 0
    } else {
      // 取得に失敗した場合は0のままにする
      cartItemCount.value = 0
    }
  } catch (err) {
    console.error('カートの数量の取得に失敗:', err)
    cartItemCount.value = 0
  }
}

// カートの更新通知を受信するためのイベントリスナーを追加
const handleCartUpdated = () => {
  fetchCartItemCount();
}

// イベントリスナーを登録
onMounted(() => {
  window.addEventListener('cart-updated', handleCartUpdated);
  checkUserLoginStatus();
  fetchCartItemCount();
})

// イベントリスナーをクリーンアップ
onUnmounted(() => {
  window.removeEventListener('cart-updated', handleCartUpdated);
})

// ログインボタンのクリックを処理
const handleLogin = () => {
  router.push('/login')
}

// ログアウトを処理
const handleLogout = async () => {
  try {
    // バックエンドのログアウトAPIを呼び出す
    const logoutUrl = getApiUrl(env.LOGOUT_URL)
    await fetch(logoutUrl, {
      method: 'POST',
      credentials: 'include'
    })
    
    // ローカルストレージのユーザー情報を削除
    localStorage.removeItem('user')
    currentUser.value = null
    
    // ホームページにリダイレクト
    router.push('/')
  } catch (err) {
    console.error('ログアウトに失敗しました:', err)
    alert('ログアウトに失敗しました。後でもう一度お試しください。')
  }
}

// カートボタンのクリックを処理
const handleCart = () => {
  router.push('/cart')
}

// ユーザーのログイン状態を確認
const checkUserLoginStatus = () => {
  const userData = localStorage.getItem('user')
  if (userData) {
    try {
      currentUser.value = JSON.parse(userData)
    } catch (e) {
      console.error('ユーザーデータの解析に失敗しました:', e)
      localStorage.removeItem('user')
    }
  }
}

// コンポーネントマウント時にユーザーのログイン状態を確認し、カートの数量を取得
// 注意：ここのonMountedは上に移動されています、イベントリスナーの登録が含まれています

// 通知関連の状態
const notification = ref<{ show: boolean; message: string; type: 'success' | 'error' }>({
  show: false,
  message: '',
  type: 'success'
})

// 通知を表示する関数
const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  }
  
  // 3秒後に自動的に通知を非表示にする
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

// 通知を表示する関数をwindowオブジェクトにマウントし、他のコンポーネントで使用できるようにする
(window as any).showNotification = showNotification
</script>

<template>
  <div class="app">
    <!-- 通知コンポーネント -->
    <div 
      v-if="notification.show" 
      class="notification" 
      :class="notification.type"
    >
      {{ notification.message }}
    </div>
    
    <!-- ナビゲーションバー -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <router-link to="/" class="logo-link">
            <h1>このラノベすごいランキング</h1>
          </router-link>
        </div>
        <div class="user-actions">
          <!-- 用户已登录时显示用户名和登出按钮 -->
          <div v-if="currentUser" class="user-info">
            <span class="username">{{ currentUser.username }}</span>
            <button class="logout-button" @click="handleLogout">ログアウト</button>
          </div>
          <!-- 用户未登录时显示登录按钮 -->
          <button v-else class="login-button" @click="handleLogin">ログイン</button>
          <button class="cart-button" @click="handleCart">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24" height="24"
              viewBox="0 0 24 24"
              fill="none"
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
            <span v-if="cartItemCount > 0" class="cart-count">{{ cartItemCount }}</span>
          </button>
        </div>
      </div>
    </header>

    <!-- ルートビュー -->
    <router-view />
  </div>
</template>

<style scoped>
/* グローバルスタイル */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans JP', sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

/* ナビゲーションバースタイル */
.header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-link {
  text-decoration: none;
}

.logo h1 {
  font-size: 1.5rem;
  color: #333;
  font-weight: bold;
}

.user-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

.login-button {
  padding: 0.75rem 1.5rem;
  border: 1px solid #333;
  background-color: #fff;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.login-button:hover {
  background-color: #333;
  color: #fff;
}

.cart-button {
  padding: 0.75rem;
  border: none;
  background-color: #f8f8f8;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.cart-count {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #e74c3c;
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-button:hover {
  background-color: #e8e8e8;
}

@media (max-width: 768px) {
    .header-content {
      flex-direction: column;
      gap: 1rem;
    }
  }
  
  /* 通知スタイル */
  .notification {
    position: fixed;
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
    padding: 1rem 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 2000;
    font-size: 1rem;
    font-weight: 500;
    opacity: 0.9;
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
  }
  
  .notification.success {
    background-color: rgba(255, 255, 255, 0.95);
    color: #27ae60;
    border: 1px solid rgba(39, 174, 96, 0.3);
  }
  
  .notification.error {
    background-color: rgba(255, 255, 255, 0.95);
    color: #e74c3c;
    border: 1px solid rgba(231, 76, 60, 0.3);
  }
  
  @media (max-width: 768px) {
    .notification {
      width: 90%;
      text-align: center;
    }
  }
</style>
