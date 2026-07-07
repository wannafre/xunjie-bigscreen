<template>
  <div class="role-container">
    <a-card class="box-card" :bordered="false">
      <template #title>
        <div class="card-header">
          <span class="title">角色管理</span>
          <div class="header-actions">
            <a-button type="primary" @click="handleCreate">
              <template #icon>
                <IconPlus />
              </template>
              新增角色
            </a-button>
          </div>
        </div>
      </template>

      <a-scrollbar style="height: calc(100vh - 240px); overflow: auto;">
        <a-table :loading="loading" :data="tableData" row-key="id" :columns="columns" :pagination="false"
          :bordered="false">
          <template #status="{ record }">
            <a-tag :color="record.status === '0' ? 'green' : 'red'">
              {{ dictStore.getDictLabel('general_status', record.status) }}
            </a-tag>
          </template>

          <template #optional="{ record }">
            <div class="table-actions">
              <a-link type="primary" @click="handleUpdate(record)">修改</a-link>
              <a-link status="danger" @click="handleDelete(record)">删除</a-link>
            </div>
          </template>
        </a-table>
      </a-scrollbar>
    </a-card>

    <!-- Dialog -->
    <a-modal v-model:visible="dialogVisible" :title="dialogType === 'create' ? '新增角色' : '修改角色'" width="540px"
      @before-ok="submitForm" :mask-closable="false" align-center>
      <a-form :model="roleForm" :rules="formRules" ref="roleFormRef" layout="vertical">
        <a-form-item field="role_name" label="角色名称" required>
          <a-input v-model="roleForm.role_name" placeholder="请输入角色名称" />
        </a-form-item>

        <a-form-item field="role_key" label="角色权限字符" required>
          <a-input v-model="roleForm.role_key" placeholder="请输入权限字符 (如: admin)" :disabled="dialogType === 'update'" />
        </a-form-item>

        <a-form-item field="status" label="角色状态">
          <a-radio-group v-model="roleForm.status">
            <a-radio value="0">正常</a-radio>
            <a-radio value="1">停用</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="菜单权限分配">
          <div class="menu-tree-wrapper">
            <a-tree v-if="menuTreeData.length > 0" checkable check-strictly v-model:checked-keys="roleForm.menu_ids"
              :data="menuTreeData" :field-names="{ key: 'id', title: 'menu_name', children: 'children' }"
              :default-expand-all="true" />
          </div>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { TableColumnData } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import { getRoleList, createRole, updateRole, deleteRole, getRole } from '../../../api/role'
import { getMenuTree } from '../../../api/menu'
import { useDictStore } from '../../../store/dict'

const loading = ref(false)
const tableData = ref<any[]>([])
const menuTreeData = ref<any[]>([])
const dictStore = useDictStore()
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'update'>('create')
const roleFormRef = ref()

const columns: TableColumnData[] = [
  { title: '角色名称', dataIndex: 'role_name', width: 180 },
  { title: '权限字符', dataIndex: 'role_key', width: 180 },
  { title: '状态', slotName: 'status', width: 120, align: 'center' },
  { title: '操作', slotName: 'optional', align: 'left', width: 160 }
]

const roleForm = reactive({
  id: undefined,
  role_name: '',
  role_key: '',
  status: '0',
  menu_ids: [] as number[]
})

const formRules = {
  role_name: [{ required: true, message: '角色名称不能为空' }],
  role_key: [{ required: true, message: '权限字符不能为空' }]
}

function cleanMenuTree(nodes: any[]): any[] {
  return nodes.map(node => {
    const cleaned = { ...node }
    delete cleaned.icon
    if (cleaned.children && cleaned.children.length > 0) {
      cleaned.children = cleanMenuTree(cleaned.children)
    }
    return cleaned
  })
}

async function getMenus() {
  try {
    const res: any = await getMenuTree()
    menuTreeData.value = cleanMenuTree(res || [])
  } catch (err) {
    console.error('获取菜单树失败', err)
  }
}

async function getList() {
  loading.value = true
  try {
    const res: any = await getRoleList()
    tableData.value = res || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(roleForm, {
    id: undefined,
    role_name: '',
    role_key: '',
    status: '0',
    menu_ids: []
  })
}

function handleCreate() {
  resetForm()
  dialogType.value = 'create'
  dialogVisible.value = true
}

async function handleUpdate(row: any) {
  resetForm()
  // Fetch latest role info including menu bindings from server
  try {
    const res: any = await getRole(row.id)
    Object.assign(roleForm, {
      id: res.id,
      role_name: res.role_name,
      role_key: res.role_key,
      status: res.status,
      menu_ids: (res.menus || []).map((m: any) => m.id)
    })
    dialogType.value = 'update'
    dialogVisible.value = true
  } catch (err) {
    console.error(err)
  }
}

async function submitForm(done: any) {
  if (!roleFormRef.value) return done(true)
  const validationRes = await roleFormRef.value.validate()
  if (validationRes) {
    return done(false)
  }

  // Convert menu keys to numbers (handles both array and strictly checked object formats)
  let menuIds: number[] = []
  if (Array.isArray(roleForm.menu_ids)) {
    menuIds = roleForm.menu_ids.map(Number)
  } else if (roleForm.menu_ids && typeof roleForm.menu_ids === 'object') {
    const checkedList = (roleForm.menu_ids as any).checked || []
    menuIds = checkedList.map(Number)
  }

  try {
    if (dialogType.value === 'create') {
      await createRole({
        role_name: roleForm.role_name,
        role_key: roleForm.role_key,
        status: roleForm.status,
        menu_ids: menuIds
      })
      Message.success('新增角色成功')
    } else {
      await updateRole(roleForm.id!, {
        role_name: roleForm.role_name,
        role_key: roleForm.role_key,
        status: roleForm.status,
        menu_ids: menuIds
      })
      Message.success('修改角色成功')
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
    content: `您确定要删除角色 "${row.role_name}" 吗？该操作不可撤销。`,
    okText: '确定',
    cancelText: '取消',
    simple: false,
    okButtonProps: {
      status: 'danger'
    },
    async onOk() {
      try {
        await deleteRole(row.id)
        Message.success('删除成功')
        getList()
      } catch (err) {
        console.error(err)
      }
    }
  })
}

onMounted(() => {
  getList()
  getMenus()
  dictStore.loadDict('general_status')
})
</script>

<style scoped>
.role-container {
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

.menu-tree-wrapper {
  border: 1px solid #E5E6EB;
  border-radius: 4px;
  padding: 8px 12px;
  max-height: 250px;
  overflow-y: auto;
  width: 100%;
}

.table-actions {
  display: flex;
  gap: 8px;
}
</style>
