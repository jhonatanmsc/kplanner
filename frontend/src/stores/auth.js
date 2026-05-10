import { defineStore } from 'pinia'
import { authApi, setAuthToken } from '../api'

const storedToken = localStorage.getItem('auth_token') || ''
if (storedToken) setAuthToken(storedToken)

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: storedToken,
    user: null,
    loading: false,
    error: null,
  }),
  getters: {
    authenticated: (state) => !!state.token,
  },
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('auth_token', token)
      setAuthToken(token)
    },
    clearToken() {
      this.token = ''
      this.user = null
      localStorage.removeItem('auth_token')
      setAuthToken(null)
    },
    async login(credentials) {
      const { data } = await authApi.login(credentials)
      this.setToken(data.access_token)
      await this.fetchCurrentUser()
    },
    async register(payload) {
      await authApi.register(payload)
      await this.login({ username: payload.username, password: payload.password })
    },
    async fetchCurrentUser() {
      if (!this.token) return
      try {
        const { data } = await authApi.me()
        this.user = data
      } catch (err) {
        this.clearToken()
        throw err
      }
    },
    logout() {
      this.clearToken()
    },
  },
})
