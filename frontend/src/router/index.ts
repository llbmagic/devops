import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'system/users', name: 'Users', component: () => import('../views/Users.vue') },
      { path: 'system/roles', name: 'Roles', component: () => import('../views/Roles.vue') },
      { path: 'cmdb/hosts', name: 'Hosts', component: () => import('../views/Hosts.vue') },
      { path: 'cmdb/business-lines', name: 'BusinessLines', component: () => import('../views/BusinessLines.vue') },
      { path: 'cicd/jenkins', name: 'Jenkins', component: () => import('../views/Jenkins.vue') },
      { path: 'cicd/jobs', name: 'Jobs', component: () => import('../views/Jobs.vue') },
      { path: 'cicd/builds', name: 'Builds', component: () => import('../views/Builds.vue') },
      { path: 'monitor/instances', name: 'Prometheus', component: () => import('../views/Prometheus.vue') },
      { path: 'monitor/rules', name: 'AlertRules', component: () => import('../views/AlertRules.vue') },
      { path: 'monitor/alerts', name: 'Alerts', component: () => import('../views/Alerts.vue') },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router