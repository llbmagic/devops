<!--
  服务树管理页面
  @description 服务树用于管理业务的层级结构，支持业务线、服务、模块、实例等多级组织。
              可将资产挂载到服务树节点上。
-->
<template>
  <div class="business-tree-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreateRoot">
        新建根节点
      </el-button>
      <el-button @click="handleAttachAssets">
        挂载资产
      </el-button>
    </div>

    <!-- 服务树 -->
    <el-card v-loading="loading" class="tree-card">
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="treeProps"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span class="node-label">
              <el-icon v-if="data.type === 'business'"><Briefcase /></el-icon>
              <el-icon v-else-if="data.type === 'service'"><Connection /></el-icon>
              <el-icon v-else-if="data.type === 'module'"><Box /></el-icon>
              <el-icon v-else><Document /></el-icon>
              <span>{{ node.label }}</span>
              <el-tag size="small" type="success" style="margin-left: 8px">
                {{ typeLabel[data.type] }}
              </el-tag>
            </span>
            <span class="node-actions">
              <el-button
                v-if="data.type !== 'instance'"
                size="small"
                link
                @click.stop="handleAddChild(data)"
              >
                添加子节点
              </el-button>
              <el-button
                size="small"
                link
                type="primary"
                @click.stop="handleEdit(data)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                link
                type="danger"
                @click.stop="handleDelete(data)"
              >
                删除
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

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
        label-width="80px"
      >
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="节点类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择节点类型">
            <el-option label="业务线" value="business" />
            <el-option label="服务" value="service" />
            <el-option label="模块" value="module" />
            <el-option label="实例" value="instance" />
          </el-select>
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入唯一编码" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 挂载资产对话框 -->
    <el-dialog
      v-model="attachDialogVisible"
      title="挂载资产到节点"
      width="600px"
    >
      <el-transfer
        v-model="selectedAssetIds"
        :data="availableAssets"
        :props="{
          key: 'id',
          label: 'name'
        }"
        filterable
        :titles="['可挂载资产', '已选资产']"
        placeholder="搜索资产名称"
      />
      <template #footer>
        <el-button @click="attachDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAttachSubmit">确定挂载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 服务树节点数据
 * @description 服务树节点的所有字段
 */
interface BusinessServiceNode {
  id: number
  name: string
  type: 'business' | 'service' | 'module' | 'instance'
  code: string
  parent?: number
  parent_name?: string
  description?: string
  children?: BusinessServiceNode[]
  created_at: string
}

/** 资产数据 */
interface AssetItem {
  id: number
  name: string
  asset_type: string
}

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Briefcase, Connection, Box, Document } from '@element-plus/icons-vue'
import api from '../api'

/** 树数据 */
const treeData = ref<BusinessServiceNode[]>([])

/** 加载状态 */
const loading = ref(false)

/** 树节点配置 */
const treeProps = {
  children: 'children',
  label: 'name'
}

/** 节点类型映射 */
const typeLabel: Record<string, string> = {
  business: '业务线',
  service: '服务',
  module: '模块',
  instance: '实例'
}

/** 对话框 */
const dialogVisible = ref(false)
const dialogTitle = ref('新建节点')
const isEdit = ref(false)
const currentNode = ref<BusinessServiceNode | null>(null)

/** 挂载资产对话框 */
const attachDialogVisible = ref(false)
const attachTargetNode = ref<BusinessServiceNode | null>(null)
const availableAssets = ref<AssetItem[]>([])
const selectedAssetIds = ref<number[]>([])

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 表单数据 */
const formData = ref({
  name: '',
  type: 'service' as BusinessServiceNode['type'],
  code: '',
  description: '',
  parent: undefined as number | undefined
})

