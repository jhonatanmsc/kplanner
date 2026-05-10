<template>
  <div class="min-h-screen flex flex-col" style="background:var(--bg)">
    <!-- Topbar -->
    <header class="flex items-center gap-4 px-6 py-3 border-b" style="border-color:var(--border);background:var(--surface)">
      <router-link to="/" class="text-sm hover:opacity-70 transition-opacity" style="color:var(--muted)">← Boards</router-link>
      <div class="w-px h-4" style="background:var(--border)"></div>
      <div v-if="currentBoard">
        <span class="font-semibold">{{ currentBoard.title }}</span>
        <span v-if="currentBoard.sprint_end_date" class="ml-3 text-xs px-2 py-0.5 rounded-full"
          :class="isOverdue(currentBoard.sprint_end_date) ? 'bg-red-900 text-red-300' : 'bg-emerald-900 text-emerald-300'">
          Sprint até {{ formatDate(currentBoard.sprint_end_date) }}
        </span>
      </div>
      <div class="flex items-center gap-3 ml-auto">
        <span v-if="user" class="text-sm" style="color:var(--muted)">Olá, {{ user.username }}</span>
        <button @click="logout"
          class="text-sm px-3 py-1.5 rounded-lg transition-all"
          style="background:var(--surface2);color:var(--text);border:1px solid var(--border)">
          Sair
        </button>
        <button @click="showAddList = true"
          class="text-sm px-3 py-1.5 rounded-lg transition-all"
          style="background:var(--surface2);color:var(--text);border:1px solid var(--border)">
          + Lista
        </button>
      </div>
    </header>

    <!-- Board -->
    <div v-if="currentBoard" class="flex-1 overflow-x-auto p-6">
      <div class="flex gap-4 items-start" style="min-height: calc(100vh - 120px)">
        <div v-for="list in currentBoard.lists" :key="list.id"
          :data-list-id="list.id"
          class="flex-shrink-0 w-72 rounded-xl flex flex-col"
          style="background:var(--surface);border:1px solid var(--border)">

          <!-- List header -->
          <div class="flex items-center justify-between px-4 py-3 border-b" style="border-color:var(--border)">
            <span v-if="editingListId !== list.id" @dblclick="startEditList(list)"
              class="font-medium text-sm cursor-pointer">{{ list.title }}</span>
            <input v-else v-model="editListTitle" @blur="saveListTitle(list)"
              @keydown.enter="saveListTitle(list)" @keydown.esc="editingListId = null"
              class="text-sm font-medium bg-transparent outline-none border-b w-full"
              style="border-color:var(--accent);color:var(--text)" />
            <button @click="store.deleteList(list.id)"
              class="text-xs opacity-30 hover:opacity-100 transition-opacity ml-2"
              style="color:var(--muted)">✕</button>
          </div>

          <!-- Cards -->
          <draggable v-model="list.cards" :group="{ name: 'cards' }"
            item-key="id" ghost-class="card-drag"
            @end="onDragEnd($event, list.id)"
            class="flex-1 flex flex-col gap-2 p-3 min-h-[40px]">
            <template #item="{ element: card }">
              <div @click="openCard(card, list.id)"
                class="rounded-lg p-3 cursor-pointer transition-all hover:translate-y-[-1px]"
                style="background:var(--surface2);border:1px solid var(--border)">
                <!-- Labels -->
                <div v-if="card.labels?.length" class="flex flex-wrap gap-1 mb-2">
                  <span v-for="lbl in card.labels" :key="lbl.id"
                    class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :style="`background:${lbl.color}22;color:${lbl.color}`">
                    {{ lbl.name }}
                  </span>
                </div>
                <p class="text-sm leading-snug" style="color:var(--text)">{{ card.title }}</p>
                <!-- Indicators -->
                <div class="flex items-center gap-3 mt-2">
                  <span v-if="card.due_date" class="text-xs"
                    :class="isOverdue(card.due_date) ? 'text-red-400' : 'text-slate-400'">
                    📅 {{ formatDate(card.due_date) }}
                  </span>
                  <span v-if="card.checklist_items?.length" class="text-xs" style="color:var(--muted)">
                    ☑ {{ card.checklist_items.filter(i => i.done).length }}/{{ card.checklist_items.length }}
                  </span>
                  <span v-if="card.description" class="text-xs" style="color:var(--muted)">≡</span>
                </div>
              </div>
            </template>
          </draggable>

          <!-- Add card -->
          <div class="p-3 border-t" style="border-color:var(--border)">
            <div v-if="addingCardListId !== list.id">
              <button @click="addingCardListId = list.id; newCardTitle = ''"
                class="w-full text-left text-sm px-2 py-1.5 rounded transition-colors"
                style="color:var(--muted)">+ Adicionar card</button>
            </div>
            <div v-else>
              <input v-model="newCardTitle" placeholder="Título do card"
                @keydown.enter="submitCard(list.id)" @keydown.esc="addingCardListId = null"
                autofocus
                class="w-full px-2 py-1.5 rounded text-sm outline-none mb-2"
                style="background:var(--bg);border:1px solid var(--accent);color:var(--text)" />
              <div class="flex gap-2">
                <button @click="submitCard(list.id)"
                  class="text-xs px-3 py-1 rounded"
                  style="background:var(--accent);color:#fff">Adicionar</button>
                <button @click="addingCardListId = null"
                  class="text-xs px-2 py-1 rounded"
                  style="color:var(--muted)">✕</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Add list inline -->
        <div v-if="showAddList" class="flex-shrink-0 w-72 rounded-xl p-4"
          style="background:var(--surface);border:1px solid var(--border)">
          <input v-model="newListTitle" placeholder="Título da lista"
            @keydown.enter="submitList" @keydown.esc="showAddList = false"
            autofocus
            class="w-full px-3 py-2 rounded-lg text-sm outline-none mb-3"
            style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          <div class="flex gap-2">
            <button @click="submitList"
              class="text-sm px-4 py-1.5 rounded-lg"
              style="background:var(--accent);color:#fff">Criar</button>
            <button @click="showAddList = false"
              class="text-sm px-3 py-1.5 rounded-lg"
              style="color:var(--muted)">Cancelar</button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="store.loading" class="flex-1 flex items-center justify-center" style="color:var(--muted)">
      Carregando...
    </div>

    <!-- Card modal -->
    <CardModal v-if="selectedCard" :card="selectedCard" :list-id="selectedListId"
      @close="selectedCard = null" />

    <!-- Add list modal -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBoardStore } from '../stores/board'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import draggable from 'vuedraggable'
