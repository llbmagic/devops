<!--
  资产详情页面
  @description 展示资产详细信息、标签、依赖关系和变更历史。使用 Tabs 组件组织内容。
-->
<template>
  <div class="asset-detail-container" v-loading="loading">
    <!-- 资产基本信息卡片 -->
    <el-card class="basic-info-card" v-if="asset">
      <template #header>
        <div class="card-header">
          <span>资产信息</span>
          <el-button-group>
            <el-button size="small" @click="goToEdit">编辑</el-button>
            <el-button size="small" type="primary" @click="openLifecycleDialog">
              生命周期操作
            </el-button>
          </el-button-group>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="资产名称">{{ asset.name }}</el-descriptions-item>
        <el-descriptions-item label="资产类型">
          <el-tag>{{ asset.asset_type }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType[asset.status]">
            {{ statusLabel[asset.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="唯一标识">{{ asset.unique_id }}</el-descriptions-item>
        <el-descriptions-item label="位置">{{ asset.location_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ asset.owner || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ asset.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ asset.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ asset.created_by_name || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 标签展示 -->
      <div class="tags-section">
        <span class="section-label">标签:</span>
        <el-tag
          v-for="tag in asset.tags"
          :key="tag.id"
          size="small"
          style="margin-right: 8px; margin-bottom: 4px"
        >
          {{ tag.key }}:{{ tag.value }}
        </el-tag>
        <span v-if="!asset.tags || asset.tags.length === 0" class="no-data">无</span>
      </div>
    </el-card>

    <!-- Tabs 切换区域 -->
    <el-tabs v-model="activeTab" class="detail-tabs" v-if="asset">
      <!-- 依赖关系 Tab -->
      <el-tab-pane label="依赖关系 (depends_on)" name="dependencies">
        <el-table :data="asset.dependencies" stripe empty-text="无依赖关系">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="target_asset_name" label="目标资产" min-width="150">
            <template #default="{ row }">
              <el-link type="primary" @click="goToAssetDetail(row.target_asset)">
                {{ row.target_asset_name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="dependency_type" label="依赖类型" width="120" />
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="handleDeleteRelation(row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 被依赖关系 Tab -->
      <el-tab-pane label="被依赖关系 (depended_by)" name="dependents">
        <el-table :data="asset.dependents" stripe empty-text="无被依赖关系">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="source_asset_name" label="源资产" min-width="150">
            <template #default="{ row }">
              <el-link type="primary" @click="goToAssetDetail(row.source_asset)">
                {{ row.source_asset_name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="dependency_type" label="依赖类型" width="120" />
        </el-table>
      </el-tab-pane>

      <!-- 变更历史 Tab -->
      <el-tab-pane label="变更历史" name="history">
        <el-table :data="changeLogs" stripe v-loading="historyLoading" empty-text="无变更记录">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="action" label="操作" width="100">
            <template #default="{ row }">
              <el-tag :type="actionType[row.action]">
                {{ actionLabel[row.action] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="field_name" label="字段" width="120" />
          <el-table-column prop="old_value" label="旧值" min-width="150">
            <template #default="{ row }">
              {{ row.old_value || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="new_value" label="新值" min-width="150">
            <template #default="{ row }">
              {{ row.new_value || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="operator_name" label="操作人" width="100" />
          <el-table-column prop="created_at" label="时间" width="180" />
        </el-table>
      </el-tab-pane>

      <!-- 配置属性 Tab -->
      <el-tab-pane label="配置属性" name="properties">
        <el-descriptions :column="2" border>
          <el-descriptions-item
            v-for="(value, key) in asset.fields"
            :key="key"
            :label="String(key)"
          >
            {{ value ?? '-' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="!asset.fields || Object.keys(asset.fields).length === 0" label="配置">
            <span class="no-data">无配置属性</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>
    </el-tabs>

    <!-- 生命周期操作对话框 -->
    <el-dialog v-model="lifecycleDialogVisible" title="生命周期操作" width="400px">
      <el-form :model="lifecycleForm" label-width="100px">
        <el-form-item label="操作类型">
          <el-select v-model="lifecycleForm.action" style="width: 100%">
            <el-option label="上线" value="online" />
            <el-option label="下线" value="offline" />
            <el-option label="维护" value="maintenance" />
            <el-option label="退役" value="decommission" />
            <el-option label="归档" value="archive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="lifecycleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleLifecycle">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 资产详情页面逻辑
 * @description 获取并展示资产详细信息、依赖关系、变更历史
 */
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import type { AssetChangeLog } from '../api'

/** 资产详情数据 */
interface AssetDetail {
  id: number
  asset_type: string
  name: string
  unique_id?: string
  owner?: string
  status: 'online' | 'offline' | 'maintenance' | 'unknown'
  location?: number
  location_name?: string
  fields: Record<string, any>
  tags: Array<{ id: number; key: string; value: string }>
  dependencies: Array<{
    id: number
    target_asset: number
    target_asset_name: string
    dependency_type: string
  }>
  dependents: Array<{
    id: number
    source_asset: number
    source_asset_name: string
    dependency_type: string
  }>
  created_at: string
  updated_at: string
  created_by?: number
  created_by_name?: string
}

/** 路由实例 */
const router = useRouter()
const route = useRoute()

/** 资产详情数据 */
const asset = ref<AssetDetail | null>(null)

/** 变更日志数据 */
const changeLogs = ref<AssetChangeLog[]>([])

/** 加载状态 */
const loading = ref(false)
const historyLoading = ref(false)

/** 当前激活的 Tab */
const activeTab = ref('dependencies')

/** 生命周期操作对话框 */
const lifecycleDialogVisible = ref(false)
const lifecycleForm = ref({
  action: 'online'
})

/** 状态标签类型映射 */
const statusType: Record<string, string> = {
  online: 'success',
  offline: 'danger',
  maintenance: 'warning',
  unknown: 'info'
}

/** 状态标签文本映射 */
const statusLabel: Record<string, string> = {
  online: '在线',
  offline: '离线',
  maintenance: '维护中',
  unknown: '未知'
}

/** 操作类型映射 */
const actionType: Record<string, string> = {
  create: 'success',
  update: 'warning',
  delete: 'danger'
}

/** 操作类型文本映射 */
const actionLabel: Record<string, string> = {
  create: '创建',
  update: '更新',
  delete: '删除'
}

/** 资产 ID */
const assetId = ref<number>(0)

/**
 * 获取资产详情
 * @description 根据路由参数获取资产 ID，然后获取详情
 */
const fetchAssetDetail = async (): Promise<void> => {
  loading.value = true
  try {
    const id = route.params.id
    assetId.value = Number(id)
    const { data } = await api.get<AssetDetail>(`/api/cmdb/assets/${id}/`)
    asset.value = data
  } catch (error) {
    ElMessage.error('获取资产详情失败')
  } finally {
    loading.value = false
  }
}

/**
 * 获取变更历史
 * @description 获取资产的变更记录
 */
const fetchChangeHistory = async (): Promise<void> => {
  historyLoading.value = true
  try {
    const { data } = await api.get<AssetChangeLog[]>(
      `/api/cmdb/assets/${assetId.value}/history/`
    )
    changeLogs.value = data
  } catch (error) {
    console.error('获取变更历史失败', error)
  } finally {
    historyLoading.value = false
  }
}

/**
 * 跳转到资产编辑页
 */
const goToEdit = (): void => {
  router.push(`/cmdb/assets/${assetId.value}/edit`)
}

/**
 * 跳转到指定资产详情页
 * @param id - 资产 ID
 */
const goToAssetDetail = (id: number): void => {
  router.push(`/cmdb/assets/${id}`)
}

/**
 * 打开生命周期操作对话框
 */
const openLifecycleDialog = (): void => {
  lifecycleDialogVisible.value = true
}

/**
 * 执行生命周期操作
 * @description 调用后端 API 执行生命周期操作
 */
const handleLifecycle = async (): Promise<void> => {
  try {
    await api.post(`/api/cmdb/assets/${assetId.value}/lifecycle/`, {
      action: lifecycleForm.value.action
    })
    ElMessage.success('操作成功')
    lifecycleDialogVisible.value = false
    fetchAssetDetail()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

/**
 * 删除依赖关系
 * @param relationId - 关系 ID
 */
const handleDeleteRelation = async (relationId: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除该依赖关系?', '警告', { type: 'warning' })
    await api.delete(`/api/cmdb/relationships/${relationId}/`)
    ElMessage.success('删除成功')
    fetchAssetDetail()
  } catch {
    // 用户取消或删除失败
  }
}

/** 监听 Tab 切换，加载变更历史 */
const handleTabChange = (tabName: string): void => {
  if (tabName === 'history' && changeLogs.value.length === 0) {
    fetchChangeHistory()
  }
}

/** 组件挂载时获取数据 */
onMounted(() => {
  fetchAssetDetail()
})
</script>

<style scoped>
.asset-detail-container {
  padding: 20px;
}

.basic-info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-tabs {
  background: #fff;
  padding: 0 20px;
}

.tags-section {
  margin-top: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.section-label {
  font-weight: 500;
  margin-right: 8px;
}

.no-data {
  color: #999;
  font-size: 14px;
}
</style>
