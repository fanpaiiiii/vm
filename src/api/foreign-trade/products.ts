/**
 * 产品管理 API
 * 对接后端 /api/products/* 接口
 */
import request from '@/utils/http'
import type {
  Product,
  ProductCreateParams,
  ProductUpdateParams,
  ProductSearchParams,
  ProductListResponse
} from './types'

/** 获取产品列表 */
export function fetchProducts(params?: ProductSearchParams) {
  return request.get<ProductListResponse>({
    url: '/api/products',
    params
  })
}

/** 获取产品详情 */
export function fetchProductDetail(id: number) {
  return request.get<Product>({
    url: `/api/products/${id}`
  })
}

/** 创建产品 */
export function fetchCreateProduct(params: ProductCreateParams) {
  return request.post<Product>({
    url: '/api/products',
    params,
    showSuccessMessage: true
  })
}

/** 更新产品 */
export function fetchUpdateProduct(id: number, params: ProductUpdateParams) {
  return request.put<Product>({
    url: `/api/products/${id}`,
    params,
    showSuccessMessage: true
  })
}

/** 删除产品 */
export function fetchDeleteProduct(id: number) {
  return request.del<{ message: string }>({
    url: `/api/products/${id}`,
    showSuccessMessage: true
  })
}

/** 导入产品 (CSV) */
export function fetchImportProducts(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.request<{ message: string; imported_count: number }>({
    url: '/api/products/import',
    method: 'POST',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    showSuccessMessage: true
  })
}

/** 导出产品 (CSV) - 返回下载URL */
export function getExportProductsUrl() {
  return '/api/products/export/csv'
}
