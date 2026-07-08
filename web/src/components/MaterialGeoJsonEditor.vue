<template>
  <a-form-item label="数据导入方式" required style="margin-bottom: 12px;">
    <a-radio-group v-model="importMode" type="button" size="small">
      <a-radio value="upload">上传 JSON 文件</a-radio>
      <a-radio value="edit">在线粘贴/编辑</a-radio>
    </a-radio-group>
  </a-form-item>

  <!-- Upload Mode -->
  <a-form-item label="GeoJSON 地图文件" required v-if="importMode === 'upload'" style="margin-bottom: 12px;">
    <div style="width: 100%; display: flex; flex-direction: column;">
      <div v-if="!uploadedFileInfo" class="geojson-upload-zone" @click="triggerGeoJsonFileInput" @dragover.prevent @drop.prevent="handleGeoJsonFileDrop">
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
        <span>当前文件: <strong>{{ uploadedFileInfo.name }}</strong> ({{ uploadedFileInfo.size }})</span>
        <a-link status="danger" @click="clearUploadedGeoJson">清除</a-link>
      </div>
      <div v-if="syntaxError" class="json-error-msg" style="margin-top: 6px;">{{ syntaxError }}</div>
    </div>
  </a-form-item>

  <!-- Text/Edit Mode -->
  <a-form-item label="地图 JSON 内容" required v-if="importMode === 'edit'" style="margin-bottom: 12px;">
    <template #extra>
      <div class="json-tips">
        <span>请输入符合标准 JSON 规范的内容 (属性名须用双引号包裹，不可含注释)。</span>
        <a-link type="primary" size="mini" @click="formatGeoJsonString">格式化 JSON</a-link>
      </div>
    </template>
    <div style="width: 100%; display: flex; flex-direction: column;">
      <a-textarea 
        v-model="configJsonStr" 
        placeholder='请输入合法的 GeoJSON 数据，例如: &#10;{&#10;  "type": "FeatureCollection",&#10;  "features": []&#10;}' 
        :auto-size="{ minRows: 8, maxRows: 12 }" 
        class="code-editor" 
        @input="validatePasteJson" 
      />
      <div v-if="syntaxError" class="json-error-msg" style="margin-top: 6px;">{{ syntaxError }}</div>
    </div>
  </a-form-item>

  <!-- File Preview (Upload Mode only, shows read-only text of parsed JSON) -->
  <a-form-item label="地图数据预览" v-if="importMode === 'upload' && configJsonStr && !syntaxError" style="margin-bottom: 12px;">
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

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconUpload } from '@arco-design/web-vue/es/icon'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  importMode: {
    type: String,
    default: 'upload'
  },
  uploadedFileInfo: {
    type: Object as () => { name: string; size: string } | null,
    default: null
  },
  syntaxError: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'update:modelValue',
  'update:importMode',
  'update:uploadedFileInfo',
  'update:syntaxError'
])

const configJsonStr = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const importMode = computed({
  get: () => props.importMode,
  set: (val) => emit('update:importMode', val)
})

const uploadedFileInfo = computed({
  get: () => props.uploadedFileInfo,
  set: (val) => emit('update:uploadedFileInfo', val)
})

const syntaxError = computed({
  get: () => props.syntaxError,
  set: (val) => emit('update:syntaxError', val)
})

const geoJsonFileInputRef = ref<HTMLInputElement | null>(null)

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
      syntaxError.value = ''
      uploadedFileInfo.value = {
        name: file.name,
        size: formatBytes(file.size)
      }
      Message.success('JSON文件解析并验证成功')
    } catch (err: any) {
      syntaxError.value = 'JSON 规范校验失败: ' + err.message
      Message.error('文件不是合法的 JSON 格式')
      configJsonStr.value = ''
      uploadedFileInfo.value = null
    }
  }
  reader.onerror = () => {
    Message.error('文件读取失败')
  }
  reader.readAsText(file)
}

function clearUploadedGeoJson() {
  configJsonStr.value = ''
  syntaxError.value = ''
  uploadedFileInfo.value = null
  if (geoJsonFileInputRef.value) {
    geoJsonFileInputRef.value.value = ''
  }
}

function validatePasteJson() {
  if (!configJsonStr.value.trim()) {
    syntaxError.value = ''
    return
  }
  try {
    JSON.parse(configJsonStr.value)
    syntaxError.value = ''
  } catch (err: any) {
    syntaxError.value = 'JSON 规范校验失败: ' + err.message
  }
}

function formatGeoJsonString() {
  try {
    const parsed = JSON.parse(configJsonStr.value)
    configJsonStr.value = JSON.stringify(parsed, null, 2)
    syntaxError.value = ''
  } catch (e: any) {
    syntaxError.value = '格式化失败 (不是合法的 JSON): ' + e.message
  }
}

const editGeoJsonPreviewText = computed(() => {
  if (!configJsonStr.value) return '{}'
  if (configJsonStr.value.length > 5000) {
    return configJsonStr.value.slice(0, 5000) + '\n\n... (地图数据过长，已截断显示，全部内容可在保存后查看) ...'
  }
  return configJsonStr.value
})
</script>

<style scoped>
.code-editor {
  font-family: 'Fira Code', monospace;
  background-color: #0f172a !important;
  color: #38bdf8 !important;
  font-size: 13px;
  line-height: 1.5;
}

.code-editor.readonly {
  opacity: 0.85;
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
</style>
