<template>
  <div class="dict-container">
    <a-card title="字典管理" class="box-card" :bordered="false">
      <a-row :gutter="16">
        <!-- Left panel: Dictionary Type -->
        <a-col :span="8">
          <div class="dict-left-panel">
            <div class="dict-panel-header">
              <span class="dict-panel-title">字典类型</span>
              <a-button size="small" type="text" @click="handleCreateType">
                <template #icon><IconPlus /></template>
                新增类型
              </a-button>
            </div>
            <div class="dict-list">
              <div 
                v-for="dict in dictTypes" 
                :key="dict.dict_type" 
                :class="['dict-list-item', selectedDictType === dict.dict_type ? 'active' : '']" 
                @click="selectDictType(dict.dict_type)"
              >
                <div class="dict-item-text">
                  <span class="dict-name">{{ dict.dict_name }}</span>
                  <span class="dict-code">{{ dict.dict_type }}</span>
                </div>
                <div class="dict-item-actions">
                  <a-button size="mini" type="text" @click.stop="handleUpdateType(dict)">
                    <template #icon><IconEdit /></template>
                  </a-button>
                  <a-button size="mini" type="text" status="danger" @click.stop="handleDeleteType(dict)">
                    <template #icon><IconDelete /></template>
                  </a-button>
                </div>
              </div>
            </div>
          </div>
        </a-col>

        <!-- Right panel: Dictionary Data -->
        <a-col :span="16">
          <div class="dict-right-panel">
            <div class="dict-panel-header">
              <span class="dict-panel-title">字典项列表 <span v-if="selectedDictType" class="selected-badge">({{ selectedDictType }})</span></span>
              <a-button size="small" type="primary" :disabled="!selectedDictType" @click="handleCreateData">
                <template #icon><IconPlus /></template>
                新增字典项
              </a-button>
            </div>
            
            <a-table :loading="dataLoading" :data="dictDataList" :columns="dataColumns" :pagination="false" :bordered="false">
              <template #status="{ record }">
                <a-tag :color="record.status === '0' ? 'green' : 'red'">
                  {{ record.status === '0' ? '正常' : '停用' }}
                </a-tag>
              </template>
              
              <template #optional="{ record }">
                <div class="table-actions">
                  <a-link type="primary" @click="handleUpdateData(record)">修改</a-link>
                  <a-link status="danger" @click="handleDeleteData(record)">删除</a-link>
                </div>
              </template>
            </a-table>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- Dict Type Dialog -->
    <a-modal v-model:visible="typeDialogVisible" :title="typeDialogType === 'create' ? '新增字典类型' : '修改字典类型'" width="480px" @before-ok="submitTypeForm" :mask-closable="false" align-center>
      <a-form :model="typeForm" :rules="typeRules" ref="typeFormRef" layout="vertical">
        <a-form-item field="dict_name" label="字典分类名称" required>
          <a-input v-model="typeForm.dict_name" placeholder="请输入分类名称 (如: 用户状态)" />
        </a-form-item>
        
        <a-form-item field="dict_type" label="字典类型标识" required>
          <a-input v-model="typeForm.dict_type" placeholder="请输入唯一标识 (如: sys_user_status)" :disabled="typeDialogType === 'update'" />
        </a-form-item>

        <a-form-item field="status" label="状态">
          <a-radio-group v-model="typeForm.status">
            <a-radio value="0">正常</a-radio>
            <a-radio value="1">停用</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item field="remark" label="备注">
          <a-textarea v-model="typeForm.remark" placeholder="请输入备注说明" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Dict Data Dialog -->
    <a-modal v-model:visible="dataDialogVisible" :title="dataDialogType === 'create' ? '新增字典数据' : '修改字典数据'" width="480px" @before-ok="submitDataForm" :mask-closable="false" align-center>
      <a-form :model="dataForm" :rules="dataRules" ref="dataFormRef" layout="vertical">
        <a-form-item field="dict_label" label="字典标签" required>
          <a-input v-model="dataForm.dict_label" placeholder="请输入字典显示标签 (如: 男)" />
        </a-form-item>

        <a-form-item field="dict_value" label="字典键值" required>
          <a-input v-model="dataForm.dict_value" placeholder="请输入字典键值 (如: 0)" />
        </a-form-item>

        <a-form-item field="dict_sort" label="排序">
          <a-input-number v-model="dataForm.dict_sort" :min="0" class="full-width" />
        </a-form-item>

        <a-form-item field="status" label="状态">
          <a-radio-group v-model="dataForm.status">
            <a-radio value="0">正常</a-radio>
            <a-radio value="1">停用</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item field="remark" label="备注">
          <a-textarea v-model="dataForm.remark" placeholder="请输入备注说明" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { TableColumnData } from '@arco-design/web-vue'
