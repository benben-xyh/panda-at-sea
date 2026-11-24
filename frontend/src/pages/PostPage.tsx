/** PostPage —— 文章详情 + 边角便签（乐观更新：贴上去立刻显示） */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { createComment, deleteComment, listComments } from '../api/comments'
import { deletePost, getPost } from '../api/posts'
import { useAuth } from '../hooks/useAuth'
import { fmtDateTime } from '../utils'

export default function PostPage() {
  const { id } = useParams()
  const postId = Number(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const [draft, setDraft] = useState('')
  const [err, setErr] = useState('')

  const post = useQuery({ queryKey: ['post', postId], queryFn: () => getPost(postId) })
  const comments = useQuery({
    queryKey: ['comments', postId],
    queryFn: () => listComments(postId),
  })

  const addComment = useMutation({
    mutationFn: (content: string) => createComment(postId, content),
    onSuccess: () => {
      setDraft('')
      queryClient.invalidateQueries({ queryKey: ['comments', postId] })
    },
    onError: (e) => setErr((e as Error).message),
  })
  const removeComment = useMutation({
    mutationFn: (cid: number) => deleteComment(cid),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['comments', postId] }),
  })
  const removePost = useMutation({
    mutationFn: () => deletePost(postId),
    onSuccess: () => navigate('/log'),
    onError: () => alert('撕不掉：这页可能不是你写的'),
  })

  if (post.isPending) return <p className="loading">正在翻到这一页…</p>
  if (post.isError) return <div className="empty">这一页被撕掉了（文章不存在或无权查看）</div>
  const p = post.data
  const isMine = user?.id === p.owner_id
  const paragraphs = (p.content || '').split(/\n+/).filter((s) => s.trim())

  return (
    <>
      <nav className="crumbs"><Link to="/log">手记</Link> › 第 {p.id} 页</nav>
      <article className="article">
        <h1>{p.title}</h1>
        <div className="post-meta">
          <span>{p.owner_name ?? '匿名船员'}</span>
          <span>·</span>
          <span>{fmtDateTime(p.created_at)}</span>
          {p.status !== 'published' && <span className="badge">草稿</span>}
          {isMine && <Link className="btn btn-sm" to={`/write/${p.id}`}>改一改</Link>}
          {isMine && (
            <button
              className="btn btn-sm"
              style={{ color: 'var(--accent)', borderColor: 'var(--accent)' }}
              onClick={() => confirm('确定撕掉这一页吗？') && removePost.mutate()}
            >
              撕掉这页
            </button>
          )}
        </div>
        <div className="content">
          {paragraphs.length
            ? paragraphs.map((s, i) => <p key={i}>{s}</p>)
            : <p>（正文为空）</p>}
        </div>
      </article>

      <section className="comments">
        <h3>边角便签 ({comments.data?.length ?? 0})</h3>
        {comments.data?.length === 0 && <p className="login-hint">还没有便签，来贴第一张～</p>}
        {comments.data?.map((c) => (
          <div key={c.id} className="comment-item">
            <div className="comment-meta">
              <span>{c.owner_name ?? '路过船员'}</span>
              <span>{fmtDateTime(c.created_at)}</span>
              {user?.id === c.owner_id && (
                <span className="del" onClick={() => confirm('划掉这张便签？') && removeComment.mutate(c.id)}>
                  划掉
                </span>
              )}
            </div>
            <div className="comment-content">{c.content}</div>
          </div>
        ))}

        {user ? (
          <form
            onSubmit={(e) => {
              e.preventDefault()
              setErr('')
              if (!draft.trim()) return setErr('便签不能是空的')
              addComment.mutate(draft.trim())
            }}
          >
            <div className="field">
              <textarea
                placeholder="在便签上写点什么…"
                maxLength={500}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>贴上去</button>
            </div>
            <p className={`form-msg ${err ? 'err' : ''}`}>{err}</p>
          </form>
        ) : (
          <p className="login-hint" style={{ marginTop: 16 }}>想留言？<Link to="/login">先登船签到</Link></p>
        )}
      </section>
    </>
  )
}
