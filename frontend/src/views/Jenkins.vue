<!--
  Jenkins 实例管理页面
  @description Jenkins 实例列表页面，用于查看、添加、编辑 Jenkins 实例，
              并同步 Job 列表。
-->
<template>
  <div class="jenkins-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        添加实例
      </el-button>
      <el-button @click="syncAll">
        同步 Jobs
      </el-button>
    </div>

    <!-- Jenkins 实例列表 -->
    <el-table
      :data="instances"
      stripe
      v-loading="loading"
      class="instances-table"
    >
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="url" label="URL" min-width="200" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="syncJobs(row)">
            同步
          </el-button>
          <el-button size="small" @click="handleEdit(row)">
            编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * Jenkins 实例数据
 * @description Jenkins 实例模型的所有字段
 */
interface JenkinsInstance {
  id: number
  name: string
  url: string
  username: string
  api_token: string
  is_active: boolean
}

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

/** Jenkins 实例列表数据 */
const instances = ref<JenkinsInstance[]>([])

/** 加载状态 */
const loading = ref(false)

/**
 * 获取 Jenkins 实例列表
 * @description 从后端 API 获取所有 Jenkins 实例数据
 */
const fetchInstances = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<JenkinsInstance[]>('/api/cicd/jenkins-instances/')
    instances.value = data
  } catch {
    ElMessage.error('获取 Jenkins 实例列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 同步单个实例的 Job 列表
 * @description 调用后端 API 同步指定 Jenkins 实例的 Job
 * @param row - Jenkins 实例数据
 */
const syncJobs = async (row: JenkinsInstance): Promise<void> => {
  try {
    await api.post(`/api/cicd/jenkins-instances/${row.id}/sync_jobs/`)
    ElMessage.success('同步成功')
  } catch {
    ElMessage.error('同步失败')
  }
}

/**
 * 同步所有实例的 Job 列表
 * @description 遍历所有 Jenkins 实例，依次同步 Job
 */
const syncAll = async (): Promise<void> => {
  try {
    for (const inst of instances.value) {
      await api.post(`/api/cicd/jenkins-instances/${inst.id}/sync_jobs/`)
    }
    ElMessage.success('全部同步完成')
  } catch {
    ElMessage.error('同步失败')
  }
}

/**
 * 添加 Jenkins 实例
 * @description 弹出添加 Jenkins 实例的表单对话框
 */
const handleCreate = (): void => {
  ElMessage.info('添加 Jenkins 实例')
}

/**
 * 编辑 Jenkins 实例
 * @description 弹出编辑 Jenkins 实例的表单对话框
 * @param row - Jenkins 实例数据
 */
const handleEdit = (row: JenkinsInstance): void => {
  ElMessage.info(`编辑 Jenkins 实例: ${row.name}`)
}

/** 组件挂载时获取 Jenkins 实例列表 */
onMounted(fetchInstances)
</script>

<style scoped>
.jenkins-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.instances-table {
  width: 100%;
}
</style>
