<template>
  <div>
    <div style="margin-bottom: 20px">
      <el-button type="primary" @click="ElMessage.info('新建角色')">新建角色</el-button>
    </div>
    <el-table :data="roles" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="角色名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="权限数量">
        <template #default="{ row }">{{ row.permissions?.length || 0 }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const roles = ref([])

onMounted(async () => {
  const { data } = await api.get('/api/users/roles/')
  roles.value = data
})
</script>