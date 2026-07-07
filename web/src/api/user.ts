import request from '../utils/request'

export function getUserList(params?: any) {
  return request.get('/user/', { params })
}

export function getUser(id: number | string) {
  return request.get(`/user/${id}`)
}

export function createUser(data: any) {
  return request.post('/user/', data)
}

export function updateUser(id: number | string, data: any) {
  return request.put(`/user/${id}`, data)
}

export function deleteUser(id: number | string) {
  return request.delete(`/user/${id}`)
}

export function resetUserPassword(id: number | string) {
  return request.put(`/user/${id}/reset-pwd`)
}

export function updateUserProfile(data: any) {
  return request.put('/user/profile', data)
}

export function updateUserPassword(data: any) {
  return request.put('/user/profile/update-pwd', data)
}

