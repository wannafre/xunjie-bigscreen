import request from '../utils/request'

export function getOfficialMaterials(category?: string) {
  return request.get('/materials/official', { params: { category } })
}

export function getMyMaterials(category?: string) {
  return request.get('/materials/my', { params: { category } })
}

export function pullMaterial(officialId: number | string) {
  return request.post(`/materials/pull/${officialId}`)
}

export function createMyMaterial(data: {
  name: string
  category: string
  subcategory?: string
  thumbnail?: string
  config_data?: any
}) {
  return request.post('/materials/my', data)
}

export function updateMyMaterial(id: number | string, data: any) {
  return request.put(`/materials/my/${id}`, data)
}

export function deleteMyMaterial(id: number | string) {
  return request.delete(`/materials/my/${id}`)
}

export function deleteFile(fileUrl: string) {
  return request.delete('/materials/delete-file', { params: { file_url: fileUrl } })
}

export function uploadFile(formData: FormData, folder: string = 'assets') {
  return request.post('/materials/upload', formData, {
    params: { folder },
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function createOfficialMaterial(data: any) {
  return request.post('/materials/official', data)
}

export function updateOfficialMaterial(id: number | string, data: any) {
  return request.put(`/materials/official/${id}`, data)
}

export function deleteOfficialMaterial(id: number | string) {
  return request.delete(`/materials/official/${id}`)
}
