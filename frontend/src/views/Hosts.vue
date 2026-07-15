<!--
  主机管理页面
  @description 主机列表页面，用于查看、筛选、创建、编辑和删除主机记录。
              支持按状态筛选主机，查看主机详情、所属业务线和标签信息。
-->
<template>
  <div class="hosts-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="openForm()">
        新建主机
      </el-button>
      <el-select
        v-model="filterStatus"
        placeholder="状态筛选"
        clearable
        style="width: 120px; margin-left: 10px"
      >
        <el-option label="在线" value="online" />
        <el-option label="离线" value="offline" />
        <el-option label="维护中" value="maintenance" />
      </el-select>
    </div>

    <!-- 主机列表 -->
    <el-table
      :data="hosts"
      stripe
      v-loading="loading"
      class="hosts-table"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="hostname" label="主机名" />
      <el-table-column prop="ip_address" label="IP" />
      <el-table-column prop="business_line_name" label="业务线" />
      <el-table-column prop="cluster_name" label="集群" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">
            {{ statusLabel[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="cpu" label="CPU" width="80" />
      <el-table-column prop="memory" label="内存" width="80" />
      <el-table-column label="标签" min-width="150">
        <template #default="{ row }">
          <el-tag
            v-for="tag in row.tags_detail"
            :key="tag.id"
            size="small"
            style="margin-right: 4px; margin-bottom: 2px"
          >
            {{ tag.key }}:{{ tag.value }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openForm(row)">
            编辑
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 主机数据
 * @description 主机模型的所有字段
 */
interface Host {
  id: number
  hostname: string
  ip_address: string
  ssh_port: number
  ssh_user: string
  cpu?: string
  memory?: string
  disk?: string
  status: 'online' | 'offline' | 'maintenance'
  business_line: number
  business_line_name?: string
  cluster?: number
  cluster_name?: string
  cluster_code?: string
  tags: Array<{ id: number; key: string; value: string }>
  tags_detail: Array<{ id: number; key: string; value: string }>
  created_at: string
  updated_at: string
}

/** 主机状态映射 */
type HostStatus = 'online' | 'offline' | 'maintenance'

import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

/** 主机列表数据 */
const hosts = ref<Host[]>([])

/** 加载状态 */
const loading = ref(false)

/** 状态筛选值 */
const filterStatus = ref<HostStatus | ''>('')

/** 状态标签类型映射 */
const statusType: Record<HostStatus, string> = {
  online: 'success',
  offline: 'danger',
  maintenance: 'warning'
}

/** 状态标签文本映射 */
const statusLabel: Record<HostStatus, string> = {
  online: '在线',
  offline: '离线',
  maintenance: '维护中'
}

/**
 * 获取主机列表
 * @description 根据筛选条件获取主机数据，支持按状态筛选
 */
const fetchHosts = async (): Promise<void> => {
  loading.value = true
  try {
    const params = filterStatus.value ? { status: filterStatus.value } : {}
    const { data } = await api.get<Host[]>('/api/cmdb/hosts/', { params })
    hosts.value = data
  } catch (error) {
    ElMessage.error('获取主机列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 打开主机表单
 * @description 弹出新建或编辑主机的表单对话框
 * @param row - 主机数据，传入时为编辑模式，不传时为新建模式
 */
const openForm = (row?: Host): void => {
  if (row) {
    ElMessage.info(`编辑主机 ${row.hostname}`)
  } else {
    ElMessage.info('新建主机')
  }
}

/**
 * 删除主机
 * @description 确认后删除指定主机，刷新列表
 * @param id - 主机 ID
 */
const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除该主机?', '警告', { type: 'warning' })
    await api.delete(`/api/cmdb/hosts/${id}/`)
    ElMessage.success('删除成功')
    fetchHosts()
  } catch {
    // 用户取消或删除失败
  }
}

/** 监听状态筛选变化，自动刷新列表 */
watch(filterStatus, fetchHosts)

/** 组件挂载时获取主机列表 */
onMounted(fetchHosts)
</script>

<style scoped>
.hosts-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.hosts-table {
  width: 100%;
}
</style>
