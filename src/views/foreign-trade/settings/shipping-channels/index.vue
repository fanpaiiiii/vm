<template>
  <div class="settings-shipping-channels">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>物流渠道管理</span>
          <div class="header-actions">
            <el-tag type="info" size="small">共 {{ channels.length }} 个渠道</el-tag>
            <el-tag type="success" size="small">{{ channels.filter(c => c.enabled).length }} 个启用</el-tag>
            <el-button type="primary" @click="addChannel">
              <el-icon><i class="ep-plus" /></el-icon>
              添加渠道
            </el-button>
            <el-button type="warning" @click="resetToDefault">
              <el-icon><i class="ep-refresh-right" /></el-icon>
              恢复默认
            </el-button>
          </div>
        </div>
      </template>

      <el-alert title="物流渠道说明" type="info" :closable="false" class="mb-4">
        <template #default>
          <div>
            <p>• 管理可用的物流渠道和运费规则，配置不同渠道的首重价格、续重价格和时效</p>
            <p>• 运费计算器会根据这些渠道参数计算各渠道的报价</p>
            <p>• 修改后点击"保存配置"生效，数据保存在本地浏览器中</p>
          </div>
        </template>
      </el-alert>

      <!-- 渠道列表 -->
      <div v-for="(channel, index) in channels" :key="channel.id" class="channel-card">
        <el-card shadow="hover" class="mb-4">
          <template #header>
            <div class="channel-header">
              <div class="channel-title">
                <el-tag :type="getTypeTagType(channel.type)" size="small">{{ channel.type }}</el-tag>
                <el-tag size="small" style="margin-left: 4px">{{ channel.code }}</el-tag>
                <span class="channel-name">{{ channel.name }}</span>
              </div>
              <div class="channel-actions">
                <el-switch
                  v-model="channel.enabled"
                  active-text="启用"
                  inactive-text="禁用"
                  style="margin-right: 12px"
                />
                <el-button type="danger" link @click="removeChannel(index)">
                  <el-icon><i class="ep-delete" /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </template>

          <el-form :model="channel" label-width="120px" class="channel-form">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="渠道名称">
                  <el-input v-model="channel.name" placeholder="如: DHL国际快递" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="渠道代码">
                  <el-input v-model="channel.code" placeholder="如: DHL" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="渠道类型">
                  <el-select v-model="channel.type" style="width: 100%">
                    <el-option label="快递" value="快递" />
                    <el-option label="空运" value="空运" />
                    <el-option label="海运" value="海运" />
                    <el-option label="铁路" value="铁路" />
                    <el-option label="邮政" value="邮政" />
                    <el-option label="专线" value="专线" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="首重价格 (USD)">
                  <el-input-number v-model="channel.firstWeightPrice" :min="0" :precision="2" :step="0.5" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="续重价格 (USD/kg)">
                  <el-input-number v-model="channel.additionalWeightPrice" :min="0" :precision="2" :step="0.5" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最大重量 (kg)">
                  <el-input-number v-model="channel.maxWeight" :min="0" :step="1" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="时效范围">
                  <el-input v-model="channel.avgDays" placeholder="如: 3-5天" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="可追踪">
                  <el-switch v-model="channel.tracking" active-text="是" inactive-text="否" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="基础费率 (¥/kg)">
                  <el-input-number v-model="channel.baseRate" :min="0" :precision="2" :step="1" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row>
              <el-col :span="24">
                <el-form-item label="渠道说明">
                  <el-input v-model="channel.description" type="textarea" :rows="2" placeholder="渠道描述信息" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="channels.length === 0" description="暂无物流渠道，点击上方按钮添加">
        <el-button type="primary" @click="resetToDefault">恢复默认渠道</el-button>
      </el-empty>

      <!-- 底部操作 -->
      <div class="bottom-actions" v-if="channels.length > 0">
        <el-button type="primary" size="large" @click="saveChannels">
          <el-icon><i class="ep-check" /></el-icon>
          保存配置
        </el-button>
        <el-button size="large" @click="resetToDefault">
          <el-icon><i class="ep-refresh-right" /></el-icon>
          恢复默认配置
        </el-button>
      </div>

      <!-- 运费计算说明 -->
      <div class="mt-4" v-if="channels.length > 0">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <span>运费计算说明</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="运费计算公式">首重价格 + (计费重量 - 首重) × 续重价格</el-descriptions-item>
            <el-descriptions-item label="体积重计算公式">长(cm) × 宽(cm) × 高(cm) ÷ 5000 = 体积重(kg)</el-descriptions-item>
            <el-descriptions-item label="计费重量">取实际重量与体积重的较大值</el-descriptions-item>
            <el-descriptions-item label="快递渠道">DHL、FedEx、UPS 等国际快递，时效快但费用较高</el-descriptions-item>
            <el-descriptions-item label="空运渠道">空运专线服务，性价比高，适合中等批量货物</el-descriptions-item>
            <el-descriptions-item label="海运渠道">海运服务，费用最低但时效较长，适合大批量货物</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ShippingChannel } from '@/api/foreign-trade/types'
import { STORAGE_KEYS } from '@/constants/storage-keys'

