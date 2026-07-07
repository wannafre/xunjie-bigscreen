<template>
  <div class="menu-container">
    <a-card class="box-card" :bordered="false">
      <!-- Reverted Card Header strictly to the original title and layout -->
      <template #title>
        <div class="card-header">
          <span class="title">菜单管理</span>
          <div class="header-actions">
            <a-input-search v-model="searchQuery" placeholder="输入关键字搜索" allow-clear class="search-input"
              @input="handleSearch" />
            <a-button type="primary" @click="handleCreate" class="add-btn">
              <template #icon>
                <IconPlus />
              </template>
              新增记录
            </a-button>
          </div>
        </div>
      </template>

      <!-- Upgraded Table content inside the layout -->
      <a-table :loading="loading" :data="filteredTableData" row-key="id" :columns="columns"
        v-model:expanded-keys="expandedKeys" :pagination="false" :bordered="false" class="menu-table">
        <!-- Custom expand icon: Clean caret arrow instead of gray square +/- box -->
        <template #expand-icon="{ expanded }">
          <IconDown v-if="expanded" style="font-size: 12px; color: #4E5969;" />
          <IconRight v-else style="font-size: 12px; color: #4E5969;" />
        </template>
        <!-- Custom menu icon render -->
        <template #icon="{ record }">
          <div class="icon-wrap-inner">
            <component :is="getIconComponent(record.icon)" v-if="record.icon && record.icon !== '#'"
              class="menu-icon" />
            <span v-else class="text-secondary">-</span>
          </div>
        </template>

        <!-- Custom combined path info column -->
        <template #path_info="{ record }">
          <div v-if="record.menu_type !== 'F'" class="path-details">
            <div class="path-row font-mono">{{ record.path || '-' }}</div>
            <div class="component-row font-mono" v-if="record.component">{{ record.component }}</div>
          </div>
          <span v-else class="text-secondary font-mono">-</span>
        </template>

        <!-- Styled Permission string -->
        <template #perms="{ record }">
          <span v-if="record.perms" class="permission-badge font-mono">{{ record.perms }}</span>
          <span v-else class="text-secondary font-mono">-</span>
        </template>

        <!-- Styled Menu Type tag -->
        <template #menu_type="{ record }">
          <a-tag :color="getTypeTagColor(record.menu_type)" size="small" class="custom-type-tag">
            {{ getTypeLabel(record.menu_type) }}
          </a-tag>
        </template>

        <!-- Styled Status tag -->
        <template #status="{ record }">
          <a-tag :color="record.status === '0' ? 'green' : 'red'" size="small">
            {{ dictStore.getDictLabel('general_status', record.status) }}
          </a-tag>
        </template>

        <!-- Operational actions with 'Add Child' shortcut -->
        <template #optional="{ record }">
          <div class="table-actions">
            <a-link type="primary" @click="handleUpdate(record)">编辑</a-link>
            <a-link type="primary" status="success" @click="handleCreateChild(record)" v-if="record.menu_type !== 'F'">
              新增下级
            </a-link>
            <a-link status="danger" @click="handleDelete(record)">删除</a-link>
          </div>
        </template>
      </a-table>
    </a-card>

    <!-- Menu Create/Edit Dialog -->
    <a-modal v-model:visible="dialogVisible" :title="dialogType === 'create' ? '新增菜单' : '编辑菜单'" width="600px"
      @before-ok="submitForm" :mask-closable="false" align-center>
      <a-form :model="menuForm" :rules="formRules" ref="menuFormRef" layout="vertical">
        <a-form-item field="parent_id" label="上级菜单">
          <a-tree-select v-model="menuForm.parent_id" :data="treeSelectData"
            :fieldNames="{ key: 'id', title: 'menu_name', children: 'children' }" placeholder="选择上级菜单 (不选默认为顶级目录)"
            allow-clear class="full-width" />
        </a-form-item>

        <a-form-item field="menu_type" label="菜单类型">
          <a-radio-group v-model="menuForm.menu_type" type="button">
            <a-radio value="M">目录</a-radio>
            <a-radio value="C">菜单</a-radio>
            <a-radio value="F">按钮/接口</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item field="menu_name" label="菜单名称" required>
          <a-input v-model="menuForm.menu_name" placeholder="请输入菜单名称" />
        </a-form-item>

        <a-form-item field="order_num" label="显示顺序">
          <a-input-number v-model="menuForm.order_num" :min="0" class="full-width" />
        </a-form-item>

        <a-form-item field="icon" label="菜单图标" v-if="menuForm.menu_type !== 'F'">
          <a-select v-model="menuForm.icon" placeholder="请选择菜单图标" allow-clear allow-search class="full-width">
            <a-option v-for="item in iconOptions" :key="item" :value="item">
              <div style="display: flex; align-items: center; gap: 8px; font-size: 18px;">
                <component :is="getIconComponent(item)" />
                <span style="font-size: 14px;">{{ item }}</span>
              </div>
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item field="path" label="路由地址" v-if="menuForm.menu_type !== 'F'">
          <a-input v-model="menuForm.path" placeholder="请输入路由地址 (如: /system/user)" />
        </a-form-item>

        <a-form-item field="component" label="组件路径" v-if="menuForm.menu_type === 'C'">
          <a-input v-model="menuForm.component" placeholder="请输入组件路径 (如: system/user/index)" />
        </a-form-item>

        <a-form-item field="perms" label="权限标识">
          <a-input v-model="menuForm.perms" placeholder="请输入权限标识 (如: system:user:list)" />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12" v-if="menuForm.menu_type !== 'F'">
            <a-form-item field="visible" label="显示状态">
              <a-radio-group v-model="menuForm.visible">
                <a-radio value="0">显示</a-radio>
                <a-radio value="1">隐藏</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="status" label="菜单状态">
              <a-radio-group v-model="menuForm.status">
                <a-radio value="0">正常</a-radio>
                <a-radio value="1">停用</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item field="remark" label="备注">
          <a-textarea v-model="menuForm.remark" placeholder="请输入备注信息" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { TableColumnData } from '@arco-design/web-vue'
