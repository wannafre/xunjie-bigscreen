import { defineStore } from 'pinia'
import { resetDynamicRoutesFlag } from '../router'
import { login as loginApi, getInfo as getInfoApi, logout as logoutApi } from '../api/auth'

export interface UserState {
  token: string | null
  username: string
  roles: string[]
  permissions: string[]
  avatar: string
  introduction: string
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token'),
    username: '',
    roles: [],
    permissions: [],
    avatar: '',
    introduction: ''
  }),
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem('token', token)
    },
    clearToken() {
      this.token = null
      this.username = ''
      this.roles = []
      this.permissions = []
      this.avatar = ''
      this.introduction = ''
      localStorage.removeItem('token')
      resetDynamicRoutesFlag()
    },
    async login(loginForm: { username: string; password: string; captchaVerification?: string }) {
      const res: any = await loginApi(loginForm)
      if (res.access_token) {
        this.setToken(res.access_token)
        return res
      }
      throw new Error('Login failed')
    },
    async getInfo() {
      const res: any = await getInfoApi()
      this.username = res.username
      this.roles = res.roles
      this.permissions = res.permissions || []
      this.avatar = res.avatar
      this.introduction = res.remark || ''
      return res
    },
    async logout() {
      try {
        await logoutApi()
      } finally {
        this.clearToken()
      }
    }
  }
})

