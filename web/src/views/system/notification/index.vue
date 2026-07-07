<template>
  <div class="notification-management-container">
    <a-card class="box-card" :bordered="false">
      <template #title>
        <div class="card-header">
          <span class="title">通知公告管理</span>
          <div class="header-actions">
            <a-input v-model="searchForm.title" placeholder="标题" allow-clear class="search-input" />
            <a-select v-model="searchForm.type" placeholder="类型" allow-clear class="search-select">
              <a-option value="system">系统通知</a-option>
              <a-option value="message">内部消息</a-option>
              <a-option value="todo">待办事项</a-option>
            </a-select>
            <!-- No user selection selector needed as all notices default to all users -->
            <a-button type="outline" @click="handleSearch">查询</a-button>
            <a-button type="primary" @click="handleCreate">
              <template #icon>
                <IconPlus />
              </template>
              新建通知
            </a-button>
          </div>
        </div>
      </template>

      <a-scrollbar style="height: calc(100vh - 240px); overflow: auto;">
        <a-table :loading="loading" :data="tableData" row-key="id" :columns="columns" :pagination="pagination"
          @page-change="onPageChange" :bordered="false">
          
          <template #type="{ record }">
            <a-tag :color="getTypeTagColor(record.type)">
              {{ getTypeText(record.type) }}
            </a-tag>
          </template>

          <!-- Removed recipient template as all notices default to all users -->

          <template #create_time="{ record }">
            <span>{{ formatDate(record.create_time) }}</span>
          </template>

          <template #sys_create_time="{ record }">
            <span>{{ formatDate(record.sys_create_time) }}</span>
          </template>

          <template #expire_time="{ record }">
            <span>{{ record.expire_time ? formatDate(record.expire_time) : '永久有效' }}</span>
          </template>

          <template #optional="{ record }">
            <div class="table-actions">
              <a-link type="primary" @click="handleViewDetail(record)">查看详情</a-link>
              <a-link type="primary" @click="handleShowReadUsers(record)">已读列表</a-link>
              <a-link type="primary" @click="handleUpdate(record)">编辑</a-link>
              <a-link status="danger" @click="handleDelete(record)">删除</a-link>
            </div>
          </template>
        </a-table>
      </a-scrollbar>
    </a-card>

    <!-- Create/Edit Modal Dialog -->
    <a-modal v-model:visible="dialogVisible" :title="dialogType === 'create' ? '新建通知' : '编辑通知'" width="500px"
      @before-ok="submitForm" :mask-closable="false" align-center>
      <a-form :model="noticeForm" :rules="formRules" ref="noticeFormRef" layout="vertical">
        <!-- Removed recipient select item as all notices default to all users -->

        <a-form-item field="type" label="通知类型" required>
          <a-radio-group v-model="noticeForm.type">
            <a-radio value="system">系统通知</a-radio>
            <a-radio value="message">内部消息</a-radio>
            <a-radio value="todo">待办事项</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item field="title" label="通知标题" required>
          <a-input v-model="noticeForm.title" placeholder="请输入通知标题" maxLength="100" show-word-limit />
        </a-form-item>

        <a-form-item field="create_time" label="发送时间（可选）">
          <a-date-picker v-model="noticeForm.create_time" show-time format="YYYY-MM-DD HH:mm:ss" placeholder="不设则默认为当前发布时间" style="width: 100%" />
        </a-form-item>

        <a-form-item field="expire_time" label="截止时间（可选）">
          <a-date-picker v-model="noticeForm.expire_time" show-time format="YYYY-MM-DD HH:mm:ss" placeholder="不设则永久有效" style="width: 100%" />
        </a-form-item>

        <a-form-item field="content" label="通知内容" required>
          <RichTextEditor v-model="noticeForm.content" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Detail Modal -->
    <DetailModal v-model:visible="detailVisible" :notification="selectedNotice" />

    <!-- Read Users Modal -->
    <a-modal v-model:visible="readListVisible" title="已读人员列表" width="400px" :footer="false" align-center>
      <div class="read-users-list">
        <a-list :loading="readUsersLoading" :bordered="false" size="small">
          <a-list-item v-for="user in readUsers" :key="user.user_id">
            <div class="user-item-info">
              <span class="user-nickname">{{ user.nickname }}</span>
              <span class="user-username">({{ user.username }})</span>
            </div>
            <template #actions>
              <span class="read-time">{{ formatDate(user.read_time) }}</span>
            </template>
          </a-list-item>
          <template #empty v-if="readUsers.length === 0">
            <div class="empty-read-users">
              <a-empty description="暂无用户阅读" />
            </div>
          </template>
        </a-list>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { TableColumnData } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import { getNotificationList, createNotification, updateNotification, deleteNotification, getNotificationReadUsers } from '../../../api/notification'
