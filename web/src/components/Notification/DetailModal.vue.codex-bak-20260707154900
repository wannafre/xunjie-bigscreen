<template>
  <a-modal
    v-model:visible="visible"
    :title="notification?.title || '通知详情'"
    @ok="handleClose"
    @cancel="handleClose"
    width="500px"
    align-center
    :footer="null"
    :lock-scroll="false"
  >
    <div v-if="notification" class="notice-detail-container">
      <div class="notice-meta">
        <a-tag :color="getTypeColor(notification.type)" class="notice-tag">
          {{ getTypeText(notification.type) }}
        </a-tag>
        <span class="notice-time">
          {{ formatDate(notification.create_time) }}
        </span>
      </div>
      
      <div class="notice-body">
        <div class="notice-content" v-html="notification.content"></div>
      </div>

      <div class="notice-footer">
        <a-button type="primary" size="medium" @click="handleClose">我知道了</a-button>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatDate } from '../../utils'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  notification: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'close'])

const visible = computed({
  get() {
    return props.visible
  },
  set(val) {
    emit('update:visible', val)
  }
})

function handleClose() {
  visible.value = false
  emit('close')
}

function getTypeText(type: string) {
  switch (type) {
    case 'system':
      return '系统通知'
    case 'message':
      return '内部消息'
    case 'todo':
      return '待办事项'
    default:
      return '普通通知'
  }
}

function getTypeColor(type: string) {
  switch (type) {
    case 'system':
      return 'red'
    case 'message':
      return 'arcoblue'
    case 'todo':
      return 'orangered'
    default:
      return 'gray'
  }
}
</script>

<style scoped>
.notice-detail-container {
  padding: 10px 0;
}

.notice-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.notice-tag {
  font-weight: 500;
}

.notice-time {
  font-size: 13px;
  color: #86909c;
}

.notice-body {
  background: #f7f8fa;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
  min-height: 120px;
  margin-bottom: 24px;
}

.notice-content {
  margin: 0;
  font-size: 14px;
  color: #1d2129;
  line-height: 1.8;
  white-space: pre-wrap;
}

.notice-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
