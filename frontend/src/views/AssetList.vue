<!--
  资产列表页面
  @description 展示所有资产列表，支持按资产类型、状态、位置筛选，支持搜索和分页。
-->
<template>
  <div class="asset-list-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="goToCreate">
        创建资产
      </el-button>
      <el-select
        v-model="filterAssetType"
        placeholder="资产类型"
        clearable
        style="width: 150px; margin-left: 10px"
        @change="fetchAssets"
      >
        <el-option
          v-for="item in assetTypeOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select
        v-model="filterStatus"
        placeholder="状态筛选"
        clearable
        style="width: 120px; margin-left: 10px"
        @change="fetchAssets"
      >
        <el-option label="在线" value="online" />
        <el-option label="离线" value="offline" />
        <el-option label="维护中" value="maintenance" />
        <el-option label="未知" value="unknown" />
      </el-select>
      <el-select
        v-model="filterLocation"
        placeholder="位置筛选"
        clearable
        filterable
        style="width: 200px; margin-left: 10px"
        @change="fetchAssets"
      >
        <el-option
          v-for="loc in locationOptions"
          :key="loc.id"
          :label="loc.name"
          :value="loc.id"
        />
      </el-select>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索资产名称/标识/负责人"
        clearable
        style="width: 250px; margin-left: 10px"
        @keyup.enter="fetchAssets"
      >
        <template #append>
          <el-button icon="Search" @click="fetchAssets" />
        </template>
      </el-input>
    </div>

    <!-- 资产列表 -->
    <el-table
      :data="assets"
      stripe
      v-loading="loading"
      class="asset-table"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="资产名称" min-width="150">
        <template #default="{ row }">
          <el-link type="primary" @click="goToDetail(row.id)">
            {{ row.name }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column prop="asset_type" label="资产类型" width="120">
        <template #default="{ row }">
          <el-tag>{{ row.asset_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">
            {{ statusLabel[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="location_name" label="位置" min-width="120">
        <template #default="{ row }">
          {{ row.location_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="标签" min-width="150">
        <template #default="{ row }">
          <el-tag
            v-for="tag in row.tags"
            :key="tag.id"
            size="small"
            style="margin-right: 4px; margin-bottom: 2px"
          >
            {{ tag.key }}:{{ tag.value }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="goToDetail(row.id)">
            详情
          </el-button>
          <el-button size="small" @click="goToEdit(row.id)">
            编辑
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchAssets"
        @current-change="fetchAssets"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 资产列表页面逻辑
 * @description 获取资产列表、筛选、搜索、分页功能
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import type { LocationNode } from '../api'

/** 资产列表项数据 */
interface AssetListItem {
  id: number
  asset_type: string
  name: string
  status: 'online' | 'offline' | 'maintenance' | 'unknown'
  location?: number
  location_name?: string
  tags: Array<{ id: number; key: string; value: string }>
  created_at: string
  updated_at: string
}

/** 路由实例 */
const router = useRouter()

/** 资产列表数据 */
const assets = ref<AssetListItem[]>([])

/** 加载状态 */
const loading = ref(false)

/** 筛选条件 */
const filterAssetType = ref('')
const filterStatus = ref('')
const filterLocation = ref<number | ''>('')
const searchKeyword = ref('')

/** 分页数据 */
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

/** 资产类型选项 */
const assetTypeOptions = ref<Array<{ label: string; value: string }>>([
  { label: '服务器', value: 'server' },
  { label: '网络设备', value: 'network' },
  { label: '存储设备', value: 'storage' },
  { label: '数据库', value: 'database' },
  { label: '中间件', value: 'middleware' },
  { label: '应用服务', value: 'application' }
])

/** 位置选项 */
const locationOptions = ref<LocationNode[]>([])

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

/**
 * 获取资产列表
 * @description 根据筛选条件获取资产数据
 */
const fetchAssets = async (): Promise<void> => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterAssetType.value) {
      params.asset_type = filterAssetType.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    if (filterLocation.value) {
      params.location = filterLocation.value
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    const { data } = await api.get<{ results: AssetListItem[]; count: number }>(
      '/api/cmdb/assets/',
      { params }
    )
    assets.value = data.results
    total.value = data.count
  } catch (error) {
    ElMessage.error('获取资产列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 获取位置列表
 * @description 用于位置筛选下拉框
 */
const fetchLocations = async (): Promise<void> => {
  try {
    const { data } = await api.get<LocationNode[]>('/api/cmdb/locations/')
    locationOptions.value = data
  } catch (error) {
    console.error('获取位置列表失败', error)
  }
}

/**
 * 跳转到资产详情页
 * @param id - 资产 ID
 */
const goToDetail = (id: number): void => {
  router.push(`/cmdb/assets/${id}`)
}

/**
 * 跳转到资产编辑页
 * @param id - 资产 ID
 */
const goToEdit = (id: number): void => {
  router.push(`/cmdb/assets/${id}/edit`)
}

/**
 * 跳转到创建资产页
 */
const goToCreate = (): void => {
  router.push('/cmdb/assets/create')
}

/**
 * 删除资产
 * @description 确认后删除指定资产，刷新列表
 * @param id - 资产 ID
 */
const handleDelete = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确认删除该资产?', '警告', { type: 'warning' })
    await api.delete(`/api/cmdb/assets/${id}/`)
    ElMessage.success('删除成功')
    fetchAssets()
  } catch {
    // 用户取消或删除失败
  }
}

/** 组件挂载时获取数据 */
onMounted(() => {
  fetchAssets()
  fetchLocations()
})
</script>

<style scoped>
.asset-list-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.asset-table {
  width: 100%;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
