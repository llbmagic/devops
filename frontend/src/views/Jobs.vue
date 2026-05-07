<template>
  <div>
    <el-table :data="jobs" stripe v-loading="loading">
      <el-table-column prop="instance_name" label="实例" />
      <el-table-column prop="name" label="Job 名称" />
      <el-table-column prop="last_build_number" label="最后构建号" />
      <el-table-column prop="last_build_status" label="状态">
        <template #default="{ row }">
          <el-tag :type="statusType[row.last_build_status]">{{ row.last_build_status || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="triggerBuild(row)">触发构建</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const jobs = ref([])
const loading = ref(false)
const statusType = { SUCCESS: 'success', FAILURE: 'danger', RUNNING: 'warning', ABORTED: 'info' }

const fetchJobs = async () => {
  loading.value = true
  const { data } = await api.get('/api/cicd/jobs/')
  jobs.value = data
  loading.value = false
}

const triggerBuild = async (row) => {
  await api.post(`/api/cicd/jobs/${row.id}/build/`)
  ElMessage.success('构建已触发')
}

onMounted(fetchJobs)
</script>