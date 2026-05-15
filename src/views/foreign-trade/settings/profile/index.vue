<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左侧：头像卡片 -->
      <el-col :span="8">
        <el-card shadow="never">
          <div class="avatar-section">
            <el-avatar :size="120" :src="form.avatar || defaultAvatar" />
            <el-upload
              class="avatar-upload"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
              accept="image/jpeg,image/png,image/gif,image/webp"
            >
              <el-button type="primary" link class="mt-3">更换头像</el-button>
            </el-upload>
            <h3 class="mt-3">{{ form.username }}</h3>
            <el-tag :type="form.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ form.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：信息表单 -->
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <span>个人信息</span>
          </template>
          <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="form.username" disabled />
            </el-form-item>
            <el-form-item label="姓名" prop="full_name">
              <el-input v-model="form.full_name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveInfo" :loading="saving">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="mt-4">
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="100px">
            <el-form-item label="新密码" prop="password">
              <el-input v-model="pwdForm.password" type="password" placeholder="请输入新密码" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="pwdForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="changingPwd">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted } from 'vue'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, UploadRequestOptions } from 'element-plus'
  import { useUserStore } from '@/store/modules/user'
  import request from '@/utils/http'
  import defaultAvatar from '@/assets/images/user/avatar.webp'

  defineOptions({ name: 'Profile' })

  const userStore = useUserStore()
  const formRef = ref<FormInstance>()
  const pwdFormRef = ref<FormInstance>()
  const saving = ref(false)
  const changingPwd = ref(false)

  const form = reactive({
    username: '',
    full_name: '',
    email: '',
    avatar: '',
    role: '',
  })

  const pwdForm = reactive({
    password: '',
    confirmPassword: '',
  })

  const rules = {
    email: [{ type: 'email' as const, message: '请输入正确的邮箱格式', trigger: 'blur' }],
  }

  const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
    if (!value) {
      callback(new Error('请再次输入密码'))
    } else if (value !== pwdForm.password) {
      callback(new Error('两次密码不一致'))
    } else {
      callback()
    }
  }

  const pwdRules = {
    password: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, message: '密码至少6个字符', trigger: 'blur' },
    ],
    confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
  }

  // 加载用户信息
  const loadProfile = async () => {
    try {
      const res = await request.get<any>({ url: '/api/auth/me' })
      if (res) {
        form.username = res.username || ''
        form.full_name = res.full_name || ''
        form.email = res.email || ''
        form.avatar = res.avatar || ''
        form.role = res.role || 'user'
      }
    } catch (e) {
      ElMessage.error('加载个人信息失败')
    }
  }

  // 头像上传前验证
  const beforeAvatarUpload = (file: File) => {
    const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
    const isLt5M = file.size / 1024 / 1024 < 5
    if (!isImage) {
      ElMessage.error('只能上传 JPG/PNG/GIF/WebP 格式图片')
      return false
    }
    if (!isLt5M) {
      ElMessage.error('图片大小不能超过 5MB')
      return false
    }
    return true
  }

  // 上传头像
  const handleAvatarUpload = async (options: UploadRequestOptions) => {
    const formData = new FormData()
    formData.append('file', options.file)
    try {
      const res = await request.post<any>({
        url: '/api/upload/image',
        data: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      if (res && res.url) {
        // 更新头像
        const avatarUrl = res.url
        await request.put<any>({ url: '/api/auth/me', data: { avatar: avatarUrl } })
        form.avatar = avatarUrl
        // 同步到 store
        const userInfo = userStore.getUserInfo
        if (userInfo) {
          userStore.setUserInfo({ ...userInfo, avatar: avatarUrl } as Api.Auth.UserInfo)
        }
        ElMessage.success('头像更新成功')
      }
    } catch (e) {
      ElMessage.error('头像上传失败')
    }
  }

  // 保存个人信息
  const handleSaveInfo = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
      if (!valid) return
      saving.value = true
      try {
        await request.put<any>({
          url: '/api/auth/me',
          data: {
            full_name: form.full_name,
            email: form.email || '',
          },
        })
        // 同步到 store
        const userInfo = userStore.getUserInfo
        if (userInfo) {
          userStore.setUserInfo({
            ...userInfo,
            nickName: form.full_name,
            email: form.email,
          } as Api.Auth.UserInfo)
        }
        ElMessage.success('个人信息已更新')
      } catch (e) {
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    })
  }

  // 修改密码
  const handleChangePassword = async () => {
    if (!pwdFormRef.value) return
    await pwdFormRef.value.validate(async (valid) => {
      if (!valid) return
      changingPwd.value = true
      try {
        await request.put<any>({
          url: '/api/auth/me',
          data: { password: pwdForm.password },
        })
        ElMessage.success('密码修改成功')
        pwdForm.password = ''
        pwdForm.confirmPassword = ''
      } catch (e) {
        ElMessage.error('密码修改失败')
      } finally {
        changingPwd.value = false
      }
    })
  }

  onMounted(() => {
    loadProfile()
  })
</script>

<style scoped lang="scss">
  .profile-page {
    padding: 20px;
  }
  .avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
  }
  .mt-3 {
    margin-top: 12px;
  }
  .mt-4 {
    margin-top: 16px;
  }
</style>
