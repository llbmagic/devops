<!--
  Ansible 剧本管理页面
  @description Ansible 剧本列表页面，用于查看和管理剧本。
-->
<template>
  <div class="playbooks-container">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        添加剧本
      </el-button>
    </div>

    <el-table :data="playbooks" stripe v-loading="loading" class="playbooks-table">
      <el-table-column prop="name" label="剧本名称" />
      <el-table-column prop="playbook_path" label="剧本路径" min-width="200" show-overflow-tooltip />
      <el-table-column prop="created_by_username" label="创建人" width="120" />
      <el-table-column prop="task_count" label="执行次数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="runPlaybook(row)">执行</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * Ansible 剧本数据
 */
interface Playbook {
  id: number
  name: string
  playbook_path: string
  description?: string
  variables?: string
  created_by: number
  created_by_username?: string
  task_count: number
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const playbooks = ref<Playbook[]>([])
const loading = ref(false)

const fetchPlaybooks = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<Playbook[]>('/api/ansible/playbooks/')
    playbooks.value = data
  } catch {
    ElMessage.error('获取剧本列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = (): void => {
  ElMessage.info('添加剧本')
}

const runPlaybook = async (row: Playbook): Promise<void> => {
  try {
    const { data } = await api.post<{ status: string; record_id?: number }>(
      `/api/ansible/playbooks/${row.id}/run/`,
      { target_hosts: 'all' }
    )
    ElMessage.success(`执行${data.status === 'success' ? '成功' : '失败'}，记录ID: ${data.record_id}`)
    fetchPlaybooks()
  } catch {
    ElMessage.error('执行失败')
  }
}

const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除?', '警告', { type: 'warning' })
    await api.delete(`/api/ansible/playbooks/${id}/`)
    ElMessage.success('删除成功')
    fetchPlaybooks()
  } catch {
    // 用户取消或失败
  }
}

onMounted(fetchPlaybooks)
</script>

<style scoped>
.playbooks-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
}
.playbooks-table {
  width: 100%;
}
</style>