import { format, isPast, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import CardModal from '../components/card/CardModal.vue'

const route = useRoute()
const router = useRouter()
const store = useBoardStore()
const auth = useAuthStore()
const { currentBoard } = storeToRefs(store)
const { user } = storeToRefs(auth)

const showAddList = ref(false)
const newListTitle = ref('')
const addingCardListId = ref(null)
const newCardTitle = ref('')
const editingListId = ref(null)
const editListTitle = ref('')
const selectedCard = ref(null)
const selectedListId = ref(null)

onMounted(async () => {
  if (auth.token) {
    await auth.fetchCurrentUser().catch(() => auth.logout())
  }
  await store.fetchBoard(route.params.id)
  await store.fetchLabels()
})

const formatDate = (d) => format(parseISO(d), 'dd MMM', { locale: ptBR })
const isOverdue = (d) => isPast(parseISO(d))

function openCard(card, listId) {
  selectedCard.value = card
  selectedListId.value = listId
}

async function submitList() {
  if (!newListTitle.value.trim()) return
  const pos = currentBoard.value.lists.length
  await store.createList({ title: newListTitle.value, board_id: route.params.id, position: pos })
  newListTitle.value = ''
  showAddList.value = false
}

async function submitCard(listId) {
  if (!newCardTitle.value.trim()) return
  const list = currentBoard.value.lists.find(l => l.id === listId)
  await store.createCard({ title: newCardTitle.value, list_id: listId, position: list.cards.length })
  newCardTitle.value = ''
  addingCardListId.value = null
}

function startEditList(list) {
  editingListId.value = list.id
  editListTitle.value = list.title
}

async function saveListTitle(list) {
  if (editListTitle.value.trim() && editListTitle.value !== list.title)
    await store.updateList(list.id, { title: editListTitle.value })
  editingListId.value = null
}

async function onDragEnd(evt, toListId) {
  const fromListId = evt.from.closest('[data-list-id]')?.dataset.listId || toListId
  const toList = currentBoard.value.lists.find(l => l.id === toListId)
  const card = toList?.cards?.[evt.newIndex]
  if (!card) return
  await store.moveCard(card.id, fromListId, toListId, evt.newIndex)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
