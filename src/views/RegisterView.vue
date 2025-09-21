<template>
  <div class="register">
    <div class="register-container">
      <h2 class="register-title">サインイン</h2>
      <form class="register-form" @submit.prevent="handleRegister">
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
          <label for="email">メールアドレス</label>
          <input
            type="email"
            id="email"
            v-model="formData.email"
            placeholder="メールアドレスを入力してください"
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
        
        <div class="form-group">
          <label for="confirmPassword">パスワード（確認）</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="formData.confirm_password"
            placeholder="パスワードを再入力してください"
            required
          />
        </div>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <button type="submit" class="register-button" :disabled="isLoading">
          <span v-if="isLoading">サインイン中...</span>
          <span v-else>サインイン</span>
        </button>
      </form>
      
      <div class="login-link">
        既にアカウントをお持ちですか？
        <router-link to="/login">ログイン</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { getApiUrl, env } from '../config/env'

const router = useRouter()

// フォームデータ
const formData = ref({
  username: '',
  email: '',
  password: '',
  confirm_password: ''
})

// エラーメッセージ
const error = ref('')

// ローディング状態
const isLoading = ref(false)

// 登録処理
const handleRegister = async () => {
  // エラーメッセージをリセット
  error.value = ''
  
  // 簡単なフォームバリデーション
  if (formData.value.password !== formData.value.confirm_password) {
    error.value = 'パスワードが一致しません'
    return
  }
  
  // パスワードの長さをチェック
  if (formData.value.password.length < 6) {
    error.value = 'パスワードは6文字以上で入力してください'
    return
  }
  
  try {
    // ローディング状態を設定
    isLoading.value = true
    
    // 使用环境配置中的API地址
    const registerUrl = getApiUrl(env.REGISTER_URL)
    console.log('fetch APIを使用してリクエストを送信:', registerUrl)
    
    // リクエストパラメータを準備
    const requestOptions: RequestInit = {
      method: 'POST',
      credentials: 'include' as RequestCredentials, // セッションを維持するためにクレデンシャルを含める
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    }
    
    // fetchリクエストを送信
    const response = await fetch(registerUrl, requestOptions)
    
    // レスポンスデータを取得
    const responseData = await response.json()
    
    // 成功レスポンスを処理
    console.log('リクエストが正常に送信されました:', registerUrl)
    console.log('レスポンスステータス:', response.status)
    console.log('レスポンスデータ:', responseData)
    
    if (response.ok) {
      // 成功メッセージを表示
      alert('サインインが完了しました！ログインしてください。')
      
      // 登録成功後にログインページにリダイレクト
      router.push('/login')
    } else {
      // エラーレスポンスを処理
      error.value = responseData.error || '登録に失敗しました'
    }
    
  } catch (err) {
    // 詳細なエラー情報を表示
    console.error('登録リクエストエラー:', err)
    error.value = 'ネットワークエラーが発生しました'
  } finally {
    // ローディング状態をリセット
    isLoading.value = false
  }
}
</script>

<style scoped>
.register {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 2rem;
}

.register-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  width: 100%;
  max-width: 500px;
}

.register-title {
  text-align: center;
  font-size: 1.75rem;
  margin-bottom: 2rem;
  color: #333;
}

.register-form {
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

.form-group input {
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

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  text-align: center;
}

.register-button {
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

.register-button:hover {
  background-color: #2980b9;
}

.login-link {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: #666;
}

.login-link a {
  color: #3498db;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .register-container {
    padding: 1.5rem;
  }
}
</style>