const LS_KEY = STORAGE_KEYS.SHIPPING_CHANNELS

// 默认渠道配置
const defaultChannels: ShippingChannel[] = [
  { id: 'dhl', name: 'DHL国际快递', code: 'DHL', type: '快递', tracking: true, baseRate: 85, firstWeightPrice: 35, additionalWeightPrice: 12, avgDays: '3-5天', maxWeight: 70, enabled: true, description: '全球快递服务，适合小件高价值商品，时效稳定' },
  { id: 'fedex', name: 'FedEx国际快递', code: 'FEDEX', type: '快递', tracking: true, baseRate: 90, firstWeightPrice: 38, additionalWeightPrice: 13, avgDays: '3-5天', maxWeight: 68, enabled: true, description: '全球快递服务，北美优势明显，清关能力强' },
  { id: 'ups', name: 'UPS国际快递', code: 'UPS', type: '快递', tracking: true, baseRate: 88, firstWeightPrice: 36, additionalWeightPrice: 12.5, avgDays: '4-6天', maxWeight: 70, enabled: true, description: '全球快递服务，欧美优势，适合商业快递' },
  { id: 'ems', name: 'EMS国际快递', code: 'EMS', type: '邮政', tracking: true, baseRate: 60, firstWeightPrice: 25, additionalWeightPrice: 8, avgDays: '7-15天', maxWeight: 30, enabled: true, description: '邮政特快专递，价格适中，覆盖范围广' },
  { id: 'air', name: '空运专线', code: 'AIR', type: '空运', tracking: true, baseRate: 45, firstWeightPrice: 20, additionalWeightPrice: 6, avgDays: '7-10天', maxWeight: 500, enabled: true, description: '空运专线服务，性价比高，适合中等批量货物' },
  { id: 'sea', name: '海运', code: 'SEA', type: '海运', tracking: false, baseRate: 15, firstWeightPrice: 8, additionalWeightPrice: 2, avgDays: '20-35天', maxWeight: 10000, enabled: true, description: '海运服务，适合大批量货物，费用最低' },
  { id: 'rail', name: '铁路运输', code: 'RAIL', type: '铁路', tracking: true, baseRate: 30, firstWeightPrice: 15, additionalWeightPrice: 4, avgDays: '15-20天', maxWeight: 5000, enabled: true, description: '中欧铁路运输，适合欧洲线路，性价比高' },
  { id: 'special', name: '专线物流', code: 'SPECIAL', type: '专线', tracking: true, baseRate: 50, firstWeightPrice: 22, additionalWeightPrice: 7, avgDays: '10-15天', maxWeight: 200, enabled: true, description: '特定国家/地区专线，价格和时效平衡' },
]

const channels = ref<ShippingChannel[]>([])

// 加载配置
function loadChannels() {
  try {
    const saved = localStorage.getItem(LS_KEY)
    if (saved) {
      channels.value = JSON.parse(saved)
    } else {
      channels.value = JSON.parse(JSON.stringify(defaultChannels))
    }
  } catch (e) {
    console.error('加载物流渠道配置失败:', e)
    channels.value = JSON.parse(JSON.stringify(defaultChannels))
  }
}

// 保存配置
function saveChannels() {
  localStorage.setItem(LS_KEY, JSON.stringify(channels.value))
  ElMessage.success('物流渠道配置已保存')
}

// 添加渠道
function addChannel() {
  const id = `custom_${Date.now()}`
  channels.value.push({
    id,
    name: '新渠道',
    code: 'NEW',
    type: '专线',
    tracking: true,
    baseRate: 0,
    firstWeightPrice: 0,
    additionalWeightPrice: 0,
    avgDays: '',
    maxWeight: 0,
    enabled: true,
    description: '',
  })
}

// 删除渠道
async function removeChannel(index: number) {
  try {
    await ElMessageBox.confirm(`确定要删除渠道"${channels.value[index].name}"吗？`, '确认', { type: 'warning' })
    channels.value.splice(index, 1)
    ElMessage.success('已删除')
  } catch {
    // 取消
  }
}

// 恢复默认配置
async function resetToDefault() {
  try {
    await ElMessageBox.confirm('确定要恢复默认渠道配置吗？当前的自定义配置将丢失。', '确认', { type: 'warning' })
    channels.value = JSON.parse(JSON.stringify(defaultChannels))
    localStorage.setItem(LS_KEY, JSON.stringify(channels.value))
    ElMessage.success('已恢复默认配置')
  } catch {
    // 取消
  }
}

const getTypeTagType = (type: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
    '快递': 'primary',
    '空运': 'warning',
    '海运': 'success',
    '铁路': 'info',
    '邮政': 'danger',
    '专线': 'primary',
  }
  return map[type] || 'primary'
}

onMounted(() => {
  loadChannels()
})
</script>

<style scoped lang="scss">
.settings-shipping-channels { padding: 20px; }

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

.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 24px; }

.channel-card {
  margin-bottom: 16px;
}

.channel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.channel-name {
  font-weight: bold;
  font-size: 15px;
  margin-left: 4px;
}

.channel-actions {
  display: flex;
  align-items: center;
}

.channel-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}

.bottom-actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.info-card {
  background: #f5f7fa;
}
</style>
