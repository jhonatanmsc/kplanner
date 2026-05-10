<template>
  <div class="min-h-screen flex items-center justify-center p-6" style="background:var(--bg)">
    <div class="w-full max-w-md rounded-3xl p-8" style="background:var(--surface);border:1px solid var(--border)">
      <h1 class="text-2xl font-semibold mb-4" style="color:var(--text)">Registrar</h1>
      <form @submit.prevent="submitRegister" class="space-y-4">
        <div>
          <label class="block text-sm mb-2" style="color:var(--muted)">Usuário</label>
          <input v-model="form.username" required class="w-full rounded-xl px-4 py-3 text-sm outline-none" style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
        </div>
        <div>
          <label class="block text-sm mb-2" style="color:var(--muted)">Senha</label>
          <input type="password" v-model="form.password" required class="w-full rounded-xl px-4 py-3 text-sm outline-none" style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
        </div>
        <div v-if="error" class="text-sm text-red-400">{{ error }}</div>
        <button type="submit" class="w-full py-3 rounded-xl text-sm font-medium" style="background:var(--accent);color:#fff">Registrar</button>
      </form>
      <p class="text-sm mt-5" style="color:var(--muted)">Já tem conta? <router-link to="/login" class="text-accent">Entrar</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: '', password: '' })
const error = ref(null)

async function submitRegister() {
  error.value = null
  try {
    await auth.register(form.value)
    router.push('/')
  } catch (err) {
    error.value = 'Não foi possível criar a conta. Verifique o usuário.'
  }
}
</script>
