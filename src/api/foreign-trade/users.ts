/**
 * 用户管理 API
 * 对接后端 /api/auth/* 接口
 */
import request from '@/utils/http'
import type { UserInfo } from './types'

/** 用户创建参数 */
export interface UserCreateParams {
  username: string
  password: string
  email: string
  full_name?: string
  role?: string
  is_active?: boolean
}

/** 用户更新参数 */
export interface UserUpdateParams {
  email?: string
  full_name?: string
  role?: string
  is_active?: boolean
  password?: string
}

/** 获取用户列表 */
export function fetchUsers() {
  return request.get<UserInfo[]>({
    url: '/api/auth/users'
  })
}

/** 获取用户详情 */
export function fetchUserDetail(id: number) {
  return request.get<UserInfo>({
    url: `/api/auth/users/${id}`
  })
}

/** 创建用户 */
export function createUser(params: UserCreateParams) {
  return request.post<UserInfo>({
    url: '/api/auth/register',
    params,
    showSuccessMessage: true
  })
}

/** 更新用户 */
export function updateUser(id: number, params: UserUpdateParams) {
  return request.put<UserInfo>({
    url: `/api/auth/users/${id}`,
    params,
    showSuccessMessage: true
  })
}

/** 禁用/启用用户 */
export function toggleUserStatus(id: number, is_active: boolean) {
  return request.put<UserInfo>({
    url: `/api/auth/users/${id}`,
    params: { is_active },
    showSuccessMessage: true
  })
}

/** 删除用户 */
export function deleteUser(id: number) {
  return request.del<{ message: string }>({
    url: `/api/auth/users/${id}`,
    showSuccessMessage: true
  })
}
