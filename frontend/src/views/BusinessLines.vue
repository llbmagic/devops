<!--
  业务线管理页面
  @description 业务线列表页面，用于查看和创建业务线。
              业务线是主机的顶层分类，每个业务线可包含多台主机。
-->
<template>
  <div class="business-lines-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        新建业务线
      </el-button>
    </div>

    <!-- 业务线列表 -->
    <el-table
      :data="businessLines"
      stripe
      v-loading="loading"
      class="business-lines-table"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="业务线名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="host_count" label="主机数量" width="120" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 业务线数据
 * @description 业务线模型的所有字段
 */
interface BusinessLine {
  id: number
  name: string
  description?: string
  host_count: number
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/** 业务线列表数据 */
const businessLines = ref<BusinessLine[]>([])

/** 加载状态 */
const loading = ref(false)

/**
 * 获取业务线列表
 * @description 从后端 API 获取所有业务线数据
 */
const fetchBusinessLines = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<BusinessLine[]>('/api/cmdb/business-lines/')
    businessLines.value = data
  } catch {
    ElMessage.error('获取业务线列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 新建业务线
 * @description 弹出新建业务线的表单对话框
 */
const handleCreate = (): void => {
  ElMessage.info('新建业务线')
}

/** 组件挂载时获取业务线列表 */
onMounted(fetchBusinessLines)
</script>

<style scoped>
.business-lines-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.business-lines-table {
  width: 100%;
}
</style>
