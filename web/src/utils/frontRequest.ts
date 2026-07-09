import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useFrontUserStore } from '../store/frontUser'

// Create an axios instance for client/C-side requests
const frontService = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || '/api/v1', // api base_url
  timeout: 10000 // request timeout
})

// Request interceptor
frontService.interceptors.request.use(
  config => {
    const token = localStorage.getItem('front_token')
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  error => {
    console.error('Front request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
frontService.interceptors.response.use(
  response => {
    const res = response.data
    return res
  },
  error => {
    console.error('Front response error:', error.response)
    let message = '请求失败，请稍后重试'
    if (error.response && error.response.data) {
      const detail = error.response.data.detail
      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        message = detail.map(item => item.msg).join(', ')
      } else {
        message = error.response.data.message || message
      }
    }
    
    // Front-end Unauthorized or token expired
    if (error.response && error.response.status === 401) {
      const frontUserStore = useFrontUserStore()
      frontUserStore.clearToken()
      frontUserStore.showLogin()
      ElMessage.error('登录过期，请重新登录')
    } else if (error.response && error.response.status === 428) {
      // Captcha challenge required, bypass global error message to handle in the login component
    } else {
      ElMessage.error(message)
    }
    
    return Promise.reject(error)
  }
)

export default frontService
