<template>
  <div class="settings-exchange-rate">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>汇率设置</span>
          <div class="header-actions">
            <el-button type="primary" @click="refreshRates" :loading="loading">
              <el-icon><i class="ep-refresh" /></el-icon>
              刷新实时汇率
            </el-button>
            <el-button type="warning" @click="resetToRealtime">
              <el-icon><i class="ep-refresh-right" /></el-icon>
              重置为实时汇率
            </el-button>
          </div>
        </div>
      </template>

      <el-alert title="汇率数据来源说明" type="info" :closable="false" class="mb-4">
        <template #default>
          <div>
            <p>• 汇率数据来自 <strong>Frankfurter API</strong>（基于欧洲央行 ECB 数据）</p>
            <p>• 仪表盘优先使用 <strong>手动设置的汇率</strong>，如果没有则使用 API 实时汇率</p>
            <p>• 点击"重置为实时汇率"可清除所有手动设置，恢复使用 API 汇率</p>
          </div>
        </template>
      </el-alert>

      <!-- 实时汇率显示 -->
      <el-divider content-position="left">实时汇率（来自 Frankfurter/ECB）</el-divider>
      <el-descriptions :column="2" border class="mb-4">
        <el-descriptions-item label="美元/人民币 (USD/CNY)">
          <span class="rate-value">{{ apiRates.USD_CNY?.toFixed(4) || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="欧元/人民币 (EUR/CNY)">
          <span class="rate-value">{{ apiRates.EUR_CNY?.toFixed(4) || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="英镑/人民币 (GBP/CNY)">
          <span class="rate-value">{{ apiRates.GBP_CNY?.toFixed(4) || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="日元/人民币 (JPY/CNY)">
          <span class="rate-value">{{ apiRates.JPY_CNY?.toFixed(4) || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="最后更新时间">
          {{ lastRateUpdate || '未更新' }}
        </el-descriptions-item>
        <el-descriptions-item label="数据来源">
          <el-tag type="success">Frankfurter (ECB)</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 手动设置汇率 -->
      <el-divider content-position="left">手动设置汇率</el-divider>
      <div class="manual-rates-section">
        <el-form label-width="180px" class="manual-rates-form">
          <el-form-item v-for="item in rateKeys" :key="item.key" :label="item.label">
            <div class="rate-input-row">
              <el-input-number
                v-model="manualRates[item.key]"
                :precision="4"
                :step="0.01"
                :min="0"
                style="width: 240px"
                placeholder="输入汇率"
              />
              <el-tag v-if="manualRates[item.key]" type="warning" size="small" style="margin-left: 8px">
                手动设置
              </el-tag>
              <el-tag v-else type="info" size="small" style="margin-left: 8px">
                使用实时汇率: {{ (apiRates as any)[item.key]?.toFixed(4) || '-' }}
              </el-tag>
              <el-button
                v-if="manualRates[item.key]"
                type="danger"
                link
                size="small"
                @click="clearSingleRate(item.key)"
                style="margin-left: 8px"
              >
                清除
              </el-button>
            </div>
          </el-form-item>
        </el-form>
        <div class="manual-rates-actions">
          <el-button type="primary" @click="saveManualRates">
            <el-icon><i class="ep-check" /></el-icon>
            保存手动汇率
          </el-button>
          <el-button @click="clearAllManualRates">
            <el-icon><i class="ep-close" /></el-icon>
            清除所有手动设置
          </el-button>
        </div>
      </div>

      <!-- 自定义汇率查询 -->
      <el-divider content-position="left">自定义汇率查询</el-divider>
      <el-form :inline="true" class="mt-2">
        <el-form-item label="基础货币">
          <el-input v-model="queryBase" placeholder="如: USD" style="width: 120px" />
        </el-form-item>
        <el-form-item label="目标货币">
          <el-input v-model="queryTarget" placeholder="如: CNY" style="width: 120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="queryRate" :loading="queryLoading">查询</el-button>
        </el-form-item>
      </el-form>
      <div v-if="queryResult" class="query-result">
        <el-tag type="success" size="large">1 {{ queryBase.toUpperCase() }} = {{ queryResult.toFixed(4) }} {{ queryTarget.toUpperCase() }}</el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import { storeToRefs } from 'pinia'
import { fetchExchangeRate } from '@/api/foreign-trade/statistics'
import { STORAGE_KEYS } from '@/constants/storage-keys'

const LS_KEY = STORAGE_KEYS.MANUAL_RATES

const foreignTradeStore = useForeignTradeStore()
const { effectiveRates: apiRates, lastRateUpdate } = storeToRefs(foreignTradeStore)
const loading = ref(false)
const queryBase = ref('USD')
const queryTarget = ref('CNY')
const queryResult = ref<number | null>(null)
const queryLoading = ref(false)

// 汇率键配置
const rateKeys = [
  { key: 'USD_CNY', label: '美元/人民币 (USD/CNY)' },
  { key: 'EUR_CNY', label: '欧元/人民币 (EUR/CNY)' },
  { key: 'GBP_CNY', label: '英镑/人民币 (GBP/CNY)' },
  { key: 'JPY_CNY', label: '日元/人民币 (JPY/CNY)' },
]

// 手动汇率
const manualRates = reactive<Record<string, number | undefined>>({
  USD_CNY: undefined,
  EUR_CNY: undefined,
  GBP_CNY: undefined,
  JPY_CNY: undefined,
})

// 加载手动汇率
function loadManualRates() {
  try {
    const saved = localStorage.getItem(LS_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      Object.keys(manualRates).forEach(key => {
        if (parsed[key] !== undefined) {
          manualRates[key] = parsed[key]
        }
      })
    }
  } catch (e) {
    console.error('加载手动汇率失败:', e)
  }
}

// 保存手动汇率
function saveManualRates() {
  const rates: Record<string, number> = {}
  Object.entries(manualRates).forEach(([key, value]) => {
    if (value !== undefined && value > 0) {
      rates[key] = value
    }
  })
  localStorage.setItem(LS_KEY, JSON.stringify(rates))
  // 同步到 store（仪表盘使用）
  foreignTradeStore.setManualRates(rates)
  ElMessage.success('手动汇率已保存')
}

// 清除单个手动汇率
function clearSingleRate(key: string) {
  manualRates[key] = undefined
  saveManualRates()
}

// 清除所有手动汇率
function clearAllManualRates() {
  Object.keys(manualRates).forEach(key => {
    manualRates[key] = undefined
  })
  localStorage.removeItem(LS_KEY)
  foreignTradeStore.clearManualRates()
  ElMessage.success('已清除所有手动设置')
}

// 重置为实时汇率
const resetToRealtime = async () => {
  try {
    await ElMessageBox.confirm('确定要清除所有手动设置的汇率，恢复使用实时汇率吗？', '确认', { type: 'warning' })
    clearAllManualRates()
    await refreshRates()
  } catch {
    // 取消
  }
}

const refreshRates = async () => {
  loading.value = true
  try {
    await foreignTradeStore.loadExchangeRates()
    ElMessage.success('实时汇率已刷新')
  } finally {
    loading.value = false
  }
}

const queryRate = async () => {
  if (!queryBase.value || !queryTarget.value) return
  queryLoading.value = true
  try {
    const res = await fetchExchangeRate(queryBase.value.toUpperCase(), queryTarget.value.toUpperCase())
    if (res && res.rate) {
      queryResult.value = res.rate
    } else if (res && res.rates) {
      queryResult.value = res.rates[queryTarget.value.toUpperCase()] || null
    }
  } catch (e) {
    ElMessage.error('查询汇率失败')
  } finally {
    queryLoading.value = false
  }
}

onMounted(() => {
  loadManualRates()
  refreshRates()
})
</script>

<style scoped lang="scss">
.settings-exchange-rate { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 8px; }
.mb-4 { margin-bottom: 16px; }
.mt-2 { margin-top: 8px; }
.query-result { margin-top: 12px; }
.rate-value { font-weight: bold; font-size: 16px; color: #409eff; }

.manual-rates-section {
  margin-bottom: 20px;
}

.manual-rates-form {
  max-width: 700px;
}

.rate-input-row {
  display: flex;
  align-items: center;
}

.manual-rates-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  padding-left: 180px;
}
</style>
