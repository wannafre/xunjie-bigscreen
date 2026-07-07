<template>
  <div class="notification-center-container">
    <a-card class="box-card" :bordered="false">
      <template #title>
        <div class="card-header">
          <span class="title">通知公告中心</span>
          <div class="header-actions">
            <a-button type="outline" size="medium" @click="fetchData">刷新</a-button>
            <a-button type="primary" size="medium" @click="handleMarkAllRead" :disabled="unreadCount === 0">
              全部标记为已读
            </a-button>
          </div>
        </div>
      </template>

      <a-tabs v-model:active-key="activeTab" type="line" @change="handleTabChange">
        <a-tab-pane key="all" title="全部通知" />
        <a-tab-pane key="unread" title="未读通知" />
        <a-tab-pane key="read" title="已读通知" />
      </a-tabs>

      <div class="list-wrapper">
        <a-list :loading="loading" :bordered="false" hoverable>
          <a-list-item v-for="item in pagedList" :key="item.id" class="notice-list-item" @click="handleViewDetail(item)">
            <a-list-item-meta>
              <template #avatar>
                <div class="notice-icon-wrapper" :style="{ backgroundColor: getBgColor(item.type) }">
                  <component :is="getIcon(item.type)" :style="{ color: getIconColor(item.type) }" class="notice-list-icon" />
                </div>
              </template>
              <template #title>
                <div class="item-title-row">
                  <span class="item-title-text" :class="{ 'unread-title': item.is_read === 0 }">
                    {{ item.title }}
                  </span>
                  <a-tag v-if="item.is_read === 0" color="red" size="small" class="unread-badge">未读</a-tag>
                  <a-tag :color="getTypeTagColor(item.type)" size="small" class="type-tag">
                    {{ getTypeText(item.type) }}
                  </a-tag>
                </div>
              </template>
              <template #description>
                <div class="item-desc">
                  {{ stripHtml(item.content) }}
                </div>
              </template>
            </a-list-item-meta>
            <template #actions>
              <div class="item-meta-info">
                <span class="item-time-text">{{ formatDate(item.create_time) }}</span>
                <div class="actions-buttons" @click.stop>
                  <a-button type="text" size="small" @click="handleViewDetail(item)">查看详情</a-button>
                  <a-button v-if="item.is_read === 0" type="text" size="small" status="success" @click="handleMarkReadSingle(item)">
                    设为已读
                  </a-button>
                </div>
              </div>
            </template>
          </a-list-item>
          <template #empty v-if="filteredList.length === 0">
            <div class="empty-container">
              <a-empty description="暂无符合条件的通知" />
            </div>
          </template>
        </a-list>

        <div v-if="filteredList.length > 0" class="pagination-wrapper">
          <a-pagination
            v-model:current="currentPage"
            v-model:page-size="pageSize"
            :total="filteredList.length"
            show-total
            show-jumper
            @change="currentPage = $event"
          />
        </div>
      </div>
    </a-card>

    <!-- Detail Modal -->
    <DetailModal v-model:visible="detailVisible" :notification="selectedNotice" @close="fetchData" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconNotification, IconMessage, IconSchedule
} from '@arco-design/web-vue/es/icon'
import { getMyNotifications, markAsRead, markAllAsRead } from '../../api/notification'
import DetailModal from '../../components/Notification/DetailModal.vue'
import { formatDate } from '../../utils'

function stripHtml(html: string) {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '')
}

const loading = ref(false)
const activeTab = ref('all')
const noticeList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)

const detailVisible = ref(false)
const selectedNotice = ref<any>(null)

const unreadCount = computed(() => noticeList.value.filter(n => n.is_read === 0).length)

const filteredList = computed(() => {
  if (activeTab.value === 'unread') {
    return noticeList.value.filter(n => n.is_read === 0)
  }
  if (activeTab.value === 'read') {
    return noticeList.value.filter(n => n.is_read === 1)
  }
  return noticeList.value
})

const pagedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = currentPage.value * pageSize.value
  return filteredList.value.slice(start, end)
})

async function fetchData() {
  loading.value = true
  try {
    const res: any = await getMyNotifications()
    noticeList.value = res || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

function handleTabChange() {
  currentPage.value = 1
}

async function handleViewDetail(item: any) {
  selectedNotice.value = item
  detailVisible.value = true
  if (item.is_read === 0) {
    try {
      await markAsRead(item.id)
      item.is_read = 1 // optimistic update locally
    } catch (err) {
      console.error(err)
    }
  }
}

async function handleMarkReadSingle(item: any) {
  try {
    await markAsRead(item.id)
    Message.success('已设为已读')
    await fetchData()
  } catch (err) {
    console.error(err)
  }
}

async function handleMarkAllRead() {
  try {
    await markAllAsRead()
    Message.success('已将全部通知设为已读')
    await fetchData()
  } catch (err) {
    console.error(err)
  }
}

function getTypeText(type: string) {
  switch (type) {
    case 'system':
      return '系统通知'
    case 'message':
      return '内部消息'
    case 'todo':
      return '待办事项'
    default:
      return '公告'
  }
}

function getTypeTagColor(type: string) {
  switch (type) {
    case 'system':
      return 'red'
    case 'message':
      return 'arcoblue'
    case 'todo':
      return 'orangered'
    default:
      return 'gray'
  }
}

function getIcon(type: string) {
  switch (type) {
    case 'system':
      return IconNotification
    case 'message':
      return IconMessage
    case 'todo':
      return IconSchedule
    default:
      return IconNotification
  }
}

function getIconColor(type: string) {
  switch (type) {
    case 'system':
      return '#F53F3F'
    case 'message':
      return '#165DFF'
    case 'todo':
      return '#FF7D00'
    default:
      return '#86909C'
  }
}

function getBgColor(type: string) {
  switch (type) {
    case 'system':
      return '#FFE8E8'
    case 'message':
      return '#E8F1FF'
    case 'todo':
      return '#FFF3E8'
    default:
      return '#F2F3F5'
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.notification-center-container {
  height: 100%;
}

.box-card {
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #E5E6EB;
  background: #FFFFFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title {
  font-size: 16px;
  font-weight: 500;
  color: #1D2129;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.list-wrapper {
  margin-top: 16px;
}

.notice-list-item {
  cursor: pointer;
  padding: 16px 20px !important;
  border-bottom: 1px solid #F2F3F5;
  transition: all 0.25s ease;
}

.notice-list-item:hover {
  background-color: #F7F8FA;
}

.notice-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notice-list-icon {
  font-size: 20px;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.item-title-text {
  font-size: 15px;
  color: #4E5969;
  font-weight: 500;
}

.unread-title {
  color: #1D2129;
  font-weight: 600;
}

.item-desc {
  font-size: 13px;
  color: #86909C;
  margin-top: 6px;
  line-height: 1.6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 75vw;
}

.item-meta-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.item-time-text {
  font-size: 13px;
  color: #86909C;
}

.actions-buttons {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.notice-list-item:hover .actions-buttons {
  opacity: 1;
}

.empty-container {
  padding: 80px 0;
}

:deep(.arco-list-item-meta) {
  align-items: center;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
