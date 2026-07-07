import { computed, ref } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  getMyNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead
} from '../../api/notification'

export interface LayoutNoticeItem {
  id: string | number
  title?: string
  content?: string
  create_time?: string
  is_read?: number
  [key: string]: any
}

export function useNoticeCenter() {
  const unreadCount = ref(0)
  const noticeList = ref<LayoutNoticeItem[]>([])
  const detailModalVisible = ref(false)
  const selectedNotice = ref<LayoutNoticeItem | null>(null)

  const unreadNoticeList = computed(() => {
    return noticeList.value.filter(item => item.is_read === 0)
  })

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

  async function refreshNotices() {
    await Promise.all([fetchUnreadCount(), fetchNotices()])
  }

  async function handleMarkAllRead() {
    try {
      await markAllAsRead()
      Message.success('已将所有未读通知标记为已读')
      await refreshNotices()
    } catch (err) {
      console.error(err)
    }
  }

  async function handleViewNotice(item: LayoutNoticeItem) {
    selectedNotice.value = item
    detailModalVisible.value = true

    if (item.is_read === 0) {
      try {
        await markAsRead(item.id)
        await refreshNotices()
      } catch (err) {
        console.error(err)
      }
    }
  }

  return {
    unreadCount,
    noticeList,
    unreadNoticeList,
    detailModalVisible,
    selectedNotice,
    fetchUnreadCount,
    fetchNotices,
    refreshNotices,
    handleMarkAllRead,
    handleViewNotice
  }
}
