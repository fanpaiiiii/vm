<template>
  <div class="suppliers-list">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>供货商列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><i class="ep-plus" /></el-icon>
            添加供货商
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="供货商名称">
          <el-input v-model="searchForm.keyword" placeholder="请输入供货商名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable>
            <el-option label="活跃" :value="true" />
            <el-option label="已禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" border style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="供货商名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="contact_person" label="联系人" width="120" />
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip />
        <el-table-column prop="city" label="城市" width="120" />
        <el-table-column prop="alibaba_store" label="阿里巴巴店铺" width="200">
          <template #default="{ row }">
            <el-link v-if="row.alibaba_store" :href="row.alibaba_store" target="_blank" type="primary">
              查看店铺
            </el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="评级" width="160" align="center">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled show-score />
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '活跃' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除该供货商吗？" @confirm="handleDelete(row)">
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

const router = useRouter()
const foreignTradeStore = useForeignTradeStore()
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref<any[]>([])

const searchForm = reactive({
  keyword: '',
  is_active: undefined as boolean | undefined,
})

const loadData = async () => {
  loading.value = true
  try {
    await foreignTradeStore.loadSuppliers({
      keyword: searchForm.keyword || undefined,
      is_active: searchForm.is_active,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    tableData.value = foreignTradeStore.suppliers
    total.value = foreignTradeStore.suppliersTotal
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { currentPage.value = 1; loadData() }
const handleReset = () => { searchForm.keyword = ''; searchForm.is_active = undefined; handleSearch() }
const handleAdd = () => router.push('/foreign-trade/suppliers/add')
const handleEdit = (row: any) => router.push(`/foreign-trade/suppliers/edit/${row.id}`)

const handleDelete = async (row: any) => {
  const success = await foreignTradeStore.deleteSupplier(row.id)
  if (success) loadData()
}

const handleSizeChange = (val: number) => { pageSize.value = val; loadData() }
const handleCurrentChange = (val: number) => { currentPage.value = val; loadData() }

onMounted(() => loadData())
</script>

<style scoped lang="scss">
.suppliers-list { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
