<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="ElMessage.info('新建规则')">新建规则</el-button>
    </div>
    <el-table :data="rules" stripe>
      <el-table-column prop="name" label="规则名称" />
      <el-table-column prop="prometheus_name" label="Prometheus" />
      <el-table-column prop="severity" label="级别">
        <template #default="{ row }">
          <el-tag :type="severityType[row.severity]">{{ severityLabel[row.severity] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="expr" label="表达式" show-overflow-tooltip />
      <el-table-column label="状态">
        <template #default="{ row }">
          <el-switch v-model="row.enabled" @change="toggleRule(row)" />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const rules = ref([])
const severityType = { critical: 'danger', warning: 'warning', info: 'info' }
const severityLabel = { critical: 'Critical', warning: 'Warning', info: 'Info' }

const fetchRules = async () => {
  const { data } = await api.get('/api/monitor/alert-rules/')
  rules.value = data
}

const toggleRule = async (row) => {
  await api.patch(`/api/monitor/alert-rules/${row.id}/`, { enabled: row.enabled })
  ElMessage.success('更新成功')
}

onMounted(fetchRules)
</script>
