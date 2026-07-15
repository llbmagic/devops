<!--
  GitLab 合并请求页面
  @description GitLab 合并请求列表页面，用于查看 MR 状态并刷新。
-->
<template>
  <div class="merge-requests-container">
    <div class="toolbar">
      <el-select v-model="filterState" placeholder="状态筛选" clearable style="width: 150px">
        <el-option label="开启" value="opened" />
        <el-option label="已关闭" value="closed" />
        <el-option label="已合并" value="merged" />
      </el-select>
      <el-button @click="refreshAll">刷新全部</el-button>
    </div>

    <el-table :data="mergeRequests" stripe v-loading="loading" class="mr-table">
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="project_path" label="项目" width="180" />
      <el-table-column prop="author" label="作者" width="120" />
      <el-table-column prop="source_branch" label="源分支" width="150" />
      <el-table-column prop="target_branch" label="目标分支" width="150" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="stateType[row.state]">{{ stateLabel[row.state] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="CI 状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.pipeline_status" :type="pipelineType[row.pipeline_status]">
            {{ pipelineLabel[row.pipeline_status] }}
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="refreshMR(row)">刷新</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * GitLab 合并请求数据
 */
interface MergeRequest {
  id: number
  project: number
  project_path?: string
  gitlab_id: number
  title: string
  source_branch: string
  target_branch: string
  state: 'opened' | 'closed' | 'merged'
  author: string
  review_status: 'pending' | 'approved' | 'rejected'
  pipeline_status?: 'running' | 'success' | 'failed' | 'canceled' | 'pending'
  web_url: string
}

import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const mergeRequests = ref<MergeRequest[]>([])
const loading = ref(false)
const filterState = ref('')

const stateType: Record<string, string> = {
  opened: 'success',
  closed: 'danger',
  merged: 'info'
}

const stateLabel: Record<string, string> = {
  opened: '开启',
  closed: '已关闭',
  merged: '已合并'
}

const pipelineType: Record<string, string> = {
  running: 'warning',
  success: 'success',
  failed: 'danger',
  canceled: 'info',
  pending: 'info'
}

const pipelineLabel: Record<string, string> = {
  running: '运行中',
  success: '成功',
  failed: '失败',
  canceled: '取消',
  pending: '等待'
}

const fetchMergeRequests = async (): Promise<void> => {
  loading.value = true
  try {
    const params = filterState.value ? { state: filterState.value } : {}
    const { data } = await api.get<MergeRequest[]>('/api/gitlab/merge-requests/', { params })
    mergeRequests.value = data
  } catch {
    ElMessage.error('获取合并请求列表失败')
  } finally {
    loading.value = false
  }
}

const refreshMR = async (row: MergeRequest): Promise<void> => {
  try {
    await api.post(`/api/gitlab/merge-requests/${row.id}/refresh/`)
    ElMessage.success('刷新成功')
    fetchMergeRequests()
  } catch {
    ElMessage.error('刷新失败')
  }
}

const refreshAll = async (): Promise<void> => {
  try {
    for (const mr of mergeRequests.value) {
      await api.post(`/api/gitlab/merge-requests/${mr.id}/refresh/`)
    }
    ElMessage.success('全部刷新完成')
    fetchMergeRequests()
  } catch {
    ElMessage.error('刷新失败')
  }
}

watch(filterState, fetchMergeRequests)

onMounted(fetchMergeRequests)
</script>

<style scoped>
.merge-requests-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 10px;
}
.mr-table {
  width: 100%;
}
</style>
