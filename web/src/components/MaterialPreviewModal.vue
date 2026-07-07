<template>
  <a-modal
    v-model:visible="visible"
    :title="material?.name || '素材预览'"
    :footer="false"
    width="600px"
    @close="handleClose"
    @open="handleOpen"
    body-class="preview-modal-body"
  >
    <div class="preview-container">
      <!-- Background / Image / Custom Media Preview -->
      <div 
        v-if="material?.category === 'background' || material?.category === 'image'" 
        class="background-preview"
        :style="backgroundStyle"
      >
        <div v-if="!material?.config_data?.image && !material?.thumbnail" class="color-indicator">
          <span>背景颜色: {{ material?.config_data?.color || '#000000' }}</span>
        </div>
      </div>

      <!-- ECharts Component Sandboxed Preview -->
      <div 
        v-else-if="material?.category === 'echarts'" 
        class="chart-preview-container-wrapper"
      >
        <div class="preview-theme-bar">
          <span class="preview-theme-title">效果背景底色测试:</span>
          <a-radio-group v-model="previewTheme" size="mini" type="button" @change="handleThemeChange">
            <a-radio value="dark">深色背景</a-radio>
            <a-radio value="light">浅色背景</a-radio>
          </a-radio-group>
        </div>
        <div 
          class="chart-preview-container"
          :style="{ backgroundColor: previewTheme === 'dark' ? '#0f172a' : '#ffffff', border: previewTheme === 'dark' ? '1px solid #1e293b' : '1px solid #e5e6eb' }"
        >
          <div ref="chartRef" class="chart-sandbox"></div>
          <div v-if="chartError" class="chart-error-overlay">
            <icon-exclamation-circle-fill />
            <span>无法加载图表配置: {{ chartError }}</span>
          </div>
        </div>
      </div>

      <!-- Raw Configuration JSON Preview (e.g. Map GeoJSON, configs) -->
      <div v-else class="raw-preview">
        <div class="category-tag">分类: {{ material?.category }}</div>
        <pre class="json-content"><code>{{ JSON.stringify(material?.config_data || {}, null, 2) }}</code></pre>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { IconExclamationCircleFill } from '@arco-design/web-vue/es/icon'
import { resolveImageUrl } from '../utils'

// Dynamic import for ECharts to prevent crash if not yet installed
let echartsModule: any = null
import('echarts').then(mod => {
  echartsModule = mod
}).catch(err => {
  console.warn('ECharts is not installed or loaded:', err)
})

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  material: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible'])

const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: any = null
const chartError = ref('')
const previewTheme = ref<'dark' | 'light'>('dark')

function handleThemeChange() {
  initChartSandbox()
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

const backgroundStyle = computed(() => {
  if (!props.material) return {}
  const config = props.material.config_data || {}
  const bgImage = config.image || props.material.thumbnail
  const resolvedUrl = resolveImageUrl(bgImage)
  
  return {
    backgroundColor: formatHexColor(config.color),
    backgroundImage: resolvedUrl ? `url(${resolvedUrl})` : 'none',
    backgroundRepeat: 'no-repeat',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    width: '100%',
    height: '350px',
    borderRadius: '8px',
    border: '1px solid #334155'
  }
})

function handleClose() {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  chartError.value = ''
}

function handleOpen() {
  chartError.value = ''
  previewTheme.value = 'dark'
  if (props.material?.category === 'echarts') {
    nextTick(() => {
      initChartSandbox()
    })
  }
}

function initChartSandbox() {
  if (!chartRef.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }

  if (!echartsModule) {
    chartError.value = 'ECharts 库未就绪，请稍后...'
    return
  }

  try {
    const option = props.material?.config_data || {}
    const theme = previewTheme.value === 'dark' ? 'dark' : undefined
    
    chartInstance = echartsModule.init(chartRef.value, theme, {
      backgroundColor: 'transparent'
    })
    
    chartInstance.setOption(option)
    
    // Auto resize
    window.addEventListener('resize', handleResize)
  } catch (err: any) {
    console.error('Failed to init ECharts preview sandbox:', err)
    chartError.value = err.message || '配置解析异常'
  }
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(() => props.material, () => {
  if (props.visible && props.material?.category === 'echarts') {
    nextTick(() => {
      initChartSandbox()
    })
  }
}, { deep: true })

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.preview-container {
  padding: 10px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.background-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  position: relative;
  overflow: hidden;
}

.color-indicator {
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(8px);
  padding: 8px 16px;
  border-radius: 20px;
  color: #38bdf8;
  font-family: monospace;
  font-weight: bold;
  border: 1px solid rgba(255,255,255,0.1);
}

.chart-preview-container {
  width: 100%;
  height: 350px;
  background: #0f172a;
  border-radius: 8px;
  border: 1px solid #1e293b;
  position: relative;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
  overflow: hidden;
}

.chart-sandbox {
  width: 100%;
  height: 100%;
}

.chart-error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  gap: 12px;
  font-size: 14px;
}

.raw-preview {
  width: 100%;
  background: #1e293b;
  border-radius: 8px;
  padding: 16px;
  max-height: 350px;
  overflow-y: auto;
  border: 1px solid #334155;
  color: #e2e8f0;
}

.category-tag {
  background: #3b82f6;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
  font-size: 12px;
  margin-bottom: 12px;
  font-weight: 500;
}

.json-content {
  margin: 0;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #38bdf8;
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

.chart-preview-container-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>