import { IconPlus, IconEdit, IconDelete } from '@arco-design/web-vue/es/icon'
import {
  getDictTypeList, createDictType, updateDictType, deleteDictType,
  getDictDataList, createDictData, updateDictData, deleteDictData
} from '../../../api/dict'
import { deepClone } from '../../../utils'

const dictTypes = ref<any[]>([])
const selectedDictType = ref<string>('')
const dictDataList = ref<any[]>([])
const dataLoading = ref(false)

const typeDialogVisible = ref(false)
const typeDialogType = ref<'create' | 'update'>('create')
const typeFormRef = ref()

const dataDialogVisible = ref(false)
const dataDialogType = ref<'create' | 'update'>('create')
const dataFormRef = ref()

const dataColumns: TableColumnData[] = [
  { title: '字典标签', dataIndex: 'dict_label' },
  { title: '字典键值', dataIndex: 'dict_value' },
  { title: '排序', dataIndex: 'dict_sort', align: 'center', width: 80 },
  { title: '状态', slotName: 'status', align: 'center', width: 100 },
  { title: '备注说明', dataIndex: 'remark' },
  { title: '操作', slotName: 'optional', align: 'left', width: 140 }
]

const typeForm = reactive({
  dict_id: undefined,
  dict_name: '',
  dict_type: '',
  status: '0',
  remark: ''
})

const dataForm = reactive({
  dict_code: undefined,
  dict_label: '',
  dict_value: '',
  dict_sort: 0,
  dict_type: '',
  status: '0',
  remark: ''
})

const typeRules = {
  dict_name: [{ required: true, message: '名称不能为空' }],
  dict_type: [{ required: true, message: '类型标识不能为空' }]
}

const dataRules = {
  dict_label: [{ required: true, message: '标签不能为空' }],
  dict_value: [{ required: true, message: '键值不能为空' }]
}

async function loadDictTypes() {
  try {
    const res: any = await getDictTypeList()
    dictTypes.value = res || []
    if (res && res.length > 0 && !selectedDictType.value) {
      selectDictType(res[0].dict_type)
    }
  } catch (err) {
    console.error('加载字典类型失败', err)
  }
}

async function selectDictType(type: string) {
  selectedDictType.value = type
  loadDictData()
}

async function loadDictData() {
  if (!selectedDictType.value) return
  dataLoading.value = true
  try {
    const res: any = await getDictDataList(selectedDictType.value)
    dictDataList.value = res || []
  } catch (err) {
    console.error('加载字典数据失败', err)
  } finally {
    dataLoading.value = false
  }
}

// Dict Type Forms
function resetTypeForm() {
  Object.assign(typeForm, {
    dict_id: undefined,
    dict_name: '',
    dict_type: '',
    status: '0',
    remark: ''
  })
}

function handleCreateType() {
  resetTypeForm()
  typeDialogType.value = 'create'
  typeDialogVisible.value = true
}

function handleUpdateType(row: any) {
  resetTypeForm()
  Object.assign(typeForm, deepClone(row))
  typeDialogType.value = 'update'
  typeDialogVisible.value = true
}

async function submitTypeForm(done: any) {
  if (!typeFormRef.value) return done(true)
  const validation = await typeFormRef.value.validate()
  if (validation) return done(false)

  try {
    if (typeDialogType.value === 'create') {
      await createDictType(typeForm)
      Message.success('新增字典类型成功')
    } else {
      await updateDictType(typeForm.dict_id!, typeForm)
      Message.success('修改字典类型成功')
    }
    loadDictTypes()
    done(true)
  } catch (err) {
    console.error(err)
    done(false)
  }
}

