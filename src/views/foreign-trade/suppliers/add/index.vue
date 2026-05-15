<template>
  <div class="add-supplier">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>添加供货商</span>
          <el-button @click="handleBack">返回列表</el-button>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="supplier-form">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供货商名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入供货商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="form.contact_person" placeholder="请输入联系人姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电话">
              <el-input v-model="form.phone" placeholder="请输入电话号码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="微信号">
              <el-input v-model="form.wechat" placeholder="请输入微信号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评级">
              <el-rate v-model="form.rating" show-score allow-half />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">地址信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="国家">
              <el-input v-model="form.country" placeholder="如: 中国" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="省份">
              <el-input v-model="form.province" placeholder="如: 广东省" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="城市">
              <el-input v-model="form.city" placeholder="如: 深圳市" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="详细地址">
          <el-input v-model="form.address" placeholder="请输入详细地址" />
        </el-form-item>

        <el-divider content-position="left">在线信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="网站">
              <el-input v-model="form.website" placeholder="请输入公司网站" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="阿里巴巴店铺">
              <el-input v-model="form.alibaba_store" placeholder="请输入阿里巴巴店铺链接" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useForeignTradeStore } from '@/store/modules/foreign-trade'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const foreignTradeStore = useForeignTradeStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  wechat: '',
  address: '',
  city: '',
  province: '',
  country: '',
  website: '',
  alibaba_store: '',
  rating: 0,
  notes: '',
})

const rules = {
  name: [{ required: true, message: '请输入供货商名称', trigger: 'blur' }],
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const result = await foreignTradeStore.createSupplier({ ...form })
        if (result) {
          ElMessage.success('供货商创建成功')
          router.push('/foreign-trade/suppliers/list')
        }
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleReset = () => formRef.value?.resetFields()
const handleBack = () => router.push('/foreign-trade/suppliers/list')
</script>

<style scoped lang="scss">
.add-supplier { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.supplier-form { max-width: 1000px; }
</style>
