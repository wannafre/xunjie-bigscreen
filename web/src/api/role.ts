import request from '../utils/request'

export function getRoleList(params?: any) {
  return request.get('/role/', { params })
}

export function getRole(id: number | string) {
  return request.get(`/role/${id}`)
}

export function createRole(data: any) {
  return request.post('/role/', data)
}

export function updateRole(id: number | string, data: any) {
  return request.put(`/role/${id}`, data)
}

export function deleteRole(id: number | string) {
  return request.delete(`/role/${id}`)
}
