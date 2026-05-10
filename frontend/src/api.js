import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const userApi = {
  list: () => api.get('/auth/users'),
  update: (id, data) => api.patch(`/auth/users/${id}`, data),
  remove: (id) => api.delete(`/auth/users/${id}`),
}

export const boardsApi = {
  list: () => api.get('/boards/'),
  get: (id) => api.get(`/boards/${id}`),
  create: (data) => api.post('/boards/', data),
  update: (id, data) => api.patch(`/boards/${id}`, data),
  remove: (id) => api.delete(`/boards/${id}`),
}

export const listsApi = {
  create: (data) => api.post('/lists/', data),
  update: (id, data) => api.patch(`/lists/${id}`, data),
  remove: (id) => api.delete(`/lists/${id}`),
}

export const cardsApi = {
  get: (id) => api.get(`/cards/${id}`),
  create: (data) => api.post('/cards/', data),
  update: (id, data) => api.patch(`/cards/${id}`, data),
  remove: (id) => api.delete(`/cards/${id}`),
  addChecklist: (cardId, data) => api.post(`/cards/${cardId}/checklist`, data),
  updateChecklist: (cardId, itemId, data) => api.patch(`/cards/${cardId}/checklist/${itemId}`, data),
  removeChecklist: (cardId, itemId) => api.delete(`/cards/${cardId}/checklist/${itemId}`),
  addLabel: (cardId, labelId) => api.post(`/cards/${cardId}/labels/${labelId}`),
  removeLabel: (cardId, labelId) => api.delete(`/cards/${cardId}/labels/${labelId}`),
}

export const labelsApi = {
  list: () => api.get('/labels/'),
  create: (data) => api.post('/labels/', data),
  remove: (id) => api.delete(`/labels/${id}`),
}
