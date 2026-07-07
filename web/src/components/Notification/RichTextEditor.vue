<template>
  <div class="rich-text-editor">
    <QuillEditor
      v-model:content="content"
      content-type="html"
      theme="snow"
      :options="editorOptions"
      @update:content="handleUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const content = ref(props.modelValue || '')

watch(() => props.modelValue, (newVal) => {
  if (newVal !== content.value) {
    content.value = newVal || ''
  }
})

function handleUpdate(val: string) {
  emit('update:modelValue', val)
}

const editorOptions = {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'align': [] }],
      ['clean']
    ]
  },
  placeholder: '请输入通知内容...'
}
</script>

<style>
.rich-text-editor {
  width: 100%;
}
.rich-text-editor .ql-container {
  min-height: 150px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 14px;
}
.rich-text-editor .ql-toolbar.ql-snow {
  border: 1px solid #e5e6eb;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  background-color: #f2f3f5;
  padding: 6px 8px;
}
.rich-text-editor .ql-container.ql-snow {
  border: 1px solid #e5e6eb;
  border-top: none;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}
</style>
