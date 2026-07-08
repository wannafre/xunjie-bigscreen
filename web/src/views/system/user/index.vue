<template>
  <div class="user-container">
    <a-card class="box-card" :bordered="false">
      <template #title>
        <div class="card-header">
          <span class="title">用户管理</span>
          <div class="header-actions">
            <a-input v-model="searchForm.username" placeholder="用户名" allow-clear class="search-input" />
            <a-input v-model="searchForm.nickname" placeholder="昵称" allow-clear class="search-input" />
            <a-select v-model="searchForm.status" placeholder="状态" allow-clear class="search-select">
              <a-option value="0">正常</a-option>
              <a-option value="1">停用</a-option>
            </a-select>
            <a-button type="outline" @click="handleSearch">查询</a-button>
            <a-button type="primary" @click="handleCreate">
              <template #icon>
                <IconPlus />
              </template>
              新增用户
            </a-button>
          </div>
        </div>
      </template>

      <a-scrollbar style="height: calc(100vh - 240px); overflow: auto;">
        <a-table :loading="loading" :data="tableData" row-key="id" :columns="columns" :pagination="pagination"
          @page-change="onPageChange" :bordered="false">
          <template #sex="{ record }">
            <a-tag :color="dictStore.getDictTagColor('sys_user_sex', record.sex)">
              {{ dictStore.getDictLabel('sys_user_sex', record.sex) }}
            </a-tag>
          </template>

          <template #status="{ record }">
            <a-tag :color="record.status === '0' ? 'green' : 'red'">
              {{ dictStore.getDictLabel('general_status', record.status) }}
            </a-tag>
          </template>

          <template #roles="{ record }">
            <span v-if="record.roles && record.roles.length > 0">
              <a-tag v-for="role in record.roles" :key="role" color="blue" style="margin-right: 4px;">{{ role }}</a-tag>
            </span>
            <span v-else class="text-secondary">-</span>
          </template>

          <template #login_date="{ record }">
            <span>{{ record.login_date ? formatDate(record.login_date) : '-' }}</span>
          </template>

          <template #create_time="{ record }">
            <span>{{ formatDate(record.create_time) }}</span>
          </template>

          <template #optional="{ record }">
            <div class="table-actions">
              <a-link type="primary" @click="handleUpdate(record)">修改</a-link>
              <a-link
                v-if="record.username !== 'admin' && record.username !== userStore.username"
                status="warning"
                @click="handleResetPwd(record)"
              >
                重置密码
              </a-link>
              <a-link status="danger" @click="handleDelete(record)">删除</a-link>
            </div>
          </template>
        </a-table>
      </a-scrollbar>
    </a-card>

    <!-- Dialog -->
    <a-modal v-model:visible="dialogVisible" :title="dialogType === 'create' ? '新增用户' : '修改用户'" width="540px"
      @before-ok="submitForm" :mask-closable="false" align-center>
      <a-form :model="userForm" :rules="formRules" ref="userFormRef" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item field="username" label="用户名" required>
              <a-input v-model="userForm.username" placeholder="请输入用户名" :disabled="dialogType === 'update'" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="nickname" label="用户昵称" required>
              <a-input v-model="userForm.nickname" placeholder="请输入用户昵称" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16" v-if="dialogType === 'create'">
          <a-col :span="24">
            <a-form-item field="password" label="密码" required>
              <a-input-password v-model="userForm.password" placeholder="请输入密码 (至少6位)" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item field="email" label="邮箱">
              <a-input v-model="userForm.email" placeholder="请输入邮箱" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="phonenumber" label="手机号码">
              <a-input v-model="userForm.phonenumber" placeholder="请输入手机号码" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item field="sex" label="性别">
              <a-radio-group v-model="userForm.sex">
                <a-radio value="0">男</a-radio>
                <a-radio value="1">女</a-radio>
                <a-radio value="2">未知</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="status" label="帐号状态">
              <a-radio-group v-model="userForm.status">
                <a-radio value="0">正常</a-radio>
                <a-radio value="1">停用</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item field="roles" label="分配角色">
          <a-select 
            v-model="userForm.roles" 
            placeholder="请选择角色" 
            multiple 
            allow-clear 
            allow-search
            :filter-option="false"
            @search="handleRoleSearch"
            @popup-scroll="handleRolePopupScroll"
            class="full-width"
          >
            <a-option v-for="item in roleOptions" :key="item.role_key" :value="item.role_key">{{ item.role_name }}</a-option>
            <template #footer v-if="hasMoreRoles">
              <div style="padding: 6px; text-align: center; color: #86909c; font-size: 11px;">
                滚动加载更多...
              </div>
            </template>
          </a-select>
        </a-form-item>

        <a-form-item field="remark" label="备注">
          <a-textarea v-model="userForm.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { TableColumnData } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import { getUserList, createUser, updateUser, deleteUser, resetUserPassword } from '../../../api/user'
import { getRoleList } from '../../../api/role'
import { useUserStore } from '../../../store/user'
import { useDictStore } from '../../../store/dict'
import { deepClone, formatDate } from '../../../utils'

const loading = ref(false)
const tableData = ref<any[]>([])
const roleOptions = ref<any[]>([])
const roleSearchKeyword = ref('')
const rolePage = ref(1)
const hasMoreRoles = ref(false)
const dictStore = useDictStore()
const userStore = useUserStore()
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'update'>('create')
const userFormRef = ref()

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true
})

const searchForm = reactive({
  username: '',
  nickname: '',
  status: undefined
})

