<template>
  <a-layout class="layout-container">
    <!-- Light-themed Premium Sidebar with Collapse state -->
    <a-layout-sider :collapsible="true" :trigger="null" hide-trigger :width="256" v-model:collapsed="isCollapse"
      class="sidebar-container">
      <div class="sidebar-logo-wrap">
        <!-- Logo shield matching reference -->
        <div class="sidebar-logo-icon">
          <component :is="settings.logoComponent" style="font-size: 20px;" />
        </div>
        <span class="sidebar-logo-text" v-if="!isCollapse">{{ settings.shortTitle }}</span>
      </div>

      <a-menu :selected-keys="[activeMenu]" :collapsed="isCollapse" :default-open-keys="defaultOpenKeys"
        :style="{ width: '100%', flex: 1 }" @menu-item-click="handleMenuClick" theme="light">
        <!-- Static Dashboard Item -->
        <a-menu-item key="/dashboard">
          <template #icon>
            <IconHome />
          </template>
          首页 (Dashboard)
        </a-menu-item>

        <!-- Dynamic Menus fetched from backend -->
        <template v-for="menu in menuList" :key="menu.id">
          <!-- With child items / Submenu -->
          <a-sub-menu v-if="menu.children && menu.children.length > 0" :key="String(menu.id)">
            <template #[getMenuIcon(menu)?'icon':'_none']>
              <component :is="getMenuIcon(menu)" />
            </template>
            <template #title>{{ menu.menu_name }}</template>

            <a-menu-item v-for="child in menu.children" :key="resolvePath(child.path)">
              <template #[getMenuIcon(child)?'icon':'_none']>
                <component :is="getMenuIcon(child)" />
              </template>
              {{ child.menu_name }}
            </a-menu-item>
          </a-sub-menu>

          <!-- Single Menu Item -->
          <a-menu-item v-else :key="resolvePath(menu.path)">
            <!-- prettier-ignore -->
            <template #[getMenuIcon(menu)?'icon':'_none']>
              <component :is="getMenuIcon(menu)" />
            </template>
            {{ menu.menu_name }}
          </a-menu-item>
        </template>
      </a-menu>

      <!-- Sidebar footer matching reference V1.0.0 -->
      <div class="sidebar-version" v-if="!isCollapse">
        系统版本 V1.0.0
      </div>
    </a-layout-sider>

    <a-layout class="main-layout">
      <!-- White top header -->
      <a-layout-header class="header-container">
        <div class="header-left">
          <!-- Fold/Unfold button to toggle sidebar -->
          <component :is="isCollapse ? 'IconMenuUnfold' : 'IconMenuFold'" class="fold-btn"
            @click="isCollapse = !isCollapse" />
          <div class="breadcrumbs">
            <span class="breadcrumb-prefix">{{ settings.title }}</span>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">{{ currentRouteTitle }}</span>
          </div>
        </div>
        <div class="header-right">
          <!-- Header search box -->
          <div class="header-search">
            <a-input-search placeholder="搜索菜单或功能" size="small" class="search-bar" />
          </div>

          <!-- Notification bell -->
          <a-popover trigger="click" position="br" content-class="notice-popover-content" :position-offset="[0, 12]" :show-arrow="false">
            <a-badge :count="unreadCount" :dot="unreadCount > 0" class="notice-badge">
              <IconNotification class="notice-icon" />
            </a-badge>
            <template #content>
              <div class="notice-popover-container">
                <div class="notice-popover-header">
                  <span class="notice-popover-title">通知公告</span>
                  <a-link v-if="unreadCount > 0" @click="handleMarkAllRead">全部已读</a-link>
                </div>
                <a-tabs default-active-key="all" type="line" size="small" class="notice-popover-tabs">
                  <a-tab-pane key="all" title="全部">
                    <a-list :bordered="false" size="small" :split="false">
                      <a-list-item v-for="item in noticeList.slice(0, 5)" :key="item.id" class="notice-popover-item" @click="handleViewNotice(item)">
                        <div class="item-wrap" :class="{ 'item-unread': item.is_read === 0 }">
                          <div class="item-title">{{ item.title }}</div>
                          <div class="item-time">{{ formatDate(item.create_time) }}</div>
                        </div>
                      </a-list-item>
                      <template #empty v-if="noticeList.length === 0">
                        <div class="empty-notices">暂无通知</div>
                      </template>
                    </a-list>
                  </a-tab-pane>
                  <a-tab-pane key="unread" title="未读">
                    <a-list :bordered="false" size="small" :split="false">
                      <a-list-item v-for="item in unreadNoticeList.slice(0, 5)" :key="item.id" class="notice-popover-item" @click="handleViewNotice(item)">
                        <div class="item-wrap item-unread">
                          <div class="item-title">{{ item.title }}</div>
                          <div class="item-time">{{ formatDate(item.create_time) }}</div>
                        </div>
                      </a-list-item>
                      <template #empty v-if="unreadNoticeList.length === 0">
                        <div class="empty-notices">暂无未读通知</div>
                      </template>
                    </a-list>
                  </a-tab-pane>
                </a-tabs>
                <div class="notice-popover-footer">
                  <a-button type="text" size="small" long @click="goToNotificationCenter">查看全部</a-button>
                </div>
              </div>
            </template>
          </a-popover>

          <a-dropdown trigger="click" @select="handleCommand">
            <div class="header-avatar-wrap">
              <a-avatar :key="userStore.avatar" :size="32" style="background-color: #165DFF; color: #fff; font-weight: 600;" :image-url="userStore.avatar">
                {{ userStore.username?.slice(0, 1).toUpperCase() }}
              </a-avatar>
              <span class="user-name">{{ userStore.username }}</span>
              <IconDown style="font-size: 12px; color: #86909C;" />
            </div>
            <template #content>
              <a-doption value="profile">
                <template #icon>
                  <IconUser />
                </template>
                个人中心
              </a-doption>
              <a-doption value="logout" style="color: #F53F3F;">
                <template #icon>
                  <IconExport />
                </template>
                退出登录
              </a-doption>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>

      <a-scrollbar style="height: 100%; overflow: auto;" outer-style="flex: 1; min-height: 0;">
      <a-layout-content class="app-main">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </a-layout-content>
      </a-scrollbar>

      <!-- Footer -->

    </a-layout>
  </a-layout>
  <DetailModal v-model:visible="detailModalVisible" :notification="selectedNotice" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { settings } from '../config/settings'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../store/user'
