<!--
  用户管理页面
  @description 用户列表页面，用于查看、新建、编辑和删除用户。
              展示用户基本信息、部门、状态等。
-->
<template>
  <div class="users-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">
        新建用户
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-table
      :data="users"
      stripe
      v-loading="loading"
      class="users-table"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="phone" label="手机" />
      <el-table-column prop="department_name" label="部门" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">
            编辑
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 用户数据
 * @description 用户模型的所有字段
 */
interface User {
  id: number
  username: string
  email: string
  phone?: string
  department?: number
  department_name?: string
  is_active: boolean
  date_joined: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

/** 用户列表数据 */
const users = ref<User[]>([])

/** 加载状态 */
const loading = ref(false)

/**
 * 获取用户列表
 * @description 从后端 API 获取用户数据
 */
const fetchUsers = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<User[]>('/api/users/users/')
    users.value = data
  } catch {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 打开用户表单
 * @description 弹出新建或编辑用户的表单对话框
 * @param row - 用户数据，传入时为编辑模式，不传时为新建模式
 */
const openDialog = (row?: User): void => {
  if (row) {
    ElMessage.info(`编辑用户 ${row.username}`)
  } else {
    ElMessage.info('新建用户')
  }
}

/**
 * 删除用户
 * @description 确认后删除指定用户，刷新列表
 * @param id - 用户 ID
 */
const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除该用户?', '警告', { type: 'warning' })
    await api.delete(`/api/users/users/${id}/`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch {
    // 用户取消或删除失败
  }
}

/** 组件挂载时获取用户列表 */
onMounted(fetchUsers)
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
}

.users-table {
  width: 100%;
}
</style>
