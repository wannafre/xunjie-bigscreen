<template>
  <header class="landing-header">
    <div class="header-content">
      <div class="brand">
        <div class="logo-icon">
          <icon-apps :style="{ fontSize: '24px', color: '#fff' }" />
        </div>
        <span class="brand-name">迅捷大屏</span>
        <span class="brand-badge">Beta</span>
      </div>
      <nav class="nav-links">
        <a href="#features" class="nav-link">产品功能</a>
        <a href="#mockup" class="nav-link">编辑器预览</a>
        <a href="#templates" class="nav-link">大屏模板</a>
        <a href="#help" class="nav-link">帮助中心</a>
      </nav>
      <div class="header-actions">
        <template v-if="frontUserStore.frontToken">
          <span class="user-greeting">你好，{{ frontUserStore.username || '体验用户' }}</span>
          <a-button type="primary" shape="round" class="console-btn" @click="handleConsoleClick">
            个人空间
            <icon-right />
          </a-button>
          <a-button type="text" class="login-btn" @click="handleLogout">退出登录</a-button>
        </template>
        <template v-else>
          <a-button type="text" class="login-btn" @click="handleLoginClick">登录</a-button>
          <a-button type="primary" shape="round" class="register-btn" @click="handleLoginClick">
            免费使用
          </a-button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useFrontUserStore } from '../../../store/frontUser'
import { ElMessage } from 'element-plus'

const frontUserStore = useFrontUserStore()

onMounted(() => {
  if (frontUserStore.frontToken && !frontUserStore.username) {
    frontUserStore.getInfo().catch(() => {
      frontUserStore.clearToken()
    })
  }
})

function handleLoginClick() {
  frontUserStore.showLogin()
}

function handleConsoleClick() {
  ElMessage.info('个人工作台正在拼命开发中，敬请期待！')
}

function handleLogout() {
  frontUserStore.logout()
}
</script>

<style scoped>
.landing-header {
  position: sticky;
  top: 0;
  width: 100%;
  height: 72px;
  background-color: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(229, 230, 235, 0.6);
  z-index: 1000;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #4f46e5 0%, #ec4899 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);
}

.brand-name {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-badge {
  font-size: 10px;
  background-color: #f3f4f6;
  color: #6b7280;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-link {
  font-size: 14px;
  color: #4e5969;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #4f46e5;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-greeting {
  font-size: 14px;
  color: #4e5969;
}

.console-btn {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
  color: #fff !important;
  border: none !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
  transition: all 0.3s !important;
}

.console-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
}

.login-btn {
  color: #4e5969 !important;
  font-weight: 500 !important;
}

.login-btn:hover {
  color: #4f46e5 !important;
}

.register-btn {
  background-color: #f3f4f6 !important;
  color: #1f2937 !important;
  border: 1px solid #e5e6eb !important;
  font-weight: 600 !important;
  transition: all 0.2s !important;
}

.register-btn:hover {
  background-color: #e5e6eb !important;
  color: #000 !important;
}

@media (max-width: 992px) {
  .nav-links { display: none; }
}
</style>