const columns: TableColumnData[] = [
  { title: '用户名', dataIndex: 'username', width: 120 },
  { title: '昵称', dataIndex: 'nickname', width: 120 },
  { title: '性别', slotName: 'sex', width: 80, align: 'center' },
  { title: '手机号', dataIndex: 'phonenumber', width: 140 },
  { title: '邮箱', dataIndex: 'email', width: 180 },
  { title: '状态', slotName: 'status', width: 100, align: 'center' },
  { title: '角色', slotName: 'roles', width: 180 },
  { title: '最后登录时间', slotName: 'login_date', width: 180 },
  { title: '创建时间', slotName: 'create_time', width: 180 },
  { title: '操作', slotName: 'optional', align: 'left', width: 220 }
]

const userForm = reactive({
  id: undefined,
  username: '',
  nickname: '',
  password: '',
  email: '',
  phonenumber: '',
  sex: '0',
  status: '0',
  roles: [] as string[],
  remark: ''
})

const formRules = {
  username: [{ required: true, message: '用户名不能为空' }],
  nickname: [{ required: true, message: '用户昵称不能为空' }],
  password: [{ required: true, message: '密码不能为空', trigger: 'blur' }, { min: 6, message: '密码不能少于6位' }]
}

async function getRoles(append = false) {
  try {
    const res: any = await getRoleList({
      page: rolePage.value,
      page_size: 10,
      role_name: roleSearchKeyword.value || undefined
    })
    const items = res.items || []
    const merged = append ? [...roleOptions.value] : []
    
    for (const item of items) {
      if (!merged.some(r => r.role_key === item.role_key)) {
        merged.push(item)
      }
    }
    
    roleOptions.value = merged
    hasMoreRoles.value = roleOptions.value.length < (res.total || 0)
  } catch (err) {
    console.error('获取角色列表失败', err)
  }
}

async function handleRoleSearch(searchText: string) {
  roleSearchKeyword.value = searchText
  rolePage.value = 1
  await getRoles(false)
}

async function handleRolePopupScroll(e: any) {
  const target = e.target
  if (target.scrollTop + target.clientHeight >= target.scrollHeight - 5) {
    if (hasMoreRoles.value && !loading.value) {
      rolePage.value += 1
      await getRoles(true)
    }
  }
}

async function getList() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      username: searchForm.username || undefined,
      nickname: searchForm.nickname || undefined,
      status: searchForm.status || undefined
    }
    const res: any = await getUserList(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
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
  getList()
}

function resetForm() {
  Object.assign(userForm, {
    id: undefined,
    username: '',
    nickname: '',
    password: '',
    email: '',
    phonenumber: '',
    sex: '0',
    status: '0',
    roles: [],
    remark: ''
  })
}

function syncSelectedRolesToOptions() {
  if (userForm.roles && userForm.roles.length > 0) {
    for (const roleKey of userForm.roles) {
      if (!roleOptions.value.some(r => r.role_key === roleKey)) {
        roleOptions.value.push({
          id: -roleOptions.value.length - 1,
          role_name: roleKey,
          role_key: roleKey,
          status: '0'
        })
      }
    }
  }
}

async function handleCreate() {
  resetForm()
  dialogType.value = 'create'
  roleSearchKeyword.value = ''
  rolePage.value = 1
  await getRoles(false)
  dialogVisible.value = true
}

async function handleUpdate(row: any) {
  resetForm()
  Object.assign(userForm, deepClone(row))
  dialogType.value = 'update'
  roleSearchKeyword.value = ''
  rolePage.value = 1
  await getRoles(false)
  syncSelectedRolesToOptions()
  dialogVisible.value = true
}

async function submitForm(done: any) {
  if (!userFormRef.value) return done(true)
  const validationRes = await userFormRef.value.validate()
  if (validationRes) {
    return done(false)
  }

  try {
    if (dialogType.value === 'create') {
      await createUser(userForm)
      Message.success('新增用户成功')
    } else {
      const { password, ...updatePayload } = userForm
      await updateUser(userForm.id!, updatePayload)
      Message.success('修改用户成功')
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
    content: `您确定要删除用户 "${row.username}" 吗？该操作不可撤销。`,
    okText: '确定',
    cancelText: '取消',
    simple: false,
    okButtonProps: {
      status: 'danger'
    },
    async onOk() {
      try {
        await deleteUser(row.id)
        Message.success('删除成功')
        getList()
      } catch (err) {
        console.error(err)
      }
    }
  })
}

async function handleResetPwd(row: any) {
  Modal.confirm({
    title: '确认重置密码',
    titleAlign: 'start',
    content: `您确定要重置用户 "${row.username}" 的密码吗？该操作不可撤销。`,
    okText: '确定',
    cancelText: '取消',
    simple: false,
    okButtonProps: {
      status: 'warning'
    },
    async onOk() {
      try {
        const res: any = await resetUserPassword(row.id)
        if (res && res.new_password) {
          Modal.info({
            title: '重置密码成功',
            titleAlign: 'start',
            simple: false,
            content: () => h('div', { style: 'text-align: center; padding: 10px 0;' }, [
              h('p', { style: 'color: #86909C; margin-bottom: 8px;' }, '该用户的新密码已随机生成，请通知用户登录后及时修改：'),
              h('div', { 
                style: 'font-size: 20px; font-weight: bold; color: #165DFF; background-color: #F2F3F5; padding: 12px; border-radius: 4px; display: inline-block; letter-spacing: 1px; margin: 8px 0; border: 1px dashed #B3D4FF;' 
              }, res.new_password)
            ]),
            okText: '好的，我已记住'
          })
        }
      } catch (err) {
        console.error(err)
      }
    }
  })
}

onMounted(() => {
  getList()
  getRoles()
  dictStore.loadDict('sys_user_sex')
  dictStore.loadDict('general_status')
})
</script>

<style scoped>
.user-container {
  height: 100%;
}

.box-card {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
  width: 120px;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.full-width {
  width: 100%;
}
</style>