import { IconPlus, IconDown, IconRight } from '@arco-design/web-vue/es/icon'
import * as ArcoIcons from '@arco-design/web-vue/es/icon'
import { getMenuTree, getMenuList, createMenu, updateMenu, deleteMenu } from '../../../api/menu'
import { useDictStore } from '../../../store/dict'
import { deepClone, listToTree } from '../../../utils'

const loading = ref(false)
const tableData = ref<any[]>([])
const treeSelectData = ref<any[]>([])
const dictStore = useDictStore()
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'update'>('create')
const menuFormRef = ref()
const expandedKeys = ref<any[]>([])

const columns: TableColumnData[] = [
  { title: '菜单名称', dataIndex: 'menu_name', width: 220 },
  { title: '图标', dataIndex: 'icon', slotName: 'icon', align: 'center', width: 70 },
  { title: '类型', dataIndex: 'menu_type', slotName: 'menu_type', align: 'center', width: 90 },
  { title: '路由/组件路径', slotName: 'path_info', width: 240 },
  { title: '权限标识', slotName: 'perms', width: 180 },
  { title: '排序', dataIndex: 'order_num', align: 'center', width: 70 },
  { title: '状态', dataIndex: 'status', slotName: 'status', align: 'center', width: 90 },
  { title: '操作', slotName: 'optional', align: 'left', width: 200 }
]

const iconOptions = ref([
  'Setting', 'User', 'Avatar', 'List', 'Key', 'Notebook', 'Folder', 'Document',
  'Odometer', 'Monitor', 'Bell', 'Search', 'Plus', 'Edit', 'Delete', 'Operation',
  'Grid', 'Menu', 'Location', 'Cpu'
])

const menuForm = reactive({
  id: undefined,
  parent_id: 0,
  menu_name: '',
  menu_type: 'M',
  order_num: 0,
  path: '',
  component: '',
  perms: '',
  icon: '#',
  visible: '0',
  status: '0',
  remark: ''
})

const formRules = {
  menu_name: [{ required: true, message: '菜单名称不能为空' }],
  menu_type: [{ required: true, message: '菜单类型不能为空' }]
}

// Resolve dynamic icon components from Arco icons
function getIconComponent(iconName: string) {
  if (!iconName || iconName === '#') return null
  const iconMap: any = {
    'Setting': 'IconSettings',
    'Settings': 'IconSettings',
    'User': 'IconUser',
    'Avatar': 'IconUser',
    'List': 'IconMenu',
    'Key': 'IconLock',
    'Notebook': 'IconBook',
    'Folder': 'IconFolder',
    'Document': 'IconFile',
    'Odometer': 'IconDashboard',
    'Monitor': 'IconDesktop',
    'Bell': 'IconNotification',
    'Search': 'IconSearch',
    'Plus': 'IconPlus',
    'Location': 'IconLocation',
    'Cpu': 'IconCpu',
    'Apps': 'IconApps'
  }
  const mapped = iconMap[iconName] || iconName
  const componentName = mapped.startsWith('Icon') ? mapped : 'Icon' + mapped.charAt(0).toUpperCase() + mapped.slice(1)
  return (ArcoIcons as any)[componentName] || ArcoIcons.IconFile
}

const getTypeLabel = (type: string) => {
  if (type === 'M') return '目录'
  if (type === 'C') return '菜单'
  return '按钮/接口'
}

const getTypeTagColor = (type: string) => {
  if (type === 'M') return 'arcoblue'
  if (type === 'C') return 'green'
  return 'purple'
}

