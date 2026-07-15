<!--
  告警记录页面
  @description 告警记录列表页面，用于查看所有告警事件并确认告警。
              告警关联 Prometheus 实例和告警规则，包含触发、恢复、确认三种状态。
-->
<template>
  <div class="alerts-container">
    <!-- 状态筛选栏 -->
    <div class="toolbar">
      <el-select
        v-model="filterStatus"
        placeholder="状态筛选"
        clearable
        style="width: 150px"
      >
        <el-option label="触发中" value="firing" />
        <el-option label="已恢复" value="resolved" />
        <el-option label="已确认" value="acknowledged" />
      </el-select>
    </div>

    <!-- 告警记录列表 -->
    <el-table
      :data="alerts"
      stripe
      v-loading="loading"
      class="alerts-table"
    >
      <el-table-column prop="alert_name" label="告警名称" />
      <el-table-column prop="rule_name" label="规则" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">
            {{ statusLabel[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="starts_at" label="开始时间" width="180" />
      <el-table-column prop="acknowledged_by" label="确认人" width="120" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'firing'"
            size="small"
            @click="acknowledge(row)"
          >
            确认
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 告警记录数据
 * @description 告警记录模型的所有字段
 */
interface AlertRecord {
  id: number
  alert_name: string
  rule: number
  rule_name?: string
  status: AlertStatus
  severity: 'critical' | 'warning' | 'info'
  starts_at: string
  ends_at?: string
  acknowledged_by?: string
  acknowledged_at?: string
  labels: Record<string, string>
  annotations: Record<string, string>
}

/** 告警状态映射 */
type AlertStatus = 'firing' | 'resolved' | 'acknowledged'

import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/** 告警记录列表数据 */
const alerts = ref<AlertRecord[]>([])

/** 加载状态 */
const loading = ref(false)

/** 状态筛选值 */
const filterStatus = ref('')

/** 状态标签类型映射 */
const statusType: Record<AlertStatus, string> = {
  firing: 'danger',
  resolved: 'success',
  acknowledged: 'warning'
}

/** 状态标签文本映射 */
const statusLabel: Record<AlertStatus, string> = {
  firing: '触发中',
  resolved: '已恢复',
  acknowledged: '已确认'
}

/**
 * 获取告警记录列表
 * @description 从后端 API 获取所有告警记录数据，支持按状态筛选
 */
const fetchAlerts = async (): Promise<void> => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const { data } = await api.get<AlertRecord[]>('/api/monitor/alerts/', { params })
    alerts.value = data
  } catch {
    ElMessage.error('获取告警记录列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 确认告警
 * @description 调用后端 API 确认指定告警记录
 * @param row - 告警记录数据
 */
const acknowledge = async (row: AlertRecord): Promise<void> => {
  try {
    await api.patch(`/api/monitor/alerts/${row.id}/acknowledge/`)
    ElMessage.success('已确认')
    fetchAlerts()
  } catch {
    ElMessage.error('确认告警失败')
  }
}

/** 监听状态筛选变化，重新获取列表 */
watch(filterStatus, fetchAlerts)

/** 组件挂载时获取告警记录列表 */
onMounted(fetchAlerts)
</script>

<style scoped>
.alerts-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.alerts-table {
  width: 100%;
}
</style>
