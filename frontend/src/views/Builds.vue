<!--
  构建记录页面
  @description 构建历史记录页面，用于查看所有 Jenkins 构建的历史信息。
              展示 Job 名称、构建号、状态、执行人、开始时间和耗时。
-->
<template>
  <div class="builds-container">
    <!-- 构建记录列表 -->
    <el-table
      :data="builds"
      stripe
      v-loading="loading"
      class="builds-table"
    >
      <el-table-column prop="job_name" label="Job" />
      <el-table-column prop="build_number" label="构建号" width="80" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">
            {{ statusLabel[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="executor" label="执行人" width="120" />
      <el-table-column prop="started_at" label="开始时间" width="180" />
      <el-table-column prop="duration" label="耗时(秒)" width="100">
        <template #default="{ row }">
          {{ row.duration || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="commit_id" label="提交 ID" width="150" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 构建记录数据
 * @description 构建记录模型的所有字段
 */
interface BuildRecord {
  id: number
  job: number
  job_name?: string
  build_number: number
  status: 'pending' | 'running' | 'success' | 'failure' | 'aborted'
  duration?: number
  executor?: string
  commit_id?: string
  log_url?: string
  started_at: string
  finished_at?: string
}

/** 构建状态映射 */
type BuildStatus = 'pending' | 'running' | 'success' | 'failure' | 'aborted'

import { ref, onMounted } from 'vue'
import api from '../api'

/** 构建记录列表数据 */
const builds = ref<BuildRecord[]>([])

/** 加载状态 */
const loading = ref(false)

/** 状态标签类型映射 */
const statusType: Record<BuildStatus, string> = {
  pending: 'info',
  running: 'warning',
  success: 'success',
  failure: 'danger',
  aborted: 'info'
}

/** 状态标签文本映射 */
const statusLabel: Record<BuildStatus, string> = {
  pending: '排队中',
  running: '运行中',
  success: '成功',
  failure: '失败',
  aborted: '中止'
}

/**
 * 获取构建记录列表
 * @description 从后端 API 获取所有构建记录数据
 */
const fetchBuilds = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<BuildRecord[]>('/api/cicd/builds/')
    builds.value = data
  } catch {
    console.error('获取构建记录失败')
  } finally {
    loading.value = false
  }
}

/** 组件挂载时获取构建记录列表 */
onMounted(fetchBuilds)
</script>

<style scoped>
.builds-container {
  padding: 20px;
}

.builds-table {
  width: 100%;
}
</style>
