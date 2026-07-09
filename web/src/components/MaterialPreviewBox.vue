<template>
  <div class="edit-preview-container">
    <div class="preview-title">
      <span>实时预览 (所见即所得)</span>
      <a-radio-group v-if="category === 'echarts' || category === 'geojson'" v-model="editPreviewTheme" size="mini" type="button" @change="handleEditThemeChange">
        <a-radio value="dark">暗底色</a-radio>
        <a-radio value="light">亮底色</a-radio>
      </a-radio-group>
    </div>
    <div class="preview-body">
      <!-- ECharts preview -->
      <div v-if="category === 'echarts' || category === 'geojson'" 
        class="edit-chart-preview-wrapper"
        :style="{ backgroundColor: editPreviewTheme === 'dark' ? '#0f172a' : '#ffffff', border: editPreviewTheme === 'dark' ? '1px solid #1e293b' : '1px solid #e5e6eb' }"
      >
        <div ref="editChartRef" class="edit-chart-sandbox"></div>
        <div v-if="editChartError" class="chart-error-msg">
          <span>等待有效 JSON 输入...</span>
        </div>
      </div>
      
      <!-- Background / Image preview -->
      <div v-else-if="category === 'background' || category === 'image'" class="edit-bg-preview" :style="editBackgroundStyle">
        <div v-if="!thumbnail && !configData?.image" class="color-text-indicator">
          背景颜色: {{ configData?.color || '#000000' }}
        </div>
      </div>
      
      <!-- GeoJSON or raw config -->
      <div v-else class="edit-raw-preview">
        <pre class="json-code-box"><code>{{ editGeoJsonPreviewText }}</code></pre>
      </div>
    </div>
    <div class="preview-footer">
      <a-button type="secondary" size="small" long @click="forceUpdatePreview">手动刷新渲染</a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { resolveImageUrl, escapeXml, isSvgUrl } from '../utils'
import * as echarts from 'echarts'

const props = defineProps({
  category: {
    type: String,
    required: true
  },
  thumbnail: {
    type: String,
    default: ''
  },
  configJsonStr: {
    type: String,
    default: ''
  },
  configData: {
    type: Object,
    default: null
  },
  geoJsonMap: {
    type: Object as () => Record<string, number>,
    default: () => ({})
  },
  geoJsonMaterials: {
    type: Array as () => any[],
    default: () => []
  }
})

const emit = defineEmits([
  'detect-subcategory',
  'validation-error'
])

const editPreviewTheme = ref<'dark' | 'light'>('dark')
const editChartRef = ref<HTMLDivElement | null>(null)
const editChartError = ref(false)
let editChartInstance: any = null
let editRegisteredMaps: string[] = []

const chartTypeValues = [
  'line', 'bar', 'pie', 'scatter', 'map', 'candlestick', 'radar', 'boxplot',
  'heatmap', 'graph', 'lines', 'tree', 'treemap', 'sunburst', 'parallel',
  'sankey', 'funnel', 'gauge', 'pictorialBar', 'themeRiver', 'calendar',
  'matrix', 'chord', 'custom', 'dataset', 'dataZoom', 'graphic', 'richText',
  'globe', 'bar3D', 'scatter3D', 'surface', 'map3D', 'lines3D', 'line3D',
  'scatterGL', 'linesGL', 'flowGL', 'graphGL'
]

function handleEditThemeChange() {
  updateEditPreview()
}

function formatHexColor(color: string | null | undefined): string {
  if (!color) return '#0b132b'
  const trimmed = color.trim()
  if (trimmed.startsWith('#')) return trimmed
  if (/^[0-9a-fA-F]{3,8}$/.test(trimmed)) {
    return `#${trimmed}`
  }
  return trimmed
}

const editBackgroundStyle = computed(() => {
  const bgImage = resolveImageUrl(props.thumbnail)
  const color = props.category === 'background' ? formatHexColor(props.configData?.color) : '#0f172a'
  
  return {
    backgroundColor: color,
    backgroundImage: bgImage ? `url(${bgImage})` : 'none',
    backgroundRepeat: 'no-repeat',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    width: '100%',
    height: '350px',
    borderRadius: '4px',
    border: '1px solid #e5e6eb',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }
})

const editGeoJsonPreviewText = computed(() => {
  if (props.category !== 'geojson') return props.configJsonStr || '{}'
  if (!props.configJsonStr) return '{}'
  if (props.configJsonStr.length > 5000) {
    return props.configJsonStr.slice(0, 5000) + '\n\n... (地图数据过长，已截断显示，全部内容可在保存后查看) ...'
  }
  return props.configJsonStr
})

function parseJsObject(str: string): any {
  if (!str || !str.trim()) return {}
  return new Function(`return (${str})`)()
}

