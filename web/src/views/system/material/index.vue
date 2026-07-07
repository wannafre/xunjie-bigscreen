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
            <span v-else-if="record.subcategory">{{ record.subcategory }}</span>
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

    <!-- Create/Edit Modal Dialog -->
    <a-modal v-model:visible="dialogVisible" :title="dialogType === 'create' ? '新建官方图表素材' : '编辑官方图表素材'" width="980px"
      @before-ok="submitForm" :mask-closable="false" align-center @close="handleEditModalClose">
      <a-row :gutter="24">
        <!-- Left: Form inputs -->
        <a-col :span="13">
          <a-form :model="materialForm" :rules="formRules" ref="materialFormRef" layout="vertical">
            <a-grid :cols="2" :col-gap="16">
              <a-grid-item>
                <a-form-item field="name" label="素材名称" required>
                  <a-input v-model="materialForm.name" placeholder="请输入素材名称" maxLength="100" />
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

            <a-grid :cols="2" :col-gap="16">
              <!-- ECharts subcategory (Dropdown select) -->
              <a-grid-item v-if="materialForm.category === 'echarts'">
                <a-form-item field="subcategory" label="图表子类型" required>
                  <a-select v-model="materialForm.subcategory" placeholder="请选择图表子类型">
                    <a-option value="line">折线图 (line)</a-option>
                    <a-option value="bar">柱状图 (bar)</a-option>
                    <a-option value="pie">饼图/环形图 (pie)</a-option>
                    <a-option value="scatter">散点图 (scatter)</a-option>
                    <a-option value="radar">雷达图 (radar)</a-option>
                    <a-option value="gauge">仪表盘 (gauge)</a-option>
                    <a-option value="other">其它图表 (other)</a-option>
                  </a-select>
                </a-form-item>
              </a-grid-item>
              
              <!-- Background / Image upload -->
              <a-grid-item v-if="materialForm.category === 'background' || materialForm.category === 'image'">
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

            <!-- JSON Option Editor (Only for charts/maps) -->
            <a-form-item label="配置选项 Option (JSON 语法结构)" required v-if="materialForm.category === 'echarts' || materialForm.category === 'geojson'">
              <template #extra>
                <div class="json-tips">
                  <span>配置必须符合有效的 JSON 结构 。</span>
                  <a-link type="primary" size="mini" @click="formatJsonString">美化格式</a-link>
                </div>
              </template>
              <a-textarea v-model="configJsonStr" placeholder="请输入核心配置选项" :auto-size="{ minRows: 8, maxRows: 12 }" class="code-editor" @input="debouncedUpdatePreview" @keydown="handleJsonEditorKeydown" />
              <div v-if="jsonSyntaxError" class="json-error-msg">{{ jsonSyntaxError }}</div>
            </a-form-item>

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
              <a-radio-group v-if="materialForm.category === 'echarts'" v-model="editPreviewTheme" size="mini" type="button" @change="handleEditThemeChange">
                <a-radio value="dark">暗底色</a-radio>
                <a-radio value="light">亮底色</a-radio>
              </a-radio-group>
            </div>
            <div class="preview-body">
              <!-- ECharts preview -->
              <div v-if="materialForm.category === 'echarts'" 
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
                <pre class="json-code-box"><code>{{ configJsonStr || '{}' }}</code></pre>
              </div>
            </div>
            <div class="preview-footer">
              <a-button type="secondary" size="small" long @click="forceUpdatePreview">手动刷新渲染</a-button>
            </div>
          </div>
        </a-col>
      </a-row>
    </a-modal>

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
        <div v-else-if="previewItem?.category === 'echarts'" class="chart-preview-container-wrapper">
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
          <pre class="json-code-box"><code>{{ JSON.stringify(previewItem?.config_data || {}, null, 2) }}</code></pre>
        </div>
      </div>
    </a-modal>

    <!-- Original Image Viewer -->
    <a-image-preview v-model:visible="imagePreviewVisible" :src="previewImageUrl" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { TableColumnData } from '@arco-design/web-vue'
import { IconPlus, IconUpload } from '@arco-design/web-vue/es/icon'
import { 
  getOfficialMaterials, createOfficialMaterial, updateOfficialMaterial, deleteOfficialMaterial, uploadFile 
} from '../../../api/material'
import { formatDate, resolveImageUrl } from '../../../utils'
import * as echarts from 'echarts'

const loading = ref(false)
const tableData = ref<any[]>([])
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'update'>('create')
const materialFormRef = ref()
const uploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

// Preview variables
const previewVisible = ref(false)
const previewItem = ref<any>(null)
const previewChartRef = ref<HTMLDivElement | null>(null)
const previewChartError = ref('')
let previewChartInstance: any = null

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

// Background and Image form fields options mapping
const bgOptions = reactive({
  color: '#0b132b',
  image: ''
})

const defaultPresets = ['科技', '蓝色', '边框', '渐变', '扁平', '深色', '浅色', '装饰', '高亮', '大屏']
const selectedTags = ref<string[]>([])

