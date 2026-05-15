<template>
  <div class="edit-product">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>编辑产品</span>
          <el-button @click="handleBack">返回列表</el-button>
        </div>
      </template>

      <el-form v-if="form" :model="form" :rules="rules" ref="formRef" label-width="120px" class="product-form">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SKU" prop="sku">
              <el-input v-model="form.sku" placeholder="请输入SKU" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
                <el-option label="电子产品" value="electronics" />
                <el-option label="服装" value="clothing" />
                <el-option label="家居" value="home" />
                <el-option label="玩具" value="toys" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="图片URL">
              <el-input v-model="form.image_url" placeholder="请输入产品图片URL" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="产品描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入产品描述" />
        </el-form-item>

        <el-divider content-position="left">价格信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="成本(CNY)" prop="price_cny">
              <el-input-number v-model="form.price_cny" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="售价(USD)" prop="price_usd">
              <el-input-number v-model="form.price_usd" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="利润率">
              <el-input :value="calculateProfit + '%'" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">规格信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="重量(kg)">
              <el-input-number v-model="form.weight" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="长(cm)">
              <el-input-number v-model="form.length" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="宽(cm)">
              <el-input-number v-model="form.width" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="高(cm)">
              <el-input-number v-model="form.height" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="库存数量">
              <el-input-number v-model="form.stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最低起订量">
              <el-input-number v-model="form.min_order_qty" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="标签">
              <el-input v-model="form.tags" placeholder="多个标签用逗号分隔" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">其他信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="阿里巴巴链接">
              <el-input v-model="form.alibaba_link" placeholder="请输入阿里巴巴产品链接" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="在售" value="active" />
                <el-option label="下架" value="inactive" />
                <el-option label="草稿" value="draft" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供货商">
              <el-select v-model="form.supplier_id" placeholder="请选择供货商" style="width: 100%" clearable>
                <el-option v-for="s in supplierOptions" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
          <el-button @click="handleBack">取消</el-button>
        </el-form-item>
      </el-form>

      <el-skeleton v-else :rows="10" animated />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import { fetchSuppliers } from '@/api/foreign-trade/suppliers'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const route = useRoute()
const foreignTradeStore = useForeignTradeStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const supplierOptions = ref<any[]>([])

const form = reactive({
  name: '',
  sku: '',
  category: '',
  image_url: '',
  description: '',
  price_cny: 0,
  price_usd: 0,
  cost: 0,
  weight: 0,
  length: 0,
  width: 0,
  height: 0,
  stock: 0,
  min_order_qty: 1,
  tags: '',
  alibaba_link: '',
  status: 'active',
  supplier_id: null as number | null,
})

const rules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  sku: [{ required: true, message: '请输入SKU', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price_cny: [{ required: true, message: '请输入成本价', trigger: 'blur' }],
  price_usd: [{ required: true, message: '请输入售价', trigger: 'blur' }],
}

const calculateProfit = computed(() => {
  if (form.price_cny === 0 || form.price_usd === 0) return 0
  const rate = 7.2
  const costInUSD = form.price_cny / rate
  const profit = ((form.price_usd - costInUSD) / form.price_usd) * 100
  return profit.toFixed(2)
})

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const id = Number(route.params.id)
        const result = await foreignTradeStore.updateProduct(id, { ...form })
        if (result) {
          ElMessage.success('产品更新成功')
          router.push('/foreign-trade/products/list')
        }
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleBack = () => {
  router.push('/foreign-trade/products/list')
}

onMounted(async () => {
  const id = Number(route.params.id)
  // 加载产品详情
  const product = await foreignTradeStore.loadProductDetail(id)
  if (product) {
    Object.assign(form, {
      name: product.name,
      sku: product.sku,
      category: product.category,
      image_url: product.image_url || '',
      description: product.description || '',
      price_cny: product.price_cny || 0,
      price_usd: product.price_usd || 0,
      cost: product.cost || 0,
      weight: product.weight || 0,
      length: product.length || 0,
      width: product.width || 0,
      height: product.height || 0,
      stock: product.stock || 0,
      min_order_qty: product.min_order_qty || 1,
      tags: product.tags || '',
      alibaba_link: product.alibaba_link || '',
      status: product.status,
      supplier_id: product.supplier_id || null,
    })
  }
  // 加载供货商选项
  try {
    const res = await fetchSuppliers({ page_size: 100 })
    if (res) supplierOptions.value = res.items || []
  } catch (e) {
    console.error('加载供货商列表失败:', e)
  }
})
</script>

<style scoped lang="scss">
.edit-product { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.product-form { max-width: 1000px; }
</style>