import { getMenuTree } from '../api/menu'
import { Message } from '@arco-design/web-vue'
import {
  IconHome, IconUser, IconNotification, IconDown, IconExport
} from '@arco-design/web-vue/es/icon'
import { getMyNotifications, getUnreadCount, markAsRead, markAllAsRead } from '../api/notification'
import { formatDate } from '../utils'
import DetailModal from '../components/Notification/DetailModal.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const menuList = ref<any[]>([])
const isCollapse = ref(false)
const defaultOpenKeys = ref<string[]>(['system', 'basic', 'business'])

// Notification states
const unreadCount = ref(0)
const noticeList = ref<any[]>([])
const unreadNoticeList = computed(() => noticeList.value.filter(n => n.is_read === 0))

const detailModalVisible = ref(false)
const selectedNotice = ref<any>(null)

async function fetchUnreadCount() {
  try {
    const res: any = await getUnreadCount()
    unreadCount.value = res.count || 0
  } catch (err) {
    console.error(err)
  }
}

async function fetchNotices() {
  try {
    const res: any = await getMyNotifications()
    noticeList.value = res || []
  } catch (err) {
    console.error(err)
  }
}

async function handleMarkAllRead() {
  try {
    await markAllAsRead()
    Message.success('已将所有未读通知标记为已读')
    await fetchUnreadCount()
    await fetchNotices()
  } catch (err) {
    console.error(err)
  }
}

async function handleViewNotice(item: any) {
  selectedNotice.value = item
  detailModalVisible.value = true
  
  if (item.is_read === 0) {
    try {
      await markAsRead(item.id)
      await fetchUnreadCount()
      await fetchNotices()
    } catch (err) {
      console.error(err)
    }
  }
}

function goToNotificationCenter() {
  router.push('/notification')
}


const activeMenu = computed(() => {
  return route.path
})

const currentRouteTitle = computed(() => {
  return (route.meta.title as string) || '首页'
})

