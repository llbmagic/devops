<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="openForm()">新建主机</el-button>
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px; margin-left: 10px">
        <el-option label="在线" value="online" />
        <el-option label="离线" value="offline" />
        <el-option label="维护中" value="maintenance" />
      </el-select>
    </div>
    <el-table :data="hosts" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="hostname" label="主机名" />
      <el-table-column prop="ip_address" label="IP" />
      <el-table-column prop="business_line_name" label="业务线" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">{{ statusLabel[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="cpu" label="CPU" />
      <el-table-column prop="memory" label="内存" />
      <el-table-column label="标签">
        <template #default="{ row }">
          <el-tag v-for="tag in row.tags_detail" :key="tag.id" size="small" style="margin-right: 4px">
            {{ tag.key }}:{{ tag.value }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="openForm(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const hosts = ref([])
const loading = ref(false)
const filterStatus = ref('')

const statusType = { online: 'success', offline: 'danger', maintenance: 'warning' }
const statusLabel = { online: '在线', offline: '离线', maintenance: '维护中' }

const fetchHosts = async () => {
  loading.value = true
  const params = filterStatus.value ? { status: filterStatus.value } : {}
  const { data } = await api.get('/api/cmdb/hosts/', { params })
  hosts.value = data
  loading.value = false
}

const openForm = (row) => ElMessage.info(row ? `编辑主机 ${row.hostname}` : '新建主机')
const handleDelete = async (id) => {
  await ElMessageBox.confirm('确认删除?', '警告', { type: 'warning' })
  await api.delete(`/api/cmdb/hosts/${id}/`)
  ElMessage.success('删除成功')
  fetchHosts()
}

watch(filterStatus, fetchHosts)
onMounted(fetchHosts)
</script>