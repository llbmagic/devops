/**
 * Vue Router 路由配置
 * @description 定义应用的路由结构，包括登录页和主布局页及其子路由。

 * 路由结构:
 * - /login - 登录页（无需认证）
 * - / - 主布局页（需认证）
 *   - /dashboard - 控制台
 *   - /system/users - 用户管理
 *   - /system/roles - 角色管理
 *   - /cmdb/assets - 资产列表
 *   - /cmdb/assets/create - 创建资产
 *   - /cmdb/assets/:id - 资产详情
 *   - /cmdb/locations - 位置树
 *   - /cmdb/business-tree - 服务树
 *   - /cmdb/cloud-accounts - 云账号
 *   - /cmdb/tags - 标签管理
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
        path: 'cmdb/assets',
        name: 'AssetList',
        component: () => import('../views/AssetList.vue'),
        meta: { title: '资产列表' }
      },
      {
        path: 'cmdb/assets/create',
        name: 'AssetCreate',
        component: () => import('../views/AssetCreate.vue'),
        meta: { title: '创建资产' }
      },
      {
        path: 'cmdb/assets/:id',
        name: 'AssetDetail',
        component: () => import('../views/AssetDetail.vue'),
        meta: { title: '资产详情' }
      },
      {
        path: 'cmdb/locations',
        name: 'LocationTree',
        component: () => import('../views/LocationTree.vue'),
        meta: { title: '位置树' }
      },
      {
        path: 'cmdb/business-tree',
        name: 'BusinessTree',
        component: () => import('../views/BusinessTree.vue'),
        meta: { title: '服务树' }
      },
      {
        path: 'cmdb/cloud-accounts',
        name: 'CloudAccounts',
        component: () => import('../views/CloudAccounts.vue'),
        meta: { title: '云账号' }
      },
      {
        path: 'cmdb/tags',
        name: 'TagManage',
        component: () => import('../views/TagManage.vue'),
        meta: { title: '标签管理' }
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
        path: 'cicd/release-orders',
        name: 'ReleaseOrders',
        component: () => import('../views/ReleaseOrderList.vue'),
        meta: { title: '发布单' }
      },
      {
        path: 'cicd/release-orders/create',
        name: 'ReleaseOrderCreate',
        component: () => import('../views/ReleaseOrderCreate.vue'),
        meta: { title: '创建发布单' }
      },
      {
        path: 'cicd/release-orders/my',
        name: 'MyReleaseOrders',
        component: () => import('../views/MyReleaseOrders.vue'),
        meta: { title: '我的待审批' }
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
      },
      {
        path: 'tickets/templates',
        name: 'TicketTemplates',
        component: () => import('../views/TicketTemplates.vue'),
        meta: { title: '工单模板' }
      },
      {
        path: 'tickets/list',
        name: 'TicketList',
        component: () => import('../views/TicketList.vue'),
        meta: { title: '工单列表' }
      },
      {
        path: 'tickets/my',
        name: 'MyTickets',
        component: () => import('../views/MyTickets.vue'),
        meta: { title: '我的待审批' }
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
