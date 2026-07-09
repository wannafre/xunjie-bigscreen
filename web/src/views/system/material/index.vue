<template>
  <div class="material-management-container">
    <a-card class="box-card" :bordered="false">
      <template #title>
        <div class="card-header">
          <span class="title">大屏图表素材管理</span>
          <div class="header-actions">
            <a-input v-model="searchForm.name" placeholder="素材名称" allow-clear class="search-input" />
            <a-select v-model="searchForm.category" placeholder="大类过滤" allow-clear class="search-select">
              <a-option value="echarts">ECharts 图表</a-option>
              <a-option value="background">大屏背景板</a-option>
              <a-option value="image">静态装饰图片</a-option>
              <a-option value="geojson">GeoJSON 地图</a-option>
            </a-select>
            <a-button type="outline" @click="handleSearch">查询</a-button>
            <a-button type="primary" @click="handleCreate">
              <template #icon>
                <IconPlus />
              </template>
              新建系统素材
            </a-button>
          </div>
        </div>
      </template>

      <a-scrollbar style="height: calc(100vh - 240px); overflow: auto;">
        <a-table :loading="loading" :data="tableData" row-key="id" :columns="columns" :pagination="pagination"
          @page-change="onPageChange" :bordered="false">
          
          <template #category="{ record }">
            <a-tag :color="getCategoryTagColor(record.category)">
              {{ getCategoryText(record.category) }}
            </a-tag>
          </template>

          <template #tags="{ record }">
            <div v-if="record.category === 'image' && record.config_data?.tags">
              <a-tag v-for="tag in record.config_data.tags.split(',')" :key="tag" color="arcoblue" size="small" style="margin-right: 4px; margin-bottom: 4px;">
                {{ tag.trim() }}
              </a-tag>
            </div>
            <span v-else-if="record.subcategory">{{ getSubcategoryLabel(record.subcategory) }}</span>
            <span v-else class="thumb-empty">-</span>
          </template>

          <template #thumbnail="{ record }">
            <div class="thumb-cell">
              <img v-if="record.thumbnail" :src="resolveImageUrl(record.thumbnail)" class="table-thumb-img" @click="viewOriginalImage(resolveImageUrl(record.thumbnail))" />
              <span v-else class="thumb-empty">无缩略图</span>
            </div>
          </template>

          <template #create_time="{ record }">
            <span>{{ formatDate(record.create_time) }}</span>
          </template>

          <template #optional="{ record }">
            <div class="table-actions">
              <a-link type="primary" @click="handlePreview(record)">预览</a-link>
              <a-link type="primary" @click="handleUpdate(record)">编辑</a-link>
              <a-link status="danger" @click="handleDelete(record)">删除</a-link>
            </div>
          </template>
        </a-table>
      </a-scrollbar>
    </a-card>

    <!-- Create/Edit Modal Dialog (Componentized) -->
    <MaterialEditModal 
      v-model:visible="editModalVisible" 
      :type="editModalType" 
      :data="editRecord" 
      @success="getList" 
    />

    <!-- Interactive Sandboxed Live Preview Modal -->
    <a-modal v-model:visible="previewVisible" title="素材实时效果预览" width="600px" :footer="false" align-center @close="destroyPreviewChart">
      <div class="preview-box">
        <!-- Static background image/decor preview -->
        <div v-if="previewItem?.category === 'background' || previewItem?.category === 'image'" class="image-preview-panel" :style="previewBackgroundStyle">
          <div v-if="!previewItem?.config_data?.image && !previewItem?.thumbnail" class="color-text-indicator">
            背景颜色: {{ previewItem?.config_data?.color || '#000000' }}
          </div>
        </div>

        <!-- Live ECharts interactive preview -->
        <div v-else-if="previewItem?.category === 'echarts' || previewItem?.category === 'geojson'" class="chart-preview-container-wrapper">
          <div class="preview-theme-bar">
            <span class="preview-theme-title">效果背景底色测试:</span>
            <a-radio-group v-model="standalonePreviewTheme" size="mini" type="button" @change="handleStandaloneThemeChange">
              <a-radio value="dark">深色背景</a-radio>
              <a-radio value="light">浅色背景</a-radio>
            </a-radio-group>
          </div>
          <div class="chart-preview-panel" :style="{ backgroundColor: standalonePreviewTheme === 'dark' ? '#0f172a' : '#ffffff', border: standalonePreviewTheme === 'dark' ? '1px solid #1e293b' : '1px solid #e5e6eb' }">
            <div ref="previewChartRef" class="chart-sandbox"></div>
            <div v-if="previewChartError" class="chart-error">
              <span>图表选项渲染失败: {{ previewChartError }}</span>
            </div>
          </div>
        </div>

        <!-- Map GeoJSON text view -->
        <div v-else class="raw-config-preview">
          <pre class="json-code-box"><code>{{ previewGeoJsonText }}</code></pre>
        </div>
      </div>
    </a-modal>

    <!-- Original Image Viewer -->
    <a-image-preview v-model:visible="imagePreviewVisible" :src="previewImageUrl" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { TableColumnData } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import { 
  getOfficialMaterials, deleteOfficialMaterial 
} from '../../../api/material'
import { formatDate, resolveImageUrl, escapeXml, isSvgUrl } from '../../../utils'
import * as echarts from 'echarts'
import MaterialEditModal from '../../../components/MaterialEditModal.vue'

