import { defineStore } from 'pinia'
import { getApiUrl, env } from '../config/env'

// 小説データの型を定義
interface Novel {
  id: number
  name: string
  author: string
  publisher: string
  rank: number
  price: number
}

// 年間小説データの型を定義
interface YearlyNovels {
  [year: string]: {
    novels: Novel[]
    loading: boolean
    error: string | null
  }
}

export const useNovelsStore = defineStore('novels', {
  state: (): {
    yearlyNovels: YearlyNovels
    years: string[]
    selectedYear: string
  } => ({
    yearlyNovels: {},
    years: ['2025', '2024', '2023', '2022', '2021', '2020'],
    selectedYear: '2025'
  }),

  getters: {
    currentNovels: (state) => {
      return state.yearlyNovels[state.selectedYear]?.novels || []
    },
    
    currentLoading: (state) => {
      return state.yearlyNovels[state.selectedYear]?.loading || false
    },
    
    currentError: (state) => {
      return state.yearlyNovels[state.selectedYear]?.error || null
    },
    
    firstPlace: (state) => {
      const novels = state.yearlyNovels[state.selectedYear]?.novels || []
      return novels.find(novel => novel.rank === 1)
    },
    
    otherPlaces: (state) => {
      const novels = state.yearlyNovels[state.selectedYear]?.novels || []
      return novels.filter(novel => novel.rank > 1)
    }
  },

  actions: {
    setSelectedYear(year: string) {
      if (this.years.includes(year)) {
        this.selectedYear = year
      }
    },
    
    async fetchNovels(year?: string) {
      const targetYear = year || this.selectedYear
      if (!this.yearlyNovels[targetYear]) {
        this.yearlyNovels[targetYear] = {
          novels: [],
          loading: false,
          error: null
        }
      }
      
      this.yearlyNovels[targetYear].loading = true
      this.yearlyNovels[targetYear].error = null
      
      try {
        const novelsUrl = getApiUrl(`${env.NOVELS_URL}?year=${targetYear}`)
        const response = await fetch(novelsUrl)
        if (!response.ok) {
          throw new Error('小説の取得に失敗しました')
        }
        const data = await response.json()
        this.yearlyNovels[targetYear].novels = data.results || []
        
        if (this.yearlyNovels[targetYear].novels.length === 0) {
          this.yearlyNovels[targetYear].novels = this.getMockNovelsForYear(targetYear)
        }
      } catch (err) {
        this.yearlyNovels[targetYear].error = err instanceof Error ? err.message : '未知のエラー'
        this.yearlyNovels[targetYear].novels = this.getMockNovelsForYear(targetYear)
      } finally {
        this.yearlyNovels[targetYear].loading = false
      }
    },
    
    getMockNovelsForYear(year: string): Novel[] {
      if (year === '2025') {
        return [
          {
            id: 1,
            name: '負けヒロインが多すぎる！',
            author: '雨森たきび(著) / いみぎむる(イラスト)',
            publisher: 'ガガガ文庫 / 小学館 (全8巻)',
            rank: 1,
            price: 89.00
          },
          {
            id: 2,
            name: '誰が勇者を殺したか',
            author: '駄犬',
            publisher: 'KADOKAWA (スニーカー文庫)',
            rank: 2,
            price: 75.00
          },
          {
            id: 3,
            name: '時々ボソッとロシア語でデレる隣のアーリャさん',
            author: '燦々SUN',
            publisher: 'KADOKAWA (角川スニーカー文庫)',
            rank: 3,
            price: 68.00
          },
          {
            id: 4,
            name: 'こちら、終末停滞委員会。',
            author: '逢縁奇演',
            publisher: 'KADOKAWA (電撃文庫)',
            rank: 4,
            price: 59.00
          },
          {
            id: 5,
            name: 'お隣の天使様にいつの間にか駄目人間にされていた件',
            author: '佐伯さん',
            publisher: 'SBクリエイティブ (GA文庫)',
            rank: 5,
            price: 85.00
          }
        ]
      }
      
      // 2025年のデータのみ保持し、他の年は空配列を返す
      return []
    },
    
    async getNovelDetail(novelId: number) {
      try {
        const novelDetailUrl = getApiUrl(`${env.NOVELS_URL}${novelId}/`)
        const response = await fetch(novelDetailUrl)
        if (!response.ok) {
          throw new Error('小説の詳細の取得に失敗しました')
        }
        const data = await response.json()
        return data
      } catch (err) {
        console.error('小説の詳細の取得に失敗:', err)
        throw err
      }
    },
    
    async addToCart(novelId: number) {
      try {
        // CSRFトークンを取得
        const getCookie = (name: string) => {
          const cookieValue = document.cookie
            .split('; ') 
            .find(row => row.startsWith(name + '=')) 
            ?.split('=')[1];
          return cookieValue ? decodeURIComponent(cookieValue) : '';
        };
        
        const csrftoken = getCookie('csrftoken');
        
        const addItemUrl = getApiUrl(env.CART_ADD_ITEM_URL)
        const response = await fetch(addItemUrl, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify({
            novel_id: novelId,
            quantity: 1
          })
        })
        
        if (!response.ok) {
          throw new Error('カートへの追加に失敗しました')
        }
        
        // 成功メッセージを表示（透明な白い枠の通知を使用）
        (window as any).showNotification('カートに追加しました！', 'success');
        window.dispatchEvent(new Event('cart-updated'))
      } catch (err) {
        console.error('カートへの追加に失敗:', err)
        alert('カートへの追加に失敗しました。後でもう一度お試しください。')
      }
    }
  }
})