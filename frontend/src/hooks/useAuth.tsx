/** useAuth —— 登录态 Context（替代原 renderNav + sessionStorage 回跳） */
import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import * as authApi from '../api/auth'
import type { User } from '../api/types'

interface AuthState {
  user: User | null
  loading: boolean          // 首次恢复会话中
  login: (phone: string, code: string) => Promise<boolean>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  login: async () => false,
  logout: async () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // 挂载时用 refresh cookie 静默恢复会话
  useEffect(() => {
    authApi.trySilentRestore().then((u) => {
      setUser(u)
      setLoading(false)
    })
  }, [])

  const login = useCallback(async (phone: string, code: string) => {
    try {
      const token = await authApi.verifyOtp(phone, code)
      setUser(token.user)
      return true
    } catch (e) {
      throw e
    }
  }, [])

  const logout = useCallback(async () => {
    await authApi.logout()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
