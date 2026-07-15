<!--
  角色管理页面
  @description 角色列表页面，用于查看和创建角色。
              展示角色名称、描述和关联的权限数量。
-->
<template>
  <div class="roles-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        新建角色
      </el-button>
    </div>

    <!-- 角色列表 -->
    <el-table
      :data="roles"
      stripe
      v-loading="loading"
      class="roles-table"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="角色名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="权限数量" width="100">
        <template #default="{ row }">
          {{ row.permissions?.length || 0 }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 角色数据
 * @description 角色模型的所有字段
 */
interface Role {
  id: number
  name: string
  description?: string
  permissions?: Array<{ id: number; name: string }>
}

/**
 * 权限数据
 * @description 权限模型的所有字段
 */
interface Permission {
  id: number
  name: string
  codename: string
  module: string
}

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/** 角色列表数据 */
const roles = ref<Role[]>([])

/** 加载状态 */
const loading = ref(false)

/**
 * 获取角色列表
 * @description 从后端 API 获取所有角色数据
 */
const fetchRoles = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<Role[]>('/api/users/roles/')
    roles.value = data
  } catch {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 新建角色
 * @description 弹出新建角色的表单对话框
 */
const handleCreate = (): void => {
  ElMessage.info('新建角色')
}

/** 组件挂载时获取角色列表 */
onMounted(fetchRoles)
</script>

<style scoped>
.roles-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
}

.roles-table {
  width: 100%;
}
</style>
