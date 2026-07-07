import request from '../utils/request'

// ==========================================
// User Notification APIs (No permission check, only authenticated)
// ==========================================

export function getMyNotifications(params?: { status?: string; type?: string }) {
  return request.get('/notification/my', { params })
}

export function getUnreadCount() {
  return request.get('/notification/unread-count')
}

export function markAsRead(id: number | string) {
  return request.put(`/notification/${id}/read`)
}

export function markAllAsRead() {
  return request.put('/notification/read-all')
}

// ==========================================
// Admin Notification CRUD APIs (Requires permissions)
// ==========================================

export function getNotificationList(params?: { status?: string; type?: string; user_id?: number | string }) {
  return request.get('/notification/', { params })
}

export function createNotification(data: { user_id: number | string; title: string; content: string; type?: string }) {
  return request.post('/notification/', data)
}

export function updateNotification(id: number | string, data: any) {
  return request.put(`/notification/${id}`, data)
}

export function deleteNotification(id: number | string) {
  return request.delete(`/notification/${id}`)
}

export function getNotificationReadUsers(id: number | string) {
  return request.get(`/notification/${id}/read-users`)
}
