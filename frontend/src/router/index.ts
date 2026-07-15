/**
 * Vue Router 路由配置
 * @description 定义应用的路由结构，包括登录页和主布局页及其子路由。

 * 路由结构:
 * - /login - 登录页（无需认证）
 * - / - 主布局页（需认证）
 *   - /dashboard - 控制台
 *   - /system/users - 用户管理
 *   - /system/roles - 角色管理
 *   - /cmdb/hosts - 主机管理
 *   - /cmdb/business-lines - 业务线管理
 *   - /cicd/jenkins - Jenkins 实例管理
 *   - /cicd/jobs - Jenkins Job 管理
 *   - /cicd/builds - 构建记录
 *   - /monitor/instances - Prometheus 实例管理
 *   - /monitor/rules - 告警规则
 *   - /monitor/alerts - 告警记录
 *
 * 使用示例:
 * ```typescript
 * import router from '@/router'
 * // 在 main.ts 中使用
 * app.use(router)
 * ```
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

/**
 * 路由配置
 * @description 定义所有路由规则，包括路径、名称、组件和层级关系
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    meta: { title: '控制台', requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '控制台' }
      },
      {
        path: 'system/users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'system/roles',
        name: 'Roles',
        component: () => import('../views/Roles.vue'),
        meta: { title: '角色管理' }
      },
      {
        path: 'cmdb/hosts',
        name: 'Hosts',
        component: () => import('../views/Hosts.vue'),
        meta: { title: '主机管理' }
      },
      {
        path: 'cmdb/business-lines',
        name: 'BusinessLines',
        component: () => import('../views/BusinessLines.vue'),
        meta: { title: '业务线管理' }
      },
      {
        path: 'cicd/jenkins',
        name: 'Jenkins',
        component: () => import('../views/Jenkins.vue'),
        meta: { title: 'Jenkins 实例' }
      },
      {
        path: 'cicd/jobs',
        name: 'Jobs',
        component: () => import('../views/Jobs.vue'),
        meta: { title: 'Jenkins Job' }
      },
      {
        path: 'cicd/builds',
        name: 'Builds',
        component: () => import('../views/Builds.vue'),
        meta: { title: '构建记录' }
      },
      {
        path: 'monitor/instances',
        name: 'Prometheus',
        component: () => import('../views/Prometheus.vue'),
        meta: { title: 'Prometheus 实例' }
      },
      {
        path: 'monitor/rules',
        name: 'AlertRules',
        component: () => import('../views/AlertRules.vue'),
        meta: { title: '告警规则' }
      },
      {
        path: 'monitor/alerts',
        name: 'Alerts',
        component: () => import('../views/Alerts.vue'),
        meta: { title: '告警记录' }
      }
    ]
  }
]

/**
 * 创建路由实例
 * @description 使用 HTML5 History 模式创建路由，基础路径为空
 */
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
