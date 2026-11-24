/** LoginPage —— 登船签到（OTP 两步流程） */
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { requestOtp } from '../api/auth'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [phoneErr, setPhoneErr] = useState('')
  const [msg, setMsg] = useState('')
  const [kind, setKind] = useState<'ok' | 'err'>('ok')
  const [countdown, setCountdown] = useState(0)
  const [busy, setBusy] = useState(false)

  if (user) { navigate('/'); return null }

  const sendCode = async () => {
    if (!/^1\d{10}$/.test(phone)) return setPhoneErr('请输入正确的 11 位手机号')
    setPhoneErr('')
    setBusy(true)
    try {
      const note = await requestOtp(phone)
      setMsg(note)
      setKind('ok')
      setCountdown(60)
      const timer = setInterval(() => {
        setCountdown((s) => {
          if (s <= 1) clearInterval(timer)
          return s - 1
        })
      }, 1000)
    } catch (e) {
      setMsg((e as Error).message)
      setKind('err')
    } finally {
      setBusy(false)
    }
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setMsg('')
    try {
      await login(phone, code)
      navigate(sessionStorage.getItem('loginRedirect') || '/')
      sessionStorage.removeItem('loginRedirect')
    } catch (e2) {
      setMsg((e2 as Error).message)
      setKind('err')
    }
  }

  return (
    <div className="form-card">
      <img className="login-mascot" src="/mascot.png" alt="手绘小熊猫头像" />
      <h2>登船签到</h2>
      <form onSubmit={submit}>
        <div className="field">
          <label>手机号</label>
          <input
            type="tel" maxLength={11} placeholder="11 位手机号" autoComplete="tel"
            value={phone} onChange={(e) => { setPhone(e.target.value); setPhoneErr('') }}
          />
          <p className="error">{phoneErr}</p>
        </div>
        <div className="field">
          <label>验证码</label>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              type="text" maxLength={6} placeholder="6 位验证码" style={{ flex: 1 }}
              value={code} onChange={(e) => setCode(e.target.value)}
            />
            <button type="button" className="btn btn-sm" disabled={busy || countdown > 0} onClick={sendCode}>
              {countdown > 0 ? `${countdown}s` : busy ? '发送中…' : '获取验证码'}
            </button>
          </div>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn-primary">登陆 / 注册</button>
        </div>
        <p className={`form-msg ${kind}`} style={kind === 'err' ? { color: 'var(--accent)' } : undefined}>{msg}</p>
      </form>
      <p className="login-hint" style={{ textAlign: 'center', marginTop: 12 }}>
        新手机号验证后自动注册，无需密码
      </p>
    </div>
  )
}
