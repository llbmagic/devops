<!--
  告警规则管理页面
  @description 告警规则列表页面，用于查看、创建告警规则和启用/禁用规则。
              告警规则关联 Prometheus 实例，定义告警条件和严重级别。
-->
<template>
  <div class="alert-rules-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        新建规则
      </el-button>
    </div>

    <!-- 告警规则列表 -->
    <el-table
      :data="rules"
      stripe
      v-loading="loading"
      class="rules-table"
    >
      <el-table-column prop="name" label="规则名称" />
      <el-table-column prop="prometheus_name" label="Prometheus" />
      <el-table-column prop="severity" label="级别" width="100">
        <template #default="{ row }">
          <el-tag :type="severityType[row.severity]">
            {{ severityLabel[row.severity] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="expr" label="表达式" show-overflow-tooltip min-width="200" />
      <el-table-column prop="duration" label="持续时间(秒)" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-switch
            v-model="row.enabled"
            @change="toggleRule(row)"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 告警规则数据
 * @description 告警规则模型的所有字段
 */
interface AlertRule {
  id: number
  name: string
  prometheus: number
  prometheus_name?: string
  expr: string
  duration: number
  severity: 'critical' | 'warning' | 'info'
  labels: Record<string, string>
  annotations: Record<string, string>
  enabled: boolean
  created_at: string
}

/** 告警级别映射 */
type AlertSeverity = 'critical' | 'warning' | 'info'

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/** 告警规则列表数据 */
const rules = ref<AlertRule[]>([])

/** 加载状态 */
const loading = ref(false)

/** 级别标签类型映射 */
const severityType: Record<AlertSeverity, string> = {
  critical: 'danger',
  warning: 'warning',
  info: 'info'
}

/** 级别标签文本映射 */
const severityLabel: Record<AlertSeverity, string> = {
  critical: 'Critical',
  warning: 'Warning',
  info: 'Info'
}

/**
 * 获取告警规则列表
 * @description 从后端 API 获取所有告警规则数据
 */
const fetchRules = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<AlertRule[]>('/api/monitor/alert-rules/')
    rules.value = data
  } catch {
    ElMessage.error('获取告警规则列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 切换告警规则启用状态
 * @description 调用后端 API 更新规则的 enabled 状态
 * @param row - 告警规则数据
 */
const toggleRule = async (row: AlertRule): Promise<void> => {
  try {
    await api.patch(`/api/monitor/alert-rules/${row.id}/`, { enabled: row.enabled })
    ElMessage.success('更新成功')
  } catch {
    ElMessage.error('更新失败')
    // 回滚状态
    row.enabled = !row.enabled
  }
}

/**
 * 新建告警规则
 * @description 弹出新建告警规则的表单对话框
 */
const handleCreate = (): void => {
  ElMessage.info('新建规则')
}

/** 组件挂载时获取告警规则列表 */
onMounted(fetchRules)
</script>

<style scoped>
.alert-rules-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.rules-table {
  width: 100%;
}
</style>