// ECharts preview theme toggles (runtime-only display)
const editPreviewTheme = ref<'dark' | 'light'>('dark')
const standalonePreviewTheme = ref<'dark' | 'light'>('dark')

function handleEditThemeChange() {
  updateEditPreview()
}

function handleStandaloneThemeChange() {
  initPreviewChart()
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

function updateEditPreview() {
  if (materialForm.category !== 'echarts' || !editChartRef.value) return
  try {
    const parsed = JSON.parse(configJsonStr.value)
    editChartError.value = false
    
    if (editChartInstance) {
      editChartInstance.dispose()
      editChartInstance = null
    }
    const currentTheme = editPreviewTheme.value === 'dark' ? 'dark' : undefined
    editChartInstance = echarts.init(editChartRef.value, currentTheme)
    
    editChartInstance.setOption(parsed, true)
    nextTick(() => {
      editChartInstance.resize()
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
    const parsed = JSON.parse(configJsonStr.value)
    configJsonStr.value = JSON.stringify(parsed, null, 2)
    jsonSyntaxError.value = ''
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
  editChartError.value = false
}

// Watch modal state and trigger preview
watch([dialogVisible, () => materialForm.category], ([visibleVal, catVal]) => {
  if (visibleVal && catVal === 'echarts') {
    nextTick(() => {
      updateEditPreview()
    })
  } else {
    handleEditModalClose()
  }
})

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
    const res: any = await getOfficialMaterials(searchForm.category)
    let filtered = res || []
    if (searchForm.name.trim()) {
      filtered = filtered.filter((m: any) => m.name.toLowerCase().includes(searchForm.name.toLowerCase()))
    }
    tableData.value = filtered
    pagination.total = filtered.length
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
  editPreviewTheme.value = 'dark'
}

function handleCreate() {
  resetForm()
  editPreviewTheme.value = 'dark'
  configJsonStr.value = JSON.stringify({
    title: { text: "新折线图", textStyle: { color: "#fff" } },
    xAxis: { type: "category", data: ["Mon", "Tue", "Wed"] },
    yAxis: { type: "value" },
    series: [{ data: [10, 30, 20], type: "line" }]
  }, null, 2)
  dialogType.value = 'create'
  dialogVisible.value = true
}

function handleUpdate(row: any) {
  resetForm()
  Object.assign(materialForm, {
    id: row.id,
    name: row.name,
    category: row.category,
    subcategory: row.subcategory,
    thumbnail: row.thumbnail,
    config_data: row.config_data
  })
  if (row.category === 'echarts' || row.category === 'geojson') {
    configJsonStr.value = JSON.stringify(row.config_data || {}, null, 2)
  } else if (row.category === 'background') {
    bgOptions.color = row.config_data?.color || '#0b132b'
    bgOptions.image = row.config_data?.image || ''
  } else if (row.category === 'image') {
    selectedTags.value = row.config_data?.tags ? row.config_data.tags.split(',') : []
  }
  dialogType.value = 'update'
  dialogVisible.value = true
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

// Format config JSON string
function formatJsonString() {
  try {
    const parsed = JSON.parse(configJsonStr.value)
    configJsonStr.value = JSON.stringify(parsed, null, 2)
    jsonSyntaxError.value = ''
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

async function submitForm(done: any) {
  if (!materialFormRef.value) return done(true)
  const validationRes = await materialFormRef.value.validate()
  if (validationRes) {
    return done(false)
  }

  // Parse option JSON validation
  if (materialForm.category === 'echarts' || materialForm.category === 'geojson') {
    if (!configJsonStr.value.trim()) {
      jsonSyntaxError.value = '配置选项 JSON 不能为空'
      return done(false)
    }
    try {
      const parsed = JSON.parse(configJsonStr.value)
      materialForm.config_data = parsed
      jsonSyntaxError.value = ''
    } catch (e: any) {
      jsonSyntaxError.value = 'JSON 配置语法格式不正确: ' + e.message
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
    if (dialogType.value === 'create') {
      await createOfficialMaterial(materialForm as any)
      Message.success('新建官方内置素材模版成功')
    } else {
      const { id, ...updatePayload } = materialForm
      await updateOfficialMaterial(id!, updatePayload)
      Message.success('编辑官方内置素材模版成功')
    }
    getList()
    done(true)
  } catch (err) {
    console.error(err)
    done(false)
  }
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

// Sandboxed Live Preview Modal handlers
function handlePreview(row: any) {
  previewItem.value = row
  standalonePreviewTheme.value = 'dark'
  previewVisible.value = true
  previewChartError.value = ''
  
  if (row.category === 'echarts') {
    nextTick(() => {
      initPreviewChart()
    })
  }
}

function initPreviewChart() {
  if (!previewChartRef.value) return
  destroyPreviewChart()
  
  try {
    const opt = previewItem.value.config_data || {}
    const theme = standalonePreviewTheme.value === 'dark' ? 'dark' : undefined
    
    previewChartInstance = echarts.init(previewChartRef.value, theme)
    previewChartInstance.setOption(opt)
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
  margin-left: 20px;
}

.preview-theme-title {
  font-size: 13px;
  color: #86909c;
}
</style>
