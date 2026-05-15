/**
 * 运费计算 API
 * 对接后端 /api/shipping/* 接口
 */
import request from '@/utils/http'
import type { ShippingCalcParams, ShippingCalcResponse } from './types'

/** 计算运费 */
export function fetchCalculateShipping(params: ShippingCalcParams) {
  return request.post<ShippingCalcResponse>({
    url: '/api/shipping/calculate',
    params
  })
}
