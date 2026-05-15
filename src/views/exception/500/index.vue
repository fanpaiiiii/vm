<!-- 500页面 -->
<template>
  <div style="padding: 40px; max-width: 800px; margin: 0 auto;">
    <h1 style="color: #f56c6c;">服务器出错</h1>
    <div v-if="errorMsg" style="background: #fef0f0; border: 1px solid #fbc4c4; padding: 16px; border-radius: 4px; margin: 16px 0; word-break: break-all;">
      <pre style="white-space: pre-wrap; font-size: 13px; color: #606266;">{{ errorMsg }}</pre>
    </div>
    <p v-else style="color: #909399;">{{ $t('exceptionPage.500') }}</p>
    <el-button type="primary" @click="$router.push('/')">回到首页</el-button>
    <el-button @click="$router.push('/auth/login')">重新登录</el-button>
  </div>
</template>

<script setup lang="ts">
  import { useRoute } from 'vue-router'
  defineOptions({ name: 'Exception500' })
  const route = useRoute()
  const errorMsg = route.query.msg as string || ''
</script>
