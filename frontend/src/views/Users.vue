<template>
  <div>
    <div style="margin-bottom: 20px">
      <el-button type="primary" @click="openDialog()">新建用户</el-button>
    </div>
    <el-table :data="users" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="phone" label="手机" />
      <el-table-column prop="department_name" label="部门" />
      <el-table-column prop="is_active" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const users = ref([])

const fetchUsers = async () => {
  const { data } = await api.get('/api/users/users/')
  users.value = data
}

const openDialog = (row) => {
  // 简化：实际项目使用 el-dialog
  ElMessage.info(row ? `编辑用户 ${row.username}` : '新建用户')
}

const handleDelete = async (id) => {
  await ElMessageBox.confirm('确认删除?', '警告', { type: 'warning' })
  await api.delete(`/api/users/users/${id}/`)
  ElMessage.success('删除成功')
  fetchUsers()
}

onMounted(fetchUsers)
</script>