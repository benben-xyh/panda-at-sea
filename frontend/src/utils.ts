/** 通用小工具 */
export function fmtDate(ts: string | undefined): string {
  if (!ts) return ''
  const d = new Date(ts)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}.${p(d.getMonth() + 1)}.${p(d.getDate())}`
}

export function fmtDateTime(ts: string | undefined): string {
  if (!ts) return ''
  const d = new Date(ts)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}.${p(d.getMonth() + 1)}.${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

/** 关键词句：优先摘要，否则正文第一句，截 40 字 */
export function keywordOf(post: { summary?: string | null; content?: string | null }): string {
  const first = (post.summary || (post.content || '').split(/\n/)[0] || '').trim()
  return first.length > 40 ? first.slice(0, 40) + '…' : first
}
