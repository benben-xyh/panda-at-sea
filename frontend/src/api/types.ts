/** 与后端 Pydantic schema 对齐的类型（openapi-typescript 生成前的手写版） */

export interface User {
  id: number
  phone: string | null
  nickname: string | null
}

export interface Post {
  id: number
  owner_id: number
  owner_name: string | null
  title: string
  summary: string | null
  content: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface Comment {
  id: number
  post_id: number
  owner_id: number
  owner_name: string | null
  content: string
  created_at: string
}
