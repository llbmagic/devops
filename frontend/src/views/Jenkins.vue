<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="ElMessage.info('添加 Jenkins 实例')">添加实例</el-button>
      <el-button @click="syncAll">同步 Jobs</el-button>
    </div>
    <el-table :data="instances" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="url" label="URL" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column label="状态">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="syncJobs(row)">同步</el-button>
          <el-button size="small" @click="ElMessage.info('编辑')">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const instances = ref([])

const fetchInstances = async () => {
  const { data } = await api.get('/api/cicd/jenkins-instances/')
  instances.value = data
}

const syncJobs = async (row) => {
  await api.post(`/api/cicd/jenkins-instances/${row.id}/sync_jobs/`)
  ElMessage.success('同步成功')
}

const syncAll = async () => {
  for (const inst of instances.value) {
    await api.post(`/api/cicd/jenkins-instances/${inst.id}/sync_jobs/`)
  }
  ElMessage.success('全部同步完成')
}

onMounted(fetchInstances)
</script>