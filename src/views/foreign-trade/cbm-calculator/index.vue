<template>
  <div class="cbm-calculator">
    <!-- 单箱计算 -->
    <el-card shadow="never" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>📦 单箱 CBM 计算</span>
        </div>
      </template>

      <el-form :model="singleForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="长 (cm)">
              <el-input-number v-model="singleForm.length" :min="0.1" :precision="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="宽 (cm)">
              <el-input-number v-model="singleForm.width" :min="0.1" :precision="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="高 (cm)">
              <el-input-number v-model="singleForm.height" :min="0.1" :precision="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="毛重 (kg)">
              <el-input-number v-model="singleForm.weight" :min="0" :precision="2" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-row :gutter="20">
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">体积 (CBM)</div>
            <div class="result-value primary">{{ singleCbm.toFixed(4) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">体积重 (kg)</div>
            <div class="result-value">{{ singleVolumeWeight.toFixed(2) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">计费重 (kg)</div>
            <div class="result-value warning">{{ singleChargeableWeight.toFixed(2) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">单箱尺寸 (cm)</div>
            <div class="result-value text-sm">{{ singleForm.length }} × {{ singleForm.width }} × {{ singleForm.height }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 多箱计算 -->
    <el-card shadow="never" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>📋 多箱装柜计算</span>
          <el-button type="primary" size="small" @click="addCartonRow">
            <el-icon><Plus /></el-icon> 添加纸箱
          </el-button>
        </div>
      </template>

      <el-table :data="cartonRows" border stripe style="width: 100%">
        <el-table-column label="序号" width="60" type="index" align="center" />
        <el-table-column label="长 (cm)" width="140">
          <template #default="{ row }">
            <el-input-number v-model="row.length" :min="0.1" :precision="1" :step="1" size="small" controls-position="right" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="宽 (cm)" width="140">
          <template #default="{ row }">
            <el-input-number v-model="row.width" :min="0.1" :precision="1" :step="1" size="small" controls-position="right" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="高 (cm)" width="140">
          <template #default="{ row }">
            <el-input-number v-model="row.height" :min="0.1" :precision="1" :step="1" size="small" controls-position="right" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="毛重 (kg)" width="140">
          <template #default="{ row }">
            <el-input-number v-model="row.weight" :min="0" :precision="2" :step="0.5" size="small" controls-position="right" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="数量" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" :step="1" size="small" controls-position="right" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="单箱 CBM" width="110" align="center">
          <template #default="{ row }">
            {{ calcCbm(row.length, row.width, row.height).toFixed(4) }}
          </template>
        </el-table-column>
        <el-table-column label="小计 CBM" width="110" align="center">
          <template #default="{ row }">
            {{ (calcCbm(row.length, row.width, row.height) * row.quantity).toFixed(4) }}
          </template>
        </el-table-column>
        <el-table-column label="小计重量 (kg)" width="120" align="center">
          <template #default="{ row }">
            {{ (row.weight * row.quantity).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="removeCartonRow($index)" :disabled="cartonRows.length <= 1">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 汇总 -->
      <el-row :gutter="20" class="mt-4">
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">总箱数</div>
            <div class="result-value primary">{{ totalBoxes }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">总体积 (CBM)</div>
            <div class="result-value primary">{{ totalCbm.toFixed(4) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">总重量 (kg)</div>
            <div class="result-value">{{ totalWeight.toFixed(2) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="result-item">
            <div class="result-label">总体积重 (kg)</div>
            <div class="result-value warning">{{ totalVolumeWeight.toFixed(2) }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 装柜估算 & 集装箱利用率 -->
    <el-card shadow="never" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>🚢 集装箱装载估算</span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8" v-for="container in containers" :key="container.type">
          <el-card shadow="hover" class="container-card">
            <div class="container-title">{{ container.type }}</div>
            <div class="container-capacity">{{ container.capacity }} CBM</div>
            <el-progress
              :percentage="getContainerUtilization(container.capacity)"
              :color="getProgressColor(getContainerUtilization(container.capacity))"
              :stroke-width="20"
              :text-inside="true"
              class="mb-2"
            />
            <div class="container-detail">
              <div>可装箱数：<strong>{{ getContainerBoxCount(container.capacity) }}</strong> 箱</div>
              <div>剩余空间：<strong>{{ getContainerRemainder(container.capacity).toFixed(4) }}</strong> CBM</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 运费估算 -->
    <el-card shadow="never" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>💰 运费估算</span>
        </div>
      </template>

      <el-form :model="freightForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="运费方式">
              <el-radio-group v-model="freightForm.method">
                <el-radio value="sea">海运 (按CBM)</el-radio>
                <el-radio value="air">空运 (按kg)</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item :label="freightForm.method === 'sea' ? '海运单价 ($/CBM)' : '空运单价 ($/kg)'">
              <el-input-number v-model="freightForm.rate" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="附加费 ($)">
              <el-input-number v-model="freightForm.surcharge" :min="0" :precision="2" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <div class="result-item" style="margin-top: 4px;">
              <div class="result-label">预估运费</div>
              <div class="result-value primary large">${{ estimatedFreight.toFixed(2) }}</div>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'ForeignTradeCBMCalculator' })

interface CartonRow {
  length: number
  width: number
  height: number
  weight: number
  quantity: number
}

/** 单箱表单 */
const singleForm = reactive({
  length: 60,
  width: 40,
  height: 50,
  weight: 15,
})

/** 运费表单 */
const freightForm = reactive({
  method: 'sea' as 'sea' | 'air',
  rate: 80,
  surcharge: 0,
})

/** 多箱行 */
const cartonRows = ref<CartonRow[]>([
  { length: 60, width: 40, height: 50, weight: 15, quantity: 100 },
])

/** 集装箱规格 */
const containers = [
  { type: '20尺标准柜', capacity: 28 },
  { type: '20尺大柜', capacity: 33 },
  { type: '40尺标准柜', capacity: 56 },
  { type: '40尺大柜', capacity: 67 },
  { type: '40尺高柜 (HQ)', capacity: 60 },
  { type: '40尺高柜 (HQ大)', capacity: 76 },
]

/** 计算 CBM：长×宽×高 (cm→m) */
function calcCbm(l: number, w: number, h: number): number {
  return (l * w * h) / 1000000
}

/** 单箱 CBM */
const singleCbm = computed(() => calcCbm(singleForm.length, singleForm.width, singleForm.height))

/** 单箱体积重 (1 CBM = 167 kg) */
const singleVolumeWeight = computed(() => singleCbm.value * 167)

/** 单箱计费重 = max(实际重量, 体积重) */
const singleChargeableWeight = computed(() => Math.max(singleForm.weight, singleVolumeWeight.value))

/** 总箱数 */
const totalBoxes = computed(() => cartonRows.value.reduce((sum, r) => sum + r.quantity, 0))

/** 总 CBM */
const totalCbm = computed(() =>
  cartonRows.value.reduce((sum, r) => sum + calcCbm(r.length, r.width, r.height) * r.quantity, 0)
)

/** 总重量 */
const totalWeight = computed(() =>
  cartonRows.value.reduce((sum, r) => sum + r.weight * r.quantity, 0)
)

/** 总体积重 */
const totalVolumeWeight = computed(() => totalCbm.value * 167)

/** 集装箱利用率 */
function getContainerUtilization(capacity: number): number {
  if (capacity <= 0 || totalCbm.value <= 0) return 0
  return Math.min(Math.round((totalCbm.value / capacity) * 100), 100)
}

/** 可装箱数（基于体积估算） */
function getContainerBoxCount(capacity: number): number {
  if (totalCbm.value <= 0) return 0
  const singleAvgCbm = totalCbm.value / totalBoxes.value
  return Math.floor(capacity / singleAvgCbm)
}

/** 剩余空间 */
function getContainerRemainder(capacity: number): number {
  if (totalCbm.value <= 0) return capacity
  return Math.max(capacity - totalCbm.value, 0)
}

/** 进度条颜色 */
function getProgressColor(pct: number): string {
  if (pct < 50) return '#67c23a'
  if (pct < 80) return '#e6a23c'
  return '#f56c6c'
}

/** 预估运费 */
const estimatedFreight = computed(() => {
  if (freightForm.method === 'sea') {
    return totalCbm.value * freightForm.rate + freightForm.surcharge
  }
  const chargeable = totalVolumeWeight.value > totalWeight.value ? totalVolumeWeight.value : totalWeight.value
  return chargeable * freightForm.rate + freightForm.surcharge
})

/** 添加行 */
function addCartonRow() {
  cartonRows.value.push({ length: 60, width: 40, height: 50, weight: 15, quantity: 100 })
}

/** 删除行 */
function removeCartonRow(index: number) {
  if (cartonRows.value.length > 1) {
    cartonRows.value.splice(index, 1)
  }
}
</script>

<style scoped>
.cbm-calculator {
  padding: 4px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-4 {
  margin-top: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
}

.result-item {
  text-align: center;
  padding: 8px 0;
}

.result-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.result-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.result-value.primary {
  color: var(--el-color-primary);
}

.result-value.warning {
  color: var(--el-color-warning);
}

.result-value.large {
  font-size: 24px;
}

.text-sm {
  font-size: 14px !important;
}

.container-card {
  text-align: center;
}

.container-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.container-capacity {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
}

.container-detail {
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.8;
}

.container-detail strong {
  color: var(--el-color-primary);
}
</style>
