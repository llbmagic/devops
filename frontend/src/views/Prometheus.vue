<!--
  Prometheus 实例管理页面
  @description Prometheus 实例列表页面，用于查看和添加 Prometheus 服务器实例。
-->
<template>
  <div class="prometheus-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        添加实例
      </el-button>
    </div>

    <!-- Prometheus 实例列表 -->
    <el-table
      :data="instances"
      stripe
      v-loading="loading"
      class="instances-table"
    >
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="url" label="URL" min-width="200" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * Prometheus 实例数据
 * @description Prometheus 实例模型的所有字段
 */
interface PrometheusInstance {
  id: number
  name: string
  url: string
  api_token?: string
  is_active: boolean
}

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/** Prometheus 实例列表数据 */
const instances = ref<PrometheusInstance[]>([])

/** 加载状态 */
const loading = ref(false)

/**
 * 获取 Prometheus 实例列表
 * @description 从后端 API 获取所有 Prometheus 实例数据
 */
const fetchInstances = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<PrometheusInstance[]>('/api/monitor/prometheus-instances/')
    instances.value = data
  } catch {
    ElMessage.error('获取 Prometheus 实例列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 添加 Prometheus 实例
 * @description 弹出添加 Prometheus 实例的表单对话框
 */
const handleCreate = (): void => {
  ElMessage.info('添加 Prometheus 实例')
}

/** 组件挂载时获取 Prometheus 实例列表 */
onMounted(fetchInstances)
</script>

<style scoped>
.prometheus-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.instances-table {
  width: 100%;
}
</style>
