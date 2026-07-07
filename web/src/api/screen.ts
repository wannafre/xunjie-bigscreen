import request from '../utils/request'

export function getScreens() {
  return request.get('/screens')
}

export function getScreenDetail(id: number | string, token?: string) {
  return request.get(`/screens/${id}`, { params: { token } })
}

export function createScreen(data: { name: string; description?: string; project_data?: any }) {
  return request.post('/screens', data)
}

export function updateScreen(id: number | string, data: any) {
  return request.put(`/screens/${id}`, data)
}

export function deleteScreen(id: number | string) {
  return request.delete(`/screens/${id}`)
}

export function publishScreen(id: number | string, isPublished: string) {
  return request.post(`/screens/${id}/publish`, null, { params: { is_published: isPublished } })
}
