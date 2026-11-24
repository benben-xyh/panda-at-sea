/** App —— 布局（标牌头部 / 滚动小字报 / 页脚涂鸦）+ React Router 路由树 */
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'

export default function App() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <>
      <header className="site-header">
        <div className="masthead">
          <NavLink to="/" className="logo-link">
            <img className="logo-mascot" src="/mascot.png" alt="小熊猫看板头像" />
            <span className="logo-text">
              熊猫海上<span className="logo-en">PANDA&nbsp;AT&nbsp;SEA</span>
            </span>
          </NavLink>
          <nav className="ink-nav">
            <NavLink to="/" end>首页</NavLink>
            <NavLink to="/log">日志</NavLink>
            <NavLink to="/about">关于</NavLink>
            {user && <NavLink to="/write">写字</NavLink>}
            {user && <NavLink to="/mine">草稿箱</NavLink>}
            {!user && <NavLink to="/login">登陆</NavLink>}
            {user && (
              <span id="nav-user">
                <span className="nav-username">{user.nickname ?? '船员'}</span>
                <a
                  href="javascript:void(0)"
                  onClick={async () => {
                    await logout()
                    navigate('/')
                  }}
                >
                  下船
                </a>
              </span>
            )}
          </nav>
        </div>
        <div className="ticker">
          <span>✳ 一本手绘的小志 ✳ 慢慢写，慢慢看 ✳ 不赶时间 ✳ 欢迎登船 ✳ 一本手绘的小志 ✳ 慢慢写，慢慢看 ✳ 不赶时间 ✳ 欢迎登船 ✳</span>
        </div>
      </header>

      <main className="page">
        {loading ? <p className="loading">正在解开缆绳…</p> : <Outlet />}
      </main>

      <footer className="site-footer">
        <div className="footer-inner">
          <span className="footer-doodle" aria-hidden="true">
            <svg viewBox="0 0 120 36" width="120" height="36" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
              <path d="M4 28c6-6 12 6 18 0s12 6 18 0 12 6 18 0 12 6 18 0 12 6 18 0" />
              <path d="M46 20l28-6 8 10-34 2z" />
              <path d="M60 14V4l10 8" />
            </svg>
          </span>
          <p>手绘 · 慢速 · 无广告 — React + TS 前端 · FastAPI 后端</p>
          <p className="footer-small">© 2026 熊猫海上 · inspired by <a href="https://100r.co" target="_blank" rel="noreferrer">100r.co</a></p>
        </div>
      </footer>
    </>
  )
}