import { getUserList } from '../../../api/user'
import { formatDate } from '../../../utils'
import DetailModal from '../../../components/Notification/DetailModal.vue'
import RichTextEditor from '../../../components/Notification/RichTextEditor.vue'

const loading = ref(false)
const tableData = ref<any[]>([])
const userOptions = ref<any[]>([])
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'update'>('create')
const noticeFormRef = ref()

const detailVisible = ref(false)
const selectedNotice = ref<any>(null)

const readListVisible = ref(false)
const readUsersLoading = ref(false)
const readUsers = ref<any[]>([])

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true
})

const searchForm = reactive({
  title: '',
  type: undefined
})

const columns: TableColumnData[] = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '类型', slotName: 'type', width: 110, align: 'center' },
  { title: '标题', dataIndex: 'title', width: 220 },
  { title: '发送时间', slotName: 'create_time', width: 180 },
  { title: '创建时间', slotName: 'sys_create_time', width: 180 },
  { title: '到期时间', slotName: 'expire_time', width: 180 },
  { title: '操作', slotName: 'optional', align: 'center', width: 220 }
]

const noticeForm = reactive({
  id: undefined,
  user_id: -1,
  type: 'system',
  title: '',
  create_time: undefined,
  expire_time: undefined,
  content: ''
})

const formRules = {
  type: [{ required: true, message: '请选择通知类型' }],
  title: [{ required: true, message: '请输入通知标题' }],
  content: [{ required: true, message: '请输入通知内容' }]
}

async function fetchUsers() {
  try {
    const res: any = await getUserList({ limit: 1000 })
    userOptions.value = res || []
  } catch (err) {
    console.error('获取用户列表失败', err)
  }
}


async function getList() {
  loading.value = true
  try {
    const params = {
      title: searchForm.title || undefined,
      type: searchForm.type || undefined
    }
    const res: any = await getNotificationList(params)
    tableData.value = res || []
    pagination.total = res.length || 0
  } catch (err) {
    console.error(err)
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
  Object.assign(noticeForm, {
    id: undefined,
    user_id: -1,
    type: 'system',
    title: '',
    create_time: undefined,
    expire_time: undefined,
    content: ''
  })
}

function handleCreate() {
  resetForm()
  dialogType.value = 'create'
  dialogVisible.value = true
}

function handleUpdate(row: any) {
  resetForm()
  Object.assign(noticeForm, {
    id: row.id,
    user_id: row.user_id,
    type: row.type,
    title: row.title,
    create_time: row.create_time,
    expire_time: row.expire_time,
    content: row.content
  })
  dialogType.value = 'update'
  dialogVisible.value = true
}

async function handleViewDetail(row: any) {
  selectedNotice.value = row
  detailVisible.value = true
}

async function handleShowReadUsers(row: any) {
  readListVisible.value = true
  readUsersLoading.value = true
  try {
    const res: any = await getNotificationReadUsers(row.id)
    readUsers.value = res || []
  } catch (err) {
    console.error(err)
  } finally {
    readUsersLoading.value = false
  }
}

async function submitForm(done: any) {
  if (!noticeFormRef.value) return done(true)
  const validationRes = await noticeFormRef.value.validate()
  if (validationRes) {
    return done(false)
  }

  try {
    if (dialogType.value === 'create') {
      await createNotification(noticeForm as any)
      Message.success('新建系统通知成功')
    } else {
      const { id, ...updatePayload } = noticeForm
      await updateNotification(id!, updatePayload)
      Message.success('编辑系统通知成功')
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
    titleAlign: 'start',
    content: `您确定要删除通知 "${row.title}" 吗？该操作不可撤销。`,
    okText: '确定',
    cancelText: '取消',
    simple: false,
    okButtonProps: {
      status: 'danger'
    },
    async onOk() {
      try {
        await deleteNotification(row.id)
        Message.success('删除通知成功')
        getList()
      } catch (err) {
        console.error(err)
      }
    }
  })
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
      return '公告'
  }
}

function getTypeTagColor(type: string) {
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

onMounted(() => {
  fetchUsers()
  getList()
})
</script>

<style scoped>
.notification-management-container {
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

.search-input {
  width: 160px;
}

.search-select {
  width: 160px;
}

.table-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.read-users-list {
  max-height: 300px;
  overflow-y: auto;
}

.user-item-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-nickname {
  font-weight: 500;
  color: #1d2129;
}

.user-username {
  color: #86909c;
  font-size: 12px;
}

.read-time {
  color: #86909c;
  font-size: 12px;
}

.empty-read-users {
  padding: 20px 0;
  text-align: center;
}

:deep(.arco-tabs-content) {
  padding-top: 0 !important;
}
</style>

