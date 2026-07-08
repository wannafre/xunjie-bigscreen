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
                  <input type="file" ref="fileInputRef" @change="handleFileUpload" accept="image/*,image/svg+xml" style="display:none;" />
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

          <!-- Associated Map key-value mapping list for ECharts Map -->
          <div v-if="materialForm.category === 'echarts' && isMapChart" class="geojson-mapping-container">
            <div class="geojson-mapping-title">
              <span>关联地图数据 (GeoJSON / 装饰素材)</span>
              <a-button type="text" size="mini" @click="addGeoJsonEntry">
                <template #icon><IconPlus /></template>
                添加地图关联
              </a-button>
            </div>
            <div v-for="(entry, index) in geoJsonMapEntries" :key="index" class="geojson-mapping-row">
              <a-input v-model="entry.mapName" placeholder="ECharts map 注册名，如 china" style="width: 150px;" @input="syncGeoJsonMap" />
              <a-select v-model="entry.sourceType" style="width: 110px;" @change="() => { entry.materialId = undefined; syncGeoJsonMap(); }">
                <a-option value="geojson">GeoJSON地图</a-option>
                <a-option value="image">装饰素材</a-option>
              </a-select>
              <a-select 
                v-model="entry.materialId" 
                placeholder="选择关联的地图数据" 
                allow-search 
                :filter-option="false"
                @search="(val) => handleMapMaterialSearch(val, entry.sourceType)"
                @popup-visible-change="(visible) => { if (visible) handleMapMaterialSearch('', entry.sourceType); }"
                style="flex: 1;" 
                @change="syncGeoJsonMap"
              >
                <a-option v-for="item in getMapOptions(entry.sourceType)" :key="item.id" :value="item.id">
                  {{ item.name }}
                </a-option>
              </a-select>
              <a-button type="text" status="danger" size="small" @click="removeGeoJsonEntry(index)">
                <template #icon><IconDelete /></template>
              </a-button>
            </div>
            <div v-if="geoJsonMapEntries.length === 0" class="geojson-mapping-empty">
              暂未添加地图数据关联，点击上方按钮添加。
            </div>
          </div>

          <!-- JSON Option Editor (Only for charts) -->
          <a-form-item label="配置选项 Option (支持 JS Object / JSON 结构)" required v-if="materialForm.category === 'echarts'">
            <template #extra>
              <div class="json-tips">
                <span>配置支持标准 JS 对象或 JSON 格式。</span>
                <div class="editor-quick-actions">
                  <a-link v-if="isMapChart" type="warning" size="mini" @click="confirmRestoreDefaultMapOption" style="margin-right: 12px;">还原地图默认 Option</a-link>
                  <a-link type="primary" size="mini" @click="formatJsonString">美化并转为 JSON</a-link>
                </div>
              </div>
            </template>
            <div style="width: 100%; display: flex; flex-direction: column;">
              <div class="editor-input-wrapper">
                <a-textarea v-model="configJsonStr" ref="jsonTextareaRef" placeholder="请输入核心配置选项，支持 JS 对象结构，例如 { title: { text: '图表' } }" :auto-size="{ minRows: 8, maxRows: 12 }" class="code-editor" @keydown="handleJsonEditorKeydown" />
                <!-- Material Library Popover / Trigger -->
                <div class="insert-asset-bar">
                  <a-popover title="选择图片资源并插入到编辑器" trigger="click" position="bottom">
                    <a-button type="outline" size="mini">
                      <template #icon><IconImage /></template>
                      插入图片资源
                    </a-button>
                    <template #content>
                      <div class="asset-selector-popover-content" style="width: 280px; display: flex; flex-direction: column;">
                        <a-input-search 
                          v-model="imageSearchKeyword" 
                          size="mini" 
                          placeholder="输入名称搜索图片..." 
                          style="margin-bottom: 8px;" 
                          @search="handleImageSearch"
                          allow-clear
                          @clear="handleImageSearchClear"
                        />
                        <div class="asset-selector-grid">
                          <div v-for="asset in imageAndSvgMaterials" :key="asset.id" class="asset-selector-item" @click="insertAssetUrl(asset)">
                            <img v-if="asset.thumbnail" :src="resolveImageUrl(asset.thumbnail)" class="asset-grid-thumb" />
                            <div class="asset-grid-name">{{ asset.name }}</div>
                          </div>
                          <div v-if="imageAndSvgMaterials.length === 0" class="asset-grid-empty">
                            暂无图片素材。
                          </div>
                        </div>
                        <div v-if="imageTotal > 12" class="asset-selector-pagination-bar" style="margin-top: 8px; display: flex; justify-content: center; align-items: center; border-top: 1px solid #e5e6eb; padding-top: 8px;">
                          <a-pagination
                            v-model:current="imagePage"
                            :total="imageTotal"
                            :page-size="12"
                            size="mini"
                            simple
                            @change="handleImagePageChange"
                          />
                        </div>
                      </div>
                    </template>
                  </a-popover>
                </div>
              </div>
              <div v-if="jsonSyntaxError" class="json-error-msg" style="margin-top: 6px;">{{ jsonSyntaxError }}</div>
            </div>
          </a-form-item>

          <!-- GeoJSON Map Data (Componentized Dual-Mode Interface) -->
          <template v-if="materialForm.category === 'geojson'">
            <MaterialGeoJsonEditor
              v-model="configJsonStr"
              v-model:importMode="geoJsonImportMode"
              v-model:uploadedFileInfo="uploadedGeoJsonFileInfo"
              v-model:syntaxError="jsonSyntaxError"
              :name="materialForm.name"
            />
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

      <!-- Right: Live Preview Box (Componentized) -->
      <a-col :span="11">
        <MaterialPreviewBox
          ref="previewBoxRef"
          :category="materialForm.category"
          :thumbnail="materialForm.thumbnail"
          :configJsonStr="configJsonStr"
          :configData="materialForm.config_data"
          :geoJsonMap="currentGeoJsonMap"
          :geoJsonMaterials="allAvailableMapMaterials"
          @detect-subcategory="handleDetectSubcategory"
          @validation-error="handleValidationError"
        />
      </a-col>
    </a-row>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, watch, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { IconUpload, IconImage, IconPlus, IconDelete } from '@arco-design/web-vue/es/icon'
