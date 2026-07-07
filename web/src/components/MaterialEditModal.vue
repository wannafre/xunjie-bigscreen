<template>
  <a-modal 
    v-model:visible="visible" 
    :title="type === 'create' ? '新建官方图表素材' : '编辑官方图表素材'" 
    width="980px"
    @before-ok="submitForm" 
    :mask-closable="false" 
    align-center 
    @close="handleEditModalClose"
  >
    <a-row :gutter="24">
      <!-- Left: Form inputs -->
      <a-col :span="13">
        <a-form :model="materialForm" :rules="formRules" ref="materialFormRef" layout="vertical">
          <a-grid :cols="2" :col-gap="16">
            <a-grid-item>
              <a-form-item field="name" label="素材名称" required>
                <a-input v-model="materialForm.name" placeholder="请输入素材名称" :maxLength="100" />
              </a-form-item>
            </a-grid-item>
            <a-grid-item>
              <a-form-item field="category" label="素材大类" required>
                <a-select v-model="materialForm.category" placeholder="请选择品类大类" @change="handleCategoryChange">
                  <a-option value="echarts">ECharts 图表</a-option>
                  <a-option value="background">大屏背景模板</a-option>
                  <a-option value="image">装饰图片素材</a-option>
                  <a-option value="geojson">GeoJSON 地图数据</a-option>
                </a-select>
              </a-form-item>
            </a-grid-item>
          </a-grid>

          <a-grid :cols="2" :col-gap="16" v-if="materialForm.category === 'echarts'">
            <!-- ECharts subcategory (Dropdown select) -->
            <a-grid-item>
              <a-form-item field="subcategory" label="图表子类型" required>
                <a-select v-model="materialForm.subcategory" placeholder="自动识别中..." disabled>
                  <a-option v-for="t in chartTypes" :key="t.value" :value="t.value">
                    {{ t.label }} ({{ t.value }})
                  </a-option>
                </a-select>
              </a-form-item>
            </a-grid-item>
            
            <!-- Map Options Toggle -->
            <a-grid-item>
              <a-form-item label="地图类型选项">
                <a-checkbox v-model="isMapChart" @change="handleIsMapChartChange">是否为地图图表</a-checkbox>
              </a-form-item>
            </a-grid-item>
          </a-grid>

          <!-- Background / Image upload -->
          <a-grid :cols="1" v-if="materialForm.category === 'background' || materialForm.category === 'image'">
            <a-grid-item>
              <a-form-item label="资源图片上传" required>
                <div class="upload-area">
                  <input type="file" ref="fileInputRef" @change="handleFileUpload" style="display:none;" />
                  <a-button type="secondary" size="small" @click="fileInputRef?.click()" :loading="uploading">
                    <template #icon><IconUpload /></template>
                    上传图片
                  </a-button>
                  <div v-if="materialForm.thumbnail" class="upload-preview-indicator">
                    <img :src="resolveImageUrl(materialForm.thumbnail)" class="uploaded-indicator-img" />
                    <a-link status="danger" size="small" @click="handleImageRemove">移除</a-link>
                  </div>
                </div>
              </a-form-item>
            </a-grid-item>
          </a-grid>

          <!-- Associated GeoJSON select for ECharts Map -->
          <a-form-item label="关联地图数据 (GeoJSON)" v-if="materialForm.category === 'echarts' && isMapChart" required style="margin-top: 10px;">
            <a-select v-model="associatedGeoJsonId" placeholder="请选择关联的 GeoJSON 地图数据" allow-clear multiple @change="handleGeoJsonAssociationChange">
              <a-option v-for="item in geoJsonMaterials" :key="item.id" :value="item.id">
                {{ item.name }}
              </a-option>
            </a-select>
          </a-form-item>

          <!-- JSON Option Editor (Only for charts) -->
          <a-form-item label="配置选项 Option (支持 JS Object / JSON 结构)" required v-if="materialForm.category === 'echarts'">
            <template #extra>
              <div class="json-tips">
                <span>配置支持标准 JS 对象或 JSON 格式 (允许单引号、注释、无引号键名)。</span>
                <a-link type="primary" size="mini" @click="formatJsonString">美化并转为 JSON</a-link>
              </div>
            </template>
            <a-textarea v-model="configJsonStr" placeholder="请输入核心配置选项，支持 JS 对象结构，例如 { title: { text: '图表' } }" :auto-size="{ minRows: 8, maxRows: 12 }" class="code-editor" @input="debouncedUpdatePreview" @keydown="handleJsonEditorKeydown" />
            <div v-if="jsonSyntaxError" class="json-error-msg">{{ jsonSyntaxError }}</div>
          </a-form-item>

          <!-- GeoJSON Map Data (Custom Dual-Mode Interface) -->
          <template v-if="materialForm.category === 'geojson'">
            <a-form-item label="数据导入方式" required style="margin-bottom: 12px;">
              <a-radio-group v-model="geoJsonImportMode" type="button" size="small">
                <a-radio value="upload">上传 JSON 文件</a-radio>
                <a-radio value="edit">在线粘贴/编辑</a-radio>
              </a-radio-group>
            </a-form-item>

            <!-- Upload Mode -->
            <a-form-item label="GeoJSON 地图文件" required v-if="geoJsonImportMode === 'upload'" style="margin-bottom: 12px;">
              <div v-if="!uploadedGeoJsonFileInfo" class="geojson-upload-zone" @click="triggerGeoJsonFileInput" @dragover.prevent @drop.prevent="handleGeoJsonFileDrop">
                <div class="upload-trigger-container">
                  <icon-upload class="upload-icon" />
                  <div class="upload-text">点击选择文件或拖拽 GeoJSON 文件到此处 (仅支持 .json)</div>
                </div>
                <input
                  type="file"
                  ref="geoJsonFileInputRef"
                  accept=".json"
                  style="display: none"
                  @change="handleGeoJsonFileChange"
                />
              </div>
              <div v-else class="file-info-bar" style="margin-top: 0;">
                <span>当前文件: <strong>{{ uploadedGeoJsonFileInfo.name }}</strong> ({{ uploadedGeoJsonFileInfo.size }})</span>
                <a-link status="danger" @click="clearUploadedGeoJson">清除</a-link>
              </div>
              <div v-if="jsonSyntaxError" class="json-error-msg" style="margin-top: 6px;">{{ jsonSyntaxError }}</div>
            </a-form-item>

            <!-- Text/Edit Mode -->
            <a-form-item label="地图 JSON 内容" required v-if="geoJsonImportMode === 'edit'" style="margin-bottom: 12px;">
              <template #extra>
                <div class="json-tips">
                  <span>请输入符合标准 JSON 规范的内容 (属性名须用双引号包裹，不可含注释)。</span>
                  <a-link type="primary" size="mini" @click="formatGeoJsonString">格式化 JSON</a-link>
                </div>
              </template>
              <a-textarea 
                v-model="configJsonStr" 
                placeholder='请输入合法的 GeoJSON 数据，例如: &#10;{&#10;  "type": "FeatureCollection",&#10;  "features": []&#10;}' 
                :auto-size="{ minRows: 8, maxRows: 12 }" 
                class="code-editor" 
                @input="validatePasteJson" 
              />
              <div v-if="jsonSyntaxError" class="json-error-msg" style="margin-top: 6px;">{{ jsonSyntaxError }}</div>
            </a-form-item>

            <!-- File Preview (Upload Mode only, shows read-only text of parsed JSON) -->
            <a-form-item label="地图数据预览" v-if="geoJsonImportMode === 'upload' && configJsonStr && !jsonSyntaxError" style="margin-bottom: 12px;">
              <div class="geojson-preview-box">
                <a-textarea
                  :model-value="editGeoJsonPreviewText"
                  readonly
                  :auto-size="{ minRows: 6, maxRows: 10 }"
                  class="code-editor readonly"
                />
              </div>
            </a-form-item>
          </template>

          <!-- Background color and image url settings (Option-style) -->
          <template v-if="materialForm.category === 'background'">
            <a-form-item label="背景色配置">
              <a-input v-model="bgOptions.color" placeholder="请输入十六进制背景颜色，例如 #0b132b" @input="updateBgOptions" />
            </a-form-item>
            <a-form-item label="背景图链接 (通过上方上传图片自动生成，不可手动修改)">
              <a-input v-model="materialForm.thumbnail" placeholder="请在上方上传缩略图片以生成链接" disabled />
            </a-form-item>
          </template>

          <!-- Image tags settings (Dropdown-style with presets + auto create) -->
          <template v-if="materialForm.category === 'image'">
            <a-form-item label="素材描述标签 (可选或输入自定义，最多5个)">
              <a-select 
                v-model="selectedTags" 
                multiple 
                allow-create 
                placeholder="请选择预设标签或输入后回车添加自定义"
                :limit="5"
              >
                <a-option v-for="tag in defaultPresets" :key="tag" :value="tag">{{ tag }}</a-option>
              </a-select>
            </a-form-item>
          </template>
        </a-form>
      </a-col>

      <!-- Right: Live Preview -->
      <a-col :span="11">
        <div class="edit-preview-container">
          <div class="preview-title">
            <span>实时预览 (所见即所得)</span>
            <a-radio-group v-if="materialForm.category === 'echarts' || materialForm.category === 'geojson'" v-model="editPreviewTheme" size="mini" type="button" @change="handleEditThemeChange">
              <a-radio value="dark">暗底色</a-radio>
              <a-radio value="light">亮底色</a-radio>
            </a-radio-group>
          </div>
          <div class="preview-body">
            <!-- ECharts preview -->
            <div v-if="materialForm.category === 'echarts' || materialForm.category === 'geojson'" 
              class="edit-chart-preview-wrapper"
              :style="{ backgroundColor: editPreviewTheme === 'dark' ? '#0f172a' : '#ffffff', border: editPreviewTheme === 'dark' ? '1px solid #1e293b' : '1px solid #e5e6eb' }"
            >
              <div ref="editChartRef" class="edit-chart-sandbox"></div>
              <div v-if="editChartError" class="chart-error-msg">
                <span>等待有效 JSON 输入...</span>
              </div>
            </div>
            
            <!-- Background preview -->
            <div v-else-if="materialForm.category === 'background' || materialForm.category === 'image'" class="edit-bg-preview" :style="editBackgroundStyle">
              <div v-if="!materialForm.thumbnail && !materialForm.config_data?.image" class="color-text-indicator">
                背景颜色: {{ materialForm.config_data?.color || '#000000' }}
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
      </a-col>
    </a-row>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, watch, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconUpload } from '@arco-design/web-vue/es/icon'
