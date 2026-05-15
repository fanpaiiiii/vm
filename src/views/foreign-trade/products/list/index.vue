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
            <el-upload
              :show-file-list="false"
              :before-upload="handleImportFile"
              accept=".csv"
            >
              <el-button type="warning">
                <el-icon><i class="ep-upload" /></el-icon>
                导入CSV
              </el-button>
            </el-upload>
            <el-button type="success" @click="handleExport">
              <el-icon><i class="ep-download" /></el-icon>
              导出CSV
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索区域 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="产品名称/SKU" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="请选择分类" clearable>
            <el-option label="电子产品" value="electronics" />
            <el-option label="服装" value="clothing" />
            <el-option label="家居" value="home" />
            <el-option label="玩具" value="toys" />
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
        <el-table-column type="selection" width="55" />
        <el-table-column prop="image_url" label="图片" width="80">
          <template #default="{ row }">
            <el-image v-if="row.image_url" :src="row.image_url" :preview-src-list="[row.image_url]" fit="cover" class="product-image" />
            <div v-else class="product-image-placeholder">
              <el-icon size="24"><i class="ep-picture" /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="产品名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag>{{ getCategoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price_usd" label="售价(USD)" width="120" align="right">
          <template #default="{ row }">
            ${{ Number(row.price_usd || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="price_cny" label="成本(CNY)" width="120" align="right">
          <template #default="{ row }">
            ¥{{ Number(row.price_cny || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.stock > 10 ? 'success' : row.stock > 0 ? 'warning' : 'danger'" size="small">
              {{ row.stock }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'inactive' ? 'info' : 'warning'">
              {{ getStatusLabel(row.status) }}
            </el-tag>
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

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入产品" width="500px">
      <el-upload
        ref="uploadRef"
        drag
        action="#"
        :auto-upload="false"
        accept=".csv"
        :limit="1"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><i class="ep-upload-filled" /></el-icon>
        <div class="el-upload__text">将CSV文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持CSV格式文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport" :loading="importing">确定导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import { fetchImportProducts, getExportProductsUrl } from '@/api/foreign-trade/products'
import type { UploadFile } from 'element-plus'

const router = useRouter()
const foreignTradeStore = useForeignTradeStore()

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref<any[]>([])
const importDialogVisible = ref(false)
const importing = ref(false)
const importFile = ref<File | null>(null)

const searchForm = reactive({
  keyword: '',
  category: '',
  status: '',
})

const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = {
    electronics: '电子产品',
    clothing: '服装',
    home: '家居',
    toys: '玩具',
  }
  return map[category] || category
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    active: '在售',
    inactive: '下架',
    draft: '草稿',
  }
  return map[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    await foreignTradeStore.loadProducts({
      keyword: searchForm.keyword || undefined,
      category: searchForm.category || undefined,
      status: searchForm.status || undefined,
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
  searchForm.category = ''
  searchForm.status = ''
  handleSearch()
}

const handleAdd = () => {
  router.push('/foreign-trade/products/add')
}

const handleView = (row: any) => {
  router.push(`/foreign-trade/products/detail/${row.id}`)
}

const handleEdit = (row: any) => {
  router.push(`/foreign-trade/products/edit/${row.id}`)
}

const handleDelete = async (row: any) => {
  const success = await foreignTradeStore.deleteProduct(row.id)
  if (success) {
    loadData()
  }
}

const handleExport = () => {
  const url = getExportProductsUrl()
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'products.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('导出请求已发送')
}

const handleImportFile = (file: File) => {
  importFile.value = file
  importDialogVisible.value = true
  return false // 阻止自动上传
}

const handleFileChange = (file: UploadFile) => {
  importFile.value = file.raw || null
}

const confirmImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  importing.value = true
  try {
    await fetchImportProducts(importFile.value)
    importDialogVisible.value = false
    importFile.value = null
    loadData()
  } catch (e) {
    console.error('导入失败:', e)
  } finally {
    importing.value = false
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
})
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
