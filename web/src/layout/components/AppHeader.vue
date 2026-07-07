<template>
  <a-layout-header class="header-container">
    <div class="header-left">
      <button class="fold-button" type="button" @click="emit('toggle-collapse')">
        <IconMenuUnfold v-if="collapsed" />
        <IconMenuFold v-else />
      </button>

      <div class="header-title-group">
        <div class="breadcrumbs">
          <span class="breadcrumb-prefix">{{ systemTitle }}</span>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ currentTitle }}</span>
        </div>
        <div class="page-subtitle">统一运维管理平台</div>
      </div>
    </div>

    <div class="header-right">
      <div class="header-search">
        <a-input-search placeholder="搜索菜单或功能" size="medium" class="search-bar" />
      </div>

      <AppNoticePopover
        :unread-count="unreadCount"
        :notice-list="noticeList"
        @mark-all-read="emit('mark-all-read')"
        @view-notice="emit('view-notice', $event)"
        @go-notification-center="emit('go-notification-center')"
      />

      <AppUserDropdown
        :user-info="userInfo"
        @profile="emit('profile')"
        @logout="emit('logout')"
      />
    </div>
  </a-layout-header>
</template>

<script setup lang="ts">
import { IconMenuFold, IconMenuUnfold } from '@arco-design/web-vue/es/icon'
import AppNoticePopover from './AppNoticePopover.vue'
import AppUserDropdown from './AppUserDropdown.vue'
import type { LayoutNoticeItem } from '../composables/useNoticeCenter'

withDefaults(defineProps<{
  collapsed: boolean
  systemTitle: string
  currentTitle: string
  userInfo: {
    username?: string
    avatar?: string
  }
  unreadCount: number
  noticeList: LayoutNoticeItem[]
}>(), {
  currentTitle: '首页'
})

const emit = defineEmits<{
  (event: 'toggle-collapse'): void
  (event: 'mark-all-read'): void
  (event: 'view-notice', item: LayoutNoticeItem): void
  (event: 'go-notification-center'): void
  (event: 'profile'): void
  (event: 'logout'): void
}>()
</script>

<style scoped>
.header-container {
  height: 68px !important;
  margin: 16px 22px 0;
  background: #ffffff !important;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px !important;
  line-height: normal;
  flex-shrink: 0;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.fold-button {
  width: 42px;
  height: 42px;
  border: 1px solid #e0e7ff;
  border-radius: 14px;
  background: #f5f3ff;
  color: #4f46e5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.2s ease;
}

.fold-button:hover {
  background: #e0e7ff;
  border-color: #c7d2fe;
}

.header-title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.breadcrumbs {
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.breadcrumb-prefix {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.breadcrumb-separator {
  color: #94a3b8;
}

.breadcrumb-current {
  color: #172033;
  font-weight: 700;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-subtitle {
  color: #8492a6;
  font-size: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-search {
  width: 280px;
}

:deep(.search-bar .arco-input-wrapper),
:deep(.search-bar.arco-input-search) {
  border-radius: 14px;
}

:deep(.search-bar .arco-input-wrapper) {
  background: #ffffff;
  border-color: #dbe4f0;
}

@media (max-width: 960px) {
  .header-search {
    display: none;
  }

  .page-subtitle {
    display: none;
  }
}
</style>