const loading = ref(false)
const tableData = ref<any[]>([])

// Componentized Edit Modal states
const editModalVisible = ref(false)
const editModalType = ref<'create' | 'update'>('create')
const editRecord = ref<any>(null)

// Preview variables
const previewGeoJsonText = ref('')
const previewVisible = ref(false)
const previewItem = ref<any>(null)
const previewChartRef = ref<HTMLDivElement | null>(null)
const previewChartError = ref('')
let previewChartInstance: any = null
let previewRegisteredMaps: string[] = [] // tracks map names registered for current preview

// Image viewer variables
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true
})

const searchForm = reactive({
  name: '',
  category: undefined
})

const columns: TableColumnData[] = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '品类大类', slotName: 'category', width: 130, align: 'center' },
  { title: '分类标识/标签', slotName: 'tags', width: 150 },
  { title: '素材名称', dataIndex: 'name', width: 180 },
  { title: '缩略图', slotName: 'thumbnail', width: 120, align: 'center' },
  { title: '创建人', dataIndex: 'create_by', width: 120 },
  { title: '创建时间', slotName: 'create_time', width: 180 },
  { title: '操作', slotName: 'optional', align: 'center', width: 220 }
]



const chartTypes = [
  { value: 'line', label: '折线图' },
  { value: 'bar', label: '柱状图' },
  { value: 'pie', label: '饼图' },
  { value: 'scatter', label: '散点图' },
  { value: 'map', label: '地理坐标/地图' },
  { value: 'candlestick', label: 'K 线图' },
  { value: 'radar', label: '雷达图' },
  { value: 'boxplot', label: '盒须图' },
  { value: 'heatmap', label: '热力图' },
  { value: 'graph', label: '关系图' },
  { value: 'lines', label: '路径图' },
  { value: 'tree', label: '树图' },
  { value: 'treemap', label: '矩形树图' },
  { value: 'sunburst', label: '旭日图' },
  { value: 'parallel', label: '平行坐标系' },
  { value: 'sankey', label: '桑基图' },
  { value: 'funnel', label: '漏斗图' },
  { value: 'gauge', label: '仪表盘' },
  { value: 'pictorialBar', label: '象形柱图' },
  { value: 'themeRiver', label: '主题河流图' },
  { value: 'calendar', label: '日历坐标系' },
  { value: 'matrix', label: '矩阵坐标系' },
  { value: 'chord', label: '和弦图' },
  { value: 'custom', label: '自定义系列' },
  { value: 'dataset', label: '数据集' },
  { value: 'dataZoom', label: '数据区域缩放' },
  { value: 'graphic', label: '图形组件' },
  { value: 'richText', label: '富文本' },
  { value: 'globe', label: '3D 地球' },
  { value: 'bar3D', label: '3D 柱状图' },
  { value: 'scatter3D', label: '3D 散点图' },
  { value: 'surface', label: '3D 曲面' },
  { value: 'map3D', label: '3D 地图' },
  { value: 'lines3D', label: '3D 路径图' },
  { value: 'line3D', label: '3D 折线图' },
  { value: 'scatterGL', label: 'GL 散点图' },
  { value: 'linesGL', label: 'GL 路径图' },
  { value: 'flowGL', label: 'GL 矢量场图' },
  { value: 'graphGL', label: 'GL 关系图' },
  { value: 'other', label: '其它图表' }
]

function getSubcategoryLabel(val: string): string {
  const found = chartTypes.find(t => t.value === val)
  return found ? found.label : val
}

const geoJsonMaterials = ref<any[]>([])

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

