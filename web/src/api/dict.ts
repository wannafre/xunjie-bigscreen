import request from '../utils/request'

// Dict Type APIs
export function getDictTypeList(params?: any) {
  return request.get('/dict/type', { params })
}

export function getDictType(id: number | string) {
  return request.get(`/dict/type/${id}`)
}

export function createDictType(data: any) {
  return request.post('/dict/type', data)
}

export function updateDictType(id: number | string, data: any) {
  return request.put(`/dict/type/${id}`, data)
}

export function deleteDictType(id: number | string) {
  return request.delete(`/dict/type/${id}`)
}

// Dict Data APIs
export function getDictDataList(params: any) {
  return request.get('/dict/data', { params })
}

export function getDictData(dictCode: number | string) {
  return request.get(`/dict/data/${dictCode}`)
}

export function createDictData(data: any) {
  return request.post('/dict/data', data)
}

export function updateDictData(dictCode: number | string, data: any) {
  return request.put(`/dict/data/${dictCode}`, data)
}

export function deleteDictData(dictCode: number | string) {
  return request.delete(`/dict/data/${dictCode}`)
}

export function getDictDataByType(dictType: string) {
  return request.get(`/dict/data/type/${dictType}`)
}
