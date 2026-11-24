/** LogPage —— 手记索引 */
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { listPosts } from '../api/posts'
import { fmtDate, keywordOf } from '../utils'

export default function LogPage() {
  const { data: posts, isPending, error } = useQuery({
    queryKey: ['posts', 100],
    queryFn: () => listPosts({ page: 1, size: 100 }),
  })

  return (
    <>
      <div className="ink-title"><h1>手 记</h1><span className="stamp">ALL LOGS</span></div>
      {isPending && <p className="loading">正在翻笔记本…</p>}
      {error && <div className="empty">加载失败：{(error as Error).message}</div>}
      {posts?.length === 0 && (
        <div className="empty-mascot">
          <img src="/mascot.png" alt="手绘小熊猫头像" />
          <p>还没有任何手记。</p>
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