// Fallback logic for dynamic menu icons based on keywords in menu names
function getMenuIcon(menu: any) {
  if (menu.icon && menu.icon !== '#') {
    const iconMap: any = {
      'Setting': 'IconSettings',
      'Settings': 'IconSettings',
      'User': 'IconUser',
      'Avatar': 'IconUser',
      'List': 'IconMenu',
      'Key': 'IconLock',
      'Notebook': 'IconBook',
      'Folder': 'IconFolder',
      'Document': 'IconFile',
      'Odometer': 'IconDashboard',
      'Monitor': 'IconDesktop',
      'Bell': 'IconNotification',
      'Search': 'IconSearch',
      'Plus': 'IconPlus',
      'Location': 'IconLocation',
      'Cpu': 'IconCpu',
      'Apps': 'IconApps'
    }
    const mapped = iconMap[menu.icon] || menu.icon
    if (mapped) {
      return mapped.startsWith('Icon') ? mapped : 'Icon' + mapped.charAt(0).toUpperCase() + mapped.slice(1)
    }
  }

  return null
}

// Ensure correct route index formats (e.g. '/menu')
function resolvePath(path: string) {
  if (!path) return '/'
  return path.startsWith('/') ? path : '/' + path
}

// Fetch dynamic menus from server
async function fetchMenus() {
  try {
    const res: any = await getMenuTree()
    menuList.value = res || []
  } catch (err) {
    console.error('Failed to load menus', err)
  }
}

function handleMenuClick(key: string) {
  router.push(key)
}

const handleCommand = async (val: any) => {
  if (val === 'logout') {
    await userStore.logout()
    Message.success('已安全退出登录')
    router.push('/login')
  } else if (val === 'profile') {
    router.push('/system/account')
  }
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
  background-color: #F2F3F5;
  overflow: hidden;
}

.main-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* Sidebar - White Arco Pro Style */
:deep(.sidebar-container) {
  background: #FFFFFF !important;
  border-right: 1px solid #E5E6EB;
  transition: all 0.2s ease;
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow-x: hidden !important;
}

:deep(.sidebar-container .arco-layout-sider-children) {
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
  overflow-x: hidden !important;
}

/* Sidebar Logo */
.sidebar-logo-wrap {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 10px;
  border-bottom: 1px solid #E5E6EB;
  flex-shrink: 0;
}

