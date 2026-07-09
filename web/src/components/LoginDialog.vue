<template>
  <a-modal
    v-model:visible="frontUserStore.loginVisible"
    :footer="false"
    :header="false"
    :closable="false"
    :width="780"
    align-center
    class="custom-login-modal"
    :body-style="{ padding: 0, overflow: 'visible' }"
  >
    <div class="split-login-container">
      
      <!-- Custom External Close Button (Floating on the top right) -->
      <button class="custom-close-btn" @click="frontUserStore.hideLogin()">
        <icon-close :style="{ fontSize: '18px', color: '#fff' }" />
      </button>

      <!-- Left Column: Premium 3D Banner -->
      <div class="login-banner-side">
        <!-- Brand logo overlay -->
        <div class="banner-logo">
          <div class="brand-icon-wrap">
            <icon-apps :style="{ fontSize: '20px', color: '#fff' }" />
          </div>
          <span class="brand-title-text">迅捷大屏</span>
        </div>

        <!-- Banner Slogan content -->
        <div class="banner-content">
          <h2 class="slogan-title">迅捷大屏，适合产研团队的</h2>
          <h2 class="slogan-title highlight">可视化协作与大屏设计平台</h2>
          
          <div class="feature-bullets">
            <span class="bullet-item">集 AI生成 · 3D地图 · 低代码拖拽 · 数据流于一体</span>
          </div>

          <div class="banner-footer">
            产研团队的智能大屏协作之选
          </div>
        </div>
      </div>

      <!-- Right Column: Form Panel -->
      <div class="login-form-side">
        <div class="form-container">
          <h3 class="form-title">登录迅捷账号</h3>
          <p class="form-subtitle">未注册手机号/邮箱登录时将自动创建迅捷账号</p>

          <!-- Form inputs -->
          <div class="input-fields-group" style="margin-top: 16px;">
            <!-- Username/Phone/Email input -->
            <div class="custom-input-wrap">
              <input 
                type="text" 
                v-model="loginForm.username" 
                placeholder="请输入用户名 (admin / editor)" 
                class="custom-text-input" 
              />
            </div>

            <!-- Password Input -->
            <div class="custom-input-wrap password-wrap">
              <input 
                :type="showPass ? 'text' : 'password'" 
                v-model="loginForm.password" 
                placeholder="请输入密码 (123456)" 
                class="custom-text-input" 
              />
              <span class="password-toggle" @click="showPass = !showPass">
                <icon-eye-invisible v-if="!showPass" />
                <icon-eye v-else />
              </span>
            </div>
          </div>

          <!-- Terms Agreement -->
          <div class="terms-agreement">
            <label class="checkbox-container">
              <input type="checkbox" v-model="agreeTerms" />
              <span class="checkmark"></span>
              <span class="terms-text">
                我已阅读并同意 <a href="javascript:void(0)" @click.stop="showTerms('service')">使用协议</a> 及 <a href="javascript:void(0)" @click.stop="showTerms('privacy')">隐私政策</a>
              </span>
            </label>
          </div>

          <!-- Submit Button -->
          <button 
            type="button"
            class="submit-login-btn" 
            :disabled="loading" 
            @click="handleSubmit"
          >
            <span v-if="!loading">立即登录/注册</span>
            <span v-else>正在登录...</span>
          </button>



        </div>
      </div>
    </div>
  </a-modal>

  <!-- Slider Captcha Modal for Front User Login -->
  <a-modal
    v-model:visible="captchaVisible"
    title="安全验证"
    :width="340"
    :footer="false"
    align-center
    destroy-on-close
    :mask-closable="false"
    class="captcha-dialog-wrap"
  >
    <div class="captcha-body" v-loading="captchaLoading">
      <div class="image-area" v-if="captchaData">
        <!-- Main background image -->
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
          <icon-check-circle-fill v-if="verificationStatus === 'success'" />
          <icon-close-circle-fill v-else-if="verificationStatus === 'error'" />
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
            <icon-right />
          </div>
          <span class="slider-text" v-if="sliderValue === 0">向右拖动滑块完成拼图</span>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useFrontUserStore } from '../store/frontUser'
import { getCaptcha, checkCaptcha } from '../api/frontAuth'
import { ElMessage } from 'element-plus'
import CryptoJS from 'crypto-js'

const frontUserStore = useFrontUserStore()
const loading = ref(false)

const agreeTerms = ref(false)
const showPass = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  captchaVerification: ''
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

// Fetch Captcha challenge
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
    console.error('Fetch captcha error:', err)
  } finally {
    captchaLoading.value = false
  }
}

// QR Code / Social / Terms simulation clicks
const showTerms = (type: 'service' | 'privacy') => {
  ElMessage.info(type === 'service' ? '使用协议详情' : '隐私政策详情')
}