// Flat search logic matching keywords in menu names
const filteredTableData = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()

  const filterNode = (nodes: any[]): any[] => {
    return nodes
      .map(node => {
        const matched = !query ||
          node.menu_name.toLowerCase().includes(query) ||
          (node.perms && node.perms.toLowerCase().includes(query)) ||
          (node.path && node.path.toLowerCase().includes(query))

        let children: any[] = []
        if (node.children && node.children.length > 0) {
          children = filterNode(node.children)
        }

        if (matched || children.length > 0) {
          const result = { ...node }
          if (children.length > 0) {
            result.children = children
          } else {
            delete result.children
          }
          return result
        }
        return null
      })
      .filter((n): n is any => n !== null)
  }

  return filterNode(tableData.value)
})

// Helper function to remove empty children lists recursively
function cleanEmptyChildren(nodes: any[]): any[] {
  return nodes.map(node => {
    const cleaned = { ...node }
    if (cleaned.children) {
      if (cleaned.children.length === 0) {
        delete cleaned.children
      } else {
        cleaned.children = cleanEmptyChildren(cleaned.children)
      }
    }
    return cleaned
  })
}

// Fetch all menus from database
async function getList() {
  loading.value = true
  try {
    const res: any = await getMenuTree()
    const cleaned = cleanEmptyChildren(res || [])
    tableData.value = cleaned

    // Expand all parent nodes by default programmatically
    const keys: any[] = []
    const traverse = (list: any[]) => {
      list.forEach(item => {
        if (item.children && item.children.length > 0) {
          keys.push(item.id)
          traverse(item.children)
        }
      })
    }
    traverse(cleaned)
    expandedKeys.value = keys

    // Construct tree options for parent menu selection (excluding buttons)
    const rawMenus: any = await getMenuList()
    const menuOptions = (rawMenus || []).filter((item: any) => item.menu_type !== 'F')
    treeSelectData.value = [
      { id: 0, menu_name: '主类目', children: listToTree(menuOptions) }
    ]
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // Computed filter handles search reactively
}

function resetForm() {
  Object.assign(menuForm, {
    id: undefined,
    parent_id: 0,
    menu_name: '',
    menu_type: 'M',
    order_num: 0,
    path: '',
    component: '',
    perms: '',
    icon: '#',
    visible: '0',
    status: '0',
    remark: ''
  })
}

function handleCreate() {
  resetForm()
  dialogType.value = 'create'
  dialogVisible.value = true
}

function handleCreateChild(row: any) {
  resetForm()
  menuForm.parent_id = row.id
  menuForm.menu_type = row.menu_type === 'M' ? 'C' : 'F'
  dialogType.value = 'create'
  dialogVisible.value = true
}

function handleUpdate(row: any) {
  resetForm()
  Object.assign(menuForm, deepClone(row))
  menuForm.parent_id = Number(menuForm.parent_id) || 0
  dialogType.value = 'update'
  dialogVisible.value = true
}

async function submitForm(done: any) {
  if (!menuFormRef.value) return done(true)
  const validationRes = await menuFormRef.value.validate()
  if (validationRes) {
    return done(false)
  }

  try {
    const payload = { ...menuForm }
    if (!payload.parent_id) {
      payload.parent_id = 0
    }

    if (dialogType.value === 'create') {
      await createMenu(payload)
      Message.success('新增菜单成功')
    } else {
      await updateMenu(payload.id!, payload)
      Message.success('修改菜单成功')
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
    content: `您确定要删除菜单 "${row.menu_name}" 吗？该操作不可撤销。`,
    okText: '确定',
    cancelText: '取消',
    simple: false,
    okButtonProps: {
      status: 'danger'
    },
    async onOk() {
      try {
        await deleteMenu(row.id)
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
  dictStore.loadDict('general_status')
})
</script>

<style scoped>
.menu-container {
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
  width: 240px;
}

/* Custom table overrides */
.menu-table {
  margin-top: 10px;
}

.icon-wrap-inner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: #F2F3F5;
  border-radius: 4px;
}

.menu-icon {
  font-size: 18px;
  color: #4E5969;
}

.path-details {
  display: flex;
  flex-direction: column;
}

.path-row {
  font-size: 13px;
  color: #1D2129;
  word-break: break-all;
}

.component-row {
  font-size: 11px;
  color: #86909C;
  margin-top: 2px;
  word-break: break-all;
}

.permission-badge {
  font-size: 11px;
  color: #165DFF;
  background-color: #E8F1FF;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #B3D4FF;
  word-break: break-all;
  display: inline-block;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.custom-type-tag {
  font-weight: 500;
  border-radius: 4px;
}

.table-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
  align-items: center;
}

.full-width {
  width: 100%;
}
</style>
