<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background: #304156">
      <div style="padding: 20px; color: #fff; font-size: 18px; text-align: center">DevOps</div>
      <el-menu :default-active="$route.path" router background-color="#304156" text-color="#bfcbd9">
        <el-menu-item index="/dashboard">首页</el-menu-item>
        <el-sub-menu index="system">
          <template #title>系统管理</template>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
          <el-menu-item index="/system/roles">角色管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="cmdb">
          <template #title>资产管理</template>
          <el-menu-item index="/cmdb/hosts">主机管理</el-menu-item>
          <el-menu-item index="/cmdb/business-lines">业务线</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="cicd">
          <template #title>持续集成</template>
          <el-menu-item index="/cicd/jenkins">Jenkins</el-menu-item>
          <el-menu-item index="/cicd/jobs">构建任务</el-menu-item>
          <el-menu-item index="/cicd/builds">构建历史</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="monitor">
          <template #title>监控告警</template>
          <el-menu-item index="/monitor/instances">Prometheus</el-menu-item>
          <el-menu-item index="/monitor/rules">告警规则</el-menu-item>
          <el-menu-item index="/monitor/alerts">告警列表</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display: flex; align-items: center; justify-content: flex-end; border-bottom: 1px solid #e6e6e6">
        <span style="margin-right: 20px">{{ username }}</span>
        <el-button @click="logout" size="small">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const username = ref('')

onMounted(() => {
  const user = localStorage.getItem('username')
  if (user) username.value = user
})

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  ElMessage.success('已退出')
  router.push('/login')
}
</script>
