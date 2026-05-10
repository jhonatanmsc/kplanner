<template>
  <div class="min-h-screen p-8" style="background:var(--bg)">
    <!-- Header -->
    <div class="flex items-center justify-between mb-10">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight" style="color:var(--text)">Meus Boards</h1>
        <p class="text-sm mt-1" style="color:var(--muted)">{{ boards.length }} board{{ boards.length !== 1 ? 's' : '' }}</p>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="user" class="text-sm" style="color:var(--muted)">Olá, {{ user.username }}</span>
        <button v-if="user && user.is_admin" @click="router.push('/admin/users')"
          class="text-sm px-3 py-1.5 rounded-lg transition-all"
          style="background:var(--surface2);color:var(--text);border:1px solid var(--border)">Admin</button>
        <button @click="logout"
          class="text-sm px-3 py-1.5 rounded-lg transition-all"
          style="background:var(--surface2);color:var(--text);border:1px solid var(--border)">Sair</button>
        <button @click="showCreate = true"
          class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
          style="background:var(--accent);color:#fff">
          + Novo Board
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto rounded-xl border border-solid mb-8" style="border-color:var(--border);background:var(--surface)">
      <table class="min-w-full text-left">
        <thead>
          <tr class="text-sm uppercase tracking-wide" style="color:var(--muted)">
            <th class="px-4 py-3 cursor-pointer" @click="setSort('title')">Título <span>{{ sortIndicator('title') }}</span></th>
            <th class="px-4 py-3 cursor-pointer" @click="setSort('description')">Descrição <span>{{ sortIndicator('description') }}</span></th>
            <th class="px-4 py-3 cursor-pointer" @click="setSort('sprint_end_date')">Sprint até <span>{{ sortIndicator('sprint_end_date') }}</span></th>
            <th class="px-4 py-3 cursor-pointer" @click="setSort('position')">Ordem <span>{{ sortIndicator('position') }}</span></th>
            <th class="px-4 py-3 cursor-pointer" @click="setSort('created_at')">Criado em <span>{{ sortIndicator('created_at') }}</span></th>
            <th class="px-4 py-3">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in sortedBoards" :key="b.id" class="border-t border-solid" :style="`border-color:var(--border)`">
            <td class="px-4 py-4">
              <button @click="viewBoard(b.id)" class="text-left w-full text-base font-semibold" style="color:var(--text)">{{ b.title }}</button>
            </td>
            <td class="px-4 py-4 text-sm" style="color:var(--muted)">{{ b.description || '—' }}</td>
            <td class="px-4 py-4 text-sm" :style="isOverdue(b.sprint_end_date) ? 'color:#ef4444' : 'color:#10b981'">
              {{ b.sprint_end_date ? formatDate(b.sprint_end_date) : '—' }}
            </td>
            <td class="px-4 py-4 text-sm" style="color:var(--muted)">{{ b.position }}</td>
            <td class="px-4 py-4 text-sm" style="color:var(--muted)">{{ formatDate(b.created_at) }}</td>
            <td class="px-4 py-4">
              <button @click.prevent="deleteBoard(b.id)"
                class="text-xs px-3 py-1 rounded-lg"
                style="background:#ef4444;color:#fff">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal criar board -->
    <Teleport to="body">
      <div v-if="showCreate" class="fixed inset-0 flex items-center justify-center z-50"
        style="background:rgba(0,0,0,0.7)" @click.self="showCreate = false">
        <div class="rounded-xl p-6 w-full max-w-md" style="background:var(--surface);border:1px solid var(--border)">
          <h3 class="font-semibold mb-4">Novo Board</h3>
          <input v-model="form.title" placeholder="Título" @keydown.enter="submitCreate"
            class="w-full px-3 py-2 rounded-lg text-sm mb-3 outline-none"
            style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          <input v-model="form.description" placeholder="Descrição (opcional)" @keydown.enter="submitCreate"
            class="w-full px-3 py-2 rounded-lg text-sm mb-3 outline-none"
            style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          <div class="flex items-center gap-3 mb-3">
            <label class="text-xs" style="color:var(--muted)">Cor</label>
            <input type="color" v-model="form.color" class="w-8 h-8 rounded cursor-pointer border-0 bg-transparent" />
          </div>
          <div class="mb-4">
            <label class="text-xs block mb-1" style="color:var(--muted)">Sprint end date</label>
            <input type="date" v-model="form.sprint_end_date"
              class="w-full px-3 py-2 rounded-lg text-sm outline-none"
              style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          </div>
          <div class="flex gap-2">
            <button @click="submitCreate"
              class="flex-1 py-2 rounded-lg text-sm font-medium"
              style="background:var(--accent);color:#fff">Criar</button>
            <button @click="showCreate = false"
              class="px-4 py-2 rounded-lg text-sm"
              style="background:var(--surface2);color:var(--muted)">Cancelar</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBoardStore } from '../stores/board'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import { format, isPast, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const router = useRouter()
const store = useBoardStore()
const auth = useAuthStore()
const { boards } = storeToRefs(store)
const { user } = storeToRefs(auth)

const showCreate = ref(false)
const form = ref({ title: '', description: '', color: '#6366f1', sprint_end_date: '' })
const sortKey = ref('created_at')
const sortAsc = ref(false)

onMounted(async () => {
  if (auth.token) {
    await auth.fetchCurrentUser().catch(() => auth.logout())
  }
  await store.fetchBoards()
})

const sortedBoards = computed(() => {
  return [...boards.value].sort((a, b) => {
    const valueA = a[sortKey.value] || ''
    const valueB = b[sortKey.value] || ''

    if (sortKey.value === 'created_at' || sortKey.value === 'sprint_end_date') {
      const dateA = valueA ? new Date(valueA).getTime() : 0
      const dateB = valueB ? new Date(valueB).getTime() : 0
      return sortAsc.value ? dateA - dateB : dateB - dateA
    }

    const textA = String(valueA).toLowerCase()
    const textB = String(valueB).toLowerCase()
    if (textA < textB) return sortAsc.value ? -1 : 1
    if (textA > textB) return sortAsc.value ? 1 : -1
    return 0
  })
})

const formatDate = (d) => (d ? format(parseISO(d), 'dd MMM yyyy', { locale: ptBR }) : '—')
const isOverdue = (d) => d ? isPast(parseISO(d)) : false

function setSort(key) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = key !== 'title'
  }
}

function sortIndicator(key) {
  if (sortKey.value !== key) return '↕'
  return sortAsc.value ? '↑' : '↓'
}

async function submitCreate() {
  if (!form.value.title.trim()) return
  const payload = { ...form.value }
  if (!payload.sprint_end_date) delete payload.sprint_end_date
  await store.createBoard(payload)
  showCreate.value = false
  form.value = { title: '', description: '', color: '#6366f1', sprint_end_date: '' }
}

async function deleteBoard(id) {
  if (confirm('Apagar este board?')) await store.deleteBoard(id)
}

function viewBoard(id) {
  router.push(`/board/${id}`)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
