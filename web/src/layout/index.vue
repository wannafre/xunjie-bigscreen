<template>
  <a-layout class="layout-container">
    <AppSidebar
      :collapsed="isCollapse"
      :menus="menuList"
      :active-menu="activeMenu"
      :default-open-keys="defaultOpenKeys"
      @menu-click="handleMenuClick"
    />

    <a-layout class="main-layout">
      <AppHeader
        :collapsed="isCollapse"
        :system-title="settings.title"
        :current-title="currentRouteTitle"
        :user-info="userStore"
        :unread-count="unreadCount"
        :notice-list="noticeList"
        @toggle-collapse="isCollapse = !isCollapse"
        @mark-all-read="handleMarkAllRead"
        @view-notice="handleViewNotice"
        @go-notification-center="goToNotificationCenter"
        @profile="goToProfile"
        @logout="handleLogout"
      />

      <a-scrollbar class="main-scrollbar" outer-style="flex: 1; min-height: 0">
        <a-layout-content class="app-main">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </a-layout-content>
      </a-scrollbar>
    </a-layout>
  </a-layout>

  <DetailModal v-model:visible="detailModalVisible" :notification="selectedNotice || undefined" />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { settings } from '../config/settings'
import { useUserStore } from '../store/user'
import DetailModal from '../components/Notification/DetailModal.vue'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import { useLayoutMenu } from './composables/useLayoutMenu'
import { useNoticeCenter } from './composables/useNoticeCenter'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)

const {
  menuList,
  defaultOpenKeys,
  activeMenu,
  currentRouteTitle,
  fetchMenus,
  handleMenuClick
} = useLayoutMenu(router, route)

const {
  unreadCount,
  noticeList,
  detailModalVisible,
  selectedNotice,
  fetchUnreadCount,
  fetchNotices,
  handleMarkAllRead,
  handleViewNotice
} = useNoticeCenter()

function goToNotificationCenter() {
  router.push('/notification')
}

function goToProfile() {
  router.push('/system/account')
}

async function handleLogout() {
  await userStore.logout()
  Message.success('已安全退出登录')
  router.push('/login')
}

onMounted(() => {
  fetchMenus()
  fetchUnreadCount()
  fetchNotices()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background: #edf2f8;
  overflow: hidden;
}

.main-layout {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(180deg, #edf2f8 0%, #f4f7fb 100%);
}

.main-layout::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 80% 6%, rgba(37, 99, 235, 0.08), transparent 28%),
    radial-gradient(circle at 26% 90%, rgba(14, 165, 233, 0.08), transparent 30%);
}

.main-scrollbar {
  position: relative;
  height: 100%;
  overflow: auto;
}

.app-main {
  position: relative;
  min-height: calc(100vh - 84px);
  padding: 22px 24px 30px;
  background: transparent;
  box-sizing: border-box;
  color: #172033;
}

.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.22s ease-out;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
