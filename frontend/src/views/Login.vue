<!--
  登录页面
  @description 用户登录入口页面，提供用户名密码认证功能。
              登录成功后存储 JWT Token 并跳转到控制台。
-->
<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">DevOps 登录</h2>
      <el-form
        :model="form"
        @submit.prevent="handleLogin"
        label-position="top"
      >
        <el-form-item label="用户名">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            native-type="submit"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 登录表单数据
 * @description 包含用户名和密码
 */
interface LoginForm {
  username: string
  password: string
}

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()

/** 登录表单数据 */
const form = ref<LoginForm>({ username: '', password: '' })

/** 登录按钮加载状态 */
const loading = ref(false)

/**
 * 处理登录提交
 * @description 验证表单后调用登录 API，成功后存储 Token 并跳转
 */
const handleLogin = async (): Promise<void> => {
  // 表单验证
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    // 调用登录 API（注意：路径是 /api/users/login/，不是 /api/auth/login/）
    const { data } = await api.post('/api/users/login/', form.value)
    // 存储 JWT Token
    localStorage.setItem('token', data.access)
    localStorage.setItem('username', form.value.username)
    ElMessage.success('登录成功')
    // 跳转到控制台
    router.push('/dashboard')
  } catch {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #2b3a4d;
}

.login-card {
  width: 400px;
}

.login-title {
  text-align: center;
  margin-bottom: 20px;
  color: #303133;
}
</style>