import { 
  createOfficialMaterial, updateOfficialMaterial, getOfficialMaterials, uploadFile, deleteFile
} from '../api/material'
import { resolveImageUrl } from '../utils'
import MaterialPreviewBox from './MaterialPreviewBox.vue'
import MaterialGeoJsonEditor from './MaterialGeoJsonEditor.vue'

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
const pendingFile = ref<File | null>(null)
const localPreviewUrl = ref<string>('')
const uploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const previewBoxRef = ref<any>(null)
const jsonTextareaRef = ref<any>(null)

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

const selectedTags = ref<string[]>([])
const geoJsonMapEntries = ref<Array<{ mapName: string; sourceType: 'geojson' | 'image'; materialId: number | undefined }>>([])
const geoJsonMaterials = ref<any[]>([])
const imageMaterials = ref<any[]>([])
const imageAndSvgMaterials = ref<any[]>([])
const isMapChart = ref(false)

const allAvailableMapMaterials = computed(() => {
  return [...geoJsonMaterials.value, ...imageMaterials.value]
})

// GeoJSON subcomponent bound variables
const geoJsonImportMode = ref<'upload' | 'edit'>('upload')
const uploadedGeoJsonFileInfo = ref<{ name: string; size: string } | null>(null)

// ECharts option image popover variables
const imageSearchKeyword = ref('')
const imagePage = ref(1)
const imageTotal = ref(0)

// Compute record map for PreviewBox
const currentGeoJsonMap = computed(() => {
  const obj: Record<string, number> = {}
  for (const entry of geoJsonMapEntries.value) {
    if (entry.mapName.trim() && entry.materialId) {
      obj[entry.mapName.trim()] = entry.materialId
    }
  }
  return obj
})

