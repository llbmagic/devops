<template>
  <div>
    <h2 style="margin-bottom: 20px">运维平台概览</h2>
    <el-row :gutter="20">
      <el-col :span="6"><el-card>主机数量: {{ stats.hosts }}</el-card></el-col>
      <el-col :span="6"><el-card>活跃告警: {{ stats.alerts }}</el-card></el-col>
      <el-col :span="6"><el-card>构建任务: {{ stats.builds }}</el-card></el-col>
      <el-col :span="6"><el-card>用户数: {{ stats.users }}</el-card></el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref({ hosts: 0, alerts: 0, builds: 0, users: 0 })

onMounted(async () => {
  const [hosts, users] = await Promise.all([
    api.get('/api/cmdb/hosts/').then(r => r.data.count || 0),
    api.get('/api/users/users/').then(r => r.data.length || 0)
  ])
  stats.value = { ...stats.value, hosts, users }
})
</script>