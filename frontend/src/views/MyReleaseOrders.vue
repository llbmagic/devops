<!--
  我的待审批发布单页面
  @description 我的待审批发布单列表页面，用于查看需要我审批的发布单。
-->
<template>
  <div class="my-release-orders-container">
    <el-table :data="orders" stripe v-loading="loading" class="orders-table">
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="jenkins_job_name" label="Jenkins Job" width="180" />
      <el-table-column prop="applicant_name" label="申请人" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag type="warning">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
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
/** 发布单数据 */
interface ReleaseOrder {
  id: number
  title: string
  jenkins_job_name: string
  applicant_name: string
  status: string
  status_display: string
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const orders = ref<ReleaseOrder[]>([])
const loading = ref(false)

const fetchOrders = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<ReleaseOrder[]>('/api/cicd/release-orders/my_orders/')
    orders.value = data
  } catch {
    ElMessage.error('获取待审批发布单失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (row: ReleaseOrder): void => {
  ElMessage.info(`查看发布单详情: ${row.title}`)
}

const approve = async (row: ReleaseOrder): Promise<void> => {
  try {
    await api.post(`/api/cicd/release-orders/${row.id}/approve/`, { comment: '同意' })
    ElMessage.success('已批准')
    fetchOrders()
  } catch {
    ElMessage.error('批准失败')
  }
}

const reject = async (row: ReleaseOrder): Promise<void> => {
  try {
    await api.post(`/api/cicd/release-orders/${row.id}/reject/`, { comment: '不同意' })
    ElMessage.success('已拒绝')
    fetchOrders()
  } catch {
    ElMessage.error('拒绝失败')
  }
}

onMounted(fetchOrders)
</script>

<style scoped>
.my-release-orders-container {
  padding: 20px;
}
.orders-table {
  width: 100%;
}
</style>