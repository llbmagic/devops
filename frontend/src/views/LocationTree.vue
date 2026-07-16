<!--
  位置树管理页面
  @description 位置树用于管理资产的物理或逻辑位置层级结构，
              支持区域、可用区、机房、机柜、设备位等多级组织。
-->
<template>
  <div class="location-tree-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreateRoot">
        新建根节点
      </el-button>
    </div>

    <!-- 位置树 -->
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
              <el-icon v-if="data.type === 'region'"><Location /></el-icon>
              <el-icon v-else-if="data.type === 'zone'"><Grid /></el-icon>
              <el-icon v-else-if="data.type === 'datacenter'"><OfficeBuilding /></el-icon>
              <el-icon v-else-if="data.type === 'rack'"><Box /></el-icon>
              <el-icon v-else><Cpu /></el-icon>
              <span>{{ node.label }}</span>
              <el-tag size="small" type="info" style="margin-left: 8px">
                {{ typeLabel[data.type] }}
              </el-tag>
            </span>
            <span class="node-actions">
              <el-button
                v-if="data.type !== 'device'"
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
            <el-option label="区域" value="region" />
            <el-option label="可用区" value="zone" />
            <el-option label="机房" value="datacenter" />
            <el-option label="机柜" value="rack" />
            <el-option label="设备位" value="device" />
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
  </div>
</template>

<script setup lang="ts">
/**
 * 位置树节点数据
 * @description 位置树节点的所有字段
 */
interface LocationNode {
  id: number
  name: string
  type: 'region' | 'zone' | 'datacenter' | 'rack' | 'device'
  code: string
  parent?: number
  parent_name?: string
  description?: string
  children?: LocationNode[]
  created_at: string
}

import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Location, Grid, OfficeBuilding, Box, Cpu } from '@element-plus/icons-vue'
import api from '../api'

/** 树数据 */
const treeData = ref<LocationNode[]>([])

/** 加载状态 */
const loading = ref(false)

/** 树节点配置 */
const treeProps = {
  children: 'children',
  label: 'name'
}

/** 节点类型映射 */
const typeLabel: Record<string, string> = {
  region: '区域',
  zone: '可用区',
  datacenter: '机房',
  rack: '机柜',
  device: '设备位'
}

/** 对话框 */
const dialogVisible = ref(false)
const dialogTitle = ref('新建节点')
const isEdit = ref(false)
const currentNode = ref<LocationNode | null>(null)

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 表单数据 */
const formData = ref({
  name: '',
  type: 'datacenter' as LocationNode['type'],
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
    const { data } = await api.get<LocationNode[]>('/api/cmdb/locations/')
    treeData.value = data
  } catch {
    ElMessage.error('获取位置树失败')
  } finally {
    loading.value = false
  }
}

/** 新建根节点 */
const handleCreateRoot = (): void => {
  dialogTitle.value = '新建根节点'
  isEdit.value = false
  currentNode.value = null
  formData.value = {
    name: '',
    type: 'region',
    code: '',
    description: '',
    parent: undefined
  }
  dialogVisible.value = true
}

/** 添加子节点 */
const handleAddChild = (data: LocationNode): void => {
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
const getNextType = (parentType: string): LocationNode['type'] => {
  const typeOrder = ['region', 'zone', 'datacenter', 'rack', 'device']
  const idx = typeOrder.indexOf(parentType)
  if (idx >= 0 && idx < typeOrder.length - 1) {
    return typeOrder[idx + 1] as LocationNode['type']
  }
  return 'datacenter'
}

/** 编辑节点 */
const handleEdit = (data: LocationNode): void => {
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
const handleDelete = async (data: LocationNode): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确认删除节点"${data.name}"？删除后将同时删除所有子节点。`,
      '警告',
      { type: 'warning' }
    )
    await api.delete(`/api/cmdb/locations/${data.id}/`)
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
      await api.put(`/api/cmdb/locations/${currentNode.value.id}/`, formData.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/api/cmdb/locations/', formData.value)
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

/** 组件挂载时获取树数据 */
onMounted(fetchTree)
</script>

<style scoped>
.location-tree-container {
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
