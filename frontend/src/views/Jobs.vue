<!--
  Jenkins Job 管理页面
  @description Jenkins Job 列表页面，用于查看 Job 信息和触发构建。
              从同步的 Jenkins 实例中获取 Job 列表。
-->
<template>
  <div class="jobs-container">
    <!-- Job 列表 -->
    <el-table
      :data="jobs"
      stripe
      v-loading="loading"
      class="jobs-table"
    >
      <el-table-column prop="instance_name" label="实例" />
      <el-table-column prop="name" label="Job 名称" />
      <el-table-column prop="last_build_number" label="最后构建号" width="120" />
      <el-table-column prop="last_build_status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.last_build_status]">
            {{ row.last_build_status || '-' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="triggerBuild(row)">
            触发构建
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * Jenkins Job 数据
 * @description Jenkins Job 模型的所有字段
 */
interface JenkinsJob {
  id: number
  instance: number
  instance_name?: string
  name: string
  job_url: string
  last_build_number: number
  last_build_status?: string
  last_build_time?: string
}

/** Jenkins 构建状态映射 */
type BuildStatus = 'SUCCESS' | 'FAILURE' | 'RUNNING' | 'ABORTED' | 'pending' | 'running' | 'success' | 'failure' | 'aborted' | undefined

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/** Job 列表数据 */
const jobs = ref<JenkinsJob[]>([])

/** 加载状态 */
const loading = ref(false)

/** 状态标签类型映射 */
const statusType: Record<string, string> = {
  SUCCESS: 'success',
  FAILURE: 'danger',
  RUNNING: 'warning',
  ABORTED: 'info',
  pending: 'info',
  running: 'warning',
  success: 'success',
  failure: 'danger',
  aborted: 'info'
}

/**
 * 获取 Job 列表
 * @description 从后端 API 获取所有 Jenkins Job 数据
 */
const fetchJobs = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<JenkinsJob[]>('/api/cicd/jobs/')
    jobs.value = data
  } catch {
    ElMessage.error('获取 Job 列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 触发构建
 * @description 调用后端 API 触发指定 Job 的构建
 * @param row - Jenkins Job 数据
 */
const triggerBuild = async (row: JenkinsJob): Promise<void> => {
  try {
    await api.post(`/api/cicd/jobs/${row.id}/build/`)
    ElMessage.success('构建已触发')
    fetchJobs()
  } catch {
    ElMessage.error('触发构建失败')
  }
}

/** 组件挂载时获取 Job 列表 */
onMounted(fetchJobs)
</script>

<style scoped>
.jobs-container {
  padding: 20px;
}

.jobs-table {
  width: 100%;
}
</style>
