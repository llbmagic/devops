<!--
  我的待审批工单页面
  @description 我的待审批工单列表页面，用于查看需要我审批的工单。
-->
<template>
  <div class="my-tickets-container">
    <el-table :data="tickets" stripe v-loading="loading" class="tickets-table">
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="template_name" label="模板" width="150" />
      <el-table-column prop="applicant_name" label="申请人" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag type="warning">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="current_step" label="当前步骤" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button size="small" type="success" @click="approve(row)">批准</el-button>
          <el-button size="small" type="danger" @click="reject(row)">拒绝</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 工单数据
 */
interface Ticket {
  id: number
  title: string
  template: number
  template_name?: string
  applicant: number
  applicant_name?: string
  description: string
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'closed'
  status_display?: string
  current_step: number
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const tickets = ref<Ticket[]>([])
const loading = ref(false)

const fetchTickets = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<Ticket[]>('/api/tickets/my_tickets/')
    tickets.value = data
  } catch {
    ElMessage.error('获取待审批工单失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (row: Ticket): void => {
  ElMessage.info(`查看工单详情: ${row.title}`)
}

const approve = async (row: Ticket): Promise<void> => {
  try {
    await api.post(`/api/tickets/${row.id}/approve/`, { comment: '同意' })
    ElMessage.success('已批准')
    fetchTickets()
  } catch {
    ElMessage.error('批准失败')
  }
}

const reject = async (row: Ticket): Promise<void> => {
  try {
    await api.post(`/api/tickets/${row.id}/reject/`, { comment: '不同意' })
    ElMessage.success('已拒绝')
    fetchTickets()
  } catch {
    ElMessage.error('拒绝失败')
  }
}

onMounted(fetchTickets)
</script>

<style scoped>
.my-tickets-container {
  padding: 20px;
}
.tickets-table {
  width: 100%;
}
</style>