function getCorsSafeUrl(url: string | null | undefined): string {
  if (!url) return ''
  if (url.startsWith('/api/') || url.startsWith('api/')) {
    return url
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const urlObj = new URL(url)
      if (urlObj.pathname.startsWith('/uploads')) {
        return urlObj.pathname
      }
      if (urlObj.pathname.startsWith('/api')) {
        return urlObj.pathname + urlObj.search
      }
    } catch (_) {}
    return url
  }
  if (url.startsWith('uploads/')) {
    return '/' + url
  }
  if (url.startsWith('/uploads/')) {
    return url
  }
  return resolveImageUrl(url)
}

async function loadGeoJsonData(configData: any): Promise<any> {
  if (!configData) return null
  if (configData.url) {
    try {
      const res = await fetch(getCorsSafeUrl(configData.url))
      if (res.ok) {
        return await res.json()
      }
      throw new Error(`HTTP ${res.status}`)
    } catch (e: any) {
      console.error('Failed to fetch GeoJSON from URL:', e)
      return null
    }
  }
  return configData
}

function getImageDimensions(url: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve) => {
    const img = new Image()
    img.src = url
    img.onload = () => {
      resolve({
        width: img.naturalWidth || 1920,
        height: img.naturalHeight || 1080
      })
    }
    img.onerror = () => {
      resolve({ width: 1920, height: 1080 })
    }
  })
}

