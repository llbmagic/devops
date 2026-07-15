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

/** 业务线数据 */
interface BusinessLine {
  id: number
  name: string
  description?: string
  host_count: number
  created_at: string
}

/** 主机数据 */
interface Host {
  id: number
  hostname: string
  ip_address: string
  ssh_port: number
  ssh_user: string
  cpu?: string
  memory?: string
  disk?: string
  status: 'online' | 'offline' | 'maintenance'
  business_line: number
  business_line_name?: string
  cluster?: number
  cluster_name?: string
  cluster_code?: string
  tags: Array<{ id: number; key: string; value: string }>
  tags_detail: Array<{ id: number; key: string; value: string }>
  created_at: string
  updated_at: string
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
  BusinessLine,
  Host
}

export default api
