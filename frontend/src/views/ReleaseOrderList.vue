<!--
  发布单列表页面
  @description 发布单列表页面，用于查看、筛选、创建发布单。
-->
<template>
  <div class="release-order-list-container">
    <div class="toolbar">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 150px">
        <el-option label="草稿" value="draft" />
        <el-option label="待审批" value="pending" />
        <el-option label="已批准" value="approved" />
        <el-option label="执行中" value="executing" />
        <el-option label="执行成功" value="success" />
        <el-option label="执行失败" value="failed" />
      </el-select>
      <el-button type="primary" @click="$router.push('/cicd/release-orders/create')">
        创建发布单
      </el-button>
    </div>

    <el-table :data="orders" stripe v-loading="loading" class="orders-table">
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="jenkins_job_name" label="Jenkins Job" width="180" />
      <el-table-column prop="applicant_name" label="申请人" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行模式" width="100">
        <template #default="{ row }">
          {{ row.execute_mode === 'manual' ? '手动' : '定时' }}
        </template>
      </el-table-column>
      <el-table-column prop="scheduled_time" label="定时时间" width="180" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button v-if="row.status === 'draft'" size="small" @click="submitOrder(row)">提交</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/** 发布单数据 */
interface ReleaseOrder {
  id: number
  title: string
  jenkins_job: number
  jenkins_job_name: string
  applicant_name: string
  status: string
  status_display: string
  execute_mode: string
  scheduled_time?: string
  created_at: string
}

import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const orders = ref<ReleaseOrder[]>([])
const loading = ref(false)
const filterStatus = ref('')

const statusType: Record<string, string> = {
  draft: 'info',
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  executing: 'warning',
  success: 'success',
  failed: 'danger',
  closed: 'info'
}

const fetchOrders = async (): Promise<void> => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const { data } = await api.get<ReleaseOrder[]>('/api/cicd/release-orders/', { params })
    orders.value = data
  } catch {
    ElMessage.error('获取发布单列表失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (row: ReleaseOrder): void => {
  ElMessage.info(`查看发布单详情: ${row.title}`)
}

const submitOrder = async (row: ReleaseOrder): Promise<void> => {
  try {
    await api.post(`/api/cicd/release-orders/${row.id}/submit/`)
    ElMessage.success('提交成功')
    fetchOrders()
  } catch {
    ElMessage.error('提交失败')
  }
}

watch(filterStatus, fetchOrders)

onMounted(fetchOrders)
</script>

<style scoped>
.release-order-list-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 10px;
}
.orders-table {
  width: 100%;
}
</style>