<!--
  GitLab 代码仓库页面
  @description GitLab 项目列表页面，用于查看从 GitLab 同步的代码仓库。
-->
<template>
  <div class="gitlab-projects-container">
    <div class="toolbar">
      <el-select v-model="filterInstance" placeholder="按实例筛选" clearable style="width: 200px">
        <el-option
          v-for="inst in instances"
          :key="inst.id"
          :label="inst.name"
          :value="inst.id"
        />
      </el-select>
    </div>

    <el-table :data="projects" stripe v-loading="loading" class="projects-table">
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="path_with_namespace" label="完整路径" min-width="200" />
      <el-table-column prop="instance_name" label="实例" width="150" />
      <el-table-column prop="default_branch" label="默认分支" width="120" />
      <el-table-column prop="last_activity_at" label="最后活动" width="180" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="triggerPipeline(row)">触发流水线</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * GitLab 项目数据
 */
interface Project {
  id: number
  instance: number
  instance_name?: string
  gitlab_id: number
  name: string
  path_with_namespace: string
  web_url: string
  default_branch: string
  last_activity_at?: string
}

interface GitLabInstance {
  id: number
  name: string
}

import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const projects = ref<Project[]>([])
const instances = ref<GitLabInstance[]>([])
const loading = ref(false)
const filterInstance = ref<number | null>(null)

const fetchProjects = async (): Promise<void> => {
  loading.value = true
  try {
    const params = filterInstance.value ? { instance: filterInstance.value } : {}
    const { data } = await api.get<Project[]>('/api/gitlab/projects/', { params })
    projects.value = data
  } catch {
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

const fetchInstances = async (): Promise<void> => {
  try {
    const { data } = await api.get<GitLabInstance[]>('/api/gitlab/instances/')
    instances.value = data
  } catch {
    // 忽略错误
  }
}

const triggerPipeline = async (row: Project): Promise<void> => {
  try {
    const { data } = await api.post<{ status: string; pipeline_id?: number }>(
      `/api/gitlab/projects/${row.id}/trigger_pipeline/`,
      { ref: row.default_branch }
    )
    ElMessage.success(`流水线已触发，ID: ${data.pipeline_id}`)
  } catch {
    ElMessage.error('触发流水线失败')
  }
}

watch(filterInstance, fetchProjects)

onMounted(() => {
  fetchInstances()
  fetchProjects()
})
</script>

<style scoped>
.gitlab-projects-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
}
.projects-table {
  width: 100%;
}
</style>
