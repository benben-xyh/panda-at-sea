/** axios 客户端：Bearer 注入 + 401 静默续期（升级方案 §11 关键点①③） */
import axios from 'axios'

export const client = axios.create({
  baseURL: '/api',
  withCredentials: true, // refresh cookie 走 httpOnly
})

// access token 存内存（不进 localStorage，XSS 偷不走）
let accessToken: string | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

client.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

// 401 → 用 refresh cookie 换新 token → 重放原请求一次；再失败则清态
let refreshing: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  try {
    const r = await axios.post('/api/auth/refresh', null, { withCredentials: true })
    accessToken = r.data.access_token
    return accessToken
  } catch {
    accessToken = null
    return null
  }
}

client.interceptors.response.use(undefined, async (error) => {
  const original = error.config
  if (error.response?.status === 401 && !original._retried && !original.url.includes('/auth/')) {
    original._retried = true
    refreshing = refreshing ?? refreshAccessToken()
    const token = await refreshing
    refreshing = null
    if (token) {
      original.headers.Authorization = `Bearer ${token}`
      return client(original)
    }
  }
  return Promise.reject(error)
})
