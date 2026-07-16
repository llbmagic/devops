<!--
  标签管理页面
  @description 管理资产的标签（Key-Value 键值对），用于资产的灵活分类和筛选。
-->
<template>
  <div class="tag-manage-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        新建标签
      </el-button>
    </div>

    <!-- 标签列表 -->
    <el-table
      :data="tags"
      stripe
      v-loading="loading"
      class="tags-table"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="标签" min-width="200">
        <template #default="{ row }">
          <el-tag class="tag-item">
            <span class="tag-key">{{ row.key }}</span>
            <span class="tag-separator">:</span>
            <span class="tag-value">{{ row.value }}</span>
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="asset_count" label="使用次数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建标签对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建标签"
      width="400px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="60px"
      >
        <el-form-item label="键" prop="key">
          <el-input v-model="formData.key" placeholder="请输入标签键，如 env" />
        </el-form-item>
        <el-form-item label="值" prop="value">
          <el-input v-model="formData.value" placeholder="请输入标签值，如 prod" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 标签数据
 * @description 标签模型的所有字段
 */
interface Tag {
  id: number
  key: string
  value: string
  color?: string
  asset_count: number
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import api from '../api'

/** 标签列表数据 */
const tags = ref<Tag[]>([])

/** 加载状态 */
const loading = ref(false)

/** 对话框 */
const dialogVisible = ref(false)

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 表单数据 */
const formData = ref({
  key: '',
  value: ''
})

/** 表单验证规则 */
const formRules: FormRules = {
  key: [
    { required: true, message: '请输入标签键', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '标签键只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  value: [
    { required: true, message: '请输入标签值', trigger: 'blur' }
  ]
}

/**
 * 获取标签列表
 * @description 从后端 API 获取所有标签数据
 */
const fetchTags = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<Tag[]>('/api/cmdb/tags/')
    tags.value = data
  } catch {
    ElMessage.error('获取标签列表失败')
  } finally {
    loading.value = false
  }
}

/** 新建标签 */
const handleCreate = (): void => {
  formData.value = {
    key: '',
    value: ''
  }
  dialogVisible.value = true
}

/** 删除标签 */
const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除该标签？', '警告', { type: 'warning' })
    await api.delete(`/api/cmdb/tags/${id}/`)
    ElMessage.success('删除成功')
    fetchTags()
  } catch {
    // 用户取消或删除失败
  }
}

/** 提交表单 */
const handleSubmit = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    await api.post('/api/cmdb/tags/', formData.value)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchTags()
  } catch {
    // 表单验证失败或请求失败
  }
}

/** 对话框关闭 */
const handleDialogClose = (): void => {
  formRef.value?.resetFields()
}

/** 组件挂载时获取标签列表 */
onMounted(fetchTags)
</script>

<style scoped>
.tag-manage-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.tags-table {
  width: 100%;
}

.tag-item {
  display: inline-flex;
  align-items: center;
}

.tag-key {
  font-weight: 500;
  color: var(--el-color-primary);
}

.tag-separator {
  margin: 0 4px;
  color: var(--el-text-color-secondary);
}

.tag-value {
  color: var(--el-text-color-regular);
}
</style>
