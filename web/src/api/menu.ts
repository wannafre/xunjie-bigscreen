import request from '../utils/request'

export function getMenuTree() {
  return request.get('/menu/tree')
}

export function getMenuList() {
  return request.get('/menu/')
}

export function createMenu(data: any) {
  return request.post('/menu/', data)
}

export function updateMenu(id: number | string, data: any) {
  return request.put(`/menu/${id}`, data)
}

export function deleteMenu(id: number | string) {
  return request.delete(`/menu/${id}`)
}
