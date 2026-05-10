<template>
  <div class="min-h-screen p-8" style="background:var(--bg)">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight" style="color:var(--text)">Gerenciar usuários</h1>
        <p class="text-sm mt-1" style="color:var(--muted)">Crie, promova e remova contas de usuários.</p>
      </div>
      <button @click="goBack"
        class="text-sm px-3 py-2 rounded-lg transition-all"
        style="background:var(--surface2);color:var(--text);border:1px solid var(--border)">Voltar</button>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1fr_320px]">
      <div class="space-y-4">
        <div v-if="error" class="rounded-xl p-4 text-sm" style="background:#fee2e2;color:#991b1b">{{ error }}</div>
        <div class="rounded-xl p-5" style="background:var(--surface);border:1px solid var(--border)">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold" style="color:var(--text)">Lista de usuários</h2>
            <span class="text-xs" style="color:var(--muted)">{{ users.length }} usuário{{ users.length !== 1 ? 's' : '' }}</span>
          </div>
          <div v-if="loading" class="text-sm" style="color:var(--muted)">Carregando usuários...</div>
          <div v-else>
            <div v-if="!users.length" class="text-sm" style="color:var(--muted)">Nenhum usuário encontrado.</div>
            <div v-for="item in users" :key="item.id" class="rounded-xl p-4 mb-3" style="background:var(--surface2);border:1px solid var(--border)">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="font-semibold" style="color:var(--text)">{{ item.username }}</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">
                    {{ item.is_admin ? 'Administrador' : 'Usuário' }}
                    <span v-if="item.id === auth.user?.id">• você</span>
                  </p>
                </div>
                <div class="flex flex-col items-end gap-2">
                  <label class="text-xs flex items-center gap-2" style="color:var(--muted)">
                    <input type="checkbox" :checked="item.is_admin" @change="toggleAdmin(item, $event.target.checked)" />
                    Admin
                  </label>
                  <button @click="removeUser(item)"
                    :disabled="item.id === auth.user?.id"
                    class="px-3 py-1 rounded-lg text-xs transition-all"
                    :style="item.id === auth.user?.id ? 'background:var(--surface2);color:var(--muted)' : 'background:#ef4444;color:#fff'">
                    Excluir
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-xl p-5" style="background:var(--surface);border:1px solid var(--border)">
        <h2 class="font-semibold mb-4" style="color:var(--text)">Criar novo usuário</h2>
        <form @submit.prevent="createUser" class="space-y-4">
          <div>
            <label class="text-xs block mb-2" style="color:var(--muted)">Usuário</label>
            <input v-model="form.username" placeholder="nome de usuário" class="w-full px-3 py-2 rounded-lg text-sm outline-none"
              style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          </div>
          <div>
            <label class="text-xs block mb-2" style="color:var(--muted)">Senha</label>
            <input v-model="form.password" type="password" placeholder="senha" class="w-full px-3 py-2 rounded-lg text-sm outline-none"
              style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          </div>
          <label class="flex items-center gap-2 text-sm" style="color:var(--muted)">
            <input type="checkbox" v-model="form.is_admin" /> Administrador
          </label>
          <button type="submit" class="w-full py-2 rounded-lg text-sm font-medium" style="background:var(--accent);color:#fff">Criar usuário</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { authApi, userApi } from '../api'

const router = useRouter()
const auth = useAuthStore()
const users = ref([])
const loading = ref(false)
const error = ref('')
const form = ref({ username: '', password: '', is_admin: false })

async function fetchUsers() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await userApi.list()
    users.value = data
  } catch (err) {
    error.value = 'Falha ao carregar usuários.'
  } finally {
    loading.value = false
  }
}

async function createUser() {
  if (!form.value.username.trim() || !form.value.password.trim()) return
  error.value = ''
  try {
    await authApi.register({
      username: form.value.username,
      password: form.value.password,
      is_admin: form.value.is_admin,
    })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Falha ao criar usuário.'
    return
  }
  form.value = { username: '', password: '', is_admin: false }
  await fetchUsers()
}

async function toggleAdmin(item, isAdmin) {
  try {
    await userApi.update(item.id, { is_admin: isAdmin })
    await fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Falha ao atualizar o usuário.'
  }
}

async function removeUser(item) {
  if (!confirm(`Excluir usuário ${item.username}?`)) return
  try {
    await userApi.remove(item.id)
    await fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Falha ao excluir o usuário.'
  }
}

function goBack() {
  router.push('/')
}

onMounted(() => {
  if (!auth.user || !auth.user.is_admin) {
    router.push('/')
    return
  }
  fetchUsers()
})
</script>
