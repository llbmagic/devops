<!--
  GitLab 实例管理页面
  @description GitLab 实例列表页面，用于查看、添加和同步 GitLab 实例。
-->
<template>
  <div class="gitlab-instances-container">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        添加实例
      </el-button>
      <el-button @click="syncAll">
        同步全部
      </el-button>
    </div>

    <el-table :data="instances" stripe v-loading="loading" class="instances-table">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="url" label="URL" min-width="200" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="syncProjects(row)">同步</el-button>
          <el-button size="small" @click="testConnection(row)">测试</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * GitLab 实例数据
 */
interface GitLabInstance {
  id: number
  name: string
  url: string
  access_token?: string
  is_active: boolean
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const instances = ref<GitLabInstance[]>([])
const loading = ref(false)

const fetchInstances = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<GitLabInstance[]>('/api/gitlab/instances/')
    instances.value = data
  } catch {
    ElMessage.error('获取实例列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = (): void => {
  ElMessage.info('添加 GitLab 实例')
}

const syncProjects = async (row: GitLabInstance): Promise<void> => {
  try {
    await api.post(`/api/gitlab/instances/${row.id}/sync_projects/`)
    ElMessage.success('同步成功')
  } catch {
    ElMessage.error('同步失败')
  }
}

const testConnection = async (row: GitLabInstance): Promise<void> => {
  try {
    const { data } = await api.post<{ status: string; user?: string }>(
      `/api/gitlab/instances/${row.id}/test_connection/`
    )
    ElMessage.success(`连接成功，用户: ${data.user}`)
  } catch {
    ElMessage.error('连接失败')
  }
}

const syncAll = async (): Promise<void> => {
  try {
    for (const inst of instances.value) {
      await api.post(`/api/gitlab/instances/${inst.id}/sync_projects/`)
    }
    ElMessage.success('全部同步完成')
  } catch {
    ElMessage.error('同步失败')
  }
}

const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除?', '警告', { type: 'warning' })
    await api.delete(`/api/gitlab/instances/${id}/`)
    ElMessage.success('删除成功')
    fetchInstances()
  } catch {
    // 用户取消或失败
  }
}

onMounted(fetchInstances)
</script>

<style scoped>
.gitlab-instances-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
}
.instances-table {
  width: 100%;
}
</style>
