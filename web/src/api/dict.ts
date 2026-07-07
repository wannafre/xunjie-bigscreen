import request from '../utils/request'

// Dict Type APIs
export function getDictTypeList() {
  return request.get('/dict/type')
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
export function getDictDataList(dictType: string) {
  return request.get('/dict/data', { params: { dict_type: dictType } })
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
