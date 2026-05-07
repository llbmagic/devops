<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 150px">
        <el-option label="触发中" value="firing" />
        <el-option label="已恢复" value="resolved" />
        <el-option label="已确认" value="acknowledged" />
      </el-select>
    </div>
    <el-table :data="alerts" stripe v-loading="loading">
      <el-table-column prop="alert_name" label="告警名称" />
      <el-table-column prop="rule_name" label="规则" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">{{ statusLabel[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="starts_at" label="开始时间" />
      <el-table-column prop="acknowledged_by" label="确认人" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button v-if="row.status === 'firing'" size="small" @click="acknowledge(row)">确认</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const alerts = ref([])
const loading = ref(false)
const filterStatus = ref('')
const statusType = { firing: 'danger', resolved: 'success', acknowledged: 'warning' }
const statusLabel = { firing: '触发中', resolved: '已恢复', acknowledged: '已确认' }

const fetchAlerts = async () => {
  loading.value = true
  const params = filterStatus.value ? { status: filterStatus.value } : {}
  const { data } = await api.get('/api/monitor/alerts/', { params })
  alerts.value = data
  loading.value = false
}

const acknowledge = async (row) => {
  await api.patch(`/api/monitor/alerts/${row.id}/acknowledge/`)
  ElMessage.success('已确认')
  fetchAlerts()
}

watch(filterStatus, fetchAlerts)
onMounted(fetchAlerts)
</script>
