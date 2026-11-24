/** WritePage —— 写字 / 改一改（/write 与 /write/:id 共用） */
import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createPost, getPost, updatePost } from '../api/posts'
import { useAuth } from '../hooks/useAuth'

export default function WritePage() {
  const { id } = useParams()
  const editId = id ? Number(id) : null
  const navigate = useNavigate()
  const { user } = useAuth()
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [content, setContent] = useState('')
  const [msg, setMsg] = useState('')
  const [kind, setKind] = useState<'ok' | 'err'>('err')

  // 编辑模式：取原文预填
  const existing = useQuery({
    queryKey: ['post', editId],
    queryFn: () => getPost(editId!),
    enabled: editId !== null,
  })
  useEffect(() => {
    if (existing.data) {
      setTitle(existing.data.title)
      setSummary(existing.data.summary ?? '')
      setContent(existing.data.content ?? '')
    }
  }, [existing.data])

  const save = useMutation({
    mutationFn: () => {
      const body = { title: title.trim(), summary: summary.trim(), content: content.trim() }
      return editId ? updatePost(editId, body) : createPost(body)
    },
    onSuccess: (saved) => navigate(`/post/${saved.id}`),
    onError: (e) => { setMsg((e as Error).message); setKind('err') },
  })

  if (!user) {
    sessionStorage.setItem('loginRedirect', editId ? `/write/${editId}` : '/write')
    navigate('/login')
    return null
  }
  if (editId && existing.isPending) return <p className="loading">正在翻到这一页…</p>
  if (editId && existing.isError) return <div className="empty">这一页不存在，或不是你写的</div>

  return (
    <div className="form-card wide">
      <h2>{editId ? '改一改' : '写一条手记'}</h2>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          setMsg('')
          if (!title.trim()) { setMsg('标题不能是空的'); setKind('err'); return }
          save.mutate()
        }}
      >
        <div className="field">
          <label>标题 *</label>
          <input maxLength={100} placeholder="这一页的标题" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="field">
          <label>关键词句（可选，索引页展示）</label>
          <input maxLength={120} placeholder="一句话概括这页" value={summary} onChange={(e) => setSummary(e.target.value)} />
        </div>
        <div className="field">
          <label>正文</label>
          <textarea placeholder="慢慢写，换行会保留" value={content} onChange={(e) => setContent(e.target.value)} />
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn-primary">{editId ? '保存' : '贴上去'}</button>
        </div>
        <p className={`form-msg ${kind}`}>{msg}</p>
      </form>
    </div>
  )
}
