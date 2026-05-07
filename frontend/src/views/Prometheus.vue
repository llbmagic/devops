<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="ElMessage.info('添加 Prometheus 实例')">添加实例</el-button>
    </div>
    <el-table :data="instances" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="url" label="URL" />
      <el-table-column label="状态">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const instances = ref([])

onMounted(async () => {
  const { data } = await api.get('/api/monitor/prometheus-instances/')
  instances.value = data
})
</script>