import { 
  createOfficialMaterial, updateOfficialMaterial, getOfficialMaterials, uploadFile, deleteFile
} from '../api/material'
import { resolveImageUrl } from '../utils'
import * as echarts from 'echarts'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  type: {
    type: String, // 'create' | 'update'
    default: 'create'
  },
  data: {
    type: Object, // row record or null
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success'])

const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const materialFormRef = ref()
const uploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const materialForm = reactive({
  id: undefined,
  name: '',
  category: 'echarts',
  subcategory: '',
  thumbnail: '',
  config_data: null as any
})

const configJsonStr = ref('')
const jsonSyntaxError = ref('')

const formRules = {
  name: [{ required: true, message: '请输入素材模版名称' }],
  category: [{ required: true, message: '请选择品类大类' }]
}

// Live preview states and logic inside edit dialog
const editChartRef = ref<HTMLDivElement | null>(null)
const editChartError = ref(false)
let editChartInstance: any = null
let editRegisteredMaps: string[] = [] // track registered map names for this edit session

// Background and Image form fields options mapping
const bgOptions = reactive({
  color: '#0b132b',
  image: ''
})

const defaultPresets = ['科技', '蓝色', '边框', '渐变', '扁平', '深色', '浅色', '装饰', '高亮', '大屏']

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

const selectedTags = ref<string[]>([])
const associatedGeoJsonId = ref<number[] | number | undefined>(undefined)
const geoJsonMaterials = ref<any[]>([])
const isMapChart = ref(false)

// GeoJSON variables & helpers
const geoJsonImportMode = ref<'upload' | 'edit'>('upload')
const geoJsonFileInputRef = ref<HTMLInputElement | null>(null)
const uploadedGeoJsonFileInfo = ref<{ name: string; size: string } | null>(null)

function formatBytes(bytes: number, decimals = 2) {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

function triggerGeoJsonFileInput() {
  if (geoJsonFileInputRef.value) {
    geoJsonFileInputRef.value.click()
  }
}

function handleGeoJsonFileChange(e: any) {
  const file = e.target.files[0]
  if (!file) return
  processGeoJsonFile(file)
}

function handleGeoJsonFileDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  processGeoJsonFile(file)
}

function processGeoJsonFile(file: File) {
  if (!file.name.endsWith('.json')) {
    Message.error('仅支持上传 .json 格式的文件')
    return
  }

  const reader = new FileReader()
  reader.onload = (event: any) => {
    const text = event.target.result
    try {
      const parsed = JSON.parse(text)
      configJsonStr.value = JSON.stringify(parsed, null, 2)
      jsonSyntaxError.value = ''
      uploadedGeoJsonFileInfo.value = {
        name: file.name,
        size: formatBytes(file.size)
      }
      Message.success('JSON文件解析并验证成功')
      updateEditPreview()
    } catch (err: any) {
      jsonSyntaxError.value = 'JSON 规范校验失败: ' + err.message
      Message.error('文件不是合法的 JSON 格式')
      configJsonStr.value = ''
      uploadedGeoJsonFileInfo.value = null
    }
  }
  reader.onerror = () => {
    Message.error('文件读取失败')
  }
  reader.readAsText(file)
}

function clearUploadedGeoJson() {
  configJsonStr.value = ''
  jsonSyntaxError.value = ''
  uploadedGeoJsonFileInfo.value = null
  if (geoJsonFileInputRef.value) {
    geoJsonFileInputRef.value.value = ''
  }
}

function validatePasteJson() {
  if (!configJsonStr.value.trim()) {
    jsonSyntaxError.value = ''
    return
  }
  try {
    JSON.parse(configJsonStr.value)
    jsonSyntaxError.value = ''
    debouncedUpdatePreview()
  } catch (err: any) {
    jsonSyntaxError.value = 'JSON 规范校验失败: ' + err.message
  }
}

function formatGeoJsonString() {
  try {
    const parsed = JSON.parse(configJsonStr.value)
    configJsonStr.value = JSON.stringify(parsed, null, 2)
    jsonSyntaxError.value = ''
    autoDetectSubcategory(parsed)
  } catch (e: any) {
    jsonSyntaxError.value = '格式化失败 (不是合法的 JSON): ' + e.message
  }
}

const editGeoJsonPreviewText = computed(() => {
  if (materialForm.category !== 'geojson') return configJsonStr.value || '{}'
  if (!configJsonStr.value) return '{}'
  if (configJsonStr.value.length > 5000) {
    return configJsonStr.value.slice(0, 5000) + '\n\n... (地图数据过长，已截断显示，全部内容可在保存后查看) ...'
  }
  return configJsonStr.value
})

async function loadGeoJsonData(configData: any): Promise<any> {
  if (!configData) return null
  if (configData.url) {
    try {
      const res = await fetch(resolveImageUrl(configData.url))
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

async function loadGeoJsonMaterials() {
  try {
    const res: any = await getOfficialMaterials('geojson')
    geoJsonMaterials.value = res || []
  } catch (e) {
    console.error('Failed to load GeoJSON materials:', e)
  }
}

function handleGeoJsonAssociationChange(val: any) {
  try {
    const parsed = parseJsObject(configJsonStr.value)
    if (val) {
      parsed._geoJsonId = val
    } else {
      delete parsed._geoJsonId
    }
    configJsonStr.value = JSON.stringify(parsed, null, 2)
    updateEditPreview()
  } catch (e) {
    // Ignore invalid JSON edits
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

const editPreviewTheme = ref<'dark' | 'light'>('dark')

function handleEditThemeChange() {
  updateEditPreview()
}

function updateBgOptions() {
  materialForm.config_data = {
    color: bgOptions.color,
    image: materialForm.thumbnail
  }
}

// Watch selectedTags and sync to config_data
watch(selectedTags, (val) => {
  if (materialForm.category === 'image') {
    materialForm.config_data = {
      tags: val.join(',')
    }
  }
})

// Handle category changes to prevent cross-category state leaks
function handleCategoryChange(val: any) {
  configJsonStr.value = ''
  jsonSyntaxError.value = ''
  selectedTags.value = []
  bgOptions.color = '#0b132b'
  bgOptions.image = ''
  editPreviewTheme.value = 'dark'
  materialForm.thumbnail = ''
  materialForm.subcategory = ''
  materialForm.config_data = null
  isMapChart.value = false
  
  if (val === 'echarts') {
    materialForm.subcategory = 'line'
    configJsonStr.value = JSON.stringify({
      title: { text: "新折线图", textStyle: { color: "#fff" } },
      xAxis: { type: "category", data: ["Mon", "Tue", "Wed"] },
      yAxis: { type: "value" },
      series: [{ data: [10, 30, 20], type: "line" }]
    }, null, 2)
  } else if (val === 'geojson') {
    configJsonStr.value = '{}'
    geoJsonImportMode.value = 'upload'
    uploadedGeoJsonFileInfo.value = null
  } else if (val === 'background') {
    materialForm.config_data = { color: '#0b132b', image: '' }
  } else if (val === 'image') {
    materialForm.config_data = { tags: '' }
  }
}

function handleImageRemove() {
  materialForm.thumbnail = ''
  if (materialForm.category === 'background') {
    bgOptions.image = ''
    updateBgOptions()
  }
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
  const bgImage = resolveImageUrl(materialForm.thumbnail)
  const color = materialForm.category === 'background' ? formatHexColor(bgOptions.color) : '#0f172a'
  
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

async function updateEditPreview() {
  if ((materialForm.category !== 'echarts' && materialForm.category !== 'geojson') || !editChartRef.value) return
  try {
    let parsed: any = null
    editChartError.value = false
    
    if (materialForm.category === 'geojson') {
      if (!configJsonStr.value || !configJsonStr.value.trim() || configJsonStr.value === '{}' || configJsonStr.value === '正在加载 GeoJSON 地图数据...') {
        return
      }
      const geoJsonData = JSON.parse(configJsonStr.value)
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
      parsed = parseJsObject(configJsonStr.value)
      
      // Auto-detect ECharts subcategory
      autoDetectSubcategory(parsed)

      // Sync associatedGeoJsonId from parsed option
      if (JSON.stringify(parsed._geoJsonId) !== JSON.stringify(associatedGeoJsonId.value)) {
        associatedGeoJsonId.value = parsed._geoJsonId
      }

      // Check if isMapChart is true but subcategory is not map/map3D
      if (isMapChart.value && materialForm.subcategory !== 'map' && materialForm.subcategory !== 'map3D') {
        jsonSyntaxError.value = `提示：当前图表类型识别为 [${getSubcategoryLabel(materialForm.subcategory)}]，地图图表必须包含 map 或 map3D 类型的 series`
      } else {
        if (jsonSyntaxError.value && jsonSyntaxError.value.includes('提示：当前图表类型识别为')) {
          jsonSyntaxError.value = ''
        }
      }

      // Register map if _geoJsonId exists
      if (parsed._geoJsonId) {
        const ids = Array.isArray(parsed._geoJsonId) ? parsed._geoJsonId : [parsed._geoJsonId]
        for (const id of ids) {
          const geoJsonMaterial = geoJsonMaterials.value.find(item => item.id === id)
          if (geoJsonMaterial && geoJsonMaterial.config_data) {
            const geoJsonData = await loadGeoJsonData(geoJsonMaterial.config_data)
            if (geoJsonData) {
              if (ids.length === 1) {
                const mapName = findMapName(parsed) || 'custom_map'
                echarts.registerMap(mapName, geoJsonData)
                editRegisteredMaps.push(mapName)
              }
              const idMapName = `map_${id}`
              echarts.registerMap(idMapName, geoJsonData)
              editRegisteredMaps.push(idMapName)
              if (geoJsonMaterial.name) {
                echarts.registerMap(geoJsonMaterial.name, geoJsonData)
                editRegisteredMaps.push(geoJsonMaterial.name)
              }
              if (geoJsonMaterial.config_data.filename) {
                const baseName = geoJsonMaterial.config_data.filename.replace(/\.json$/i, '')
                echarts.registerMap(baseName, geoJsonData)
                editRegisteredMaps.push(baseName)
              }
            }
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
  } catch (e) {
    editChartError.value = true
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
    if (materialForm.category === 'geojson') {
      const parsed = JSON.parse(configJsonStr.value)
      configJsonStr.value = JSON.stringify(parsed, null, 2)
      jsonSyntaxError.value = ''
    } else {
      const parsed = parseJsObject(configJsonStr.value)
      configJsonStr.value = JSON.stringify(parsed, null, 2)
      jsonSyntaxError.value = ''
    }
    updateEditPreview()
  } catch (e: any) {
    jsonSyntaxError.value = '语法有误: ' + e.message
    editChartError.value = true
  }
}

function handleEditModalClose() {
  if (editChartInstance) {
    editChartInstance.dispose()
    editChartInstance = null
  }
  // Clear all registered maps to avoid stale global ECharts cache
  const emptyGeoJson = { type: 'FeatureCollection', features: [] } as any
  for (const name of editRegisteredMaps) {
    try { echarts.registerMap(name, emptyGeoJson) } catch (_) {}
  }
  editRegisteredMaps = []
  editChartError.value = false
}

// Media upload actions
async function handleFileUpload(e: any) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  
  uploading.value = true
  try {
    const res: any = await uploadFile(formData, materialForm.category === 'background' ? 'backgrounds' : 'thumbnails')
    if (res.url) {
      materialForm.thumbnail = res.url
      // Auto build config data object for backgrounds
      if (materialForm.category === 'background') {
        bgOptions.image = res.url
        materialForm.config_data = { color: bgOptions.color, image: res.url }
      }
      Message.success('缩略图上传成功')
    }
  } catch (err) {
    Message.error('上传图片失败')
  } finally {
    uploading.value = false
  }
}

// Auto-detect ECharts subcategory based on series type / options
function autoDetectSubcategory(parsed: any) {
  if (materialForm.category !== 'echarts') return
  
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
    
    const chartTypeValues = [
      'line', 'bar', 'pie', 'scatter', 'map', 'candlestick', 'radar', 'boxplot',
      'heatmap', 'graph', 'lines', 'tree', 'treemap', 'sunburst', 'parallel',
      'sankey', 'funnel', 'gauge', 'pictorialBar', 'themeRiver', 'calendar',
      'matrix', 'chord', 'custom', 'dataset', 'dataZoom', 'graphic', 'richText',
      'globe', 'bar3D', 'scatter3D', 'surface', 'map3D', 'lines3D', 'line3D',
      'scatterGL', 'linesGL', 'flowGL', 'graphGL'
    ]
    
    if (chartTypeValues.includes(detectedType)) {
      materialForm.subcategory = detectedType
    } else {
      materialForm.subcategory = 'other'
    }
  } else {
    materialForm.subcategory = 'other'
  }
}

// Parse JS Object / JSON string safely
function parseJsObject(str: string): any {
  if (!str || !str.trim()) return {}
  return new Function(`return (${str})`)()
}

// Format config JSON string
function formatJsonString() {
  try {
    const parsed = parseJsObject(configJsonStr.value)
    configJsonStr.value = JSON.stringify(parsed, null, 2)
    jsonSyntaxError.value = ''
    autoDetectSubcategory(parsed)
  } catch (e: any) {
    jsonSyntaxError.value = '格式化失败: ' + e.message
  }
}

// Handle Shift+Alt+F keyboard shortcut for formatting JSON
function handleJsonEditorKeydown(e: KeyboardEvent) {
  if (e.shiftKey && e.altKey && (e.key === 'f' || e.key === 'F')) {
    e.preventDefault()
    formatJsonString()
  }
}

function handleIsMapChartChange(val: any) {
  if (val) {
    if (materialForm.subcategory !== 'map' && materialForm.subcategory !== 'map3D') {
      materialForm.subcategory = 'map'
    }
    try {
      const parsed = parseJsObject(configJsonStr.value)
      const hasMap = parsed.series && (Array.isArray(parsed.series) ? parsed.series : [parsed.series]).some((s: any) => s.type === 'map' || s.type === 'map3D')
      const hasGeo = parsed.geo && parsed.geo.map
      const hasGlobe = parsed.globe
      if (!hasMap && !hasGeo && !hasGlobe) {
        const mapTemplate: any = {
          title: { text: "新地图图表", textStyle: { color: "#fff" } },
          tooltip: { show: true, trigger: "item" },
          series: [
            {
              name: "地图数据",
              type: "map",
              map: "custom_map",
              roam: true,
              data: []
            }
          ]
        }
        if (associatedGeoJsonId.value) {
          mapTemplate._geoJsonId = associatedGeoJsonId.value
        }
        configJsonStr.value = JSON.stringify(mapTemplate, null, 2)
      }
      updateEditPreview()
    } catch (e) {
      // Ignore invalid JSON edits
    }
  } else {
    associatedGeoJsonId.value = []
    try {
      const parsed = parseJsObject(configJsonStr.value)
      delete parsed._geoJsonId
      configJsonStr.value = JSON.stringify(parsed, null, 2)
      autoDetectSubcategory(parsed)
      updateEditPreview()
    } catch (e) {
      // Ignore
    }
  }
}

async function submitForm(done: any) {
  if (!materialFormRef.value) return done(true)
  const validationRes = await materialFormRef.value.validate()
  if (validationRes) {
    return done(false)
  }

  // Parse option JSON validation
  if (materialForm.category === 'echarts') {
    if (!configJsonStr.value.trim()) {
      jsonSyntaxError.value = '配置选项 JSON 不能为空'
      return done(false)
    }
    try {
      const parsed = parseJsObject(configJsonStr.value)
      
      // Auto-detect ECharts subcategory
      autoDetectSubcategory(parsed)

      // Enforce map validation if isMapChart is checked
      if (isMapChart.value) {
        if (materialForm.subcategory !== 'map' && materialForm.subcategory !== 'map3D') {
          jsonSyntaxError.value = `配置不是合法的地图图表类型 (当前自动识别为: ${getSubcategoryLabel(materialForm.subcategory)})，请确认 ECharts Option 的 series.type 为 'map' 或 'map3D'`
          Message.error('表单校验失败：勾选了地图类型，但配置选项未被识别为地图 (请确保包含 map 或 map3D 类型的 series)')
          return done(false)
        }
        if (!associatedGeoJsonId.value || (Array.isArray(associatedGeoJsonId.value) && associatedGeoJsonId.value.length === 0)) {
          Message.error('表单校验失败：请选择关联的 GeoJSON 地图数据')
          return done(false)
        }
        parsed._geoJsonId = associatedGeoJsonId.value
      } else {
        if (materialForm.subcategory === 'map' || materialForm.subcategory === 'map3D') {
          Message.warning('检测到您的配置为地图图表，建议勾选“是否为地图图表”并关联 GeoJSON 地图数据，否则地图可能无法渲染。')
        }
        delete parsed._geoJsonId
      }

      materialForm.config_data = parsed
      jsonSyntaxError.value = ''
    } catch (e: any) {
      jsonSyntaxError.value = '配置语法格式不正确: ' + e.message
      return done(false)
    }
  } else if (materialForm.category === 'geojson') {
    if (!configJsonStr.value.trim() || configJsonStr.value === '正在加载 GeoJSON 地图数据...') {
      jsonSyntaxError.value = 'GeoJSON 数据不能为空或未加载完成'
      return done(false)
    }
    let parsedData: any = null
    try {
      parsedData = JSON.parse(configJsonStr.value)
      jsonSyntaxError.value = ''
    } catch (e: any) {
      jsonSyntaxError.value = 'JSON 规范校验失败: ' + e.message
      return done(false)
    }

    // Upload JSON string as a file to the resource folder
    try {
      const blob = new Blob([JSON.stringify(parsedData)], { type: 'application/json' })
      const filename = `${materialForm.name || 'map'}.json`
      const formData = new FormData()
      formData.append('file', blob, filename)

      const uploadRes: any = await uploadFile(formData, 'geojson')
      if (uploadRes && uploadRes.url) {
        materialForm.config_data = {
          url: uploadRes.url,
          filename: filename,
          size: formatBytes(blob.size)
        }
      } else {
        throw new Error('上传文件接口未返回有效 URL')
      }
    } catch (err: any) {
      Message.error('上传 JSON 文件到服务器失败: ' + err.message)
      return done(false)
    }
  } else if (materialForm.category === 'background') {
    materialForm.config_data = {
      color: bgOptions.color,
      image: materialForm.thumbnail
    }
  } else if (materialForm.category === 'image') {
    materialForm.config_data = {
      tags: selectedTags.value.join(',')
    }
  }

  try {
    if (props.type === 'create') {
      await createOfficialMaterial(materialForm as any)
      Message.success('新建官方内置素材模版成功')
    } else {
      const { id, ...updatePayload } = materialForm
      await updateOfficialMaterial(id!, updatePayload)
      Message.success('编辑官方内置素材模版成功')
      
      // Clean up old thumbnail if it changed
      const oldThumbnail = props.data?.thumbnail
      if (oldThumbnail && oldThumbnail !== materialForm.thumbnail) {
        deleteFile(oldThumbnail).catch(err => {
          console.error('Failed to clean up old thumbnail:', err)
        })
      }
      
      // Clean up old GeoJSON if it changed
      if (materialForm.category === 'geojson') {
        const oldGeoUrl = props.data?.config_data?.url
        const newGeoUrl = materialForm.config_data?.url
        if (oldGeoUrl && oldGeoUrl !== newGeoUrl) {
          deleteFile(oldGeoUrl).catch(err => {
            console.error('Failed to clean up old GeoJSON file:', err)
          })
        }
      }
    }
    emit('success')
    visible.value = false
    done(true)
  } catch (err) {
    console.error(err)
    done(false)
  }
}

function resetForm() {
  Object.assign(materialForm, {
    id: undefined,
    name: '',
    category: 'echarts',
    subcategory: '',
    thumbnail: '',
    config_data: null
  })
  configJsonStr.value = ''
  jsonSyntaxError.value = ''
  bgOptions.color = '#0b132b'
  bgOptions.image = ''
  selectedTags.value = []
  associatedGeoJsonId.value = []
  editPreviewTheme.value = 'dark'
  geoJsonImportMode.value = 'upload'
  uploadedGeoJsonFileInfo.value = null
  isMapChart.value = false
}

function initForm() {
  resetForm()
  if (props.type === 'create') {
    editPreviewTheme.value = 'dark'
    geoJsonImportMode.value = 'upload'
    uploadedGeoJsonFileInfo.value = null
    isMapChart.value = false
    configJsonStr.value = JSON.stringify({
      title: { text: "新折线图", textStyle: { color: "#fff" } },
      xAxis: { type: "category", data: ["Mon", "Tue", "Wed"] },
      yAxis: { type: "value" },
      series: [{ data: [10, 30, 20], type: "line" }]
    }, null, 2)
  } else if (props.type === 'update' && props.data) {
    const row = props.data
    Object.assign(materialForm, {
      id: row.id,
      name: row.name,
      category: row.category,
      subcategory: row.subcategory,
      thumbnail: row.thumbnail,
      config_data: row.config_data
    })
    
    if (row.category === 'echarts') {
      configJsonStr.value = JSON.stringify(row.config_data || {}, null, 2)
      if (row.subcategory === 'map' || row.subcategory === 'map3D' || row.config_data?._geoJsonId) {
        isMapChart.value = true
        const rawId = row.config_data?._geoJsonId
        associatedGeoJsonId.value = Array.isArray(rawId) ? rawId : (rawId ? [rawId] : [])
      } else {
        isMapChart.value = false
        associatedGeoJsonId.value = []
      }
    } else if (row.category === 'geojson') {
      geoJsonImportMode.value = 'upload'
      if (row.config_data && row.config_data.url) {
        uploadedGeoJsonFileInfo.value = {
          name: row.config_data.filename || 'map.json',
          size: row.config_data.size || '未知大小'
        }
        configJsonStr.value = '正在加载 GeoJSON 地图数据...'
        fetch(resolveImageUrl(row.config_data.url))
          .then(res => {
            if (res.ok) return res.json()
            throw new Error(`HTTP ${res.status}`)
          })
          .then(data => {
            configJsonStr.value = JSON.stringify(data, null, 2)
            updateEditPreview()
          })
          .catch(err => {
            configJsonStr.value = ''
            jsonSyntaxError.value = '加载 GeoJSON 文件内容失败: ' + err.message
          })
      } else {
        configJsonStr.value = JSON.stringify(row.config_data || {}, null, 2)
        uploadedGeoJsonFileInfo.value = null
      }
    } else if (row.category === 'background') {
      bgOptions.color = row.config_data?.color || '#0b132b'
      bgOptions.image = row.config_data?.image || ''
    } else if (row.category === 'image') {
      selectedTags.value = row.config_data?.tags ? row.config_data.tags.split(',') : []
    }
  }
  
  nextTick(() => {
    updateEditPreview()
  })
}

// Watch modal state and trigger preview initialization
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initForm()
  } else {
    handleEditModalClose()
  }
})

// Watch category changes (if triggered externally or reactive change)
watch(() => materialForm.category, (catVal) => {
  if (props.visible && (catVal === 'echarts' || catVal === 'geojson')) {
    nextTick(() => {
      updateEditPreview()
    })
  } else {
    handleEditModalClose()
  }
})

onMounted(() => {
  loadGeoJsonMaterials()
  if (props.visible) {
    initForm()
  }
})
</script>

<style scoped>
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

.color-text-indicator {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255,255,255,0.1);
  color: #38bdf8;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
  font-family: monospace;
}

/* Edit Preview Layout Styles */
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

.preview-theme-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  width: 100%;
}

.preview-theme-title {
  font-size: 13px;
  color: #86909c;
}

.geojson-upload-zone {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.upload-trigger-container {
  border: 1px dashed #e5e6eb;
  border-radius: 4px;
  background-color: #f8fafc;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
}

.upload-trigger-container:hover {
  border-color: #165dff;
  background-color: #f2f3f5;
}

.upload-icon {
  font-size: 32px;
  color: #86909c;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 13px;
  color: #4e5969;
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e8f3ff;
  border: 1px solid #bae0ff;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  color: #1D2129;
}

.geojson-preview-box {
  width: 100%;
}

.code-editor.readonly {
  opacity: 0.85;
}

.json-code-box {
  margin: 0;
  font-family: monospace;
  font-size: 13px;
  color: #0f172a;
}
</style>
