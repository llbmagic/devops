<!--
  主布局组件
  @description 应用主布局，包含侧边栏导航、顶部栏和内容区域。
              侧边栏包含系统管理、资产管理、持续集成、监控告警等菜单。
-->
<template>
  <el-container class="layout-container">
    <!-- 侧边栏导航 -->
    <el-aside width="200px" class="sidebar">
      <div class="sidebar-title">DevOps</div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
          <el-menu-item index="/system/roles">角色管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="cmdb">
          <template #title>
            <el-icon><Coin /></el-icon>
            <span>资产管理</span>
          </template>
          <el-menu-item index="/cmdb/assets">资产列表</el-menu-item>
          <el-menu-item index="/cmdb/locations">位置树</el-menu-item>
          <el-menu-item index="/cmdb/business-tree">服务树</el-menu-item>
          <el-menu-item index="/cmdb/cloud-accounts">云账号</el-menu-item>
          <el-menu-item index="/cmdb/tags">标签管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="cicd">
          <template #title>
            <el-icon><Refresh /></el-icon>
            <span>持续集成</span>
          </template>
          <el-menu-item index="/cicd/jenkins">Jenkins</el-menu-item>
          <el-menu-item index="/cicd/jobs">构建任务</el-menu-item>
          <el-menu-item index="/cicd/builds">构建历史</el-menu-item>
          <el-menu-item index="/cicd/release-orders">发布单</el-menu-item>
          <el-menu-item index="/cicd/release-orders/my">我的待审批</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="monitor">
          <template #title>
            <el-icon><Bell /></el-icon>
            <span>监控告警</span>
          </template>
          <el-menu-item index="/monitor/instances">Prometheus</el-menu-item>
          <el-menu-item index="/monitor/rules">告警规则</el-menu-item>
          <el-menu-item index="/monitor/alerts">告警列表</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="tickets">
          <template #title>
            <el-icon><List /></el-icon>
            <span>工单审批</span>
          </template>
          <el-menu-item index="/tickets/templates">工单模板</el-menu-item>
          <el-menu-item index="/tickets/list">工单列表</el-menu-item>
          <el-menu-item index="/tickets/my">我的待审批</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-right">
          <span class="username">{{ username }}</span>
          <el-button @click="logout" size="small">
            退出
          </el-button>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
/**
 * 退出登录
 * @description 清除本地存储的 Token 和用户名，跳转到登录页
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HomeFilled, Setting, Coin, Refresh, Bell, List } from '@element-plus/icons-vue'

const router = useRouter()

/** 当前用户名 */
const username = ref('')

/**
 * 组件挂载时获取用户名
 * @description 从 localStorage 读取保存的用户名
 */
onMounted((): void => {
  const user = localStorage.getItem('username')
  if (user) username.value = user
})

/**
 * 退出登录
 * @description 清除本地认证信息，跳转到登录页
 */
const logout = (): void => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  ElMessage.success('已退出')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
}

.sidebar-title {
  padding: 20px;
  color: #fff;
  font-size: 18px;
  text-align: center;
  font-weight: bold;
}

.sidebar-menu {
  border-right: none;
}

.header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border-bottom: 1px solid #e6e6e6;
  background: #fff;
}

.header-right {
  display: flex;
  align-items: center;
}

.username {
  margin-right: 20px;
  color: #606266;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
}
</style>