function formatBytes(bytes: number, decimals = 2) {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

async function loadGeoJsonMaterials() {
  try {
    const res: any = await getOfficialMaterials({
      category: 'geojson',
      page: 1,
      page_size: 100
    })
    geoJsonMaterials.value = res.items || []
  } catch (e) {
    console.error('Failed to load GeoJSON materials:', e)
  }
}

async function handleGeoJsonSearch(searchText: string) {
  try {
    const res: any = await getOfficialMaterials({
      category: 'geojson',
      name: searchText || undefined,
      page: 1,
      page_size: 30
    })
    const items = res.items || []
    // Merge search results with existing options so already selected items don't lose their label
    const merged = [...geoJsonMaterials.value]
    for (const item of items) {
      if (!merged.some(m => m.id === item.id)) {
        merged.push(item)
      }
    }
    geoJsonMaterials.value = merged
  } catch (e) {
    console.error('Failed to search GeoJSON materials:', e)
  }
}

async function loadImageAndSvgMaterials() {
  try {
    const res: any = await getOfficialMaterials({
      category: 'image',
      name: imageSearchKeyword.value || undefined,
      page: imagePage.value,
      page_size: 12
    })
    imageAndSvgMaterials.value = res.items || []
    imageTotal.value = res.total || 0
  } catch (e) {
    console.error('Failed to load image materials:', e)
  }
}

function handleImageSearch() {
  imagePage.value = 1
  loadImageAndSvgMaterials()
}

function handleImageSearchClear() {
  imageSearchKeyword.value = ''
  handleImageSearch()
}

function handleImagePageChange(page: number) {
  imagePage.value = page
  loadImageAndSvgMaterials()
}

async function loadImageMaterials() {
  try {
    const res: any = await getOfficialMaterials({
      category: 'image',
      page: 1,
      page_size: 100
    })
    imageMaterials.value = res.items || []
  } catch (e) {
    console.error('Failed to load image materials:', e)
  }
}

async function handleImageMaterialSearch(searchText: string) {
  try {
    const res: any = await getOfficialMaterials({
      category: 'image',
      name: searchText || undefined,
      page: 1,
      page_size: 30
    })
    const items = res.items || []
    const merged = [...imageMaterials.value]
    for (const item of items) {
      if (!merged.some(m => m.id === item.id)) {
        merged.push(item)
      }
    }
    imageMaterials.value = merged
  } catch (e) {
    console.error('Failed to search image materials:', e)
  }
}

function getMapOptions(sourceType: 'geojson' | 'image') {
  return sourceType === 'geojson' ? geoJsonMaterials.value : imageMaterials.value
}

function handleMapMaterialSearch(searchText: string, sourceType: 'geojson' | 'image') {
  if (sourceType === 'geojson') {
    handleGeoJsonSearch(searchText)
  } else {
    handleImageMaterialSearch(searchText)
  }
}

function addGeoJsonEntry() {
  geoJsonMapEntries.value.push({ mapName: '', sourceType: 'geojson', materialId: undefined })
}

function removeGeoJsonEntry(index: number) {
  const entry = geoJsonMapEntries.value[index]
  if (entry && entry.mapName && previewBoxRef.value) {
    previewBoxRef.value.unregisterMap(entry.mapName)
  }
  geoJsonMapEntries.value.splice(index, 1)
}

function syncGeoJsonMap() {
  // Triggers ECharts updates in previewBoxRef via watcher on currentGeoJsonMap
}

function insertAssetUrl(asset: any) {
  const url = asset.thumbnail
  if (!url) return

  const formattedUrl = url.startsWith('/') ? url : '/' + url
  
  const textarea = jsonTextareaRef.value?.$el?.querySelector('textarea')
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = configJsonStr.value
    configJsonStr.value = text.substring(0, start) + formattedUrl + text.substring(end)
    
    nextTick(() => {
      textarea.focus()
      textarea.setSelectionRange(start + formattedUrl.length, start + formattedUrl.length)
      if (previewBoxRef.value) {
        previewBoxRef.value.updateEditPreview()
      }
    })
  } else {
    configJsonStr.value += formattedUrl
  }
}



function handleDetectSubcategory(val: string) {
  materialForm.subcategory = val
}

function handleValidationError(msg: string) {
  jsonSyntaxError.value = msg
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
  materialForm.thumbnail = ''
  materialForm.subcategory = ''
  materialForm.config_data = null
  isMapChart.value = false
  geoJsonMapEntries.value = []
  
  pendingFile.value = null
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
    localPreviewUrl.value = ''
  }

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
  pendingFile.value = null
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
    localPreviewUrl.value = ''
  }
  materialForm.thumbnail = ''
  if (materialForm.category === 'background') {
    bgOptions.image = ''
    updateBgOptions()
  }
}

function handleFileUpload(e: any) {
  const file = e.target.files[0]
  if (!file) return

  pendingFile.value = file
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
  }
  
  localPreviewUrl.value = URL.createObjectURL(file)
  materialForm.thumbnail = localPreviewUrl.value
  
  if (materialForm.category === 'background') {
    bgOptions.image = localPreviewUrl.value
    materialForm.config_data = { color: bgOptions.color, image: localPreviewUrl.value }
  }
}

function parseJsObject(str: string): any {
  if (!str || !str.trim()) return {}
  return new Function(`return (${str})`)()
}

