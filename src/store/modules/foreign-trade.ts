/**
 * 外贸工具状态管理模块
 */
import { ElMessage } from 'element-plus'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Product,
  Supplier,
  ExchangeRate,
  DashboardStats,
  ShippingChannel
} from '@/api/foreign-trade/types'
import {
  fetchProducts,
  fetchProductDetail,
  fetchCreateProduct,
  fetchUpdateProduct,
  fetchDeleteProduct
} from '@/api/foreign-trade/products'
import {
  fetchSuppliers,
  fetchSupplierDetail,
  fetchCreateSupplier,
  fetchUpdateSupplier,
  fetchDeleteSupplier
} from '@/api/foreign-trade/suppliers'
import { fetchDashboardStats, fetchAllRates } from '@/api/foreign-trade/statistics'
import { fetchCalculateShipping } from '@/api/foreign-trade/shipping'
import type {
  ProductCreateParams,
  ProductUpdateParams,
  ProductSearchParams,
  SupplierCreateParams,
  SupplierUpdateParams,
  SupplierSearchParams,
  ShippingCalcParams
} from '@/api/foreign-trade/types'
import { STORAGE_KEYS } from '@/constants/storage-keys'

export const useForeignTradeStore = defineStore(
  'foreignTradeStore',
  () => {
    // ========== 产品状态 ==========
    const products = ref<Product[]>([])
    const productsTotal = ref(0)
    const currentProduct = ref<Product | null>(null)
    const productsLoading = ref(false)

    // ========== 供货商状态 ==========
    const suppliers = ref<Supplier[]>([])
    const suppliersTotal = ref(0)
    const currentSupplier = ref<Supplier | null>(null)
    const suppliersLoading = ref(false)

    // ========== 仪表盘状态 ==========
    const dashboardStats = ref<DashboardStats>({
      overview: {
        total_products: 0,
        active_products: 0,
        total_suppliers: 0,
        total_stock: 0,
        total_value_cny: 0,
        total_value_usd: 0
      },
      stock_alerts: {
        low_stock: 0,
        out_of_stock: 0
      },
      category_distribution: [],
      status_distribution: []
    })

    // 全量汇率（USD 为基准）
    const allRates = ref<Record<string, number>>({ USD: 1 })
    const currencyNames = ref<Record<string, string>>({})
    const popularCurrencies = ref<string[]>([])
    const ratesDate = ref('')
    const manualRates = ref<Record<string, number>>({})
    const ratesLoading = ref(false)
    const lastRateUpdate = ref('')

    // 兼容旧的 4 币种显示卡片
    const effectiveRates = computed(() => {
      const r = allRates.value
      const usdCny = r['CNY'] || 0
      return {
        USD_CNY: usdCny,
        EUR_CNY: r['EUR'] ? (usdCny / r['EUR']) : 0,
        GBP_CNY: r['GBP'] ? (usdCny / r['GBP']) : 0,
        JPY_CNY: r['JPY'] ? (usdCny / r['JPY']) : 0
      }
    })

    // ========== 运费计算状态 ==========
    const shippingResult = ref<any>(null)
    const shippingChannels = ref<ShippingChannel[]>([])
    const shippingLoading = ref(false)

    // 加载手动汇率
    function loadManualRates() {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.MANUAL_RATES)
        if (saved) {
          manualRates.value = JSON.parse(saved)
        }
      } catch (e) {
        // ignore
      }
    }

    // 设置手动汇率
    function setManualRates(rates: Record<string, number>) {
      manualRates.value = rates
      localStorage.setItem(STORAGE_KEYS.MANUAL_RATES, JSON.stringify(rates))
    }

    // 清除手动汇率
    function clearManualRates() {
      manualRates.value = {}
      localStorage.removeItem(STORAGE_KEYS.MANUAL_RATES)
    }

    // 加载物流渠道配置
    function loadShippingChannelsConfig(): ShippingChannel[] {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.SHIPPING_CHANNELS)
        if (saved) {
          return JSON.parse(saved)
        }
      } catch (e) {
        // ignore
      }
      return []
    }

    // ========== 产品操作 ==========
    async function loadProducts(params?: ProductSearchParams) {
      productsLoading.value = true
      try {
        const res = await fetchProducts(params)
        if (res) {
          products.value = res.items || []
          productsTotal.value = res.total || 0
        }
      } catch (e: any) {
        ElMessage.error(e?.message || '加载产品列表失败')
      } finally {
        productsLoading.value = false
      }
    }

    async function loadProductDetail(id: number) {
      try {
        const res = await fetchProductDetail(id)
        if (res) currentProduct.value = res
        return res
      } catch (e: any) {
        ElMessage.error(e?.message || '加载产品详情失败')
        return null
      }
    }

    async function createProduct(params: ProductCreateParams) {
      try {
        const res = await fetchCreateProduct(params)
        return res
      } catch (e: any) {
        ElMessage.error(e?.message || '创建产品失败')
        return null
      }
    }

    async function updateProduct(id: number, params: ProductUpdateParams) {
      try {
        const res = await fetchUpdateProduct(id, params)
        return res
      } catch (e: any) {
        ElMessage.error(e?.message || '更新产品失败')
        return null
      }
    }

    async function deleteProduct(id: number) {
      try {
        await fetchDeleteProduct(id)
        products.value = products.value.filter(p => p.id !== id)
        return true
      } catch (e: any) {
        ElMessage.error(e?.message || '删除产品失败')
        return false
      }
    }

    // ========== 供货商操作 ==========
    async function loadSuppliers(params?: SupplierSearchParams) {
      suppliersLoading.value = true
      try {
        const res = await fetchSuppliers(params)
        if (res) {
          suppliers.value = res.items || []
          suppliersTotal.value = res.total || 0
        }
      } catch (e: any) {
        ElMessage.error(e?.message || '加载供货商列表失败')
      } finally {
        suppliersLoading.value = false
      }
    }

    async function loadSupplierDetail(id: number) {
      try {
        const res = await fetchSupplierDetail(id)
        if (res) currentSupplier.value = res
        return res
      } catch (e: any) {
        ElMessage.error(e?.message || '加载供货商详情失败')
        return null
      }
    }

    async function createSupplier(params: SupplierCreateParams) {
      try {
        const res = await fetchCreateSupplier(params)
        return res
      } catch (e: any) {
        ElMessage.error(e?.message || '创建供货商失败')
        return null
      }
    }

    async function updateSupplier(id: number, params: SupplierUpdateParams) {
      try {
        const res = await fetchUpdateSupplier(id, params)
        return res
      } catch (e: any) {
        ElMessage.error(e?.message || '更新供货商失败')
        return null
      }
    }

    async function deleteSupplier(id: number) {
      try {
        await fetchDeleteSupplier(id)
        suppliers.value = suppliers.value.filter(s => s.id !== id)
        return true
      } catch (e: any) {
        ElMessage.error(e?.message || '删除供货商失败')
        return false
      }
    }

    // ========== 仪表盘操作 ==========
    async function loadDashboardStats() {
      try {
        const res = await fetchDashboardStats()
        if (res) dashboardStats.value = res
      } catch (e: any) {
        ElMessage.error(e?.message || '加载统计数据失败')
      }
    }

    async function loadExchangeRates() {
      ratesLoading.value = true
      try {
        const res = await fetchAllRates('USD')
        if (res && res.rates) {
          allRates.value = { USD: 1, ...res.rates }
          currencyNames.value = res.currencies || {}
          popularCurrencies.value = res.popular || []
          ratesDate.value = res.date || ''
          lastRateUpdate.value = new Date().toLocaleString('zh-CN')
        }
      } catch (e: any) {
        ElMessage.error(e?.message || '加载汇率失败')
      } finally {
        ratesLoading.value = false
      }
    }

    // ========== 运费计算操作 ==========
    async function calculateShipping(params: ShippingCalcParams) {
      shippingLoading.value = true
      try {
        const res: any = await fetchCalculateShipping(params)
        if (res) {
          shippingResult.value = res.options ? res : { options: res }
          shippingChannels.value = res.options || res || []
        }
        return res
      } catch (e: any) {
        ElMessage.error(e?.message || '运费计算失败')
        return null
      } finally {
        shippingLoading.value = false
      }
    }

    return {
      // 产品
      products,
      productsTotal,
      currentProduct,
      productsLoading,
      loadProducts,
      loadProductDetail,
      createProduct,
      updateProduct,
      deleteProduct,
      // 供货商
      suppliers,
      suppliersTotal,
      currentSupplier,
      suppliersLoading,
      loadSuppliers,
      loadSupplierDetail,
      createSupplier,
      updateSupplier,
      deleteSupplier,
      // 仪表盘
      dashboardStats,
      allRates,
      currencyNames,
      popularCurrencies,
      ratesDate,
      exchangeRates: allRates, // 兼容
      manualRates,
      effectiveRates,
      ratesLoading,
      lastRateUpdate,
      loadDashboardStats,
      loadExchangeRates,
      loadManualRates,
      setManualRates,
      clearManualRates,
      // 运费
      shippingResult,
      shippingChannels,
      shippingLoading,
      calculateShipping,
      loadShippingChannelsConfig
    }
  },
  {
    persist: false
  }
)
