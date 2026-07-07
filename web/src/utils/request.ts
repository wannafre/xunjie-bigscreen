import axios from 'axios'
import { ElMessage } from 'element-plus'

// Create an axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || '/api/v1', // api base_url
  timeout: 10000 // request timeout
})

// Request interceptor
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      // Configure Authorization header as Bearer token
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  response => {
    const res = response.data
    return res
  },
  error => {
    console.error('Response error:', error.response)
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
    
    // Unauthorized or token expired
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      ElMessage.error('登录过期，请重新登录')
      // Redirect to login page
      setTimeout(() => {
        window.location.hash = '#/login'
      }, 1000)
    } else if (error.response && error.response.status === 428) {
      // Captcha challenge required, bypass global error message to handle in the login view
    } else {
      ElMessage.error(message)
    }
    
    return Promise.reject(error)
  }
)

export default service