function formatJsonString() {
  try {
    const parsed = parseJsObject(configJsonStr.value)
    configJsonStr.value = JSON.stringify(parsed, null, 2)
    jsonSyntaxError.value = ''
    if (previewBoxRef.value) {
      previewBoxRef.value.updateEditPreview()
    }
  } catch (e: any) {
    jsonSyntaxError.value = '格式化失败: ' + e.message
  }
}

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
    if (geoJsonMapEntries.value.length === 0) {
      geoJsonMapEntries.value.push({ mapName: 'custom_map', sourceType: 'geojson', materialId: undefined })
    }
  } else {
    geoJsonMapEntries.value = []
    if (previewBoxRef.value) {
      previewBoxRef.value.cleanRegisteredMaps()
    }
  }
}

function confirmRestoreDefaultMapOption() {
  Modal.confirm({
    title: '确认还原地图默认 Option？',
    content: '此操作将用标准的 ECharts 地图渲染模板覆盖您当前的配置，已编辑的内容将会丢失。是否继续？',
    okText: '确认还原',
    cancelText: '取消',
    onOk: () => {
      const firstEntry = geoJsonMapEntries.value[0]
      const mapName = firstEntry?.mapName || 'custom_map'
      const mapTemplate = {
        title: { text: "地图图表", textStyle: { color: "#fff" } },
        tooltip: { show: true, trigger: "item", formatter: "{b}" },
        series: [
          {
            name: "地图数据",
            type: "map",
            map: mapName,
            roam: true,
            data: []
          }
        ]
      }
      configJsonStr.value = JSON.stringify(mapTemplate, null, 2)
      nextTick(() => {
        if (previewBoxRef.value) {
          previewBoxRef.value.updateEditPreview()
        }
      })
    }
  })
}

