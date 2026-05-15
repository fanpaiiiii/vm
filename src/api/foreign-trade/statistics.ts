/**
 * 统计和汇率 API
 * 对接后端 /api/statistics/* 和 /api/exchange-rate/* 接口
 */
import request from '@/utils/http'
import type { DashboardStats, ExchangeRate } from './types'

/** 获取仪表盘统计数据 */
export function fetchDashboardStats() {
  return request.get<DashboardStats>({
    url: '/api/statistics/dashboard'
  })
}

/** 获取汇率 */
export function fetchExchangeRate(base?: string, target?: string) {
  return request.get<ExchangeRate>({
    url: '/api/exchange-rate',
    params: { base, target }
  })
}

/** 获取多组汇率 */
export function fetchMultiExchangeRate(base: string, targets: string[]) {
  return request.get<ExchangeRate>({
    url: '/api/exchange-rate/multi',
    params: { base, targets: targets.join(',') }
  })
}

/** 获取全币种汇率 */
export function fetchAllRates(base: string = 'USD') {
  return request.get<{
    base: string
    date: string
    rates: Record<string, number>
    currencies: Record<string, string>
    popular: string[]
    source: string
  }>({
    url: '/api/exchange-rate/all',
    params: { base }
  })
}