// Submit Form Action
const handleSubmit = async () => {
  if (!agreeTerms.value) {
    ElMessage.warning('请先勾选并同意《使用协议》和《隐私政策》')
    return
  }

  if (!loginForm.username) {
    ElMessage.warning('请输入用户名')
    return
  }

  if (!loginForm.password) {
    ElMessage.warning('请输入密码')
    return
  }

  // Execute real backend login flow
  loading.value = true
  try {
    await frontUserStore.login({
      username: loginForm.username,
      password: loginForm.password,
      captchaVerification: loginForm.captchaVerification
    })
    ElMessage.success('登录成功')
  } catch (err: any) {
    if (err.response && err.response.status === 428) {
      loginForm.captchaVerification = ''
      captchaVisible.value = true
      fetchCaptcha()
    }
  } finally {
    loading.value = false
  }
}

// Drag captcha events
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
    e.preventDefault()
  }
  const currentX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const deltaX = currentX - startX
  // Track size: 280px (container) - 47px (jigsaw) = 233px
  sliderValue.value = Math.max(0, Math.min(233, deltaX))
}

async function endDrag() {
  if (!isDragging) return
  isDragging = false
  
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('mouseup', endDrag)
  document.removeEventListener('touchend', endDrag)
  
  if (!captchaData.value) return

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
      
      setTimeout(() => {
        captchaVisible.value = false
        handleSubmit()
      }, 800)
    } else {
      verificationStatus.value = 'error'
      setTimeout(() => {
        fetchCaptcha()
      }, 1000)
    }
  } catch (err) {
    console.error('Verify captcha error:', err)
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
/* Reset Arco Dialog Container styles */
:deep(.custom-login-modal .arco-modal) {
  background: transparent !important;
  box-shadow: none !important;
  overflow: visible !important;
}

/* Master Container Grid */
.split-login-container {
  display: flex;
  width: 780px;
  height: 480px;
  background-color: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
}

/* Floating semi-transparent close button */
.custom-close-btn {
  position: absolute;
  top: 12px;
  right: -48px; /* placed outside right border */
  width: 36px;
  height: 36px;
  background-color: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s;
  box-sizing: border-box;
}

.custom-close-btn:hover {
  background-color: rgba(15, 23, 42, 0.85);
  transform: rotate(90deg);
}

/* Left side banner decoration */
.login-banner-side {
  width: 320px;
  flex-shrink: 0;
  background-image: linear-gradient(rgba(0, 0, 0, 0.05), rgba(0, 0, 0, 0.25)), url('/login_banner.png');
  background-size: cover;
  background-position: center;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  color: #ffffff;
}

.banner-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon-wrap {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #4f46e5 0%, #ec4899 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-title-text {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #ffffff;
}

.banner-content {
  margin-top: auto;
  margin-bottom: 24px;
}

.slogan-title {
  font-size: 20px;
  font-weight: 800;
  line-height: 1.35;
  margin: 0;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.slogan-title.highlight {
  color: #e0e7ff;
}

.feature-bullets {
  margin-top: 12px;
  font-size: 12px;
  opacity: 0.85;
}

.banner-footer {
  margin-top: 24px;
  font-size: 11px;
  opacity: 0.6;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 12px;
}

/* Right side forms area */
.login-form-side {
  flex: 1;
  position: relative;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  box-sizing: border-box;
}

/* Corner QR code button styling */
.qr-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  cursor: pointer;
  overflow: hidden;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-icon-svg {
  width: 28px;
  height: 28px;
  z-index: 12;
  position: absolute;
  top: 10px;
  right: 10px;
  transition: transform 0.25s;
}

.qr-corner:hover .qr-icon-svg {
  transform: scale(1.08);
}

/* Diagonal cut corner for scan decoration */
.qr-corner-bg {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 80px;
  height: 80px;
  background-color: #f1f5f9;
  transform: rotate(45deg);
  z-index: 8;
}

.form-container {
  width: 100%;
  max-width: 340px;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 6px 0;
}

.form-subtitle {
  font-size: 12px;
  color: #86909c;
  margin: 0 0 24px 0;
}

/* Toggle Pills styling */
.login-tabs-pill {
  display: flex;
  background-color: #f2f3f5;
  border-radius: 8px;
  padding: 3px;
  margin-bottom: 20px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 13px;
  font-weight: 500;
  color: #4e5969;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  user-select: none;
}

.tab-item.active {
  background-color: #ffffff;
  color: #1d2129;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

/* Custom rounded inputs fields */
.input-fields-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.custom-input-wrap {
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

.custom-text-input {
  width: 100%;
  height: 42px;
  background-color: #f2f3f5;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 0 16px;
  font-size: 14px;
  color: #1D2129;
  transition: all 0.15s ease;
  outline: none;
  box-sizing: border-box;
}

.custom-text-input:hover {
  background-color: #eaebed;
}

.custom-text-input:focus {
  background-color: #ffffff;
  border-color: #2f6bf7;
  box-shadow: 0 0 0 3px rgba(47, 107, 247, 0.12);
}

/* Code button placement inside input wrapper */
.verification-code-wrap {
  display: flex;
  align-items: center;
}

.verification-code-wrap .custom-text-input {
  padding-right: 100px;
}

.get-code-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #2f6bf7;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  outline: none;
  transition: opacity 0.2s;
}

.get-code-btn:hover {
  opacity: 0.8;
}

.get-code-btn:disabled {
  color: #86909c;
  cursor: not-allowed;
}

/* Password eye positioning */
.password-wrap .custom-text-input {
  padding-right: 40px;
}

.password-toggle {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #86909c;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
}

.password-toggle:hover {
  color: #4e5969;
}

/* Agreement checkbox styling */
.terms-agreement {
  margin-bottom: 20px;
}

.checkbox-container {
  display: flex;
  align-items: flex-start;
  position: relative;
  cursor: pointer;
  user-select: none;
  font-size: 12px;
  color: #86909c;
  line-height: 1.4;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  height: 15px;
  width: 15px;
  background-color: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-radius: 4px;
  margin-top: 1px;
  margin-right: 8px;
  flex-shrink: 0;
  display: inline-block;
  position: relative;
  transition: all 0.15s;
  box-sizing: border-box;
}

.checkbox-container:hover input ~ .checkmark {
  border-color: #2f6bf7;
}

.checkbox-container input:checked ~ .checkmark {
  background-color: #2f6bf7;
  border-color: #2f6bf7;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 4.5px;
  top: 1.5px;
  width: 3.5px;
  height: 7px;
  border: solid white;
  border-width: 0 2.2px 2.2px 0;
  transform: rotate(45deg);
}

.terms-text a {
  color: #2f6bf7;
  text-decoration: none;
  font-weight: 500;
}

.terms-text a:hover {
  text-decoration: underline;
}

/* Blue login button */
.submit-login-btn {
  width: 100%;
  height: 44px;
  background-color: #2f6bf7;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(47, 107, 247, 0.2);
}

.submit-login-btn:hover {
  background-color: #1e59e6;
  box-shadow: 0 6px 16px rgba(47, 107, 247, 0.3);
}

.submit-login-btn:disabled {
  background-color: #a0c0f9;
  cursor: not-allowed;
  box-shadow: none;
}

/* Divider styling */
.third-party-divider {
  display: flex;
  align-items: center;
  margin: 28px 0 20px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background-color: #f1f3f5;
}

.divider-text {
  font-size: 11px;
  color: #c9cdd4;
  padding: 0 12px;
  user-select: none;
}

/* Social icons layout */
.social-login-group {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.social-btn {
  width: 38px;
  height: 38px;
  border: 1px solid #e5e6eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s;
}

.social-btn:hover {
  background-color: #f8fafc;
  transform: translateY(-1.5px);
  border-color: #cbd5e1;
}

/* Slide Captcha Modal Styles */
.captcha-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
}

.image-area {
  position: relative;
  width: 280px;
  height: 140px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  background-color: #f3f4f6;
}

.bg-img {
  width: 280px;
  height: 140px;
  display: block;
}

.jigsaw-piece {
  position: absolute;
  top: 0;
  width: 42px;
  height: 140px;
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
  font-size: 14px;
  font-weight: 600;
  z-index: 20;
  color: white;
}

.status-overlay.success {
  background-color: rgba(46, 204, 113, 0.9);
}

.status-overlay.error {
  background-color: rgba(231, 76, 60, 0.9);
}

.slider-container {
  width: 280px;
  margin-top: 16px;
}

.slider-track {
  position: relative;
  width: 100%;
  height: 36px;
  background-color: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
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
  background-color: rgba(79, 70, 229, 0.12);
  border-radius: 18px 0 0 18px;
}

.slider-handle {
  position: absolute;
  top: 0;
  width: 44px;
  height: 34px;
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 18px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: grab;
  z-index: 5;
  color: #4f46e5;
  font-size: 14px;
}

.slider-handle:hover {
  background-color: #4f46e5;
  color: #ffffff;
  border-color: #4f46e5;
}

.slider-handle:active {
  cursor: grabbing;
}

.slider-text {
  font-size: 11px;
  color: #9ca3af;
  user-select: none;
  z-index: 1;
}

:deep(.captcha-dialog-wrap) {
  border-radius: 16px;
}

@media (max-width: 820px) {
  .login-banner-side {
    display: none;
  }
  :deep(.custom-login-modal .arco-modal) {
    width: 440px !important;
  }
  .split-login-container {
    width: 440px;
  }
  .custom-close-btn {
    right: 12px;
    top: 12px;
    background-color: rgba(15, 23, 42, 0.15);
    border-color: rgba(15, 23, 42, 0.1);
  }
  .custom-close-btn:hover {
    background-color: rgba(15, 23, 42, 0.3);
  }
}
</style>
