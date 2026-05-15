<template>
  <div class="edit-product">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>编辑产品</span>
          <el-button @click="handleBack">返回列表</el-button>
        </div>
      </template>

      <el-form v-if="formLoaded" :model="form" :rules="rules" ref="formRef" label-width="120px" class="product-form">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="货号">
              <el-input v-model="form.sku" placeholder="留空自动生成 FT-XXXX" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="货品名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入货品名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="1688链接">
              <el-input v-model="form.link_1688" placeholder="请输入1688产品链接" />
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
          <el-col :span="24">
            <el-form-item label="货品图">
              <div class="image-upload-area">
                <el-upload
                  class="image-uploader"
                  action="/api/upload/image"
                  :headers="uploadHeaders"
                  :show-file-list="false"
                  :on-success="handleUploadSuccess"
                  :before-upload="beforeUpload"
                  accept="image/*"
                >
                  <el-image v-if="form.image_url" :src="form.image_url" fit="contain" class="image-preview" :preview-src-list="[form.image_url]" />
                  <div v-else class="upload-placeholder">
                    <el-icon size="40"><i class="ep-plus" /></el-icon>
                    <span>点击上传图片</span>
                  </div>
                </el-upload>
                <el-input v-model="form.image_url" placeholder="或直接输入图片URL" class="mt-2" />
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 规格信息 -->
        <el-divider content-position="left">规格信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="货品规格">
              <el-input v-model="form.spec" type="textarea" :rows="3" placeholder="请输入货品规格" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="箱规">
              <el-input v-model="form.box_spec" placeholder="请输入箱规" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 尺码规格 -->
        <el-divider content-position="left">尺码规格</el-divider>
        <div class="size-variants-section">
          <div v-for="(variant, index) in form.size_variants" :key="index" class="size-variant-row">
            <div class="size-variant-content">
              <div class="size-field">
                <span class="field-label">尺码:</span>
                <el-input v-model="variant.size" placeholder="如 S/M/L/XL" style="width: 120px" />
              </div>
              <div class="specs-field">
                <span class="field-label">规格:</span>
                <div class="spec-tags">
                  <el-tag
                    v-for="(spec, sIdx) in variant.specs"
                    :key="sIdx"
                    closable
                    @close="removeSpec(index, sIdx)"
                    class="spec-tag"
                  >
                    {{ spec }}
                  </el-tag>
                  <el-input
                    v-if="variant._adding"
                    v-model="variant._newSpec"
                    size="small"
                    style="width: 80px"
                    @keyup.enter="confirmAddSpec(index)"
                    @blur="confirmAddSpec(index)"
                  />
                  <el-button v-else size="small" @click="startAddSpec(index)">+ 添加</el-button>
                </div>
              </div>
            </div>
            <el-button type="danger" text @click="removeSizeVariant(index)">
              <el-icon><i class="ep-delete" /></el-icon> 删除
            </el-button>
          </div>
          <el-button type="primary" text @click="addSizeVariant">
            <el-icon><i class="ep-plus" /></el-icon> 添加尺码
          </el-button>
        </div>

        <!-- 价格信息 -->
        <el-divider content-position="left">价格信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="单价(¥)">
              <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="样品价(¥)">
              <el-input-number v-model="form.sample_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="运费(¥)">
              <el-input-number v-model="form.shipping_cost" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 其他信息 -->
        <el-divider content-position="left">其他信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供货商">
              <el-select v-model="form.supplier_id" placeholder="请选择供货商" style="width: 100%" clearable>
                <el-option v-for="s in supplierOptions" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入备注" />
        </el-form-item>

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
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import { fetchSuppliers } from '@/api/foreign-trade/suppliers'
import type { FormInstance } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

interface SizeVariantForm {
  size: string
  specs: string[]
  _adding?: boolean
  _newSpec?: string
}

const router = useRouter()
const route = useRoute()
const foreignTradeStore = useForeignTradeStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const supplierOptions = ref<any[]>([])
const formLoaded = ref(false)
const userStore = useUserStore()
const uploadHeaders = { Authorization: `Bearer ${userStore.accessToken}` }

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isImage) { ElMessage.error('只能上传图片文件'); return false }
  if (!isLt10M) { ElMessage.error('图片大小不能超过10MB'); return false }
  return true
}

