<template>
  <a-popover
    trigger="click"
    position="br"
    content-class="notice-popover-content"
    :position-offset="[0, 12]"
    :show-arrow="false"
  >
    <a-badge :count="unreadCount" :dot="unreadCount > 0" class="notice-badge">
      <div class="notice-trigger">
        <IconNotification class="notice-icon" />
      </div>
    </a-badge>

    <template #content>
      <div class="notice-popover-container">
        <div class="notice-popover-header">
          <div>
            <span class="notice-popover-title">通知公告</span>
            <div class="notice-popover-subtitle">最近 5 条消息</div>
          </div>
          <a-link v-if="unreadCount > 0" @click="emit('mark-all-read')">全部已读</a-link>
        </div>

        <a-tabs default-active-key="all" type="line" size="small" class="notice-popover-tabs">
          <a-tab-pane key="all" title="全部">
            <a-list :bordered="false" size="small" :split="false">
              <a-list-item
                v-for="item in noticeList.slice(0, 5)"
                :key="item.id"
                class="notice-popover-item"
                @click="emit('view-notice', item)"
              >
                <div class="item-wrap" :class="{ 'item-unread': item.is_read === 0 }">
                  <div class="item-dot"></div>
                  <div class="item-content">
                    <div class="item-title">{{ item.title }}</div>
                    <div class="item-time">{{ formatNoticeDate(item.create_time) }}</div>
                  </div>
                </div>
              </a-list-item>
              <template v-if="noticeList.length === 0" #empty>
                <div class="empty-notices">暂无通知</div>
              </template>
            </a-list>
          </a-tab-pane>

          <a-tab-pane key="unread" title="未读">
            <a-list :bordered="false" size="small" :split="false">
              <a-list-item
                v-for="item in unreadNoticeList.slice(0, 5)"
                :key="item.id"
                class="notice-popover-item"
                @click="emit('view-notice', item)"
              >
                <div class="item-wrap item-unread">
                  <div class="item-dot"></div>
                  <div class="item-content">
                    <div class="item-title">{{ item.title }}</div>
                    <div class="item-time">{{ formatNoticeDate(item.create_time) }}</div>
                  </div>
                </div>
              </a-list-item>
              <template v-if="unreadNoticeList.length === 0" #empty>
                <div class="empty-notices">暂无未读通知</div>
              </template>
            </a-list>
          </a-tab-pane>
        </a-tabs>

        <div class="notice-popover-footer">
          <a-button type="text" size="small" long @click="emit('go-notification-center')">
            查看全部
          </a-button>
        </div>
      </div>
    </template>
  </a-popover>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IconNotification } from '@arco-design/web-vue/es/icon'
import { formatDate } from '../../utils'
import type { LayoutNoticeItem } from '../composables/useNoticeCenter'

const props = defineProps<{
  unreadCount: number
  noticeList: LayoutNoticeItem[]
}>()

const emit = defineEmits<{
  (event: 'mark-all-read'): void
  (event: 'view-notice', item: LayoutNoticeItem): void
  (event: 'go-notification-center'): void
}>()

const unreadNoticeList = computed(() => {
  return props.noticeList.filter(item => item.is_read === 0)
})

function formatNoticeDate(value?: string | number | Date) {
  return value ? formatDate(value) : '-'
}
</script>

<style scoped>
.notice-trigger {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: #eef6ff;
  border: 1px solid #dbe4f0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.notice-trigger:hover {
  background: #eff6ff;
  border-color: #bfdbfe;
  transform: translateY(-1px);
}

.notice-icon {
  font-size: 18px;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.notice-popover-container {
  width: 340px;
  overflow: hidden;
}

.notice-popover-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 18px 12px;
  border-bottom: 1px solid #eef2f7;
  background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
}

.notice-popover-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.notice-popover-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: #94a3b8;
}

.notice-popover-tabs {
  padding: 0 10px;
}

:deep(.notice-popover-tabs .arco-tabs-nav) {
  margin-bottom: 8px;
}

:deep(.notice-popover-tabs .arco-tabs-content) {
  padding-top: 0;
}

.notice-popover-item {
  padding: 8px 8px;
  cursor: pointer;
  border-radius: 12px;
  transition: background-color 0.2s;
  list-style: none;
}

.notice-popover-item:hover {
  background-color: #f8fafc;
}

.item-wrap {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.item-dot {
  width: 8px;
  height: 8px;
  margin-top: 6px;
  border-radius: 50%;
  background: #cbd5e1;
  flex-shrink: 0;
}

.item-unread .item-dot {
  background: #ef4444;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1);
}

.item-content {
  min-width: 0;
}

.item-title {
  font-size: 13px;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-unread .item-title {
  color: #0f172a;
  font-weight: 700;
}

.item-time {
  margin-top: 4px;
  font-size: 11px;
  color: #94a3b8;
}

.empty-notices {
  text-align: center;
  padding: 30px 0;
  color: #94a3b8;
  font-size: 13px;
}

.notice-popover-footer {
  border-top: 1px solid #eef2f7;
  padding: 6px 10px;
  background: #f8fbff;
}
</style>

<style>
.notice-popover-content {
  padding: 0 !important;
  border-radius: 18px !important;
  box-shadow: 0 18px 52px rgba(15, 23, 42, 0.18) !important;
  border: 1px solid #e2e8f0 !important;
  transform: translateY(14px) !important;
  overflow: hidden !important;
}
</style>

