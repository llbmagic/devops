<template>
  <div>
    <el-table :data="builds" stripe>
      <el-table-column prop="job_name" label="Job" />
      <el-table-column prop="build_number" label="构建号" width="80" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">{{ statusLabel[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="executor" label="执行人" />
      <el-table-column prop="started_at" label="开始时间" />
      <el-table-column prop="duration" label="耗时(秒)">
        <template #default="{ row }">{{ row.duration || '-' }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const builds = ref([])
const statusType = { pending: 'info', running: 'warning', success: 'success', failure: 'danger', aborted: 'info' }
const statusLabel = { pending: '排队中', running: '运行中', success: '成功', failure: '失败', aborted: '中止' }

onMounted(async () => {
  const { data } = await api.get('/api/cicd/builds/')
  builds.value = data
})
</script>