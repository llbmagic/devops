/**
 * API 客户端封装
 * @description 基于 Axios 封装的 HTTP 客户端，用于与后端 Django REST API 交互。
 *              自动处理 JWT Token 认证、请求拦截、错误处理和 401 重定向。
 *
 * 主要功能:
 * - 自动附加 JWT Token 到请求头
 * - 401 响应时自动清除 Token 并跳转到登录页
 * - 统一错误提示
 * - 请求超时控制（10秒）
 *
 * 使用示例:
 * ```typescript
 * import api from '@/api'
 *
 * // GET 请求
 * const { data } = await api.get('/api/cmdb/hosts/')
 *
 * // POST 请求
 * const { data } = await api.post('/api/users/login/', { username, password })
 * ```
 */

import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

/** API 客户端配置参数 */
interface ApiConfig extends AxiosRequestConfig {
  /** 请求基础 URL，默认为后端服务器地址 */
  baseURL?: string
  /** 请求超时时间（毫秒），默认 10000 */
  timeout?: number
}

/** 认证用户信息 */
interface AuthUser {
  id: number
  username: string
  email: string
  phone?: string
  department?: number
  department_name?: string
  roles: Array<{ id: number; name: string }>
  is_active: boolean
  date_joined: string
}

/** 登录请求参数 */
interface LoginParams {
  username: string
  password: string
}

/** JWT Token 响应 */
interface TokenResponse {
  access: string
  refresh: string
}

/** 资产类型定义 */
interface AssetTypeDefinition {
  id: number
  name: string
  code: string
  icon: string
  fields: Array<{
    name: string
    type: 'string' | 'number' | 'boolean' | 'select' | 'date'
    required: boolean
    options?: string[]
  }>
  list_columns: string[]
  created_at: string
}

/** 位置节点数据 */
interface LocationNode {
  id: number
  name: string
  type: 'region' | 'idc' | 'rack' | 'server'
  parent?: number
  parent_name?: string
  children?: LocationNode[]
  asset_count: number
  created_at: string
}

/** 业务服务节点数据 */
interface BusinessServiceNode {
  id: number
  name: string
  type: 'business_line' | 'application' | 'cluster' | 'service'
  parent?: number
  parent_name?: string
  children?: BusinessServiceNode[]
  asset_count: number
  created_at: string
}

/** 标签数据 */
interface Tag {
  id: number
  key: string
  value: string
  color?: string
  asset_count: number
  created_at: string
}

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

