<template>
  <div class="incoterms-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Incoterms 2020 贸易术语速查</span>
          <el-tag type="info" size="small">共 11 个术语</el-tag>
        </div>
      </template>

      <!-- 搜索与筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索术语名称（如 EXW、工厂交货）"
          clearable
          prefix-icon="Search"
          style="width: 320px"
        />
        <el-radio-group v-model="transportFilter">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="any">任意运输方式</el-radio-button>
          <el-radio-button value="sea">仅海运/内河</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="showComparison = !showComparison">
          {{ showComparison ? '卡片视图' : '对比视图' }}
        </el-button>
      </div>

      <!-- 卡片视图 -->
      <div v-if="!showComparison" class="term-cards">
        <el-row :gutter="16">
          <el-col
            v-for="term in filteredTerms"
            :key="term.code"
            :xs="24" :sm="12" :md="8" :lg="6"
          >
            <el-card
              shadow="hover"
              class="term-card"
              :class="{ 'term-card--sea': term.transportMode === 'sea' }"
            >
              <template #header>
                <div class="term-card__header">
                  <el-tag :type="term.transportMode === 'any' ? 'primary' : 'warning'" size="small">
                    {{ term.transportMode === 'any' ? '任意运输' : '仅海运' }}
                  </el-tag>
                  <span class="term-card__code">{{ term.code }}</span>
                </div>
              </template>

              <div class="term-card__body">
                <h3 class="term-card__name">{{ term.chineseName }}</h3>
                <p class="term-card__english">{{ term.englishName }}</p>

                <el-divider content-position="left">风险转移点</el-divider>
                <p class="term-card__risk">{{ term.riskTransfer }}</p>

                <el-divider content-position="left">费用责任</el-divider>
                <div class="term-card__costs">
                  <div class="cost-item" v-for="item in costItems" :key="item.key">
                    <span class="cost-item__label">{{ item.label }}</span>
                    <el-tag :type="getCostTagType(term.costs[item.key])" size="small">
                      {{ getCostLabel(term.costs[item.key]) }}
                    </el-tag>
                  </div>
                </div>

                <el-divider content-position="left">义务等级</el-divider>
                <div class="term-card__obligations">
                  <div class="obligation-item">
                    <span>卖方义务：</span>
                    <el-rate
                      :model-value="getObligationLevel(term.sellerObligation)"
                      disabled
                      :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                    />
                    <el-tag :type="obligationTagType(term.sellerObligation)" size="small">
                      {{ obligationLabel(term.sellerObligation) }}
                    </el-tag>
                  </div>
                  <div class="obligation-item">
                    <span>买方义务：</span>
                    <el-rate
                      :model-value="getObligationLevel(term.buyerObligation)"
                      disabled
                      :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                    />
                    <el-tag :type="obligationTagType(term.buyerObligation)" size="small">
                      {{ obligationLabel(term.buyerObligation) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredTerms.length === 0" description="没有匹配的术语" />
      </div>

      <!-- 对比表格视图 -->
      <div v-else class="comparison-view">
        <div class="comparison-select">
          <span>选择要对比的术语：</span>
          <el-checkbox-group v-model="selectedForComparison">
            <el-checkbox
              v-for="term in filteredTerms"
              :key="term.code"
              :value="term.code"
              border
            >
              {{ term.code }}
            </el-checkbox>
          </el-checkbox-group>
        </div>

        <div v-if="comparisonTerms.length > 0" class="comparison-table-wrapper">
          <el-table :data="comparisonRows" border stripe style="width: 100%">
            <el-table-column prop="label" label="对比项" width="160" fixed />
            <el-table-column
              v-for="term in comparisonTerms"
              :key="term.code"
              :label="`${term.code} - ${term.chineseName}`"
              min-width="200"
            >
              <template #default="{ row }">
                <span v-if="row.key === 'transportMode'">
                  <el-tag :type="term.transportMode === 'any' ? 'primary' : 'warning'" size="small">
                    {{ term.transportMode === 'any' ? '任意运输方式' : '仅海运/内河' }}
                  </el-tag>
                </span>
                <span v-else-if="row.key === 'sellerObligation'">
                  <el-rate :model-value="getObligationLevel(term.sellerObligation)" disabled />
                  <el-tag :type="obligationTagType(term.sellerObligation)" size="small">
                    {{ obligationLabel(term.sellerObligation) }}
                  </el-tag>
                </span>
                <span v-else-if="row.key === 'buyerObligation'">
                  <el-rate :model-value="getObligationLevel(term.buyerObligation)" disabled />
                  <el-tag :type="obligationTagType(term.buyerObligation)" size="small">
                    {{ obligationLabel(term.buyerObligation) }}
                  </el-tag>
                </span>
                <span v-else-if="row.key.startsWith('cost_') && row.costKey">
                  <el-tag :type="getCostTagType(term.costs[row.costKey as keyof CostResponsibilities])" size="small">
                    {{ getCostLabel(term.costs[row.costKey as keyof CostResponsibilities]) }}
                  </el-tag>
                </span>
                <span v-else>{{ term[row.key as keyof Incoterm] }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-empty v-else description="请勾选至少一个术语进行对比" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

type ObligationLevel = 'low' | 'medium' | 'high'
type CostParty = 'seller' | 'buyer'
type TransportMode = 'any' | 'sea'

interface CostResponsibilities {
  freight: CostParty
  insurance: CostParty
  customsExport: CostParty
  customsImport: CostParty
  loading: CostParty
  unloading: CostParty
}

interface Incoterm {
  code: string
  chineseName: string
  englishName: string
  transportMode: TransportMode
  riskTransfer: string
  costs: CostResponsibilities
  sellerObligation: ObligationLevel
  buyerObligation: ObligationLevel
}

/** Incoterms 2020 全部 11 个术语数据 */
const incotermsData: Incoterm[] = [
  {
    code: 'EXW',
    chineseName: '工厂交货',
    englishName: 'Ex Works',
    transportMode: 'any',
    riskTransfer: '卖方在其所在地（工厂、仓库等）将货物交给买方处置时',
    costs: {
      freight: 'buyer',
      insurance: 'buyer',
      customsExport: 'buyer',
      customsImport: 'buyer',
      loading: 'buyer',
      unloading: 'buyer',
    },
    sellerObligation: 'low',
    buyerObligation: 'high',
  },
  {
    code: 'FCA',
    chineseName: '货交承运人',
    englishName: 'Free Carrier',
    transportMode: 'any',
    riskTransfer: '卖方在指定地点将货物交给买方指定的承运人时',
    costs: {
      freight: 'buyer',
      insurance: 'buyer',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'buyer',
    },
    sellerObligation: 'low',
    buyerObligation: 'high',
  },
  {
    code: 'FAS',
    chineseName: '船边交货',
    englishName: 'Free Alongside Ship',
    transportMode: 'sea',
    riskTransfer: '卖方将货物放置在指定装运港的船边时',
    costs: {
      freight: 'buyer',
      insurance: 'buyer',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'buyer',
      unloading: 'buyer',
    },
    sellerObligation: 'low',
    buyerObligation: 'high',
  },
  {
    code: 'FOB',
    chineseName: '船上交货',
    englishName: 'Free On Board',
    transportMode: 'sea',
    riskTransfer: '卖方将货物装上指定船只时',
    costs: {
      freight: 'buyer',
      insurance: 'buyer',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'buyer',
    },
    sellerObligation: 'medium',
    buyerObligation: 'high',
  },
  {
    code: 'CFR',
    chineseName: '成本加运费',
    englishName: 'Cost and Freight',
    transportMode: 'sea',
    riskTransfer: '卖方将货物装上船时（装运港船上交货）',
    costs: {
      freight: 'seller',
      insurance: 'buyer',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'buyer',
    },
    sellerObligation: 'medium',
    buyerObligation: 'medium',
  },
  {
    code: 'CIF',
    chineseName: '成本、保险费加运费',
    englishName: 'Cost, Insurance and Freight',
    transportMode: 'sea',
    riskTransfer: '卖方将货物装上船时（装运港船上交货）',
    costs: {
      freight: 'seller',
      insurance: 'seller',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'buyer',
    },
    sellerObligation: 'high',
    buyerObligation: 'medium',
  },
  {
    code: 'CPT',
    chineseName: '运费付至',
    englishName: 'Carriage Paid To',
    transportMode: 'any',
    riskTransfer: '卖方将货物交给第一承运人时',
    costs: {
      freight: 'seller',
      insurance: 'buyer',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'seller',
    },
    sellerObligation: 'medium',
    buyerObligation: 'medium',
  },
  {
    code: 'CIP',
    chineseName: '运费和保险费付至',
    englishName: 'Carriage and Insurance Paid To',
    transportMode: 'any',
    riskTransfer: '卖方将货物交给第一承运人时',
    costs: {
      freight: 'seller',
      insurance: 'seller',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'seller',
    },
    sellerObligation: 'high',
    buyerObligation: 'medium',
  },
  {
    code: 'DAP',
    chineseName: '目的地交货',
    englishName: 'Delivered at Place',
    transportMode: 'any',
    riskTransfer: '卖方在指定目的地将到达的运输工具上准备卸载的货物交给买方处置时',
    costs: {
      freight: 'seller',
      insurance: 'seller',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'buyer',
    },
    sellerObligation: 'high',
    buyerObligation: 'low',
  },
  {
    code: 'DPU',
    chineseName: '卸货地交货',
    englishName: 'Delivered at Place Unloaded',
    transportMode: 'any',
    riskTransfer: '卖方在指定目的地将货物从到达的运输工具上卸下后交给买方处置时',
    costs: {
      freight: 'seller',
      insurance: 'seller',
      customsExport: 'seller',
      customsImport: 'buyer',
      loading: 'seller',
      unloading: 'seller',
    },
    sellerObligation: 'high',
    buyerObligation: 'low',
  },
  {
    code: 'DDP',
    chineseName: '完税后交货',
    englishName: 'Delivered Duty Paid',
    transportMode: 'any',
    riskTransfer: '卖方在指定目的地将货物交给买方处置时（已完成进口清关）',
    costs: {
      freight: 'seller',
      insurance: 'seller',
      customsExport: 'seller',
      customsImport: 'seller',
      loading: 'seller',
      unloading: 'seller',
    },
    sellerObligation: 'high',
    buyerObligation: 'low',
  },
]

const costItems = [
  { key: 'freight' as const, label: '运费' },
  { key: 'insurance' as const, label: '保险' },
  { key: 'customsExport' as const, label: '出口清关' },
  { key: 'customsImport' as const, label: '进口清关' },
  { key: 'loading' as const, label: '装货' },
  { key: 'unloading' as const, label: '卸货' },
]

const searchText = ref('')
const transportFilter = ref<'all' | 'any' | 'sea'>('all')
const showComparison = ref(false)
const selectedForComparison = ref<string[]>(['FOB', 'CIF', 'EXW', 'DDP'])

/** 过滤后的术语列表 */
const filteredTerms = computed(() => {
  let list = incotermsData

  if (transportFilter.value !== 'all') {
    list = list.filter((t) => t.transportMode === transportFilter.value)
  }

  if (searchText.value.trim()) {
    const q = searchText.value.trim().toLowerCase()
    list = list.filter(
      (t) =>
        t.code.toLowerCase().includes(q) ||
        t.chineseName.includes(q) ||
        t.englishName.toLowerCase().includes(q),
    )
  }

  return list
})

/** 对比视图中选中的术语对象 */
const comparisonTerms = computed(() =>
  filteredTerms.value.filter((t) => selectedForComparison.value.includes(t.code)),
)

/** 对比表格行定义 */
const comparisonRows = computed(() => {
  const rows: Array<{ label: string; key: string; costKey?: keyof CostResponsibilities }> = [
    { label: '英文全称', key: 'englishName' },
    { label: '运输方式', key: 'transportMode' },
    { label: '风险转移点', key: 'riskTransfer' },
    ...costItems.map((c) => ({
      label: `费用：${c.label}`,
      key: `cost_${c.key}`,
      costKey: c.key as keyof CostResponsibilities,
    })),
    { label: '卖方义务', key: 'sellerObligation' },
    { label: '买方义务', key: 'buyerObligation' },
  ]
  return rows
})

function getCostLabel(party: CostParty): string {
  return party === 'seller' ? '卖方' : '买方'
}

function getCostTagType(party: CostParty): 'success' | 'danger' {
  return party === 'seller' ? 'success' : 'danger'
}

function getObligationLevel(level: ObligationLevel): number {
  const map: Record<ObligationLevel, number> = { low: 1, medium: 2, high: 3 }
  return map[level]
}

function obligationLabel(level: ObligationLevel): string {
  const map: Record<ObligationLevel, string> = { low: '低', medium: '中', high: '高' }
  return map[level]
}

function obligationTagType(level: ObligationLevel): 'info' | 'warning' | 'danger' {
  const map: Record<ObligationLevel, 'info' | 'warning' | 'danger'> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
  }
  return map[level]
}
</script>

<style scoped lang="scss">
.incoterms-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.term-cards {
  margin-top: 8px;
}

.term-card {
  margin-bottom: 16px;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-4px);
  }

  &--sea {
    border-top: 3px solid #e6a23c;
  }

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  &__code {
    font-size: 20px;
    font-weight: 700;
    color: #303133;
    font-family: monospace;
  }

  &__body {
    .term-card__name {
      font-size: 18px;
      font-weight: 600;
      margin: 0 0 4px;
      color: #303133;
    }

    .term-card__english {
      font-size: 13px;
      color: #909399;
      margin: 0 0 12px;
    }

    .term-card__risk {
      font-size: 13px;
      color: #606266;
      line-height: 1.6;
      margin: 0;
    }
  }

  &__costs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  &__obligations {
    .obligation-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      font-size: 13px;
      color: #606266;

      .el-rate {
        margin-right: 4px;
      }
    }
  }
}

.cost-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;

  &__label {
    color: #606266;
  }
}

.comparison-view {
  margin-top: 8px;
}

.comparison-select {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  font-size: 14px;
  color: #606266;

  .el-checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}

.comparison-table-wrapper {
  overflow-x: auto;
}
</style>
