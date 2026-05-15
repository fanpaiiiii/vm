/**
 * 供货商管理 API
 * 对接后端 /api/suppliers/* 接口
 */
import request from '@/utils/http'
import type {
  Supplier,
  SupplierCreateParams,
  SupplierUpdateParams,
  SupplierSearchParams,
  SupplierListResponse
} from './types'

/** 获取供货商列表 */
export function fetchSuppliers(params?: SupplierSearchParams) {
  return request.get<SupplierListResponse>({
    url: '/api/suppliers',
    params
  })
}

/** 获取供货商详情 */
export function fetchSupplierDetail(id: number) {
  return request.get<Supplier>({
    url: `/api/suppliers/${id}`
  })
}

/** 创建供货商 */
export function fetchCreateSupplier(params: SupplierCreateParams) {
  return request.post<Supplier>({
    url: '/api/suppliers',
    params,
    showSuccessMessage: true
  })
}

/** 更新供货商 */
export function fetchUpdateSupplier(id: number, params: SupplierUpdateParams) {
  return request.put<Supplier>({
    url: `/api/suppliers/${id}`,
    params,
    showSuccessMessage: true
  })
}

/** 删除供货商 */
export function fetchDeleteSupplier(id: number) {
  return request.del<{ message: string }>({
    url: `/api/suppliers/${id}`,
    showSuccessMessage: true
  })
}
