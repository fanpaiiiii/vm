/**
 * 外贸工具状态管理模块
 */
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
import { fetchDashboardStats, fetchExchangeRate, fetchMultiExchangeRate } from '@/api/foreign-trade/statistics'
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

const MANUAL_RATES_KEY = 'foreign_trade_manual_rates'
const SHIPPING_CHANNELS_KEY = 'foreign_trade_shipping_channels'

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
    const exchangeRates = ref<Record<string, number>>({
      USD_CNY: 0,
      EUR_CNY: 0,
      GBP_CNY: 0,
      JPY_CNY: 0
    })
    const manualRates = ref<Record<string, number>>({})
    const ratesLoading = ref(false)
    const lastRateUpdate = ref('')

    // 仪表盘使用的汇率（优先手动设置）
    const effectiveRates = computed(() => {
      const rates: Record<string, number> = {}
      const apiKeys = ['USD_CNY', 'EUR_CNY', 'GBP_CNY', 'JPY_CNY']
      for (const key of apiKeys) {
        if (manualRates.value[key] && manualRates.value[key] > 0) {
          rates[key] = manualRates.value[key]
        } else {
          rates[key] = exchangeRates.value[key]
        }
      }
      return rates
    })

    // ========== 运费计算状态 ==========
    const shippingResult = ref<{ cost: number; days: number; billable_weight: number } | null>(null)
    const shippingChannels = ref<ShippingChannel[]>([])
    const shippingLoading = ref(false)

    // 加载手动汇率
    function loadManualRates() {
      try {
        const saved = localStorage.getItem(MANUAL_RATES_KEY)
        if (saved) {
          manualRates.value = JSON.parse(saved)
        }
      } catch (e) {
        console.error('加载手动汇率失败:', e)
      }
    }

    // 设置手动汇率
    function setManualRates(rates: Record<string, number>) {
      manualRates.value = rates
      localStorage.setItem(MANUAL_RATES_KEY, JSON.stringify(rates))
    }

    // 清除手动汇率
    function clearManualRates() {
      manualRates.value = {}
      localStorage.removeItem(MANUAL_RATES_KEY)
    }

    // 加载物流渠道配置
    function loadShippingChannelsConfig(): ShippingChannel[] {
      try {
        const saved = localStorage.getItem(SHIPPING_CHANNELS_KEY)
        if (saved) {
          return JSON.parse(saved)
        }
      } catch (e) {
        console.error('加载物流渠道配置失败:', e)
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
      } catch (e) {
        console.error('加载产品列表失败:', e)
      } finally {
        productsLoading.value = false
      }
    }

    async function loadProductDetail(id: number) {
      try {
        const res = await fetchProductDetail(id)
        if (res) currentProduct.value = res
        return res
      } catch (e) {
        console.error('加载产品详情失败:', e)
        return null
      }
    }

    async function createProduct(params: ProductCreateParams) {
      try {
        const res = await fetchCreateProduct(params)
        return res
      } catch (e) {
        console.error('创建产品失败:', e)
        return null
      }
    }

    async function updateProduct(id: number, params: ProductUpdateParams) {
      try {
        const res = await fetchUpdateProduct(id, params)
        return res
      } catch (e) {
        console.error('更新产品失败:', e)
        return null
      }
    }

    async function deleteProduct(id: number) {
      try {
        await fetchDeleteProduct(id)
        products.value = products.value.filter(p => p.id !== id)
        return true
      } catch (e) {
        console.error('删除产品失败:', e)
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
      } catch (e) {
        console.error('加载供货商列表失败:', e)
      } finally {
        suppliersLoading.value = false
      }
    }

    async function loadSupplierDetail(id: number) {
      try {
        const res = await fetchSupplierDetail(id)
        if (res) currentSupplier.value = res
        return res
      } catch (e) {
        console.error('加载供货商详情失败:', e)
        return null
      }
    }

    async function createSupplier(params: SupplierCreateParams) {
      try {
        const res = await fetchCreateSupplier(params)
        return res
      } catch (e) {
        console.error('创建供货商失败:', e)
        return null
      }
    }

    async function updateSupplier(id: number, params: SupplierUpdateParams) {
      try {
        const res = await fetchUpdateSupplier(id, params)
        return res
      } catch (e) {
        console.error('更新供货商失败:', e)
        return null
      }
    }

    async function deleteSupplier(id: number) {
      try {
        await fetchDeleteSupplier(id)
        suppliers.value = suppliers.value.filter(s => s.id !== id)
        return true
      } catch (e) {
        console.error('删除供货商失败:', e)
        return false
      }
    }

    // ========== 仪表盘操作 ==========
    async function loadDashboardStats() {
      try {
        const res = await fetchDashboardStats()
        if (res) dashboardStats.value = res
      } catch (e) {
        console.error('加载统计数据失败:', e)
      }
    }

    async function loadExchangeRates() {
      ratesLoading.value = true
      try {
        // 使用后端代理的 Frankfurter API，直接获取 USD 计价的各币种汇率
        const res = await fetchExchangeRate('USD', 'CNY')
        if (res && res.rate) {
          // 获取 USD/CNY 汇率
          const usdCny = res.rate
          
          // 获取其他币种对 USD 的汇率
          const multiRes = await fetchMultiExchangeRate('USD', ['EUR', 'GBP', 'JPY'])
          
          if (multiRes && multiRes.rates) {
            const rates = multiRes.rates
            exchangeRates.value = {
              USD_CNY: usdCny,
              EUR_CNY: rates.EUR ? usdCny / rates.EUR : 0,
              GBP_CNY: rates.GBP ? usdCny / rates.GBP : 0,
              JPY_CNY: rates.JPY ? usdCny / rates.JPY : 0
            }
          } else {
            exchangeRates.value = {
              USD_CNY: usdCny,
              EUR_CNY: 0,
              GBP_CNY: 0,
              JPY_CNY: 0
            }
          }
          lastRateUpdate.value = new Date().toLocaleString('zh-CN')
        }
      } catch (e) {
        console.error('加载汇率失败，使用默认值:', e)
      } finally {
        ratesLoading.value = false
      }
    }

    // ========== 运费计算操作 ==========
    async function calculateShipping(params: ShippingCalcParams) {
      shippingLoading.value = true
      try {
        const res = await fetchCalculateShipping(params)
        if (res) {
          shippingResult.value = res.result
          shippingChannels.value = res.channels || []
        }
        return res
      } catch (e) {
        console.error('运费计算失败:', e)
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
      exchangeRates,
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
