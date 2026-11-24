/** MinePage —— 草稿箱（自己的文章列表） */
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { listPosts } from '../api/posts'
import { useAuth } from '../hooks/useAuth'
import { fmtDate } from '../utils'

export default function MinePage() {
  const { user, loading } = useAuth()
  const navigate = useNavigate()
  // 后端 /api/posts 对登录用户自动返回「已发布 + 自己的草稿」，
  // 前端再按 owner 过滤（与原 RLS 语义一致：只看得到自己的）
  const { data: posts, isPending, error } = useQuery({
    queryKey: ['mine'],
    queryFn: () => listPosts({ page: 1, size: 100 }),
    enabled: !!user,
  })
  const mine = posts?.filter((p) => p.owner_id === user?.id)

  if (!loading && !user) { navigate('/login'); return null }

  return (
    <>
      <div className="ink-title">
        <h1>草稿箱</h1>
        <Link className="btn btn-sm btn-primary" style={{ width: 'auto' }} to="/write">+ 写一条</Link>
      </div>
      {isPending && <p className="loading">正在翻你的笔记本…</p>}
      {error && <div className="empty">加载失败：{(error as Error).message}</div>}
      {mine?.length === 0 && <div className="empty">你的笔记本还是空白的</div>}
      {mine && mine.length > 0 && (
        <div className="log-list">
          {mine.map((p) => (
            <Link key={p.id} className="log-item" to={`/post/${p.id}`}>
              <h3>{p.title}</h3>
              <div className="log-meta">
                {p.status !== 'published' && <span className="badge">草稿</span>}
                <span>{fmtDate(p.created_at)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  )
}