async function submitForm(done: any) {
  if (!materialFormRef.value) return done(true)
  const validationRes = await materialFormRef.value.validate()
  if (validationRes) {
    return done(false)
  }

  // Block saving if there is an ECharts options/JSON syntax/rendering error
  if (jsonSyntaxError.value) {
    Message.error('当前配置选项存在语法或渲染错误，无法保存！请修正后再提交。')
    return done(false)
  }

  // 1. Upload thumbnail if it's pending before database save
  if (pendingFile.value) {
    const formData = new FormData()
    formData.append('file', pendingFile.value)
    
    uploading.value = true
    try {
      const res: any = await uploadFile(formData, materialForm.category === 'background' ? 'backgrounds' : 'thumbnails')
      if (res.url) {
        materialForm.thumbnail = res.url
        pendingFile.value = null
        if (localPreviewUrl.value) {
          URL.revokeObjectURL(localPreviewUrl.value)
          localPreviewUrl.value = ''
        }
      } else {
        throw new Error('未返回有效文件URL')
      }
    } catch (err: any) {
      Message.error('上传图片失败: ' + err.message)
      uploading.value = false
      return done(false)
    } finally {
      uploading.value = false
    }
  }

  // Parse option JSON validation
  if (materialForm.category === 'echarts') {
    if (!configJsonStr.value.trim()) {
      jsonSyntaxError.value = '配置选项 JSON 不能为空'
      return done(false)
    }
    try {
      const parsed = parseJsObject(configJsonStr.value)
      
      // Enforce map validation if isMapChart is checked
      if (isMapChart.value) {
        // 1. Verify ECharts subcategory and options elements
        const hasMapSeries = parsed.series && (Array.isArray(parsed.series) ? parsed.series : [parsed.series]).some((s: any) => s && (s.type === 'map' || s.type === 'map3D'))
        const hasGeoComponent = parsed.geo && parsed.geo.map
        const hasGlobeComponent = parsed.globe
        
        if (!hasMapSeries && !hasGeoComponent && !hasGlobeComponent) {
          jsonSyntaxError.value = "配置选项中未找到合法的地图系列 (请确保 series 类型为 map / map3D，或者包含 geo.map 或 globe 配置)"
          Message.error('表单校验失败：勾选了地图类型，但配置选项未包含有效的地图系列(map/map3D)或 geo.map/globe 配置')
          return done(false)
        }
        
        if (materialForm.subcategory !== 'map' && materialForm.subcategory !== 'map3D') {
          jsonSyntaxError.value = `配置不是合法的地图图表类型，请确认 ECharts Option 的 series.type 为 'map' 或 'map3D'`
          Message.error('表单校验失败：勾选了地图类型，但配置选项未被识别为地图')
          return done(false)
        }
        
        // 2. Validate mapping entries
        if (geoJsonMapEntries.value.length === 0) {
          Message.error('表单校验失败：勾选了地图类型，请至少添加一个关联的 GeoJSON 地图数据')
          return done(false)
        }

        const geoMapObj: Record<string, number> = {}
        for (const entry of geoJsonMapEntries.value) {
          if (!entry.mapName || !entry.mapName.trim()) {
            Message.error('表单校验失败：关联地图数据中的注册名（Key）不能为空')
            return done(false)
          }
          if (!entry.materialId) {
            Message.error(`表单校验失败：请为地图注册名 "${entry.mapName}" 选择对应的 GeoJSON 地图数据`)
            return done(false)
          }
          if (geoMapObj[entry.mapName.trim()]) {
            Message.error(`表单校验失败：地图注册名 "${entry.mapName}" 重复，请修改为唯一名称`)
            return done(false)
          }
          geoMapObj[entry.mapName.trim()] = entry.materialId
        }
        
        parsed._geoJsonMap = geoMapObj
        if (parsed._geoJsonId) {
          delete parsed._geoJsonId
        }
      } else {
        if (materialForm.subcategory === 'map' || materialForm.subcategory === 'map3D') {
          Message.warning('检测到您的配置为地图图表，建议勾选“是否为地图图表”并关联 GeoJSON 地图数据，否则地图可能无法渲染。')
        }
        delete parsed._geoJsonId
        delete parsed._geoJsonMap
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
  geoJsonMapEntries.value = []
  isMapChart.value = false
}

function initForm() {
  pendingFile.value = null
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
    localPreviewUrl.value = ''
  }
  resetForm()
  if (props.type === 'create') {
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
      
      const loadNeededData = async () => {
        if (geoJsonMaterials.value.length === 0) {
          await loadGeoJsonMaterials()
        }
        if (imageMaterials.value.length === 0) {
          await loadImageMaterials()
        }
        
        const rawMap = row.config_data?._geoJsonMap
        const rawId = row.config_data?._geoJsonId
        if (rawMap && typeof rawMap === 'object') {
          isMapChart.value = true
          geoJsonMapEntries.value = Object.entries(rawMap).map(([key, val]) => {
            const mId = Number(val)
            const isGeo = geoJsonMaterials.value.some(item => item.id === mId)
            return {
              mapName: key,
              sourceType: isGeo ? 'geojson' : 'image',
              materialId: mId
            }
          })
        } else if (rawId) {
          isMapChart.value = true
          const ids = Array.isArray(rawId) ? rawId : [rawId]
          geoJsonMapEntries.value = ids.map(id => {
            const material = geoJsonMaterials.value.find(item => item.id === id)
            const isGeo = material ? true : false
            return {
              mapName: material?.name || `map_${id}`,
              sourceType: isGeo ? 'geojson' : 'image',
              materialId: id
            }
          })
        } else {
          isMapChart.value = false
          geoJsonMapEntries.value = []
        }
      }
      loadNeededData()
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
}

function handleEditModalClose() {
  pendingFile.value = null
  if (localPreviewUrl.value) {
    URL.revokeObjectURL(localPreviewUrl.value)
    localPreviewUrl.value = ''
  }
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
    // handled by previewBoxRef
  } else {
    handleEditModalClose()
  }
})

onMounted(() => {
  loadGeoJsonMaterials()
  loadImageMaterials()
  loadImageAndSvgMaterials()
  if (props.visible) {
    initForm()
  }
})
</script>

<style scoped>
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

.editor-input-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.insert-asset-bar {
  display: flex;
  justify-content: flex-end;
}

.asset-selector-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px;
}

.asset-selector-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  padding: 4px;
  transition: all 0.2s;
}

.asset-selector-item:hover {
  border-color: #165dff;
  background-color: #f2f3f5;
}

.asset-grid-thumb {
  width: 70px;
  height: 50px;
  object-fit: cover;
  border-radius: 2px;
  border: 1px solid #e5e6eb;
}

.asset-grid-name {
  font-size: 11px;
  color: #4e5969;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.asset-grid-empty {
  grid-column: span 3;
  color: #86909c;
  font-size: 12px;
  text-align: center;
  padding: 16px 0;
}

.geojson-mapping-container {
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  padding: 12px;
  background-color: #f8fafc;
  margin-bottom: 16px;
}

.geojson-mapping-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 8px;
}

.geojson-mapping-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.geojson-mapping-empty {
  font-size: 12px;
  color: #86909c;
  text-align: center;
  padding: 8px 0;
}
</style>
