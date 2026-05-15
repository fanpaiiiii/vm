<template>
  <div class="products-list">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>产品列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><i class="ep-plus" /></el-icon>
              添加产品
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索区域 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="名称/货号" clearable />
        </el-form-item>
        <el-form-item label="供货商">
          <el-select v-model="searchForm.supplier_id" placeholder="请选择供货商" clearable style="width: 180px">
            <el-option v-for="s in supplierOptions" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="在售" value="active" />
            <el-option label="下架" value="inactive" />
            <el-option label="草稿" value="draft" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="sku" label="货号" width="120" />
        <el-table-column prop="image_url" label="货品图" width="80">
          <template #default="{ row }">
            <el-image v-if="row.image_url" :src="row.image_url" :preview-src-list="[row.image_url]" fit="cover" class="product-image" />
            <div v-else class="product-image-placeholder">
              <el-icon size="24"><i class="ep-picture" /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="货品名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="spec" label="货品规格" min-width="120" show-overflow-tooltip />
        <el-table-column prop="box_spec" label="箱规" width="100" show-overflow-tooltip />
        <el-table-column prop="size_variants" label="尺码" min-width="160">
          <template #default="{ row }">
            <template v-if="row.size_variants && row.size_variants.length">
              <el-tag v-for="(v, i) in row.size_variants" :key="i" size="small" class="size-tag">
                {{ v.size }}: {{ v.specs?.join('/') }}
              </el-tag>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">
            ¥{{ Number(row.unit_price || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="sample_price" label="样品价" width="100" align="right">
          <template #default="{ row }">
            ¥{{ Number(row.sample_price || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="shipping_cost" label="运费" width="90" align="right">
          <template #default="{ row }">
            ¥{{ Number(row.shipping_cost || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除该产品吗？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import { fetchSuppliers } from '@/api/foreign-trade/suppliers'
import type { Supplier, Product } from '@/api/foreign-trade/types'

const router = useRouter()
const foreignTradeStore = useForeignTradeStore()

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref<Product[]>([])
const supplierOptions = ref<Supplier[]>([])

const searchForm = reactive({
  keyword: '',
  status: '',
  supplier_id: undefined as number | undefined,
})

const loadData = async () => {
  loading.value = true
  try {
    await foreignTradeStore.loadProducts({
      keyword: searchForm.keyword || undefined,
      status: searchForm.status || undefined,
      supplier_id: searchForm.supplier_id || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    tableData.value = foreignTradeStore.products
    total.value = foreignTradeStore.productsTotal
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.supplier_id = undefined
  handleSearch()
}

const handleAdd = () => {
  router.push('/foreign-trade/products/add')
}

const handleView = (row: Product) => {
  router.push(`/foreign-trade/products/detail/${row.id}`)
}

const handleEdit = (row: Product) => {
  router.push(`/foreign-trade/products/edit/${row.id}`)
}

const handleDelete = async (row: Product) => {
  const success = await foreignTradeStore.deleteProduct(row.id)
  if (success) {
    loadData()
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

onMounted(() => {
  loadData()
  loadSupplierOptions()
})

const loadSupplierOptions = async () => {
  try {
    const res = await fetchSuppliers({ page: 1, page_size: 200 })
    if (res?.items) supplierOptions.value = res.items
  } catch (e) {
  }
}
</script>

<style scoped lang="scss">
.products-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.product-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
}

.product-image-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.size-tag {
  margin: 2px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
