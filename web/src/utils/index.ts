import { useUserStore } from '../store/user'

/**
 * Check if the user has a specific permission
 * @param value permission key or array of keys
 * @returns boolean
 */
export function hasPerm(value: string | string[]): boolean {
  if (!value) return true
  
  const userStore = useUserStore()
  const permissions: string[] = userStore.permissions || []
  
  if (Array.isArray(value)) {
    if (value.length === 0) return true
    return value.some(val => permissions.includes(val))
  }
  
  return permissions.includes(value)
}

/**
 * Format date to string
 * @param date date object or timestamp/string
 * @param format format template e.g. YYYY-MM-DD HH:mm:ss
 */
export function formatDate(date: Date | string | number, format = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  
  const opt: { [key: string]: string } = {
    'Y+': d.getFullYear().toString(),
    'M+': (d.getMonth() + 1).toString().padStart(2, '0'),
    'D+': d.getDate().toString().padStart(2, '0'),
    'H+': d.getHours().toString().padStart(2, '0'),
    'm+': d.getMinutes().toString().padStart(2, '0'),
    's+': d.getSeconds().toString().padStart(2, '0')
  }
  
  let res = format
  for (const k in opt) {
    const r = new RegExp('(' + k + ')').exec(format)
    if (r) {
      res = res.replace(r[1], opt[k])
    }
  }
  return res
}

/**
 * Deep clone an object
 * @param source source object
 */
export function deepClone<T>(source: T): T {
  if (!source || typeof source !== 'object') {
    return source
  }
  return JSON.parse(JSON.stringify(source))
}

/**
 * Parse a flat list to a hierarchical tree structure
 * @param list flat list of nodes containing id and parentId
 * @param idKey primary key name
 * @param parentIdKey parent ID key name
 * @param childrenKey children field name
 */
export function listToTree<T = any>(
  list: T[],
  idKey = 'id',
  parentIdKey = 'parent_id',
  childrenKey = 'children'
): T[] {
  const map: { [key: string]: any } = {}
  const result: T[] = []
  
  list.forEach((item: any) => {
    map[item[idKey]] = { ...item, [childrenKey]: [] }
  })
  
  list.forEach((item: any) => {
    const mappedItem = map[item[idKey]]
    const parentId = item[parentIdKey]
    
    if (parentId === 0 || parentId === '0' || !parentId) {
      result.push(mappedItem)
    } else {
      const parent = map[parentId]
      if (parent) {
        parent[childrenKey].push(mappedItem)
      } else {
        result.push(mappedItem)
      }
    }
  })
  
  return result
}
