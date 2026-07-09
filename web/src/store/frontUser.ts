import { defineStore } from 'pinia'
import { login as loginApi, getInfo as getInfoApi, logout as logoutApi } from '../api/frontAuth'

export interface FrontUserState {
  frontToken: string | null
  username: string
  avatar: string
  loginVisible: boolean
}

export const useFrontUserStore = defineStore('frontUser', {
  state: (): FrontUserState => ({
    frontToken: localStorage.getItem('front_token'),
    username: '',
    avatar: '',
    loginVisible: false
  }),
  actions: {
    setToken(token: string) {
      this.frontToken = token
      localStorage.setItem('front_token', token)
    },
    clearToken() {
      this.frontToken = null
      this.username = ''
      this.avatar = ''
      localStorage.removeItem('front_token')
    },
    showLogin() {
      this.loginVisible = true
    },
    hideLogin() {
      this.loginVisible = false
    },
    async login(loginForm: { username: string; password: string; captchaVerification?: string }) {
      const res: any = await loginApi(loginForm)
      if (res.access_token) {
        this.setToken(res.access_token)
        await this.getInfo()
        this.hideLogin()
        return res
      }
      throw new Error('Login failed')
    },
    async getInfo() {
      const res: any = await getInfoApi()
      this.username = res.username || ''
      this.avatar = res.avatar || ''
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
