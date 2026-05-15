<template>
  <div class="product-detail">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>产品详情</span>
          <div>
            <el-button type="primary" @click="handleEdit">编辑</el-button>
            <el-button @click="handleBack">返回列表</el-button>
          </div>
        </div>
      </template>

      <el-descriptions v-if="product" :column="2" border>
        <el-descriptions-item label="产品名称">{{ product.name }}</el-descriptions-item>
        <el-descriptions-item label="SKU">{{ product.sku }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ getCategoryLabel(product.category) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="product.status === 'active' ? 'success' : product.status === 'inactive' ? 'info' : 'warning'">
            {{ getStatusLabel(product.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="成本(CNY)">¥{{ Number(product.price_cny || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="售价(USD)">${{ Number(product.price_usd || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="重量">{{ product.weight || '-' }} kg</el-descriptions-item>
        <el-descriptions-item label="尺寸">{{ product.length && product.width && product.height ? `${product.length}×${product.width}×${product.height} cm` : '-' }}</el-descriptions-item>
        <el-descriptions-item label="库存">{{ product.stock ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="最低起订量">{{ product.min_order_qty || '-' }}</el-descriptions-item>
        <el-descriptions-item label="标签">{{ product.tags || '-' }}</el-descriptions-item>
        <el-descriptions-item label="供货商">{{ supplier?.name || product.supplier_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="阿里巴巴链接" :span="2">
          <el-link v-if="product.alibaba_link" :href="product.alibaba_link" target="_blank" type="primary">
            {{ product.alibaba_link }}
          </el-link>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="产品描述" :span="2">{{ product.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ product.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ product.updated_at || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-skeleton v-else :rows="10" animated />
    </el-card>

    <!-- 利润计算 -->
    <el-card v-if="product" shadow="never" class="mt-4">
      <template #header>
        <div class="card-header">
          <span>💰 利润计算</span>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="采购价 (CNY)">¥{{ Number(product.price_cny || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="售价 (USD)">${{ Number(product.price_usd || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="当前汇率 (USD/CNY)">{{ exchangeRates.USD_CNY.toFixed(4) }}</el-descriptions-item>
        <el-descriptions-item label="采购成本 (USD)">
          ${{ (Number(product.price_cny || 0) / exchangeRates.USD_CNY).toFixed(2) }}
        </el-descriptions-item>
        <el-descriptions-item label="利润 (USD)">
          <span :style="{ color: profit >= 0 ? '#67c23a' : '#f56c6c', fontWeight: 'bold' }">
            ${{ profit.toFixed(2) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="利润率">
          <el-tag :type="profitMargin >= 0 ? 'success' : 'danger'" size="large">
            {{ profitMargin.toFixed(1) }}%
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 供货商信息 -->
    <el-card v-if="supplier" shadow="never" class="mt-4">
      <template #header>
        <div class="card-header">
          <span>🏭 供货商信息</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="供货商名称">{{ supplier.name }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ supplier.contact_person || '-' }}</el-descriptions-item>
        <el-descriptions-item label="电话">
          <span v-if="supplier.phone">{{ supplier.phone }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="微信">{{ supplier.wechat || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">
          <el-link v-if="supplier.email" :href="`mailto:${supplier.email}`" type="primary">{{ supplier.email }}</el-link>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="地址">{{ [supplier.address, supplier.city, supplier.province, supplier.country].filter(Boolean).join(', ') || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import { storeToRefs } from 'pinia'
import type { Product, Supplier } from '@/api/foreign-trade/types'

const router = useRouter()
const route = useRoute()
const foreignTradeStore = useForeignTradeStore()
const { exchangeRates } = storeToRefs(foreignTradeStore)
const product = ref<Product | null>(null)
const supplier = ref<Supplier | null>(null)

const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = { electronics: '电子产品', clothing: '服装', home: '家居', toys: '玩具' }
  return map[category] || category
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { active: '在售', inactive: '下架', draft: '草稿' }
  return map[status] || status
}

// 利润计算
const profit = computed(() => {
  if (!product.value) return 0
  const costUsd = Number(product.value.price_cny || 0) / exchangeRates.value.USD_CNY
  return Number(product.value.price_usd || 0) - costUsd
})

const profitMargin = computed(() => {
  if (!product.value || !product.value.price_usd) return 0
  return (profit.value / Number(product.value.price_usd)) * 100
})

const handleEdit = () => {
  router.push(`/foreign-trade/products/edit/${route.params.id}`)
}

const handleBack = () => {
  router.push('/foreign-trade/products/list')
}

onMounted(async () => {
  const id = Number(route.params.id)
  product.value = await foreignTradeStore.loadProductDetail(id)

  // 加载供货商信息
  if (product.value?.supplier_id) {
    supplier.value = await foreignTradeStore.loadSupplierDetail(product.value.supplier_id)
  }
})
</script>

<style scoped lang="scss">
.product-detail { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.mt-4 { margin-top: 20px; }
</style>
