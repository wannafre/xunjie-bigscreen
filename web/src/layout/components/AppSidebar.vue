<template>
  <a-layout-sider
    :collapsible="true"
    :trigger="null"
    hide-trigger
    :width="260"
    :collapsed-width="72"
    :collapsed="collapsed"
    class="sidebar-container"
  >
    <div class="sidebar-logo-wrap" :class="{ 'is-collapsed': collapsed }">
      <div class="sidebar-logo-icon">
        <component :is="settings.logoComponent" style="font-size: 20px" />
      </div>
      <div v-if="!collapsed" class="sidebar-brand">
        <span class="sidebar-logo-text">{{ settings.shortTitle }}</span>
        <span class="sidebar-logo-subtitle">管理控制台</span>
      </div>
    </div>

    <div v-if="!collapsed" class="sidebar-section-title">功能导航</div>

    <a-scrollbar style="height: 100%; overflow: auto" outer-style="flex: 1; min-height: 0">
      <a-menu
        :selected-keys="[activeMenu]"
        :collapsed="collapsed"
        :default-open-keys="defaultOpenKeys"
        :style="{ width: '100%' }"
        theme="light"
        class="sidebar-menu"
        @menu-item-click="handleClick"
      >
        <a-menu-item key="/manager/dashboard" class="app-menu-item">
          <template #icon>
            <IconHome />
          </template>
          首页
        </a-menu-item>

        <AppMenuNode
          v-for="menu in menus"
          :key="menu.id ?? menu.path"
          :menu="menu"
        />
      </a-menu>
    </a-scrollbar>

    <div v-if="!collapsed" class="sidebar-version">
      <span class="version-dot"></span>
      <span>系统版本 V1.0.0</span>
    </div>
  </a-layout-sider>
</template>

<script setup lang="ts">
import { IconHome } from '@arco-design/web-vue/es/icon'
import { settings } from '../../config/settings'
import AppMenuNode from './AppMenuNode.vue'
import type { LayoutMenuItem } from '../composables/useLayoutMenu'

defineProps<{
  collapsed: boolean
  menus: LayoutMenuItem[]
  activeMenu: string
  defaultOpenKeys: string[]
}>()

const emit = defineEmits<{
  (event: 'menu-click', key: string): void
}>()

function handleClick(key: string) {
  emit('menu-click', key)
}
</script>

<style scoped>
.sidebar-container {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 46%, #f1f5f9 100%) !important;
  border-right: 1px solid #dbe4f0;
  box-shadow: 10px 0 30px rgba(15, 23, 42, 0.06);
  transition: all 0.24s ease;
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow-x: hidden !important;
}

.sidebar-container :deep(.arco-layout-sider-children) {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: transparent;
  overflow-x: hidden !important;
}

.sidebar-logo-wrap {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 18px;
  gap: 12px;
  border-bottom: 1px solid #dbe4f0;
  flex-shrink: 0;
}

.sidebar-logo-wrap.is-collapsed {
  justify-content: center;
  padding: 0;
}

.sidebar-logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 10px 22px rgba(99, 102, 241, 0.22);
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar-logo-text {
  font-size: 17px;
  line-height: 22px;
  font-weight: 700;
  color: #172033;
  white-space: nowrap;
  letter-spacing: 0.2px;
}

.sidebar-logo-subtitle {
  margin-top: 2px;
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
}

.sidebar-section-title {
  padding: 16px 22px 8px;
  color: #8492a6;
  font-size: 12px;
  letter-spacing: 1.5px;
}

.sidebar-version {
  margin-top: auto;
  margin-left: 16px;
  margin-right: 16px;
  margin-bottom: 18px;
  padding: 11px 14px;
  color: #475569;
  font-size: 12px;
  border: 1px solid #e0e7ff;
  background: #f5f3ff;
  border-radius: 14px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.version-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15);
}

:deep(.arco-menu) {
  background: transparent !important;
  border: none !important;
  padding: 4px 12px 12px;
}

:deep(.arco-menu-light .arco-menu-item),
:deep(.arco-menu-light .arco-menu-inline-header),
:deep(.arco-menu-light .arco-menu-pop-header) {
  height: 42px !important;
  line-height: 42px !important;
  color: #334155;
  font-size: 14px;
  border-radius: 12px !important;
  margin: 4px 0 !important;
  padding: 0 14px !important;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  border-left: 0 !important;
}

:deep(.arco-menu-light .arco-menu-item:hover),
:deep(.arco-menu-light .arco-menu-inline-header:hover),
:deep(.arco-menu-light .arco-menu-pop-header:hover) {
  background: #f5f3ff !important;
  color: #4f46e5 !important;
}

:deep(.arco-menu-light .arco-menu-item.arco-menu-selected) {
  background: #e0e7ff !important;
  color: #4f46e5 !important;
  font-weight: 650 !important;
}

:deep(.arco-menu-light .arco-menu-inline-header.arco-menu-selected),
:deep(.arco-menu-light .arco-menu-pop-header.arco-menu-selected) {
  color: #4f46e5 !important;
  font-weight: 600 !important;
  background: #f5f3ff !important;
}

:deep(.arco-menu-light .arco-menu-item.arco-menu-selected .arco-icon),
:deep(.arco-menu-light .arco-menu-inline-header.arco-menu-selected .arco-icon),
:deep(.arco-menu-light .arco-menu-pop-header.arco-menu-selected .arco-icon) {
  color: #4f46e5 !important;
}

:deep(.arco-menu-light .arco-menu-icon-suffix .arco-icon) {
  color: #94a3b8;
}

:deep(.arco-menu-indent) {
  width: 18px !important;
}

:deep(.arco-menu-light .arco-menu-item .arco-menu-icon),
:deep(.arco-menu-light .arco-menu-inline-header .arco-menu-icon),
:deep(.arco-menu-light .arco-menu-pop-header .arco-menu-icon) {
  margin-right: 10px !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

:deep(.arco-menu-light .arco-menu-item .arco-icon),
:deep(.arco-menu-light .arco-menu-inline-header .arco-icon),
:deep(.arco-menu-light .arco-menu-pop-header .arco-icon) {
  font-size: 18px !important;
  margin-right: 0 !important;
  color: #64748b;
  transition: color 0.2s;
}

:deep(.arco-menu-light .arco-menu-item:hover .arco-icon),
:deep(.arco-menu-light .arco-menu-inline-header:hover .arco-icon),
:deep(.arco-menu-light .arco-menu-pop-header:hover .arco-icon) {
  color: #4f46e5;
}

:deep(.arco-menu-collapse .arco-menu-item),
:deep(.arco-menu-collapse .arco-menu-pop-header) {
  justify-content: center;
  padding: 0 !important;
}

:deep(.arco-menu-collapse .arco-menu-icon) {
  margin-right: 0 !important;
}
</style>

