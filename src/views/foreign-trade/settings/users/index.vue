<template>
  <div class="settings-users">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><i class="ep-plus" /></el-icon>
            添加用户
          </el-button>
        </div>
      </template>
      <el-alert title="用户管理功能说明" type="info" description="在此管理外贸团队的用户账号，包括添加、编辑和权限分配。" show-icon :closable="false" class="mb-4" />
      <el-table :data="users" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '活跃' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button :type="row.is_active ? 'warning' : 'success'" link @click="handleToggleStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-popconfirm title="确定删除该用户吗？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '添加用户'" width="500px">
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" v-if="isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="留空则不修改密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="userForm.is_active" active-text="活跃" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitUser" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/http'
import { createUser, updateUser, toggleUserStatus, deleteUser } from '@/api/foreign-trade/users'
import type { FormInstance } from 'element-plus'
import type { UserInfo } from '@/api/foreign-trade/types'

const loading = ref(false)
const users = ref<UserInfo[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const editingUserId = ref<number | null>(null)
const userFormRef = ref<FormInstance>()

const userForm = reactive({
  username: '',
  full_name: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true,
})

const userRules = computed(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email' as const, message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: isEdit.value ? [] : [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}))

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await request.get<any>({ url: '/api/auth/users', showErrorMessage: false }).catch(() => null)
    if (res) {
      users.value = Array.isArray(res) ? res : (res.items || [])
    }
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  userForm.username = ''
  userForm.full_name = ''
  userForm.email = ''
  userForm.password = ''
  userForm.role = 'user'
  userForm.is_active = true
  editingUserId.value = null
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row: UserInfo) => {
  isEdit.value = true
  editingUserId.value = row.id
  userForm.username = row.username
  userForm.full_name = row.full_name || ''
  userForm.email = row.email
  userForm.password = ''
  userForm.role = row.role || 'user'
  userForm.is_active = row.is_active
  dialogVisible.value = true
}

const handleSubmitUser = async () => {
  if (!userFormRef.value) return
  const valid = await userFormRef.value.validate().catch(() => false)
  if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value && editingUserId.value) {
        const updateData: any = {
          full_name: userForm.full_name,
          email: userForm.email,
          role: userForm.role,
          is_active: userForm.is_active,
        }
        if (userForm.password) {
          updateData.password = userForm.password
        }
        await updateUser(editingUserId.value, updateData)
        ElMessage.success('用户更新成功')
      } else {
        await createUser({
          username: userForm.username,
          password: userForm.password,
          email: userForm.email,
          full_name: userForm.full_name,
          role: userForm.role,
          is_active: userForm.is_active,
        })
      ElMessage.success('用户创建成功')
    }
    dialogVisible.value = false
    loadUsers()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
}
const handleToggleStatus = async (row: UserInfo) => {
  try {
    await toggleUserStatus(row.id, !row.is_active)
    ElMessage.success(`用户已${row.is_active ? '禁用' : '启用'}`)
    loadUsers()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row: UserInfo) => {
  try {
    await deleteUser(row.id)
    ElMessage.success('用户已删除')
    loadUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped lang="scss">
.settings-users { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.mb-4 { margin-bottom: 16px; }
</style>
