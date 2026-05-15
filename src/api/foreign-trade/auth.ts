/**
 * 认证相关 API
 * 对接后端 /api/auth/* 接口
 */
import request from '@/utils/http'
import type { RegisterParams, LoginParams, LoginResponse, UserInfo } from './types'

/** 用户注册 */
export function fetchRegister(params: RegisterParams) {
  return request.post<{ message: string }>({
    url: '/api/auth/register',
    params,
    showSuccessMessage: true
  })
}

/** 用户登录 */
export function fetchTradeLogin(params: LoginParams) {
  return request.post<LoginResponse>({
    url: '/api/auth/login',
    params
  })
}

/** 获取当前用户信息 */
export function fetchTradeUserInfo() {
  return request.get<UserInfo>({
    url: '/api/auth/me'
  })
}
