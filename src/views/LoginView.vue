<template>
  <div class="login">
    <div class="login-container">
      <h2 class="login-title">ユーザーログイン</h2>
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">ユーザー名</label>
          <input
            type="text"
            id="username"
            v-model="formData.username"
            placeholder="ユーザー名を入力してください"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">パスワード</label>
          <input
            type="password"
            id="password"
            v-model="formData.password"
            placeholder="パスワードを入力してください"
            required
          />
        </div>
        
        <div class="form-group remember-me">
          <input
            type="checkbox"
            id="rememberMe"
            v-model="formData.rememberMe"
          />
          <label for="rememberMe">ログイン状態を保持する</label>
        </div>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <button type="submit" class="login-button" :disabled="isLoading">
          <span v-if="isLoading">ログイン中...</span>
          <span v-else>ログイン</span>
        </button>
      </form>
      
      <div class="register-link">
        アカウントをお持ちでないですか？
        <router-link to="/register">新規登録</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// フォームデータ
const formData = ref({
  username: '',
  password: '',
  rememberMe: true
})

// エラーメッセージ
const error = ref('')

// ローディング状態
const isLoading = ref(false)

// ログイン処理
const handleLogin = async () => {
  // エラーメッセージをリセット
  error.value = ''
  
  // 簡単なフォームバリデーション
  if (!formData.value.username || !formData.value.password) {
    error.value = 'ユーザー名とパスワードを入力してください'
    return
  }
  
  try {
    // ローディング状態を設定
    isLoading.value = true
    
    // axiosの設定問題を回避するため、fetch APIを使用してログインリクエストを送信
    const absoluteUrl = 'http://localhost:8000/api/auth/login/'
    console.log('fetch APIを使用してリクエストを送信:', absoluteUrl)
    
    // リクエストパラメータを準備
    const requestOptions: RequestInit = {
      method: 'POST',
      credentials: 'include' as RequestCredentials, // セッションを維持するためにクレデンシャルを含める
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: formData.value.username,
        password: formData.value.password,
        remember_me: formData.value.rememberMe
      })
    }
    
    // fetchリクエストを送信
    const response: Response = await fetch(absoluteUrl, requestOptions)
    
    // レスポンスデータを取得
    const responseData: any = await response.json()
    
    // 成功レスポンスを処理
    console.log('リクエストが正常に送信されました:', absoluteUrl)
    console.log('レスポンスステータス:', response.status)
    console.log('レスポンスデータ:', responseData)
    
    if (response.ok) {
      // ユーザー情報をローカルストレージに保存
      localStorage.setItem('user', JSON.stringify(responseData.user))
      
      // 成功メッセージを表示
      alert('ログインに成功しました！')
      
      // ログイン成功後にホームページにリダイレクト
      router.push('/')
    } else {
      // エラーレスポンスを処理
      error.value = responseData.error || 'ログインに失敗しました'
    }
    
  } catch (err) {
    // 詳細なエラー情報を表示
    console.error('ログインリクエストエラー:', err)
    error.value = 'ネットワークエラーが発生しました'
  } finally {
    // ローディング状態をリセット
    isLoading.value = false
  }
}
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 2rem;
}

.login-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  width: 100%;
  max-width: 500px;
}

.login-title {
  text-align: center;
  font-size: 1.75rem;
  margin-bottom: 2rem;
  color: #333;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 1rem;
  font-weight: 500;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.remember-me {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.remember-me input[type="checkbox"] {
  margin: 0;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  text-align: center;
}

.login-button {
  padding: 0.75rem 1rem;
  background-color: #3498db;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.login-button:hover {
  background-color: #2980b9;
}

.register-link {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: #666;
}

.register-link a {
  color: #3498db;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .login-container {
    padding: 1.5rem;
  }
}
</style>