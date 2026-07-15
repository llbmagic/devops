<!--
  Ansible 执行记录页面
  @description Ansible 任务执行记录列表页面，用于查看历史执行记录。
-->
<template>
  <div class="ansible-records-container">
    <div class="toolbar">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 150px">
        <el-option label="等待中" value="pending" />
        <el-option label="执行中" value="running" />
        <el-option label="成功" value="success" />
        <el-option label="失败" value="failed" />
      </el-select>
    </div>

    <el-table :data="records" stripe v-loading="loading" class="records-table">
      <el-table-column prop="playbook_name" label="剧本" />
      <el-table-column prop="server_name" label="控制节点" width="150" />
      <el-table-column prop="target_hosts" label="目标主机" width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">{{ statusLabel[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="executor" label="执行人" width="120" />
      <el-table-column prop="duration" label="耗时(秒)" width="100">
        <template #default="{ row }">
          {{ row.duration ? row.duration.toFixed(1) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="180" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * Ansible 执行记录数据
 */
interface TaskRecord {
  id: number
  playbook: number
  playbook_name?: string
  server: number
  server_name?: string
  target_hosts: string
  variables?: string
  status: 'pending' | 'running' | 'success' | 'failed'
  executor: string
  output?: string
  error?: string
  started_at: string
  finished_at?: string
  duration?: number
}

import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const records = ref<TaskRecord[]>([])
const loading = ref(false)
const filterStatus = ref('')

const statusType: Record<string, string> = {
  pending: 'info',
  running: 'warning',
  success: 'success',
  failed: 'danger'
}

const statusLabel: Record<string, string> = {
  pending: '等待中',
  running: '执行中',
  success: '成功',
  failed: '失败'
}

const fetchRecords = async (): Promise<void> => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const { data } = await api.get<TaskRecord[]>('/api/ansible/records/', { params })
    records.value = data
  } catch {
    ElMessage.error('获取执行记录失败')
  } finally {
    loading.value = false
  }
}

watch(filterStatus, fetchRecords)

onMounted(fetchRecords)
</script>

<style scoped>
.ansible-records-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
}
.records-table {
  width: 100%;
}
</style>