/** 资产详情数据 */
interface AssetDetail {
  id: number
  asset_type: string
  name: string
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

/** 资产关系数据 */
interface Relationship {
  id: number
  source_asset: number
  source_asset_name?: string
  target_asset: number
  target_asset_name?: string
  dependency_type: string
  description?: string
  created_at: string
}

/** 资产变更日志 */
interface AssetChangeLog {
  id: number
  asset: number
  asset_name?: string
  action: 'create' | 'update' | 'delete'
  field_name?: string
  old_value?: string
  new_value?: string
  operator: number
  operator_name?: string
  created_at: string
}

/** 资产发现请求 */
interface AssetDiscoverRequest {
  discover_type: 'ip_range' | 'cloud_account' | ' import'
  config: Record<string, any>
}

/** 云账号数据 */
interface CloudAccount {
  id: number
  provider: 'aliyun' | 'aws' | 'tencent' | 'huawei' | 'azure' | 'gcp'
  provider_display?: string
  name: string
  account_id: string
  access_key?: string
  secret_key?: string
  region?: string
  description?: string
  is_active: boolean
  last_sync_at?: string
  created_at: string
}

/** GitLab 实例数据 */
interface GitLabInstance {
  id: number
  name: string
  url: string
  access_token?: string
  is_active: boolean
  created_at: string
}

/** GitLab 项目数据 */
interface Project {
  id: number
  instance: number
  instance_name?: string
  gitlab_id: number
  name: string
  path_with_namespace: string
  web_url: string
  default_branch: string
  last_activity_at?: string
  created_at: string
}

/** GitLab 合并请求数据 */
interface MergeRequest {
  id: number
  project: number
  project_name?: string
  project_path?: string
  gitlab_id: number
  title: string
  source_branch: string
  target_branch: string
  state: 'opened' | 'closed' | 'merged'
  author: string
  assignee?: string
  review_status: 'pending' | 'approved' | 'rejected'
  pipeline_status?: 'running' | 'success' | 'failed' | 'canceled' | 'pending'
  web_url: string
  created_at: string
  updated_at: string
}

/** Ansible 控制节点数据 */
interface AnsibleServer {
  id: number
  name: string
  host: string
  ssh_port: number
  ssh_user: string
  ssh_password?: string
  private_key_path?: string
  description?: string
  is_active: boolean
  created_at: string
}

/** Ansible 剧本数据 */
interface Playbook {
  id: number
  name: string
  playbook_path: string
  description?: string
  variables?: string
  created_by: number
  created_by_username?: string
  task_count: number
  created_at: string
  updated_at: string
}

/** Ansible 执行记录数据 */
interface TaskRecord {
  id: number
  playbook: number
  playbook_name?: string
  server: number
  server_name?: string
  target_hosts: string
  variables?: string
  status: 'pending' | 'running' | 'success' | 'failed'
  executor: string
  output?: string
  error?: string
  started_at: string
  finished_at?: string
  duration?: number
}

/** 工单模板数据 */
interface TicketTemplate {
  id: number
  name: string
  code: string
  description?: string
  approvers?: string
  approval_steps: number
  variables?: string
  is_active: boolean
  ticket_count: number
  created_at: string
}

/** 审批步骤数据 */
interface ApprovalStep {
  id: number
  ticket: number
  step: number
  approver: number
  approver_name?: string
  status: 'pending' | 'approved' | 'rejected'
  status_display?: string
  comment?: string
  created_at: string
  completed_at?: string
  records: ApprovalRecord[]
}

/** 审批记录数据 */
interface ApprovalRecord {
  id: number
  step: number
  operator: number
  operator_name?: string
  action: 'approve' | 'reject'
  action_display?: string
  comment?: string
  created_at: string
}

/** 发布单数据 */
interface ReleaseOrder {
  id: number
  title: string
  description?: string
  jenkins_job: number
  jenkins_job_name?: string
  jenkins_instance_name?: string
  job_parameters: Record<string, any>
  execute_mode: 'manual' | 'scheduled'
  scheduled_time?: string
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'executing' | 'success' | 'failed' | 'closed'
  status_display?: string
  applicant: number
  applicant_name?: string
  current_step: number
  approval_steps: ApprovalStep[]
  release_records: ReleaseRecord[]
  created_at: string
  updated_at: string
  closed_at?: string
}

/** 发布执行记录数据 */
interface ReleaseRecord {
  id: number
  release_order: number
  release_order_title?: string
  build_record?: number
  build_record_id?: number
  executor: string
  result?: 'success' | 'failure' | 'aborted'
  output?: string
  started_at: string
  finished_at?: string
}

/** 工单数据 */
interface Ticket {
  id: number
  title: string
  template: number
  template_name?: string
  applicant: number
  applicant_name?: string
  description: string
  variables?: string
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'closed'
  status_display?: string
  current_step: number
  approval_steps: ApprovalStep[]
  created_at: string
  updated_at: string
  closed_at?: string
}

/** 创建 Axios 实例 */
const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
})

/**
 * 请求拦截器 - 自动附加 JWT Token
 * @description 从 localStorage 获取 Token 并附加到 Authorization 头
 * @param config - Axios 请求配置对象
 * @returns 处理后的请求配置
 */
api.interceptors.request.use(
  (config: AxiosRequestConfig): AxiosRequestConfig => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError): Promise<never> => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器 - 统一错误处理
 * @description 处理响应错误，401 时清除 Token 并跳转登录页，其他错误显示提示信息
 * @param response - Axios 响应对象
 * @returns 成功响应或错误
 */
api.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    return response
  },
  (error: AxiosError): Promise<never> => {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data as { detail?: string }

      // 401 未授权 - 清除 Token 并跳转登录页
      if (status === 401) {
        localStorage.removeItem('token')
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else {
        // 其他错误显示后端返回的错误信息
        ElMessage.error(data.detail || '请求失败')
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      // 请求配置出错
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

// 导出 API 实例和相关类型
export {
  api,
  ApiConfig,
  AuthUser,
  LoginParams,
  TokenResponse,
  // CMDB 相关
  AssetTypeDefinition,
  LocationNode,
  BusinessServiceNode,
  Tag,
  CloudAccount,
  AssetListItem,
  AssetDetail,
  Relationship,
  AssetChangeLog,
  AssetDiscoverRequest,
  // 工单相关
  TicketTemplate,
  Ticket,
  ApprovalStep,
  ApprovalRecord,
  // 发布单相关
  ReleaseOrder,
  ReleaseRecord
}

export default api
