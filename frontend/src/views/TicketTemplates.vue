<!--
  工单模板管理页面
  @description 工单模板列表页面，用于查看和管理工单模板。
-->
<template>
  <div class="ticket-templates-container">
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        添加模板
      </el-button>
    </div>

    <el-table :data="templates" stripe v-loading="loading" class="templates-table">
      <el-table-column prop="name" label="模板名称" />
      <el-table-column prop="code" label="模板代码" width="150" />
      <el-table-column prop="approval_steps" label="审批步骤" width="100" />
      <el-table-column prop="approvers" label="默认审批人" width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ticket_count" label="工单数" width="100" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
/**
 * 工单模板数据
 */
interface TicketTemplate {
  id: number
  name: string
  code: string
  description?: string
  approvers?: string
  approval_steps: number
  variables?: string
  is_active: boolean
  ticket_count: number
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const templates = ref<TicketTemplate[]>([])
const loading = ref(false)

const fetchTemplates = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<TicketTemplate[]>('/api/tickets/templates/')
    templates.value = data
  } catch {
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = (): void => {
  ElMessage.info('添加工单模板')
}

const handleEdit = (row: TicketTemplate): void => {
  ElMessage.info(`编辑模板: ${row.name}`)
}

const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除?', '警告', { type: 'warning' })
    await api.delete(`/api/tickets/templates/${id}/`)
    ElMessage.success('删除成功')
    fetchTemplates()
  } catch {
    // 用户取消或失败
  }
}

onMounted(fetchTemplates)
</script>

<style scoped>
.ticket-templates-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
}
.templates-table {
  width: 100%;
}
</style>
