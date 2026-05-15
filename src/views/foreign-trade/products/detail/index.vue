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
        <el-descriptions-item label="货号">{{ product.sku || '-' }}</el-descriptions-item>
        <el-descriptions-item label="货品名称">{{ product.name }}</el-descriptions-item>
        <el-descriptions-item label="货品图" :span="2">
          <el-image
            v-if="product.image_url"
            :src="product.image_url"
            :preview-src-list="[product.image_url]"
            fit="contain"
            class="detail-image"
          />
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="1688链接" :span="2">
          <el-link v-if="product.link_1688" :href="product.link_1688" target="_blank" type="primary">
            {{ product.link_1688 }}
          </el-link>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="货品规格">{{ product.spec || '-' }}</el-descriptions-item>
        <el-descriptions-item label="箱规">{{ product.box_spec || '-' }}</el-descriptions-item>
        <el-descriptions-item label="尺码规格" :span="2">
          <template v-if="product.size_variants && product.size_variants.length">
            <div v-for="(v, i) in product.size_variants" :key="i" class="size-variant-display">
              <el-tag type="info" size="small" class="size-label">{{ v.size }}</el-tag>
              <el-tag v-for="(s, si) in v.specs" :key="si" size="small" class="spec-label">{{ s }}</el-tag>
            </div>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="单价">¥{{ Number(product.unit_price || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="样品价">¥{{ Number(product.sample_price || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="运费">¥{{ Number(product.shipping_cost || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="product.status === 'active' ? 'success' : product.status === 'inactive' ? 'info' : 'warning'">
            {{ getStatusLabel(product.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="供货商">{{ supplier?.name || product.supplier_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ product.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ product.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ product.updated_at || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-skeleton v-else :rows="10" animated />
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import type { Product, Supplier } from '@/api/foreign-trade/types'

const router = useRouter()
const route = useRoute()
const foreignTradeStore = useForeignTradeStore()
const product = ref<Product | null>(null)
const supplier = ref<Supplier | null>(null)

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { active: '在售', inactive: '下架', draft: '草稿' }
  return map[status] || status
}

const handleEdit = () => {
  router.push(`/foreign-trade/products/edit/${route.params.id}`)
}

const handleBack = () => {
  router.push('/foreign-trade/products/list')
}

onMounted(async () => {
  const id = Number(route.params.id)
  if (!id || isNaN(id)) {
    router.replace('/foreign-trade/products/list')
    return
  }
  product.value = await foreignTradeStore.loadProductDetail(id)

  if (product.value?.supplier_id) {
    supplier.value = await foreignTradeStore.loadSupplierDetail(product.value.supplier_id)
  }
})
</script>

<style scoped lang="scss">
.product-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mt-4 {
  margin-top: 20px;
}

.detail-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 4px;
}

.size-variant-display {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.size-label {
  min-width: 40px;
  text-align: center;
}

.spec-label {
  margin: 0;
}
</style>
