<!--
  创建发布单页面
  @description 创建发布单页面，用于选择 Jenkins Job、填写参数和选择审批人。
-->
<template>
  <div class="release-order-create-container">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="release-form">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入发布标题" />
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入发布描述" />
      </el-form-item>

      <el-form-item label="Jenkins Job" prop="jenkins_job">
        <el-select v-model="form.jenkins_job" placeholder="请选择 Jenkins Job" style="width: 100%">
          <el-option
            v-for="job in jobs"
            :key="job.id"
            :label="`${job.instance_name} / ${job.name}`"
            :value="job.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="执行模式" prop="execute_mode">
        <el-radio-group v-model="form.execute_mode">
          <el-radio value="manual">手动执行</el-radio>
          <el-radio value="scheduled">定时执行</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item v-if="form.execute_mode === 'scheduled'" label="定时时间" prop="scheduled_time">
        <el-date-picker
          v-model="form.scheduled_time"
          type="datetime"
          placeholder="选择定时发布时间"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="发布参数" prop="job_parameters">
        <el-input
          v-model="jobParametersJson"
          type="textarea"
          :rows="4"
          placeholder='请输入 JSON 格式的发布参数，如 {"version": "1.0.0", "env": "prod"}'
          @blur="validateJson"
        />
      </el-form-item>

      <el-form-item label="审批人" prop="approvers">
        <el-select
          v-model="form.approvers"
          multiple
          placeholder="请选择审批人"
          style="width: 100%"
        >
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.username"
            :value="user.username"
          />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm" :loading="submitting">创建</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import api from '../api'

interface JenkinsJob {
  id: number
  name: string
  instance_name: string
}

interface User {
  id: number
  username: string
}

const router = useRouter()
const formRef = ref<FormInstance>()
const jobs = ref<JenkinsJob[]>([])
const users = ref<User[]>([])
const submitting = ref(false)
const jobParametersJson = ref('{}')

const form = ref({
  title: '',
  description: '',
  jenkins_job: null as number | null,
  execute_mode: 'manual',
  scheduled_time: '',
  approvers: [] as string[]
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入发布标题', trigger: 'blur' }],
  jenkins_job: [{ required: true, message: '请选择 Jenkins Job', trigger: 'change' }],
  execute_mode: [{ required: true, message: '请选择执行模式', trigger: 'change' }],
  approvers: [{ required: true, message: '请选择审批人', trigger: 'change', type: 'array' }]
}

const validateJson = (): void => {
  if (!jobParametersJson.value.trim()) {
    return
  }
  try {
    JSON.parse(jobParametersJson.value)
  } catch {
    ElMessage.error('JSON 格式不正确')
  }
}

const fetchJobs = async (): Promise<void> => {
  try {
    const { data } = await api.get<JenkinsJob[]>('/api/cicd/jobs/')
    jobs.value = data
  } catch {
    ElMessage.error('获取 Jenkins Job 列表失败')
  }
}

const fetchUsers = async (): Promise<void> => {
  try {
    const { data } = await api.get<User[]>('/api/users/users/')
    users.value = data
  } catch {
    ElMessage.error('获取用户列表失败')
  }
}

const submitForm = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    let job_parameters = {}
    if (jobParametersJson.value.trim()) {
      try {
        job_parameters = JSON.parse(jobParametersJson.value)
      } catch {
        ElMessage.error('发布参数 JSON 格式不正确')
        return
      }
    }

    await api.post('/api/cicd/release-orders/', {
      title: form.value.title,
      description: form.value.description,
      jenkins_job: form.value.jenkins_job,
      execute_mode: form.value.execute_mode,
      scheduled_time: form.value.scheduled_time,
      job_parameters: job_parameters,
      approvers: form.value.approvers
    })
    ElMessage.success('创建成功')
    router.push('/cicd/release-orders')
  } catch {
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchJobs()
  fetchUsers()
})
</script>

<style scoped>
.release-order-create-container {
  padding: 20px;
  max-width: 800px;
}
.release-form {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}
</style>