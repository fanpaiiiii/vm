/**
 * 外贸工具 API 类型定义
 * 与后端 FastAPI Schema 保持一致
 */

// ==================== 产品相关 ====================

export interface SizeVariant {
  size: string
  specs: string[]
}

export interface Product {
  id: number
  sku: string
  name: string
  link_1688: string
  image_url: string
  spec: string
  box_spec: string
  size_variants: SizeVariant[]
  unit_price: number
  sample_price: number
  shipping_cost: number
  description: string
  status: 'active' | 'inactive' | 'draft'
  supplier_id?: number
  created_by?: number
  created_at?: string
  updated_at?: string
}

export interface ProductCreateParams {
  sku?: string
  name: string
  link_1688?: string
  image_url?: string
  spec?: string
  box_spec?: string
  size_variants?: SizeVariant[]
  unit_price?: number
  sample_price?: number
  shipping_cost?: number
  description?: string
  status?: string
  supplier_id?: number
}

export interface ProductUpdateParams extends Partial<ProductCreateParams> {}

export interface ProductSearchParams {
  keyword?: string
  status?: string
  supplier_id?: number
  page?: number
  page_size?: number
}

export interface ProductListResponse {
  items: Product[]
  total: number
  page: number
  page_size: number
}

// ==================== 供货商相关 ====================

export interface Supplier {
  id: number
  name: string
  contact_person: string
  phone: string
  email: string
  wechat: string
  address: string
  city: string
  province: string
  country: string
  website: string
  alibaba_store: string
  rating: number
  notes: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface SupplierCreateParams {
  name: string
  contact_person?: string
  phone?: string
  email?: string
  wechat?: string
  address?: string
  city?: string
  province?: string
  country?: string
  website?: string
  alibaba_store?: string
  rating?: number
  notes?: string
}

export interface SupplierUpdateParams extends Partial<SupplierCreateParams> {}

export interface SupplierSearchParams {
  keyword?: string
  is_active?: boolean
  page?: number
  page_size?: number
}

export interface SupplierListResponse {
  items: Supplier[]
  total: number
  page: number
  page_size: number
}

// ==================== 运费计算相关 ====================

export interface ShippingCalcParams {
  weight_kg: number
  length_cm?: number
  width_cm?: number
  height_cm?: number
  origin?: string
  destination: string
  quantity?: number
}

export interface ShippingOption {
  carrier: string
  service: string
  estimated_days: string
  cost_usd: number
  cost_cny: number
  notes: string
}

export interface ShippingCalcResponse {
  options: ShippingOption[]
  weight_kg: number
  volume_weight_kg: number
  chargeable_weight_kg: number
}

// ==================== 汇率相关 ====================

export interface ExchangeRate {
  base: string
  target?: string
  rate?: number
  rates?: Record<string, number>
  date: string
  source?: string
}

// ==================== 统计相关 ====================

export interface DashboardStats {
  overview: {
    total_products: number
    active_products: number
    total_suppliers: number
    total_stock: number
    total_value_cny: number
    total_value_usd: number
  }
  stock_alerts: {
    low_stock: number
    out_of_stock: number
  }
  category_distribution: Array<{ category: string; count: number }>
  status_distribution: Array<{ status: string; count: number }>
}

// ==================== 物流渠道相关 ====================

export interface ShippingChannel {
  id: string
  name: string
  code: string
  type: string
  tracking: boolean
  baseRate: number
  firstWeightPrice: number
  additionalWeightPrice: number
  avgDays: string
  maxWeight: number
  enabled: boolean
  description: string
}

// ==================== 认证相关 ====================

export interface RegisterParams {
  username: string
  password: string
  email: string
  full_name?: string
}

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  avatar: string
  created_at?: string
}
