import { computed, ref } from 'vue'
import type { RouteLocationNormalizedLoaded, Router } from 'vue-router'
import { getMenuTree } from '../../api/menu'

export type MenuType = 'M' | 'C' | 'F' | string

export interface LayoutMenuItem {
  id?: string | number
  parent_id?: string | number
  path?: string
  menu_name?: string
  menu_type?: MenuType
  icon?: string
  visible?: string | number
  children?: LayoutMenuItem[]
  [key: string]: any
}

export function resolveMenuPath(path?: string) {
  if (!path) return '/manager'
  let p = path.startsWith('/') ? path : `/${path}`
  if (!p.startsWith('/manager')) {
    p = `/manager${p}`
  }
  return p
}

/**
 * 侧边栏只允许展示目录/菜单：
 * M = 目录，可展开；C = 菜单，可点击；F = 按钮/接口权限，绝不能进入侧边栏。
 */
export function isSidebarMenu(menu: LayoutMenuItem) {
  return menu.menu_type !== 'F'
}

export function normalizeSidebarMenus(menus: LayoutMenuItem[] = []): LayoutMenuItem[] {
  return menus
    .filter(isSidebarMenu)
    .map(menu => {
      const children = normalizeSidebarMenus(menu.children || [])
      return {
        ...menu,
        children
      }
    })
    .filter(menu => {
      // 目录没有可展示子节点时不渲染，避免 M 目录变成可点击的 “/”。
      if (menu.menu_type === 'M') return Boolean(menu.children?.length)
      // C 或未带类型的历史数据保留展示能力。
      return true
    })
}

export function getMenuIcon(menu: LayoutMenuItem) {
  if (!menu.icon || menu.icon === '#') return null

  const iconMap: Record<string, string> = {
    Setting: 'IconSettings',
    Settings: 'IconSettings',
    User: 'IconUser',
    Avatar: 'IconUser',
    List: 'IconMenu',
    Key: 'IconLock',
    Notebook: 'IconBook',
    Folder: 'IconFolder',
    Document: 'IconFile',
    Odometer: 'IconDashboard',
    Monitor: 'IconDesktop',
    Bell: 'IconNotification',
    Search: 'IconSearch',
    Plus: 'IconPlus',
    Location: 'IconLocation',
    Cpu: 'IconCpu',
    Apps: 'IconApps'
  }

  const mapped = iconMap[menu.icon] || menu.icon
  return mapped.startsWith('Icon')
    ? mapped
    : `Icon${mapped.charAt(0).toUpperCase()}${mapped.slice(1)}`
}

function collectOpenKeys(menus: LayoutMenuItem[], activePath: string, parents: string[] = []): string[] {
  for (const menu of menus) {
    const key = String(menu.id ?? resolveMenuPath(menu.path))
    const nextParents = menu.menu_type === 'M' || menu.children?.length ? [...parents, key] : parents

    if (menu.menu_type === 'C' && resolveMenuPath(menu.path) === activePath) {
      return parents
    }

    if (menu.children?.length) {
      const childResult = collectOpenKeys(menu.children, activePath, nextParents)
      if (childResult.length) return childResult
    }
  }

  return []
}

export function useLayoutMenu(router: Router, route: RouteLocationNormalizedLoaded) {
  const menuList = ref<LayoutMenuItem[]>([])
  const baseOpenKeys = ref<string[]>(['system', 'basic', 'business'])

  const activeMenu = computed(() => route.path)

  const currentRouteTitle = computed(() => {
    return (route.meta.title as string) || '首页'
  })

  const defaultOpenKeys = computed(() => {
    const routeOpenKeys = collectOpenKeys(menuList.value, route.path)
    return Array.from(new Set([...baseOpenKeys.value, ...routeOpenKeys]))
  })

  async function fetchMenus() {
    try {
      const res: any = await getMenuTree()
      menuList.value = normalizeSidebarMenus(res || [])
    } catch (err) {
      console.error('Failed to load menus', err)
    }
  }

  function handleMenuClick(key: string) {
    if (!key || key === '/') return
    router.push(key)
  }

  return {
    menuList,
    defaultOpenKeys,
    activeMenu,
    currentRouteTitle,
    fetchMenus,
    handleMenuClick
  }
}
