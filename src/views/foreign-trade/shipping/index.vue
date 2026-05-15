<template>
  <div class="shipping-calculator">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>运费计算器</span>
          <div class="header-actions">
            <el-tag type="info" size="small">支持 DHL / FedEx / UPS / EMS / 海运</el-tag>
            <el-tag v-if="hasCustomChannels" type="success" size="small">使用自定义渠道配置</el-tag>
          </div>
        </div>
      </template>

      <el-form :model="form" label-width="120px" class="calculator-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="重量 (kg)">
              <el-input-number v-model="form.weight_kg" :min="0.1" :max="1000" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="数量">
              <el-input-number v-model="form.quantity" :min="1" :max="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="目的地">
              <el-select v-model="form.destination" placeholder="请选择目的地" style="width: 100%">
                <el-option label="美国" value="US" />
                <el-option label="英国" value="UK" />
                <el-option label="德国" value="DE" />
                <el-option label="法国" value="FR" />
                <el-option label="意大利" value="IT" />
                <el-option label="西班牙" value="ES" />
                <el-option label="日本" value="JP" />
                <el-option label="韩国" value="KR" />
                <el-option label="澳大利亚" value="AU" />
                <el-option label="加拿大" value="CA" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">尺寸信息（可选，用于计算体积重）</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="长 (cm)">
              <el-input-number v-model="form.length_cm" :min="0" :max="500" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="宽 (cm)">
              <el-input-number v-model="form.width_cm" :min="0" :max="500" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="高 (cm)">
              <el-input-number v-model="form.height_cm" :min="0" :max="500" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="handleCalculate" :loading="calculating" size="large">
            <el-icon><i class="ep-calculator" /></el-icon>
            计算运费
          </el-button>
          <el-button @click="handleReset" size="large">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 计算结果 -->
      <div v-if="showResult" class="result-section">
        <el-divider content-position="left">计算结果</el-divider>
        
        <!-- 重量信息 -->
        <el-row :gutter="20" class="mb-4">
          <el-col :span="8">
            <el-card shadow="hover" class="info-card">
              <div class="info-label">实际重量</div>
              <div class="info-value">{{ result.weight_kg }} kg</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="info-card">
              <div class="info-label">体积重量</div>
              <div class="info-value">{{ result.volume_weight_kg }} kg</div>
              <div class="info-desc">长×宽×高÷5000</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="info-card highlight">
              <div class="info-label">计费重量</div>
              <div class="info-value">{{ result.chargeable_weight_kg }} kg</div>
              <div class="info-desc">取实际重量与体积重量较大值</div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 物流渠道对比 -->
        <el-card shadow="never" v-if="result.options.length > 0">
          <template #header>
            <div class="card-header">
              <span>物流渠道对比</span>
              <el-tag type="success" size="small">按价格排序</el-tag>
            </div>
          </template>
          <el-table :data="result.options" border stripe highlight-current-row>
            <el-table-column type="index" label="排名" width="60" align="center">
              <template #default="{ $index }">
                <el-tag v-if="$index === 0" type="success" size="small">最便宜</el-tag>
                <el-tag v-else-if="$index === 1" type="warning" size="small">次选</el-tag>
                <span v-else>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="carrier" label="物流商" width="120" />
            <el-table-column prop="service" label="服务类型" width="250" />
            <el-table-column prop="cost_usd" label="运费(USD)" width="120" align="right">
              <template #default="{ row }">
                <span style="color: #409eff; font-weight: bold">${{ row.cost_usd.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="cost_cny" label="运费(CNY)" width="120" align="right">
              <template #default="{ row }">
                <span style="color: #f56c6c; font-weight: bold">¥{{ row.cost_cny.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="estimated_days" label="预计时效" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="info">{{ row.estimated_days }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" min-width="150" />
          </el-table>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchCalculateShipping } from '@/api/foreign-trade/shipping'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import type { ShippingOption, ShippingChannel } from '@/api/foreign-trade/types'
import { STORAGE_KEYS } from '@/constants/storage-keys'

const LS_KEY = STORAGE_KEYS.SHIPPING_CHANNELS
const foreignTradeStore = useForeignTradeStore()

const calculating = ref(false)
const showResult = ref(false)
const hasCustomChannels = ref(false)
const customChannels = ref<ShippingChannel[]>([])

const form = reactive({
  weight_kg: 2.5,
  length_cm: 40,
  width_cm: 30,
  height_cm: 20,
  destination: 'US',
  quantity: 1,
})

const result = reactive({
  weight_kg: 0,
  volume_weight_kg: 0,
  chargeable_weight_kg: 0,
  options: [] as ShippingOption[],
})

// 加载自定义渠道配置
function loadCustomChannels() {
  try {
    const saved = localStorage.getItem(LS_KEY)
    if (saved) {
      const channels: ShippingChannel[] = JSON.parse(saved)
      customChannels.value = channels.filter(c => c.enabled)
      hasCustomChannels.value = customChannels.value.length > 0
    }
  } catch (e) {
    // 加载失败
  }
}

// 使用自定义渠道计算运费（本地计算）
function calculateWithCustomChannels(chargeableWeight: number): ShippingOption[] {
  const options: ShippingOption[] = []
  const usdCnyRate = foreignTradeStore.effectiveRates.USD_CNY || 0

  for (const channel of customChannels.value) {
    if (!channel.enabled) continue
    if (channel.maxWeight > 0 && chargeableWeight > channel.maxWeight) continue

    // 首重 + 续重计算
    let costUsd = channel.firstWeightPrice
    if (chargeableWeight > 1) {
      costUsd += (chargeableWeight - 1) * channel.additionalWeightPrice
    }

    // 如果有基础费率，按 kg 计算作为备选
    if (channel.baseRate > 0 && costUsd < chargeableWeight * (channel.baseRate / usdCnyRate)) {
      // 使用首重+续重计算
    } else if (channel.baseRate > 0 && channel.firstWeightPrice === 0) {
      costUsd = chargeableWeight * (channel.baseRate / usdCnyRate)
    }

    const costCny = costUsd * usdCnyRate

    options.push({
      carrier: channel.code,
      service: `${channel.name} - ${channel.description || channel.type}`,
      estimated_days: channel.avgDays || '未知',
      cost_usd: Number(costUsd.toFixed(2)),
      cost_cny: Number(costCny.toFixed(2)),
      notes: channel.tracking ? '可追踪' : '不可追踪',
    })
  }

  // 按价格排序
  options.sort((a, b) => a.cost_usd - b.cost_usd)
  return options
}

const handleCalculate = async () => {
  if (!form.destination) {
    ElMessage.warning('请选择目的地')
    return
  }
  
  calculating.value = true
  try {
    // 先计算体积重和计费重量
    const volumeWeight = (form.length_cm * form.width_cm * form.height_cm) / 5000
    const chargeableWeight = Math.max(form.weight_kg, volumeWeight)

    if (hasCustomChannels.value) {
      // 使用本地配置的渠道计算
      result.weight_kg = form.weight_kg
      result.volume_weight_kg = Number(volumeWeight.toFixed(2))
      result.chargeable_weight_kg = Number(chargeableWeight.toFixed(2))
      result.options = calculateWithCustomChannels(chargeableWeight)
      showResult.value = true
    } else {
      // 使用后端默认计算
      const res = await fetchCalculateShipping({
        weight_kg: form.weight_kg,
        length_cm: form.length_cm || undefined,
        width_cm: form.width_cm || undefined,
        height_cm: form.height_cm || undefined,
        destination: form.destination,
        quantity: form.quantity,
      })
      
      if (res) {
        result.weight_kg = res.weight_kg
        result.volume_weight_kg = res.volume_weight_kg
        result.chargeable_weight_kg = res.chargeable_weight_kg
        result.options = res.options || []
        showResult.value = true
      }
    }
  } catch (e) {
    ElMessage.error('计算失败，请稍后重试')
    // 计算失败
  } finally {
    calculating.value = false
  }
}

const handleReset = () => {
  form.weight_kg = 2.5
  form.length_cm = 40
  form.width_cm = 30
  form.height_cm = 20
  form.destination = 'US'
  form.quantity = 1
  showResult.value = false
}

onMounted(() => {
  loadCustomChannels()
})
</script>

<style scoped lang="scss">
.shipping-calculator {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.calculator-form {
  max-width: 900px;
}

.result-section {
  margin-top: 20px;
}

.mb-4 {
  margin-bottom: 16px;
}

.info-card {
  text-align: center;
  
  .info-label {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }
  
  .info-value {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
  }
  
  .info-desc {
    font-size: 12px;
    color: #c0c4cc;
    margin-top: 4px;
  }
  
  &.highlight {
    border-color: #409eff;
    
    .info-value {
      color: #409eff;
    }
  }
}
</style>
