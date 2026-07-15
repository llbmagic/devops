<!--
  Ansible 控制节点管理页面
  @description Ansible 控制节点列表页面，用于查看和管理 Ansible 控制节点。
-->
<template>
  <div class="ansible-servers-container">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        添加节点
      </el-button>
    </div>

    <el-table :data="servers" stripe v-loading="loading" class="servers-table">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="host" label="主机地址" />
      <el-table-column prop="ssh_port" label="SSH 端口" width="100" />
      <el-table-column prop="ssh_user" label="SSH 用户" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="testConnection(row)">测试</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * Ansible 控制节点数据
 */
interface AnsibleServer {
  id: number
  name: string
  host: string
  ssh_port: number
  ssh_user: string
  ssh_password?: string
  private_key_path?: string
  description?: string
  is_active: boolean
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const servers = ref<AnsibleServer[]>([])
const loading = ref(false)

const fetchServers = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<AnsibleServer[]>('/api/ansible/servers/')
    servers.value = data
  } catch {
    ElMessage.error('获取节点列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = (): void => {
  ElMessage.info('添加 Ansible 控制节点')
}

const testConnection = async (row: AnsibleServer): Promise<void> => {
  try {
    await api.post(`/api/ansible/servers/${row.id}/test_connection/`)
    ElMessage.success('连接成功')
  } catch {
    ElMessage.error('连接失败')
  }
}

const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除?', '警告', { type: 'warning' })
    await api.delete(`/api/ansible/servers/${id}/`)
    ElMessage.success('删除成功')
    fetchServers()
  } catch {
    // 用户取消或失败
  }
}

onMounted(fetchServers)
</script>

<style scoped>
.ansible-servers-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
}
.servers-table {
  width: 100%;
}
</style>