/** 表单验证规则 */
const formRules: FormRules = {
  name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择节点类型', trigger: 'change' }],
  code: [
    { required: true, message: '请输入编码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '编码只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ]
}

/** 获取树数据 */
const fetchTree = async (): Promise<void> => {
  loading.value = true
  try {
    const { data } = await api.get<BusinessServiceNode[]>('/api/cmdb/business-tree/')
    treeData.value = data
  } catch {
    ElMessage.error('获取服务树失败')
  } finally {
    loading.value = false
  }
}

/** 获取可挂载的资产列表 */
const fetchAvailableAssets = async (): Promise<void> => {
  try {
    const { data } = await api.get<AssetItem[]>('/api/cmdb/assets/', {
      params: { page_size: 1000 }
    })
    availableAssets.value = data.results || data
  } catch {
    ElMessage.error('获取资产列表失败')
  }
}

/** 新建根节点 */
const handleCreateRoot = (): void => {
  dialogTitle.value = '新建根节点'
  isEdit.value = false
  currentNode.value = null
  formData.value = {
    name: '',
    type: 'business',
    code: '',
    description: '',
    parent: undefined
  }
  dialogVisible.value = true
}

/** 添加子节点 */
const handleAddChild = (data: BusinessServiceNode): void => {
  dialogTitle.value = '添加子节点'
  isEdit.value = false
  currentNode.value = data
  formData.value = {
    name: '',
    type: getNextType(data.type),
    code: '',
    description: '',
    parent: data.id
  }
  dialogVisible.value = true
}

/** 根据父节点类型获取合适的子节点类型 */
const getNextType = (parentType: string): BusinessServiceNode['type'] => {
  const typeOrder = ['business', 'service', 'module', 'instance']
  const idx = typeOrder.indexOf(parentType)
  if (idx >= 0 && idx < typeOrder.length - 1) {
    return typeOrder[idx + 1] as BusinessServiceNode['type']
  }
  return 'service'
}

/** 编辑节点 */
const handleEdit = (data: BusinessServiceNode): void => {
  dialogTitle.value = '编辑节点'
  isEdit.value = true
  currentNode.value = data
  formData.value = {
    name: data.name,
    type: data.type,
    code: data.code,
    description: data.description || '',
    parent: data.parent
  }
  dialogVisible.value = true
}

/** 删除节点 */
const handleDelete = async (data: BusinessServiceNode): void => {
  try {
    await ElMessageBox.confirm(
      `确认删除节点"${data.name}"？删除后将同时删除所有子节点。`,
      '警告',
      { type: 'warning' }
    )
    await api.delete(`/api/cmdb/business-tree/${data.id}/`)
    ElMessage.success('删除成功')
    fetchTree()
  } catch {
    // 用户取消或删除失败
  }
}

/** 提交表单 */
const handleSubmit = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    if (isEdit.value && currentNode.value) {
      await api.put(`/api/cmdb/business-tree/${currentNode.value.id}/`, formData.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/api/cmdb/business-tree/', formData.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchTree()
  } catch {
    // 表单验证失败或请求失败
  }
}

/** 对话框关闭 */
const handleDialogClose = (): void => {
  formRef.value?.resetFields()
}

/** 打开挂载资产对话框 */
const handleAttachAssets = async (): Promise<void> => {
  if (!treeRef.value?.getCurrentNode()) {
    ElMessage.warning('请先在树中选择一个节点')
    return
  }
  attachTargetNode.value = treeRef.value.getCurrentNode()?.data || null
  if (!attachTargetNode.value) {
    ElMessage.warning('请先在树中选择一个节点')
    return
  }
  await fetchAvailableAssets()
  selectedAssetIds.value = []
  attachDialogVisible.value = true
}

/** 挂载资产提交 */
const handleAttachSubmit = async (): Promise<void> => {
  if (!attachTargetNode.value) return

  if (selectedAssetIds.value.length === 0) {
    ElMessage.warning('请选择要挂载的资产')
    return
  }

  try {
    await api.post(`/api/cmdb/business-tree/${attachTargetNode.value.id}/attach/`, {
      asset_ids: selectedAssetIds.value
    })
    ElMessage.success('挂载成功')
    attachDialogVisible.value = false
  } catch {
    ElMessage.error('挂载失败')
  }
}

/** 树引用 */
const treeRef = ref()

/** 组件挂载时获取树数据 */
onMounted(fetchTree)
</script>

<style scoped>
.business-tree-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.tree-card {
  width: 100%;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}

.node-label {
  display: flex;
  align-items: center;
  gap: 4px;
}

.node-actions {
  display: flex;
  gap: 8px;
}
</style>
