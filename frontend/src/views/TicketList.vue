<!--
  工单列表页面
  @description 工单列表页面，用于查看所有工单。
-->
<template>
  <div class="ticket-list-container">
    <div class="toolbar">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 150px">
        <el-option label="草稿" value="draft" />
        <el-option label="待审批" value="pending" />
        <el-option label="已批准" value="approved" />
        <el-option label="已拒绝" value="rejected" />
        <el-option label="已关闭" value="closed" />
      </el-select>
      <el-button type="primary" @click="handleCreate">创建工单</el-button>
    </div>

    <el-table :data="tickets" stripe v-loading="loading" class="tickets-table">
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="template_name" label="模板" width="150" />
      <el-table-column prop="applicant_name" label="申请人" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="current_step" label="当前步骤" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button v-if="row.status === 'draft'" size="small" @click="submitTicket(row)">提交</el-button>
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

import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const tickets = ref<Ticket[]>([])
const loading = ref(false)
const filterStatus = ref('')

const statusType: Record<string, string> = {
  draft: 'info',
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  closed: 'info'
}

const fetchTickets = async (): Promise<void> => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const { data } = await api.get<Ticket[]>('/api/tickets/', { params })
    tickets.value = data
  } catch {
    ElMessage.error('获取工单列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = (): void => {
  ElMessage.info('创建工单')
}

const viewDetail = (row: Ticket): void => {
  ElMessage.info(`查看工单详情: ${row.title}`)
}

const submitTicket = async (row: Ticket): Promise<void> => {
  try {
    await api.post(`/api/tickets/${row.id}/submit/`)
    ElMessage.success('提交成功')
    fetchTickets()
  } catch {
    ElMessage.error('提交失败')
  }
}

watch(filterStatus, fetchTickets)

onMounted(fetchTickets)
</script>

<style scoped>
.ticket-list-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 10px;
}
.tickets-table {
  width: 100%;
}
</style>
