import { client } from './client'
import type { Post } from './types'

export interface PostInput {
  title: string
  summary?: string
  content?: string
  status?: 'published' | 'draft'
}

export async function listPosts(params: { page?: number; size?: number; q?: string } = {}) {
  const r = await client.get<Post[]>('/posts', { params })
  return r.data
}

export async function getPost(id: number) {
  const r = await client.get<Post>(`/posts/${id}`)
  return r.data
}

export async function createPost(body: PostInput) {
  const r = await client.post<Post>('/posts', body)
  return r.data
}

export async function updatePost(id: number, body: Partial<PostInput>) {
  const r = await client.patch<Post>(`/posts/${id}`, body)
  return r.data
}

export async function deletePost(id: number) {
  await client.delete(`/posts/${id}`)
}
