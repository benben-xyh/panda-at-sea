import { client, setAccessToken } from './client'
import type { User } from './types'

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
  is_new_user: boolean
}

export async function requestOtp(phone: string): Promise<string> {
  const r = await client.post<{ msg: string }>('/auth/otp/request', { phone })
  return r.data.msg
}

export async function verifyOtp(phone: string, code: string): Promise<TokenResponse> {
  const r = await client.post<TokenResponse>('/auth/otp/verify', { phone, code })
  setAccessToken(r.data.access_token) // 登录成功即持票
  return r.data
}

export async function fetchMe(): Promise<User> {
  const r = await client.get<User>('/auth/me')
  return r.data
}

export async function trySilentRestore(): Promise<User | null> {
  // 刷新页面后用 refresh cookie 静默续期，再拿当前用户
  const token = await axiosRefresh()
  if (!token) return null
  return fetchMe()
}

async function axiosRefresh(): Promise<string | null> {
  try {
    const r = await client.post<TokenResponse>('/auth/refresh')
    setAccessToken(r.data.access_token)
    return r.data.access_token
  } catch {
    return null
  }
}

export async function logout(): Promise<void> {
  try {
    await client.post('/auth/logout')
  } finally {
    setAccessToken(null)
  }
}
