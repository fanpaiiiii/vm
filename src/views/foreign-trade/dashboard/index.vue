<template>
  <div class="foreign-trade-dashboard">
    <!-- 汇率显示卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6">
        <el-card class="exchange-rate-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🇺🇸 美元/人民币</span>
              <el-tag type="success" size="small">实时</el-tag>
            </div>
          </template>
          <div class="rate-value">
            <span class="rate-number">{{ exchangeRates.USD_CNY.toFixed(4) }}</span>
          </div>
          <div class="rate-source">
            <el-icon size="12"><i class="ep-data-line" /></el-icon>
            数据来源: Frankfurter (ECB)
          </div>
          <div class="rate-time">更新时间: {{ lastRateUpdate || '加载中...' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="exchange-rate-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🇪🇺 欧元/人民币</span>
              <el-tag type="success" size="small">实时</el-tag>
            </div>
          </template>
          <div class="rate-value">
            <span class="rate-number">{{ exchangeRates.EUR_CNY.toFixed(4) }}</span>
          </div>
          <div class="rate-source">
            <el-icon size="12"><i class="ep-data-line" /></el-icon>
            数据来源: Frankfurter (ECB)
          </div>
          <div class="rate-time">更新时间: {{ lastRateUpdate || '加载中...' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="exchange-rate-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🇬🇧 英镑/人民币</span>
              <el-tag type="success" size="small">实时</el-tag>
            </div>
          </template>
          <div class="rate-value">
            <span class="rate-number">{{ exchangeRates.GBP_CNY.toFixed(4) }}</span>
          </div>
          <div class="rate-source">
            <el-icon size="12"><i class="ep-data-line" /></el-icon>
            数据来源: Frankfurter (ECB)
          </div>
          <div class="rate-time">更新时间: {{ lastRateUpdate || '加载中...' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="exchange-rate-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🇯🇵 日元/人民币</span>
              <el-tag type="success" size="small">实时</el-tag>
            </div>
          </template>
          <div class="rate-value">
            <span class="rate-number">{{ exchangeRates.JPY_CNY.toFixed(4) }}</span>
          </div>
          <div class="rate-source">
            <el-icon size="12"><i class="ep-data-line" /></el-icon>
            数据来源: Frankfurter (ECB)
          </div>
          <div class="rate-time">更新时间: {{ lastRateUpdate || '加载中...' }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 汇率计算器 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>💱 汇率计算器</span>
              <span v-if="ratesDate" class="rate-date-tag">数据日期: {{ ratesDate }}</span>
            </div>
          </template>
          <div class="calc-row">
            <el-input-number
              v-model="calcAmount"
              :min="0"
              :precision="2"
              :step="100"
              size="large"
              style="width: 200px"
            />
            <el-select
              v-model="calcFrom"
              size="large"
              filterable
              style="width: 200px"
              placeholder="选择币种"
            >
              <el-option
                v-for="code in sortedCurrencies"
                :key="code"
                :label="`${code} ${currencyNames[code] || code}`"
                :value="code"
              />
            </el-select>
            <el-icon class="calc-swap" @click="swapCurrencies"><i class="ep-sort" /></el-icon>
            <el-select
              v-model="calcTo"
              size="large"
              filterable
              style="width: 200px"
              placeholder="选择币种"
            >
              <el-option
                v-for="code in sortedCurrencies"
                :key="code"
                :label="`${code} ${currencyNames[code] || code}`"
                :value="code"
              />
            </el-select>
            <div class="calc-result">
              <span class="calc-result-value">{{ calcResult }}</span>
              <span class="calc-result-unit">{{ calcToLabel }}</span>
            </div>
          </div>
          <div class="calc-rate-info">
            汇率: 1 {{ calcFrom }} = {{ calcRate }} {{ calcTo }}
            <span v-if="ratesDate" style="margin-left: 16px">来源: ECB via Frankfurter</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #409eff, #337ecc)">
            <el-icon size="24"><i class="ep-shopping-bag" /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.overview.total_products }}</div>
            <div class="stat-label">产品总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #67c23a, #529b2e)">
            <el-icon size="24"><i class="ep-circle-check" /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.overview.active_products }}</div>
            <div class="stat-label">在售产品</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6a23c, #b88230)">
            <el-icon size="24"><i class="ep-office-building" /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.overview.total_suppliers }}</div>
            <div class="stat-label">供货商数量</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🚀 快捷入口</span>
            </div>
          </template>
          <div class="quick-links">
            <el-button type="primary" @click="$router.push('/foreign-trade/products/add')">
              <el-icon><i class="ep-plus" /></el-icon>
              添加产品
            </el-button>
            <el-button type="success" @click="$router.push('/foreign-trade/suppliers/add')">
              <el-icon><i class="ep-plus" /></el-icon>
              添加供货商
            </el-button>
            <el-button type="warning" @click="$router.push('/foreign-trade/shipping')">
              <el-icon><i class="ep-calculator" /></el-icon>
              运费计算
            </el-button>
            <el-button type="info" @click="$router.push('/foreign-trade/spreadsheet')">
              <el-icon><i class="ep-document" /></el-icon>
              在线表格
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待办事项 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📋 待办事项</span>
            </div>
          </template>
          <div class="todo-list">
            <div v-for="todo in todos" :key="todo.id" class="todo-item" :class="{ done: todo.done }">
              <el-checkbox v-model="todo.done" @change="saveTodos" />
              <span class="todo-text">{{ todo.text }}</span>
            </div>
            <el-empty v-if="todos.length === 0" description="暂无待办事项" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import { storeToRefs } from 'pinia'

const foreignTradeStore = useForeignTradeStore()
const { dashboardStats: stats, effectiveRates: exchangeRates, allRates, currencyNames, popularCurrencies, ratesDate, lastRateUpdate } = storeToRefs(foreignTradeStore)

let refreshTimer: ReturnType<typeof setInterval> | null = null

const formatMoney = (value: number) => {
  if (!value) return '0'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

// ========== 汇率计算器 ==========
const calcAmount = ref(1000)
const calcFrom = ref('USD')
const calcTo = ref('CNY')

// 排序：常用币种在前
const sortedCurrencies = computed(() => {
  const rates = allRates.value
  const available = Object.keys(rates).filter(k => rates[k] > 0)
  const popular = popularCurrencies.value.filter((c: any) => available.includes(c))
  const rest = available.filter(c => !popular.includes(c)).sort()
  return [...popular, ...rest]
})

const calcToLabel = computed(() => {
  const names = currencyNames.value
  return names[calcTo.value] || calcTo.value
})

// 任意两种货币间的汇率（通过 USD 中转）
const calcRate = computed(() => {
  const rates = allRates.value
  const fromRate = rates[calcFrom.value]
  const toRate = rates[calcTo.value]
  if (!fromRate || !toRate) return '0'
  return (toRate / fromRate).toFixed(4)
})

const calcResult = computed(() => {
  const rates = allRates.value
  const fromRate = rates[calcFrom.value]
  const toRate = rates[calcTo.value]
  if (!fromRate || !toRate) return '0'
  const result = (calcAmount.value / fromRate) * toRate
  return result.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

function swapCurrencies() {
  const tmp = calcFrom.value
  calcFrom.value = calcTo.value
  calcTo.value = tmp
}

// ========== 待办事项 ==========
interface TodoItem {
  id: number
  text: string
  done: boolean
}

const defaultTodos: TodoItem[] = []

const STORAGE_KEY = 'foreign-trade-todos'
const todos = ref<TodoItem[]>([])

function loadTodos() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      todos.value = JSON.parse(saved)
    } else {
      todos.value = []
    }
  } catch {
    todos.value = []
  }
}

function saveTodos() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(todos.value))
}