async function registerMapFromMaterial(mapName: string, material: any) {
  if (!material) return
  
  if (material.category === 'geojson') {
    const geoJsonData = await loadGeoJsonData(material.config_data)
    if (geoJsonData) {
      echarts.registerMap(mapName, geoJsonData)
      if (!editRegisteredMaps.includes(mapName)) {
        editRegisteredMaps.push(mapName)
      }
    }
  } else if (material.category === 'image') {
    const relativeUrl = material.thumbnail || material.config_data?.image
    if (!relativeUrl) return
    const fileUrl = getCorsSafeUrl(relativeUrl)
    
    if (isSvgUrl(relativeUrl)) {
      const res = await fetch(fileUrl)
      if (res.ok) {
        const svgText = await res.text()
        echarts.registerMap(mapName, { svg: svgText })
        if (!editRegisteredMaps.includes(mapName)) {
          editRegisteredMaps.push(mapName)
        }
      }
    } else {
      const dimensions = await getImageDimensions(fileUrl)
      const svgText = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${dimensions.width} ${dimensions.height}">
          <image href="${escapeXml(fileUrl)}" width="${dimensions.width}" height="${dimensions.height}" x="0" y="0" />
        </svg>
      `.trim()
      echarts.registerMap(mapName, { svg: svgText })
      if (!editRegisteredMaps.includes(mapName)) {
        editRegisteredMaps.push(mapName)
      }
    }
  }
}

function autoDetectSubcategory(parsed: any) {
  if (props.category !== 'echarts') return
  
  let detectedType = ''
  if (parsed) {
    if (parsed.globe) {
      detectedType = 'globe'
    } else if (parsed.calendar) {
      detectedType = 'calendar'
    } else if (parsed.parallel) {
      detectedType = 'parallel'
    } else if (parsed.graphic) {
      detectedType = 'graphic'
    } else if (parsed.series) {
      const seriesList = Array.isArray(parsed.series) ? parsed.series : [parsed.series]
      if (seriesList.length > 0 && seriesList[0] && seriesList[0].type) {
        detectedType = seriesList[0].type
      }
    }
  }

  if (detectedType) {
    if (detectedType === 'effectScatter') {
      detectedType = 'scatter'
    } else if (detectedType === 'k') {
      detectedType = 'candlestick'
    }
    
    if (chartTypeValues.includes(detectedType)) {
      emit('detect-subcategory', detectedType)
    } else {
      emit('detect-subcategory', 'other')
    }
  } else {
    emit('detect-subcategory', 'other')
  }
}

async function updateEditPreview() {
  if ((props.category !== 'echarts' && props.category !== 'geojson') || !editChartRef.value) return
  try {
    let parsed: any = null
    editChartError.value = false
    
    if (props.category === 'geojson') {
      if (!props.configJsonStr || !props.configJsonStr.trim() || props.configJsonStr === '{}' || props.configJsonStr === '正在加载 GeoJSON 地图数据...') {
        return
      }
      const geoJsonData = JSON.parse(props.configJsonStr)
      const mapName = 'edit_preview_map_' + Date.now()
      echarts.registerMap(mapName, geoJsonData)
      editRegisteredMaps.push(mapName)
      parsed = {
        backgroundColor: 'transparent',
        tooltip: {
          show: true,
          trigger: 'item',
          formatter: '{b}'
        },
        series: [{
          name: '地图预览',
          type: 'map',
          map: mapName,
          roam: true,
          label: {
            show: true,
            color: '#e2e8f0',
            fontSize: 10
          },
          itemStyle: {
            areaColor: '#1e293b',
            borderColor: '#38bdf8',
            borderWidth: 1
          },
          emphasis: {
            label: {
              show: true,
              color: '#ffffff'
            },
            itemStyle: {
              areaColor: '#0ea5e9'
            }
          }
        }]
      }
    } else {
      parsed = parseJsObject(props.configJsonStr)
      
      // Auto-detect ECharts subcategory
      autoDetectSubcategory(parsed)

      emit('validation-error', '')

      // Register maps from props.geoJsonMap (explicit key-value mapping)
      if (props.geoJsonMap && typeof props.geoJsonMap === 'object') {
        for (const [mapName, id] of Object.entries(props.geoJsonMap)) {
          if (!mapName || !id) continue
          const geoJsonMaterial = props.geoJsonMaterials.find(item => item.id === id)
          if (geoJsonMaterial) {
            await registerMapFromMaterial(mapName, geoJsonMaterial)
          }
        }
      }
    }
    
    if (editChartInstance) {
      editChartInstance.dispose()
      editChartInstance = null
    }
    const currentTheme = editPreviewTheme.value === 'dark' ? 'dark' : undefined
    editChartInstance = echarts.init(editChartRef.value, currentTheme)
    
    editChartInstance.setOption(parsed, true)
    nextTick(() => {
      if (editChartInstance) {
        editChartInstance.resize()
      }
    })
  } catch (e: any) {
    editChartError.value = true
    emit('validation-error', e.message || '配置解析错误')
  }
}

let debounceTimer: any = null
function debouncedUpdatePreview() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    updateEditPreview()
  }, 500)
}

function forceUpdatePreview() {
  try {
    if (props.category === 'geojson') {
      JSON.parse(props.configJsonStr)
    } else {
      parseJsObject(props.configJsonStr)
    }
    emit('validation-error', '')
    updateEditPreview()
  } catch (e: any) {
    emit('validation-error', '语法有误: ' + e.message)
    editChartError.value = true
  }
}

function cleanRegisteredMaps() {
  if (editChartInstance) {
    editChartInstance.dispose()
    editChartInstance = null
  }
  const emptyGeoJson = { type: 'FeatureCollection', features: [] } as any
  for (const name of editRegisteredMaps) {
    try { echarts.registerMap(name, emptyGeoJson) } catch (_) {}
  }
  editRegisteredMaps = []
  editChartError.value = false
}

function unregisterMap(mapName: string) {
  if (!mapName) return
  const emptyGeoJson = { type: 'FeatureCollection', features: [] } as any
  try {
    echarts.registerMap(mapName, emptyGeoJson)
  } catch (_) {}
  const idx = editRegisteredMaps.indexOf(mapName)
  if (idx !== -1) {
    editRegisteredMaps.splice(idx, 1)
  }
}

// Watch inputs
watch(() => props.configJsonStr, () => {
  debouncedUpdatePreview()
})

watch(() => props.geoJsonMap, () => {
  debouncedUpdatePreview()
}, { deep: true })

watch(() => props.category, (newCat) => {
  cleanRegisteredMaps()
  if (newCat === 'echarts' || newCat === 'geojson') {
    nextTick(() => {
      updateEditPreview()
    })
  }
})

function handleResize() {
  if (editChartInstance) {
    editChartInstance.resize()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  if (props.category === 'echarts' || props.category === 'geojson') {
    updateEditPreview()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  cleanRegisteredMaps()
})

defineExpose({
  forceUpdatePreview,
  updateEditPreview,
  unregisterMap,
  cleanRegisteredMaps
})
</script>

<style scoped>
.edit-preview-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  padding: 16px;
  background-color: #f8fafc;
}

.preview-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: #1D2129;
  margin-bottom: 12px;
  border-left: 3px solid #165dff;
  padding-left: 8px;
}

.preview-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.edit-chart-preview-wrapper {
  width: 100%;
  height: 350px;
  background-color: #0f172a;
  border-radius: 4px;
  position: relative;
  border: 1px solid #e5e6eb;
}

.edit-chart-sandbox {
  width: 100%;
  height: 100%;
}

.chart-error-msg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #86909c;
  font-size: 13px;
}

.edit-bg-preview {
  width: 100%;
  height: 350px;
  border-radius: 4px;
  border: 1px solid #e5e6eb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-raw-preview {
  width: 100%;
  height: 350px;
  background-color: #f8fafc;
  border-radius: 4px;
  padding: 12px;
  overflow: auto;
  border: 1px solid #e5e6eb;
}

.preview-footer {
  margin-top: 12px;
}

.color-text-indicator {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255,255,255,0.1);
  color: #38bdf8;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
  font-family: monospace;
}

.json-code-box {
  margin: 0;
  font-family: monospace;
  font-size: 13px;
  color: #0f172a;
}
</style>
