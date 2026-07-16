<!--
  云账号管理页面
  @description 管理云平台账号配置，支持多云厂商（AWS、阿里云、腾讯云等）的账号管理和资源同步。
-->
<template>
  <div class="cloud-accounts-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        新建云账号
      </el-button>
    </div>

    <!-- 云账号列表 -->
    <el-table
      :data="accounts"
      stripe
      v-loading="loading"
      class="accounts-table"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="云厂商" width="120">
        <template #default="{ row }">
          <el-tag :type="providerType[row.provider]">
            {{ providerLabel[row.provider] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="账号名称" />
      <el-table-column prop="account_id" label="账号ID" />
      <el-table-column prop="region" label="区域" width="150" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_sync_at" label="最后同步" width="180">
        <template #default="{ row }">
          {{ row.last_sync_at || '从未同步' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleSync(row)">
            同步
          </el-button>
          <el-button size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="90px"
      >
        <el-form-item label="云厂商" prop="provider">
          <el-select v-model="formData.provider" placeholder="请选择云厂商">
            <el-option label="阿里云" value="aliyun" />
            <el-option label="AWS" value="aws" />
            <el-option label="腾讯云" value="tencent" />
            <el-option label="华为云" value="huawei" />
            <el-option label="Azure" value="azure" />
            <el-option label="Google Cloud" value="gcp" />
          </el-select>
        </el-form-item>
        <el-form-item label="账号名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入账号名称" />
        </el-form-item>
        <el-form-item label="账号ID" prop="account_id">
          <el-input v-model="formData.account_id" placeholder="请输入云账号ID" />
        </el-form-item>
        <el-form-item label="AccessKey" prop="access_key">
          <el-input v-model="formData.access_key" placeholder="请输入AccessKey" show-password />
        </el-form-item>
        <el-form-item label="SecretKey" prop="secret_key">
          <el-input v-model="formData.secret_key" placeholder="请输入SecretKey" show-password />
        </el-form-item>
        <el-form-item label="区域" prop="region">
          <el-input v-model="formData.region" placeholder="请输入区域，如 cn-hangzhou" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述信息"
          />
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
 * 云账号数据
 * @description 云账号模型的所有字段
 */
interface CloudAccount {
  id: number
  provider: 'aliyun' | 'aws' | 'tencent' | 'huawei' | 'azure' | 'gcp'
  name: string
  account_id: string
  access_key?: string
  secret_key?: string
  region?: string
  description?: string
  is_active: boolean
  last_sync_at?: string
  created_at: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import api from '../api'

/** 云账号列表数据 */
const accounts = ref<CloudAccount[]>([])

/** 加载状态 */
const loading = ref(false)

/** 云厂商映射 */
const providerLabel: Record<string, string> = {
  aliyun: '阿里云',
  aws: 'AWS',
  tencent: '腾讯云',
  huawei: '华为云',
  azure: 'Azure',
  gcp: 'Google Cloud'
}

/** 云厂商标签类型 */
const providerType: Record<string, string> = {
  aliyun: 'primary',
  aws: 'warning',
  tencent: 'danger',
  huawei: 'info',
  azure: 'success',
  gcp: 'warning'
}

/** 对话框 */
const dialogVisible = ref(false)
const dialogTitle = ref('新建云账号')
const isEdit = ref(false)
const currentId = ref<number | null>(null)

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 表单数据 */
const formData = ref({
  provider: 'aliyun' as CloudAccount['provider'],
  name: '',
  account_id: '',
  access_key: '',
  secret_key: '',
  region: '',
  description: ''
})

/** 表单验证规则 */
const formRules: FormRules = {
  provider: [{ required: true, message: '请选择云厂商', trigger: 'change' }],
  name: [{ required: true, message: '请输入账号名称', trigger: 'blur' }],
  account_id: [{ required: true, message: '请输入账号ID', trigger: 'blur' }],
  access_key: [{ required: true, message: '请输入AccessKey', trigger: 'blur' }],
  secret_key: [{ required: true, message: '请输入SecretKey', trigger: 'blur' }]
}

/**
 * 获取云账号列表
 * @description 从后端 API 获取所有云账号数据
 */
const fetchAccounts = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<CloudAccount[]>('/api/cmdb/cloud-accounts/')
    accounts.value = data
  } catch {
    ElMessage.error('获取云账号列表失败')
  } finally {
    loading.value = false
  }
}

/** 新建云账号 */
const handleCreate = (): void => {
  dialogTitle.value = '新建云账号'
  isEdit.value = false
  currentId.value = null
  formData.value = {
    provider: 'aliyun',
    name: '',
    account_id: '',
    access_key: '',
    secret_key: '',
    region: '',
    description: ''
  }
  dialogVisible.value = true
}

/** 编辑云账号 */
const handleEdit = (row: CloudAccount): void => {
  dialogTitle.value = '编辑云账号'
  isEdit.value = true
  currentId.value = row.id
  formData.value = {
    provider: row.provider,
    name: row.name,
    account_id: row.account_id,
    access_key: row.access_key || '',
    secret_key: row.secret_key || '',
    region: row.region || '',
    description: row.description || ''
  }
  dialogVisible.value = true
}

/** 删除云账号 */
const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除该云账号？', '警告', { type: 'warning' })
    await api.delete(`/api/cmdb/cloud-accounts/${id}/`)
    ElMessage.success('删除成功')
    fetchAccounts()
  } catch {
    // 用户取消或删除失败
  }
}

/** 同步云账号 */
const handleSync = async (row: CloudAccount): Promise<void> => {
  try {
    await ElMessageBox.confirm(`确认同步云账号"${row.name}"的资源？`, '同步确认', {
      type: 'info'
    })
    await api.post(`/api/cmdb/cloud-accounts/${row.id}/sync/`)
    ElMessage.success('同步任务已触发')
    fetchAccounts()
  } catch {
    // 用户取消或同步失败
  }
}

/** 提交表单 */
const handleSubmit = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    if (isEdit.value && currentId.value) {
      await api.put(`/api/cmdb/cloud-accounts/${currentId.value}/`, formData.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/api/cmdb/cloud-accounts/', formData.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchAccounts()
  } catch {
    // 表单验证失败或请求失败
  }
}

/** 对话框关闭 */
const handleDialogClose = (): void => {
  formRef.value?.resetFields()
}

/** 组件挂载时获取云账号列表 */
onMounted(fetchAccounts)
</script>

<style scoped>
.cloud-accounts-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.accounts-table {
  width: 100%;
}
</style>
