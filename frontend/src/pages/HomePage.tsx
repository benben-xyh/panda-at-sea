/** HomePage —— 瓷砖导航格 + 最新手记（TanStack Query） */
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { listPosts } from '../api/posts'
import { useAuth } from '../hooks/useAuth'
import { DoodleAbout, DoodleHome, DoodleLog, DoodleLogin, DoodleMine, DoodleWrite } from '../components/Doodle'
import { fmtDate, keywordOf } from '../utils'

export default function HomePage() {
  const { user } = useAuth()
  const { data: posts, isPending, error } = useQuery({
    queryKey: ['posts', 5],
    queryFn: () => listPosts({ page: 1, size: 5 }),
  })

  return (
    <>
      <div className="tile-grid">
        <Link className="tile" to="/log"><DoodleLog /><span className="tile-name">手 记</span><span className="tile-note">所有日志 · 慢慢翻</span></Link>
        <Link className="tile tile-accent" to="/write"><DoodleWrite /><span className="tile-name">写 字</span><span className="tile-note">记录一件小事</span></Link>
        <Link className="tile" to="/about"><DoodleAbout /><span className="tile-name">关 于</span><span className="tile-note">这本小志的来历</span></Link>
        <Link className="tile" to={user ? '/mine' : '/login'}>
          {user ? <DoodleMine /> : <DoodleLogin />}
          <span className="tile-name">{user ? '草稿箱' : '登 陆'}</span>
          <span className="tile-note">{user ? '自己写的字' : '登船签到'}</span>
        </Link>
        <div className="tile tile-panda">
          <img src="/mascot.png" alt="手绘小熊猫头像" />
          <span className="tile-name">看板熊</span><span className="tile-note">值班中</span>
        </div>
        <Link className="tile" to="/log"><DoodleHome /><span className="tile-name">最 新</span><span className="tile-note">就在下面</span></Link>
      </div>

      <div className="ink-title"><h2>最新手记</h2><span className="stamp">RECENT</span></div>

      {isPending && <p className="loading">正在翻笔记本…</p>}
      {error && <div className="empty">加载失败：{(error as Error).message}</div>}
      {posts?.length === 0 && (
        <div className="empty-mascot">
          <img src="/mascot.png" alt="手绘小熊猫头像" />
          <p>笔记本还是空白的——<br />{user ? <Link to="/write" style={{ color: 'var(--accent)' }}>写下第一条手记 →</Link> : '登陆后写下第一条手记吧'}</p>
        </div>
      )}
      {posts && posts.length > 0 && (
        <div className="log-list">
          {posts.map((p) => (
            <Link key={p.id} className="log-item" to={`/post/${p.id}`}>
              <h3>{p.title}</h3>
              <p className="log-key">「{keywordOf(p)}」</p>
              <div className="log-meta">
                <span>{fmtDate(p.created_at)}</span>
                <span>{p.owner_name ?? '匿名船员'}</span>
                {p.status !== 'published' && <span className="badge">草稿</span>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  )
}
