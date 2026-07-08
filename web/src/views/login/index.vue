<template>
  <div class="login-container">
    <!-- Clean, modern decorative background -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
    </div>
    
    <div class="login-card">
      <div class="brand">
        <div class="logo-box">
          <!-- Shield logo matching the screenshot style -->
          <svg viewBox="0 0 24 24" width="32" height="32" class="shield-logo">
            <path fill="currentColor" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path fill="white" d="M12 4.3l5.5 2.1v4.8c0 4-4.2 7.1-5.5 8.1-1.3-1-5.5-4.1-5.5-8.1V6.4L12 4.3z"/>
            <path fill="currentColor" d="M11 7h2v5h-2zm0 6h2v2h-2z"/>
          </svg>
        </div>
        <h1 class="brand-title">{{ settings.titleSuffix }}</h1>
        <p class="brand-subtitle">{{ settings.subtitleEnglish }}</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" @keyup.enter="handleLogin" label-position="top">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名 (admin / editor)" 
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            :prefix-icon="Lock"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleLogin" 
            class="submit-btn" 
            size="large"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="tips-box">
        <p>默认账号: <span class="badge">admin</span> 密码: <span class="badge">123456</span></p>
      </div>
    </div>

    <!-- Interactive Slider Captcha Dialog -->
    <el-dialog
      v-model="captchaVisible"
      title="安全验证"
      width="360px"
      align-center
      destroy-on-close
      :close-on-click-modal="false"
      class="captcha-dialog"
    >
      <div class="captcha-content" v-loading="captchaLoading">
        <div class="image-area" v-if="captchaData">
          <!-- Main background image with target slot -->
          <img 
            :src="'data:image/jpeg;base64,' + captchaData.originalImageBase64" 
            class="bg-img" 
            alt="captcha-bg" 
          />
          <!-- Jigsaw piece moving with slider -->
          <img 
            :src="'data:image/png;base64,' + captchaData.jigsawImageBase64" 
            class="jigsaw-piece" 
            :style="{ left: sliderValue + 'px' }" 
            alt="jigsaw" 
          />
          
          <!-- Validation result status overlay -->
          <div v-if="verificationStatus !== 'idle'" :class="['status-overlay', verificationStatus]">
            <el-icon v-if="verificationStatus === 'success'"><CircleCheck /></el-icon>
            <el-icon v-else-if="verificationStatus === 'error'"><CircleClose /></el-icon>
            <span>{{ verificationStatus === 'success' ? '验证通过' : '验证失败，请重试' }}</span>
          </div>
        </div>

        <!-- Interactive slider track -->
        <div class="slider-container" v-if="captchaData">
          <div class="slider-track">
            <div class="slider-bar" :style="{ width: sliderValue + 'px' }"></div>
            <div 
              class="slider-handle" 
              :style="{ left: sliderValue + 'px' }"
              @mousedown="startDrag"
              @touchstart="startDrag"
            >
              <el-icon><Right /></el-icon>
            </div>
            <span class="slider-text" v-if="sliderValue === 0">向右拖动滑块填充拼图</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { settings } from '../../config/settings'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../store/user'
import { getCaptcha, checkCaptcha } from '../../api/captcha'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock, Right, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import CryptoJS from 'crypto-js'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  captchaVerification: ''
})

const rules = reactive<FormRules>({
  username: [{ required: true, trigger: 'blur', message: '请输入用户名' }],
  password: [{ required: true, trigger: 'blur', message: '请输入密码' }]
})

// Slider Captcha States
const captchaVisible = ref(false)
const captchaLoading = ref(false)
const captchaData = ref<any>(null)
const sliderValue = ref(0)
const verificationStatus = ref<'idle' | 'success' | 'error'>('idle')

let isDragging = false
let startX = 0

// AES Encryption for Captcha coordinate
function encryptPointJson(pointJsonStr: string, secretKey: string): string {
  const key = CryptoJS.enc.Utf8.parse(secretKey)
  const srcs = CryptoJS.enc.Utf8.parse(pointJsonStr)
  const encrypted = CryptoJS.AES.encrypt(srcs, key, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  })
  return encrypted.toString()
}

// Fetch Captcha challenge from backend
async function fetchCaptcha() {
  captchaLoading.value = true
  try {
    const res: any = await getCaptcha({ captchaType: 'blockPuzzle' })
    if (res.repCode === '0000' && res.repData) {
      captchaData.value = res.repData
      sliderValue.value = 0
      verificationStatus.value = 'idle'
    } else {
      ElMessage.error(res.repMsg || '获取验证码失败')
    }
  } catch (err) {
    console.error(err)
  } finally {
    captchaLoading.value = false
  }
}

// Main Login Action
const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login({
          username: loginForm.username,
          password: loginForm.password,
          captchaVerification: loginForm.captchaVerification
        })
        ElMessage.success('登录成功')
        const redirect = (route.query.redirect as string) || '/manager'
        router.push({ path: redirect })
      } catch (err: any) {
        // Capture 428 status code indicating Captcha challenge is required
        if (err.response && err.response.status === 428) {
          loginForm.captchaVerification = ''
          captchaVisible.value = true
          fetchCaptcha()
        }
      } finally {
        loading.value = false
      }
    }
  })
}

