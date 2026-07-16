<!--
  创建资产页面
  @description 创建新资产表单页面，支持资产基本信息录入、位置选择、标签设置和配置属性。
-->
<template>
  <div class="asset-create-container">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>创建资产</span>
          <el-button size="small" @click="goBack">返回列表</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        class="asset-form"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>

        <el-form-item label="资产名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入资产名称"
            style="width: 400px"
          />
        </el-form-item>

        <el-form-item label="资产类型" prop="asset_type">
          <el-select
            v-model="formData.asset_type"
            placeholder="请选择资产类型"
            style="width: 400px"
          >
            <el-option label="服务器" value="server" />
            <el-option label="网络设备" value="network" />
            <el-option label="存储设备" value="storage" />
            <el-option label="数据库" value="database" />
            <el-option label="中间件" value="middleware" />
            <el-option label="应用服务" value="application" />
          </el-select>
        </el-form-item>

        <el-form-item label="唯一标识" prop="unique_id">
          <el-input
            v-model="formData.unique_id"
            placeholder="请输入唯一标识（如 IP、序列号等）"
            style="width: 400px"
          />
        </el-form-item>

        <el-form-item label="负责人" prop="owner">
          <el-input
            v-model="formData.owner"
            placeholder="请输入负责人"
            style="width: 400px"
          />
        </el-form-item>

        <!-- 位置和状态 -->
        <el-divider content-position="left">位置与状态</el-divider>

        <el-form-item label="位置" prop="location">
          <el-select
            v-model="formData.location"
            placeholder="请选择位置"
            clearable
            filterable
            style="width: 400px"
          >
            <el-option
              v-for="loc in locationOptions"
              :key="loc.id"
              :label="loc.name"
              :value="loc.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" style="width: 400px">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="未知" value="unknown" />
          </el-select>
        </el-form-item>

        <!-- 标签 -->
        <el-divider content-position="left">标签</el-divider>

        <el-form-item label="标签">
          <div class="tags-input">
            <div class="tag-list">
              <el-tag
                v-for="(tag, index) in formData.tags"
                :key="index"
                closable
                @close="removeTag(index)"
                style="margin-right: 8px; margin-bottom: 8px"
              >
                {{ tag.key }}:{{ tag.value }}
              </el-tag>
            </div>
            <div class="tag-input-row">
              <el-input
                v-model="newTagKey"
                placeholder="标签 Key"
                style="width: 150px; margin-right: 8px"
              />
              <el-input
                v-model="newTagValue"
                placeholder="标签 Value"
                style="width: 150px; margin-right: 8px"
              />
              <el-button @click="addTag">添加标签</el-button>
            </div>
          </div>
        </el-form-item>

        <!-- 配置属性 -->
        <el-divider content-position="left">配置属性</el-divider>

        <el-form-item label="配置属性">
          <div class="properties-input">
            <div
              v-for="(prop, index) in formData.properties"
              :key="index"
              class="property-row"
            >
              <el-input
                v-model="prop.key"
                placeholder="属性名"
                style="width: 180px; margin-right: 8px"
              />
              <el-input
                v-model="prop.value"
                placeholder="属性值"
                style="width: 180px; margin-right: 8px"
              />
              <el-button type="danger" circle @click="removeProperty(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button @click="addProperty" style="margin-top: 8px">
              添加属性
            </el-button>
          </div>
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            提交创建
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 创建资产页面逻辑
 * @description 处理资产创建表单提交、标签管理、配置属性管理
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import api from '../api'
import type { LocationNode } from '../api'

/** 路由实例 */
const router = useRouter()

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 提交状态 */
const submitting = ref(false)

/** 位置选项 */
const locationOptions = ref<LocationNode[]>([])

/** 新标签输入 */
const newTagKey = ref('')
const newTagValue = ref('')

/** 表单数据 */
const formData = ref({
  name: '',
  asset_type: '',
  unique_id: '',
  owner: '',
  location: undefined as number | undefined,
  status: 'unknown',
  tags: [] as Array<{ key: string; value: string }>,
  properties: [] as Array<{ key: string; value: string }>
})

/** 表单验证规则 */
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入资产名称', trigger: 'blur' }
  ],
  asset_type: [
    { required: true, message: '请选择资产类型', trigger: 'change' }
  ],
  unique_id: [
    { required: true, message: '请输入唯一标识', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

/**
 * 获取位置列表
 * @description 用于位置选择下拉框
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
 * 添加标签
 * @description 将输入的标签添加到列表
 */
const addTag = (): void => {
  if (!newTagKey.value || !newTagValue.value) {
    ElMessage.warning('请输入标签的 Key 和 Value')
    return
  }
  formData.value.tags.push({
    key: newTagKey.value,
    value: newTagValue.value
  })
  newTagKey.value = ''
  newTagValue.value = ''
}

/**
 * 移除标签
 * @param index - 标签索引
 */
const removeTag = (index: number): void => {
  formData.value.tags.splice(index, 1)
}

/**
 * 添加配置属性
 */
const addProperty = (): void => {
  formData.value.properties.push({ key: '', value: '' })
}

/**
 * 移除配置属性
 * @param index - 属性索引
 */
const removeProperty = (index: number): void => {
  formData.value.properties.splice(index, 1)
}

/**
 * 提交表单
 * @description 验证表单后提交创建资产
 */
const handleSubmit = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.error('请完善表单信息')
    return
  }

  submitting.value = true
  try {
    // 构建提交数据
    const submitData: Record<string, any> = {
      name: formData.value.name,
      asset_type: formData.value.asset_type,
      unique_id: formData.value.unique_id,
      owner: formData.value.owner,
      status: formData.value.status
    }

    if (formData.value.location) {
      submitData.location = formData.value.location
    }

    if (formData.value.tags.length > 0) {
      submitData.tags = formData.value.tags
    }

    if (formData.value.properties.length > 0) {
      const fields: Record<string, any> = {}
      for (const prop of formData.value.properties) {
        if (prop.key) {
          fields[prop.key] = prop.value
        }
      }
      if (Object.keys(fields).length > 0) {
        submitData.fields = fields
      }
    }

    await api.post('/api/cmdb/assets/', submitData)
    ElMessage.success('资产创建成功')
    router.push('/cmdb/assets')
  } catch (error) {
    ElMessage.error('创建资产失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 返回列表页
 */
const goBack = (): void => {
  router.push('/cmdb/assets')
}

/** 组件挂载时获取位置列表 */
onMounted(() => {
  fetchLocations()
})
</script>

<style scoped>
.asset-create-container {
  padding: 20px;
}

.form-card {
  max-width: 800px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.asset-form {
  max-width: 600px;
}

.tags-input {
  width: 100%;
}

.tag-list {
  margin-bottom: 12px;
  min-height: 32px;
}

.tag-input-row {
  display: flex;
  align-items: center;
}

.properties-input {
  width: 100%;
}

.property-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
</style>
