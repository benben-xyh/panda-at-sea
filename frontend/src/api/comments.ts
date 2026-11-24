import { client } from './client'
import type { Comment } from './types'

export async function listComments(postId: number) {
  const r = await client.get<Comment[]>(`/posts/${postId}/comments`)
  return r.data
}

export async function createComment(postId: number, content: string) {
  const r = await client.post<Comment>(`/posts/${postId}/comments`, { content })
  return r.data
}

export async function deleteComment(id: number) {
  await client.delete(`/comments/${id}`)
}
