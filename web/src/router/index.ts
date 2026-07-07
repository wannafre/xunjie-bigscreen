import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../store/user'
import { settings } from '../config/settings'
import { getMenuList } from '../api/menu'

// Glob view files for dynamic imports
const modules = import.meta.glob('../views/**/*.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'Odometer' }
      },
      {
        path: 'system/account',
        name: 'Account',
        component: () => import('../views/system/account/index.vue'),
        meta: { title: '个人信息' }
      },
      {
        path: 'system/notification',
        name: 'Notification',
        component: () => import('../views/system/notification/index.vue'),
        meta: { title: '通知管理' }
      },
      {
        path: 'notification',
        name: 'MyNotification',
        component: () => import('../views/notification/index.vue'),
        meta: { title: '通知公告中心' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// Navigation Guard
const whiteList = ['/login']
let isRoutesGenerated = false

// Reset routes generation flag on logout / session end
export function resetDynamicRoutesFlag() {
  isRoutesGenerated = false
}

// Resolve component lazy loading dynamically matching Vite Glob
function loadComponent(componentPath: string | null, path: string) {
  let comp = componentPath || path
  if (!comp) return null
  
  comp = comp.replace(/^\/+/, '') // Remove leading slash
  
  if (!comp.endsWith('.vue')) {
    if (comp.endsWith('/index')) {
      comp = comp + '.vue'
    } else if (comp.endsWith('/')) {
      comp = comp + 'index.vue'
    } else {
      comp = comp + '/index.vue'
    }
  }

  const globKey = `../views/${comp}`
  if (modules[globKey]) {
    return modules[globKey]
  }
  
  // Fallback to checking subdirectory index
  const alternativeKey = `../views/${path}/index.vue`
  if (modules[alternativeKey]) {
    return modules[alternativeKey]
  }

  return null
}

// Dynamic route generation by fetching database menus
async function generateDynamicRoutes() {
  try {
    const menus: any = await getMenuList()
    if (Array.isArray(menus)) {
      menus.forEach((item: any) => {
        // Register route component for Menu Type "C"
        if (item.menu_type === 'C' && item.path) {
          const comp = loadComponent(item.component, item.path)
          if (comp) {
            router.addRoute('Layout', {
              path: item.path,
              name: item.path,
              component: comp,
              meta: { title: item.menu_name, icon: item.icon }
            })
          }
        }
      })
    }
    isRoutesGenerated = true
  } catch (err) {
    console.error('Error generating dynamic routes:', err)
  }
}

router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore()
  const token = userStore.token

  if (token) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      // Check if we have user info
      if (userStore.roles.length === 0) {
        try {
          await userStore.getInfo()
          await generateDynamicRoutes()
          next({ ...to, replace: true })
        } catch (error) {
          userStore.clearToken()
          next(`/login?redirect=${to.path}`)
        }
      } else {
        if (!isRoutesGenerated) {
          await generateDynamicRoutes()
          next({ ...to, replace: true })
        } else {
          next()
        }
      }
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

router.afterEach((to) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - ${settings.titleSuffix}`
  }
})

export default router