const handleUploadSuccess = (response: any) => {
  if (response?.url) {
    form.image_url = response.url
    ElMessage.success('图片上传成功')
  }
}

const form = reactive({
  sku: '',
  name: '',
  link_1688: '',
  image_url: '',
  spec: '',
  box_spec: '',
  size_variants: [] as SizeVariantForm[],
  unit_price: 0,
  sample_price: 0,
  shipping_cost: 0,
  description: '',
  status: 'draft',
  supplier_id: null as number | null,
})

const rules = {
  name: [{ required: true, message: '请输入货品名称', trigger: 'blur' }],
}

const addSizeVariant = () => {
  form.size_variants.push({ size: '', specs: [], _adding: false, _newSpec: '' })
}

const removeSizeVariant = (index: number) => {
  form.size_variants.splice(index, 1)
}

const startAddSpec = (index: number) => {
  form.size_variants[index]._adding = true
  form.size_variants[index]._newSpec = ''
}

const confirmAddSpec = (index: number) => {
  const variant = form.size_variants[index]
  const val = (variant._newSpec || '').trim()
  if (val) {
    variant.specs.push(val)
  }
  variant._adding = false
  variant._newSpec = ''
}

const removeSpec = (variantIndex: number, specIndex: number) => {
  form.size_variants[variantIndex].specs.splice(specIndex, 1)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const id = Number(route.params.id)
        const size_variants = form.size_variants
          .filter(v => v.size.trim())
          .map(v => ({ size: v.size, specs: v.specs }))

        const result = await foreignTradeStore.updateProduct(id, {
          sku: form.sku || undefined,
          name: form.name,
          link_1688: form.link_1688 || undefined,
          image_url: form.image_url || undefined,
          spec: form.spec || undefined,
          box_spec: form.box_spec || undefined,
          size_variants: size_variants.length ? size_variants : undefined,
          unit_price: form.unit_price || undefined,
          sample_price: form.sample_price || undefined,
          shipping_cost: form.shipping_cost || undefined,
          description: form.description || undefined,
          status: form.status,
          supplier_id: form.supplier_id || undefined,
        })
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
  if (!id || isNaN(id)) {
    router.replace('/foreign-trade/products/list')
    return
  }
  const product = await foreignTradeStore.loadProductDetail(id)
  if (product) {
    form.sku = product.sku || ''
    form.name = product.name || ''
    form.link_1688 = product.link_1688 || ''
    form.image_url = product.image_url || ''
    form.spec = product.spec || ''
    form.box_spec = product.box_spec || ''
    form.size_variants = (product.size_variants || []).map((v: any) => ({
      size: v.size,
      specs: [...v.specs],
      _adding: false,
      _newSpec: '',
    }))
    form.unit_price = product.unit_price || 0
    form.sample_price = product.sample_price || 0
    form.shipping_cost = product.shipping_cost || 0
    form.description = product.description || ''
    form.status = product.status || 'draft'
    form.supplier_id = product.supplier_id || null
    formLoaded.value = true
  }

  try {
    const res = await fetchSuppliers({ page_size: 100 })
    if (res) supplierOptions.value = res.items || []
  } catch (e) {
    // 加载失败
  }
})
</script>

<style scoped lang="scss">
.edit-product {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-form {
  max-width: 1000px;
}

.image-preview {
  margin-top: 10px;
  max-width: 200px;
  max-height: 200px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.image-upload-area {
  width: 100%;
}

.upload-placeholder {
  width: 200px;
  height: 150px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
  gap: 8px;
  &:hover {
    border-color: #409eff;
    color: #409eff;
  }
}

.size-variants-section {
  margin-bottom: 20px;
  padding-left: 20px;
}

.size-variant-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: #fafafa;
}

.size-variant-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.size-field,
.specs-field {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.spec-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.spec-tag {
  margin: 0;
}
</style>