onMounted(async () => {
  loadTodos()

  // 加载手动汇率设置
  foreignTradeStore.loadManualRates()

  // 并行加载统计数据和汇率
  await Promise.all([
    foreignTradeStore.loadDashboardStats(),
    foreignTradeStore.loadExchangeRates()
  ])

  // 每5分钟自动刷新汇率
  refreshTimer = setInterval(() => {
    foreignTradeStore.loadExchangeRates()
  }, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped lang="scss">
.foreign-trade-dashboard {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.exchange-rate-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .rate-date-tag {
    font-size: 12px;
    color: #909399;
  }

  .rate-value {
    display: flex;
    align-items: baseline;
    gap: 10px;

    .rate-number {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
    }
  }

  .rate-source {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .rate-time {
    margin-top: 4px;
    font-size: 12px;
    color: #c0c4cc;
  }
}

.stat-card {
  :deep(.el-card__body) {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
  }

  .stat-icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    flex-shrink: 0;
  }

  .stat-content {
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      line-height: 1.2;
    }

    .stat-label {
      font-size: 13px;
      color: #909399;
      margin-top: 4px;
    }
  }
}

.quick-links {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.calc-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.calc-swap {
  font-size: 20px;
  color: #409eff;
  cursor: pointer;
  transition: transform 0.3s;
  &:hover {
    transform: rotate(180deg);
  }
}

.calc-result {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-left: 16px;
  padding-left: 16px;
  border-left: 2px solid #e4e7ed;

  .calc-result-value {
    font-size: 28px;
    font-weight: bold;
    color: #409eff;
  }

  .calc-result-unit {
    font-size: 14px;
    color: #909399;
  }
}

.calc-rate-info {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}

.todo-list {
  .todo-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 8px;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    &.done .todo-text {
      text-decoration: line-through;
      color: #c0c4cc;
    }

    .todo-text {
      font-size: 14px;
      color: #303133;
      transition: all 0.3s;
    }
  }
}
</style>
