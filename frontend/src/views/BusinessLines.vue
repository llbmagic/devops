<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="ElMessage.info('新建业务线')">新建业务线</el-button>
    </div>
    <el-table :data="businessLines" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="业务线名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="host_count" label="主机数量" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const businessLines = ref([])

onMounted(async () => {
  const { data } = await api.get('/api/cmdb/business-lines/')
  businessLines.value = data
})
</script>