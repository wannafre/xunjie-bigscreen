<template>
  <a-sub-menu v-if="hasChildren" :key="menuKey" class="app-menu-sub">
    <template v-if="menuIcon" #icon>
      <component :is="menuIcon" />
    </template>
    <template #title>{{ menu.menu_name }}</template>

    <AppMenuNode
      v-for="child in visibleChildren"
      :key="child.id ?? child.path"
      :menu="child"
    />
  </a-sub-menu>

  <a-menu-item v-else-if="isClickableMenu" :key="menuPath" class="app-menu-item">
    <template v-if="menuIcon" #icon>
      <component :is="menuIcon" />
    </template>
    {{ menu.menu_name }}
  </a-menu-item>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  getMenuIcon,
  isSidebarMenu,
  resolveMenuPath,
  type LayoutMenuItem
} from '../composables/useLayoutMenu'

defineOptions({
  name: 'AppMenuNode'
})

const props = defineProps<{
  menu: LayoutMenuItem
}>()

const visibleChildren = computed(() => {
  return (props.menu.children || []).filter(isSidebarMenu)
})

const hasChildren = computed(() => visibleChildren.value.length > 0)
const isClickableMenu = computed(() => props.menu.menu_type !== 'M' && props.menu.menu_type !== 'F')
const menuIcon = computed(() => getMenuIcon(props.menu))
const menuPath = computed(() => resolveMenuPath(props.menu.path))
const menuKey = computed(() => String(props.menu.id ?? menuPath.value))
</script>