// Drag & Drop slider logic
function startDrag(e: MouseEvent | TouchEvent) {
  if (verificationStatus.value === 'success' || captchaLoading.value) return
  isDragging = true
  startX = 'touches' in e ? e.touches[0].clientX : e.clientX
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('mouseup', endDrag)
  document.addEventListener('touchend', endDrag)
}

function onDrag(e: MouseEvent | TouchEvent) {
  if (!isDragging) return
  if ('touches' in e) {
    e.preventDefault() // Prevent mobile scrolling while dragging
  }
  const currentX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const deltaX = currentX - startX
  
  // Track size: container width (310px) - jigsaw piece width (47px) = 263px max sliding space
  sliderValue.value = Math.max(0, Math.min(263, deltaX))
}

async function endDrag() {
  if (!isDragging) return
  isDragging = false
  
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('mouseup', endDrag)
  document.removeEventListener('touchend', endDrag)
  
  if (!captchaData.value) return

  // Validate current slider position
  captchaLoading.value = true
  try {
    const pointJson = JSON.stringify({ x: sliderValue.value, y: 5 })
    const encryptedPoint = encryptPointJson(pointJson, captchaData.value.secretKey)
    
    const res: any = await checkCaptcha({
      captchaType: 'blockPuzzle',
      pointJson: encryptedPoint,
      token: captchaData.value.token
    })
    
    if (res.repCode === '0000') {
      verificationStatus.value = 'success'
      loginForm.captchaVerification = captchaData.value.token
      
      // Auto close and submit login upon success
      setTimeout(() => {
        captchaVisible.value = false
        handleLogin()
      }, 800)
    } else {
      verificationStatus.value = 'error'
      // Refresh puzzle after a brief delay on failure
      setTimeout(() => {
        fetchCaptcha()
      }, 1000)
    }
  } catch (err) {
    console.error(err)
    verificationStatus.value = 'error'
    setTimeout(() => {
      fetchCaptcha()
    }, 1000)
  } finally {
    captchaLoading.value = false
  }
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('mouseup', endDrag)
  document.removeEventListener('touchend', endDrag)
})
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background: radial-gradient(circle at 80% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 20% 80%, rgba(79, 70, 229, 0.12) 0%, transparent 50%),
              #f8fafc;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Dynamic design background circles */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%);
  filter: blur(40px);
}

.circle-1 {
  top: -10%;
  right: -5%;
  width: 600px;
  height: 600px;
}

.circle-2 {
  bottom: -15%;
  left: -10%;
  width: 700px;
  height: 700px;
}

/* Login card */
.login-card {
  position: relative;
  z-index: 2;
  width: 420px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.06), 0 1px 3px rgba(0, 0, 0, 0.02);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.login-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 48px rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.25);
}

.brand {
  text-align: center;
  margin-bottom: 36px;
}

.logo-box {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border-radius: 16px;
  margin-bottom: 16px;
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.25);
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 6px 0;
  letter-spacing: 0.5px;
}

.brand-subtitle {
  font-size: 12px;
  font-weight: 500;
  color: #9ca3af;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Custom inputs */
:deep(.el-input__wrapper) {
  background-color: #f3f4f6 !important;
  box-shadow: none !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 12px;
  padding: 8px 16px;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #d1d5db !important;
}

:deep(.el-input__wrapper.is-focus) {
  background-color: #ffffff !important;
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
}

:deep(.el-input__inner) {
  font-size: 15px;
  color: #1f2937 !important;
  height: 28px;
}

:deep(.el-input__icon) {
  color: #9ca3af;
  font-size: 18px;
}

/* Submit button */
.submit-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.22);
  transition: all 0.2s ease;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.submit-btn:active {
  transform: translateY(0);
}

.tips-box {
  margin-top: 24px;
  text-align: center;
  font-size: 13px;
  color: #6b7280;
}

.badge {
  background: #e0e7ff;
  color: #4f46e5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: bold;
}

/* Captcha dialog styles */
:deep(.captcha-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.captcha-dialog .el-dialog__header) {
  margin-right: 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.captcha-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
}

.image-area {
  position: relative;
  width: 310px;
  height: 155px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  background-color: #f3f4f6;
}

.bg-img {
  width: 310px;
  height: 155px;
  display: block;
}

.jigsaw-piece {
  position: absolute;
  top: 0;
  width: 47px;
  height: 155px;
  display: block;
  z-index: 10;
  cursor: grab;
}

.jigsaw-piece:active {
  cursor: grabbing;
}

.status-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  z-index: 20;
  color: white;
  animation: fadeIn 0.2s ease;
}

.status-overlay.success {
  background-color: rgba(46, 204, 113, 0.9);
}

.status-overlay.error {
  background-color: rgba(231, 76, 60, 0.9);
}

/* Slider Track */
.slider-container {
  width: 310px;
  margin-top: 20px;
}

.slider-track {
  position: relative;
  width: 100%;
  height: 40px;
  background-color: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.slider-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background-color: rgba(99, 102, 241, 0.15);
  border-radius: 20px 0 0 20px;
}

.slider-handle {
  position: absolute;
  top: 0;
  width: 47px;
  height: 38px;
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: grab;
  z-index: 5;
  color: #6366f1;
  font-size: 16px;
  transition: background-color 0.1s;
}

.slider-handle:hover {
  background-color: #6366f1;
  color: #ffffff;
  border-color: #6366f1;
}

.slider-handle:active {
  cursor: grabbing;
}

.slider-text {
  font-size: 12px;
  color: #9ca3af;
  user-select: none;
  z-index: 1;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