async function registerMapFromMaterialInIndex(mapName: string, material: any) {
  if (!material) return
  
  if (material.category === 'geojson') {
    const geoJsonData = await loadGeoJsonData(material.config_data)
    if (geoJsonData) {
      echarts.registerMap(mapName, geoJsonData)
      previewRegisteredMaps.push(mapName)
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
        previewRegisteredMaps.push(mapName)
      }
    } else {
      const dimensions = await getImageDimensions(fileUrl)
      const svgText = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${dimensions.width} ${dimensions.height}">
          <image href="${escapeXml(fileUrl)}" width="${dimensions.width}" height="${dimensions.height}" x="0" y="0" />
        </svg>
      `.trim()
      echarts.registerMap(mapName, { svg: svgText })
      previewRegisteredMaps.push(mapName)
    }
  }
}

async function loadGeoJsonMaterials() {
  try {
    const resGeo: any = await getOfficialMaterials({ category: 'geojson', page: 1, page_size: 100 })
    const resImg: any = await getOfficialMaterials({ category: 'image', page: 1, page_size: 100 })
    geoJsonMaterials.value = [...(resGeo.items || []), ...(resImg.items || [])]
  } catch (e) {
    console.error('Failed to load GeoJSON/Image materials:', e)
  }
}



function findMapName(option: any): string | null {
  if (!option) return null
  if (option.geo && option.geo.map) return option.geo.map
  if (option.series) {
    const list = Array.isArray(option.series) ? option.series : [option.series]
    for (const s of list) {
      if ((s?.type === 'map' || s?.type === 'map3D') && s.map) {
        return s.map
      }
    }
  }
  return null
}

// ECharts preview theme toggles (runtime-only display)
const standalonePreviewTheme = ref<'dark' | 'light'>('dark')

function handleStandaloneThemeChange() {
  initPreviewChart()
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



// Background preview HSL stylesheet helper
const previewBackgroundStyle = computed(() => {
  if (!previewItem.value) return {}
  const cfg = previewItem.value.config_data || {}
  const imgUrl = cfg.image || previewItem.value.thumbnail
  const resolvedUrl = resolveImageUrl(imgUrl)
  return {
    backgroundColor: formatHexColor(cfg.color),
    backgroundImage: resolvedUrl ? `url(${resolvedUrl})` : 'none',
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

// Load Official Materials list
async function getList() {
  loading.value = true
  try {
    const res: any = await getOfficialMaterials({
      category: searchForm.category || undefined,
      name: searchForm.name.trim() || undefined,
      page: pagination.current,
      page_size: pagination.pageSize
    })
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (err) {
    console.error(err)
    Message.error('素材列表加载失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.current = 1
  getList()
}

function onPageChange(current: number) {
  pagination.current = current
  getList()
}

function handleCreate() {
  editModalType.value = 'create'
  editRecord.value = null
  editModalVisible.value = true
}

function handleUpdate(row: any) {
  editModalType.value = 'update'
  editRecord.value = row
  editModalVisible.value = true
}

async function handleDelete(row: any) {
  Modal.confirm({
    title: '确认删除',
    content: `您确定要彻底删除官方模版素材 "${row.name}" 吗？这会导致普通用户无法再从官方商店拉取该素材。`,
    okText: '确定',
    cancelText: '取消',
    okButtonProps: {
      status: 'danger'
    },
    async onOk() {
      try {
        await deleteOfficialMaterial(row.id)
        Message.success('删除官方素材成功')
        getList()
      } catch (err) {
        console.error(err)
      }
    }
  })
}

async function handlePreview(row: any) {
  previewItem.value = row
  standalonePreviewTheme.value = 'dark'
  previewVisible.value = true
  previewChartError.value = ''
  previewGeoJsonText.value = ''
  
  if (row.category === 'echarts' || row.category === 'geojson') {
    nextTick(() => {
      initPreviewChart()
    })
  }
}

async function initPreviewChart() {
  if (!previewChartRef.value) return
  destroyPreviewChart()
  
  try {
    let opt: any = null
    
    if (previewItem.value.category === 'geojson') {
      const geoJsonData = await loadGeoJsonData(previewItem.value.config_data)
      if (geoJsonData) {
        const mapName = 'preview_geojson_' + previewItem.value.id + '_' + Date.now()
        echarts.registerMap(mapName, geoJsonData)
        previewRegisteredMaps.push(mapName)
        opt = {
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
        throw new Error('地图数据加载失败或为空')
      }
    } else {
      // ECharts Option
      opt = previewItem.value.config_data || {}
      
      // Register maps if _geoJsonMap (new format) or _geoJsonId (legacy format) exists
      const geoMap = opt._geoJsonMap
      const rawId = opt._geoJsonId
      if ((geoMap && typeof geoMap === 'object') || rawId) {
        if (geoMap && typeof geoMap === 'object') {
          for (const [mapName, id] of Object.entries(geoMap)) {
            const mapMaterial = geoJsonMaterials.value.find((item: any) => item.id === id)
            if (mapMaterial) {
              await registerMapFromMaterialInIndex(mapName, mapMaterial)
            }
          }
        }
        
        if (rawId) {
          const ids = Array.isArray(rawId) ? rawId : [rawId]
          for (const id of ids) {
            const mapMaterial = geoJsonMaterials.value.find((item: any) => item.id === id)
            if (mapMaterial) {
              if (ids.length === 1) {
                const mapName = findMapName(opt) || 'custom_map_' + Date.now()
                await registerMapFromMaterialInIndex(mapName, mapMaterial)
              }
              await registerMapFromMaterialInIndex(`map_${id}`, mapMaterial)
              if (mapMaterial.name) {
                await registerMapFromMaterialInIndex(mapMaterial.name, mapMaterial)
              }
              if (mapMaterial.config_data?.filename) {
                const baseName = mapMaterial.config_data.filename.replace(/\.json$/i, '')
                await registerMapFromMaterialInIndex(baseName, mapMaterial)
              }
            }
          }
        }
      }
    }
    
    const theme = standalonePreviewTheme.value === 'dark' ? 'dark' : undefined
    
    previewChartInstance = echarts.init(previewChartRef.value, theme)
    previewChartInstance.setOption(opt, true)
    
    nextTick(() => {
      if (previewChartInstance) {
        previewChartInstance.resize()
      }
    })
  } catch (err: any) {
    console.error(err)
    previewChartError.value = err.message || '图表 Option 渲染参数解析失败。'
  }
}

function destroyPreviewChart() {
  if (previewChartInstance) {
    previewChartInstance.dispose()
    previewChartInstance = null
  }
  // Clear all registered maps from this preview to avoid global cache pollution
  const emptyGeoJson = { type: 'FeatureCollection', features: [] } as any
  for (const name of previewRegisteredMaps) {
    try { echarts.registerMap(name, emptyGeoJson) } catch (_) {}
  }
  previewRegisteredMaps = []
}

// Click to view full image zoom
function viewOriginalImage(url: string) {
  previewImageUrl.value = url
  imagePreviewVisible.value = true
}

// Helpers category text
function getCategoryText(cat: string) {
  switch (cat) {
    case 'echarts':
      return 'ECharts 图表'
    case 'background':
      return '背景模版'
    case 'image':
      return '装饰素材'
    case 'geojson':
      return '地图底图'
    default:
      return cat
  }
}

function getCategoryTagColor(cat: string) {
  switch (cat) {
    case 'echarts':
      return 'arcoblue'
    case 'background':
      return 'purple'
    case 'image':
      return 'green'
    case 'geojson':
      return 'orangered'
    default:
      return 'gray'
  }
}

onMounted(() => {
  getList()
  loadGeoJsonMaterials()
})
</script>

<style scoped>
.material-management-container {
  height: 100%;
}

.box-card {
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #E5E6EB;
  background: #FFFFFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  
}

.title {
  font-size: 16px;
  font-weight: 500;
  color: #1D2129;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input, .search-select {
  width: 160px;
}

.table-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.thumb-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-thumb-img {
  width: 50px;
  height: 35px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #e5e6eb;
  cursor: pointer;
  transition: transform 0.2s;
}

.table-thumb-img:hover {
  transform: scale(1.1);
}

.thumb-empty {
  font-size: 12px;
  color: #86909c;
}

/* Modal Form Styles */
.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-preview-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.uploaded-indicator-img {
  width: 48px;
  height: 32px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #e5e6eb;
}

.code-editor {
  font-family: 'Fira Code', monospace;
  background-color: #0f172a !important;
  color: #38bdf8 !important;
  font-size: 13px;
  line-height: 1.5;
}

.json-tips {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 12px;
  color: #86909c;
}

.json-error-msg {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

/* Preview Modal CSS Styles */
.preview-box {
  padding: 10px 0;
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

.chart-preview-panel {
  width: 100%;
  height: 350px;
  background-color: #0f172a;
  border-radius: 4px;
  border: 1px solid #e5e6eb;
  position: relative;
  overflow: hidden;
}

.chart-sandbox {
  width: 100%;
  height: 100%;
}

.chart-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  font-size: 14px;
  padding: 20px;
  box-sizing: border-box;
}

.raw-config-preview {
  background-color: #f1f5f9;
  border-radius: 4px;
  padding: 16px;
  max-height: 350px;
  overflow-y: auto;
  border: 1px solid #e5e6eb;
}

.json-code-box {
  margin: 0;
  font-family: monospace;
  font-size: 13px;
  color: #0f172a;
}

</style>
