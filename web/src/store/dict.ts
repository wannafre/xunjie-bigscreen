import { defineStore } from 'pinia'
import { getDictDataByType } from '../api/dict'

export const useDictStore = defineStore('dict', {
  state: () => ({
    dictMap: {} as Record<string, any[]>
  }),
  actions: {
    async loadDict(dictType: string) {
      if (this.dictMap[dictType]) {
        return this.dictMap[dictType]
      }
      try {
        const res: any = await getDictDataByType(dictType)
        this.dictMap[dictType] = res || []
        return this.dictMap[dictType]
      } catch (err) {
        console.error(`加载字典失败: ${dictType}`, err)
        return []
      }
    },
    getDictLabel(dictType: string, value: string | number) {
      const list = this.dictMap[dictType] || []
      const item = list.find(d => String(d.dict_value) === String(value))
      return item ? item.dict_label : value
    },
    getDictTagColor(dictType: string, value: string | number) {
      const list = this.dictMap[dictType] || []
      const item = list.find(d => String(d.dict_value) === String(value))
      if (item && item.list_class) {
        const colorMap: Record<string, string> = {
          primary: 'arcoblue',
          success: 'green',
          warning: 'orange',
          danger: 'red',
          info: 'gray',
          default: 'gray'
        }
        return colorMap[item.list_class] || item.list_class
      }
      return 'gray'
    }
  }
})