.sidebar-logo-icon {
  width: 32px;
  height: 32px;
  background: #165DFF;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}

.sidebar-logo-text {
  font-size: 16px;
  font-weight: 500;
  color: #1D2129;
  white-space: nowrap;
}

.sidebar-version {
  padding: 12px 16px;
  color: #86909C;
  font-size: 12px;
  border-top: 1px solid #E5E6EB;
  flex-shrink: 0;
  text-align: center;
}

/* Arco Menu Light Theme Override - Premium Flat Theme with Left Indicator */
:deep(.arco-menu) {
  background: #FFFFFF !important;
  border: none !important;
}

:deep(.arco-menu-light .arco-menu-item),
:deep(.arco-menu-light .arco-menu-inline-header),
:deep(.arco-menu-light .arco-menu-pop-header) {
  height: 42px !important;
  line-height: 42px !important;
  color: #4E5969;
  font-size: 14px;
  border-radius: 0 !important;
  margin: 0 !important;
  padding: 0 16px !important;
  transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
  display: flex;
  align-items: center;
  border-left: 2px solid transparent;
}

:deep(.arco-menu-light .arco-menu-item:hover),
:deep(.arco-menu-light .arco-menu-inline-header:hover),
:deep(.arco-menu-light .arco-menu-pop-header:hover) {
  background: #F2F3F5 !important;
  color: #1D2129 !important;
}

:deep(.arco-menu-light .arco-menu-item.arco-menu-selected) {
  background: #E8F1FF !important;
  color: #165DFF !important;
  font-weight: 450 !important;
  border-left: 2px solid #165DFF !important;
  box-shadow: none !important;
}

/* Parent sub-menu title selected state (when child is active) */
:deep(.arco-menu-light .arco-menu-inline-header.arco-menu-selected),
:deep(.arco-menu-light .arco-menu-pop-header.arco-menu-selected) {
  color: #165DFF !important;
  font-weight: 450 !important;
}

:deep(.arco-menu-light .arco-menu-item.arco-menu-selected .arco-icon),
:deep(.arco-menu-light .arco-menu-inline-header.arco-menu-selected .arco-icon),
:deep(.arco-menu-light .arco-menu-pop-header.arco-menu-selected .arco-icon) {
  color: #165DFF !important;
}

/* Submenu Popup overrides */
:deep(.arco-menu-popup .arco-menu-item) {
  height: 36px;
  line-height: 36px;
  font-size: 14px;
}

:deep(.arco-menu-light .arco-menu-icon-suffix .arco-icon) {
  color: #86909C;
}

/* Submenu Indent - Control nesting indentation precisely */
:deep(.arco-menu-indent) {
  width: 32px !important;
  /* Standard spacing hierarchy between levels */
}

/* Header */
.header-container {
  height: 56px !important;
  background: #FFFFFF !important;
  border-bottom: 1px solid #E5E6EB;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px !important;
  line-height: 56px;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.fold-btn {
  font-size: 20px;
  cursor: pointer;
  color: #4E5969;
  display: flex;
  align-items: center;
}

.breadcrumbs {
  font-size: 14px;
  color: #86909C;
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb-separator {
  color: #E5E6EB;
}

.breadcrumb-current {
  color: #1D2129;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-search {
  width: 200px;
}

.notice-icon {
  font-size: 18px;
  color: #4E5969;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.header-avatar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.header-avatar-wrap :deep(.arco-avatar-image) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  align-items: center;
  justify-content: center;
}

.header-avatar-wrap :deep(img) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  border-radius: 50% !important;
  display: block !important;
}

.header-avatar-wrap .user-name {
  color: #4E5969;
  font-size: 14px;
}

/* Menu item icon wrapper and icon styling with double-margin fix */
:deep(.arco-menu-light .arco-menu-item .arco-menu-icon),
:deep(.arco-menu-light .arco-menu-inline-header .arco-menu-icon),
:deep(.arco-menu-light .arco-menu-pop-header .arco-menu-icon) {
  margin-right: 8px !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

:deep(.arco-menu-light .arco-menu-item .arco-icon),
:deep(.arco-menu-light .arco-menu-inline-header .arco-icon),
:deep(.arco-menu-light .arco-menu-pop-header .arco-icon) {
  font-size: 20px !important;
  /* Enlarge icon to 20px */
  margin-right: 0 !important;
  /* Clear inner margin to prevent double-spacing */
  color: #4E5969;
  transition: color 0.2s;
}

/* Content Area */
.app-main {
  background: #F2F3F5;
  padding: 20px;
}

.app-footer {
  height: 32px;
  background: #FFFFFF;
  border-top: 1px solid #E5E6EB;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #86909C;
  font-size: 12px;
  flex-shrink: 0;
}

/* Transitions */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.2s ease-out;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-15px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(15px);
}

/* Notice Popover Styles */

.notice-popover-container {
  width: 300px;
}

.notice-popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #F2F3F5;
}

.notice-popover-title {
  font-size: 14px;
  font-weight: 600;
  color: #1D2129;
}

.notice-popover-tabs {
  padding: 0 8px;
}

:deep(.notice-popover-tabs .arco-tabs-nav) {
  margin-bottom: 8px;
}

:deep(.notice-popover-tabs .arco-tabs-content) {
  padding-top: 0;
}

.notice-popover-item {
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
  list-style: none;
}

.notice-popover-item:hover {
  background-color: #F2F3F5;
}

.item-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.item-title {
  font-size: 13px;
  color: #4E5969;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-unread .item-title {
  color: #1D2129;
  font-weight: 550;
}

.item-time {
  font-size: 11px;
  color: #86909C;
}

.empty-notices {
  text-align: center;
  padding: 30px 0;
  color: #86909C;
  font-size: 13px;
}

.notice-popover-footer {
  border-top: 1px solid #F2F3F5;
  padding: 4px 0;
}
</style>

<style>
.notice-popover-content {
  padding: 0 !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
  border: 1px solid #E5E6EB !important;
  transform: translateY(14px) !important;
}
</style>

