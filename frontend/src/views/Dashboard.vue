<!--
  控制台页面
  @description 运维平台首页，展示关键统计信息，包括主机数量、活跃告警、构建任务、用户数等。
-->
<template>
  <div class="dashboard-container">
    <h2 class="page-title">运维平台概览</h2>

    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon hosts-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.hosts }}</div>
            <div class="stat-label">主机数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon alerts-icon">
            <el-icon><Bell /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.alerts }}</div>
            <div class="stat-label">活跃告警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon builds-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.builds }}</div>
            <div class="stat-label">构建任务</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon users-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.users }}</div>
            <div class="stat-label">用户数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
/**
 * 统计数据
 * @description 控制台展示的各项统计数据
 */
interface DashboardStats {
  /** 主机数量 */
  hosts: number
  /** 活跃告警数 */
  alerts: number
  /** 构建任务数 */
  builds: number
  /** 用户数 */
  users: number
}

import { ref, onMounted } from 'vue'
import { Monitor, Bell, Clock, User } from '@element-plus/icons-vue'
import api from '../api'

/** 统计数据 */
const stats = ref<DashboardStats>({
  hosts: 0,
  alerts: 0,
  builds: 0,
  users: 0
})

/**
 * 组件挂载时加载统计数据
 * @description 并行请求主机列表和用户列表获取数量
 */
onMounted(async (): Promise<void> => {
  try {
    // 并行请求主机和用户数据
    const [hostsRes, usersRes] = await Promise.all([
      api.get('/api/cmdb/hosts/'),
      api.get('/api/users/users/')
    ])

    // 更新统计数据
    stats.value = {
      ...stats.value,
      hosts: hostsRes.data.count || 0,
      users: usersRes.data.length || 0
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 28px;
  color: #fff;
}

.hosts-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.alerts-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.builds-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.users-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
</style>