async function handleDeleteType(row: any) {
  Modal.confirm({
    title: '确认删除',
    titleAlign: 'start',
    content: `确定要删除字典类型 "${row.dict_name}" (${row.dict_type}) 吗？此操作会同时影响相关显示。`,
    okText: '确定',
    cancelText: '取消',
    simple: false,
    okButtonProps: { status: 'danger' },
    async onOk() {
      try {
        await deleteDictType(row.dict_id)
        Message.success('删除成功')
        if (selectedDictType.value === row.dict_type) {
          selectedDictType.value = ''
          dictDataList.value = []
        }
        loadDictTypes()
      } catch (err) {
        console.error(err)
      }
    }
  })
}

// Dict Data Forms
function resetDataForm() {
  Object.assign(dataForm, {
    dict_code: undefined,
    dict_label: '',
    dict_value: '',
    dict_sort: 0,
    dict_type: selectedDictType.value,
    status: '0',
    remark: ''
  })
}

function handleCreateData() {
  resetDataForm()
  dataDialogType.value = 'create'
  dataDialogVisible.value = true
}

function handleUpdateData(row: any) {
  resetDataForm()
  Object.assign(dataForm, deepClone(row))
  dataDialogType.value = 'update'
  dataDialogVisible.value = true
}

async function submitDataForm(done: any) {
  if (!dataFormRef.value) return done(true)
  const validation = await dataFormRef.value.validate()
  if (validation) return done(false)

  try {
    if (dataDialogType.value === 'create') {
      await createDictData(dataForm)
      Message.success('新增字典数据项成功')
    } else {
      await updateDictData(dataForm.dict_code!, dataForm)
      Message.success('修改字典数据项成功')
    }
    loadDictData()
    done(true)
  } catch (err) {
    console.error(err)
    done(false)
  }
}

async function handleDeleteData(row: any) {
  Modal.confirm({
    title: '确认删除',
    titleAlign: 'start',
    content: `确定要删除字典数据项 "${row.dict_label}" 吗？`,
    okText: '确定',
    cancelText: '取消',
    simple: false,
    okButtonProps: { status: 'danger' },
    async onOk() {
      try {
        await deleteDictData(row.dict_code)
        Message.success('删除成功')
        loadDictData()
      } catch (err) {
        console.error(err)
      }
    }
  })
}

onMounted(() => {
  loadDictTypes()
})
</script>

<style scoped>
.dict-container {
  height: 100%;
}
.box-card {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #E5E6EB;
  background: #FFFFFF;
}
.dict-left-panel {
  border: 1px solid #E5E6EB;
  border-radius: 4px;
  padding: 16px;
  background: #FFFFFF;
  min-height: 500px;
}
.dict-right-panel {
  border: 1px solid #E5E6EB;
  border-radius: 4px;
  padding: 16px;
  background: #FFFFFF;
  min-height: 500px;
}
.dict-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  border-bottom: 1px solid #F2F3F5;
  padding-bottom: 8px;
}
.dict-panel-title {
  font-weight: 600;
  color: #1D2129;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.selected-badge {
  color: #165DFF;
  font-size: 12px;
}
.dict-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 440px;
  overflow-y: auto;
}
.dict-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.dict-list-item:hover {
  background: #F2F3F5;
}
.dict-list-item.active {
  background: #E8F1FF;
  border-color: #B3D4FF;
}
.dict-list-item.active .dict-name {
  color: #165DFF;
}
.dict-item-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.dict-name {
  font-size: 14px;
  font-weight: 500;
  color: #1D2129;
}
.dict-code {
  font-size: 11px;
  color: #86909C;
  font-family: monospace;
}
.dict-item-actions {
  display: none;
  gap: 4px;
}
.dict-list-item:hover .dict-item-actions {
  display: flex;
}
.table-actions {
  display: flex;
  gap: 8px;
}
.full-width {
  width: 100%;
}
</style>
