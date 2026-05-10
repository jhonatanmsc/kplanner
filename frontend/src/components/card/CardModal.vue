<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4"
      style="background:rgba(0,0,0,0.75)" @click.self="$emit('close')">
      <div class="w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl"
        style="background:var(--surface);border:1px solid var(--border);max-height:85vh;overflow-y:auto">

        <!-- Header -->
        <div class="flex items-start justify-between p-6 pb-3">
          <div class="flex-1 mr-4">
            <input v-model="localCard.title" @blur="save('title', localCard.title)"
              @keydown.enter="$event.target.blur()"
              class="text-lg font-semibold w-full bg-transparent outline-none border-b border-transparent focus:border-current"
              style="color:var(--text)" />
          </div>
          <button @click="$emit('close')" class="text-xl leading-none hover:opacity-70" style="color:var(--muted)">✕</button>
        </div>

        <div class="px-6 pb-6 flex flex-col gap-6">

          <!-- Labels -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color:var(--muted)">Labels</h4>
            <div class="flex flex-wrap gap-2 mb-2">
              <span v-for="lbl in localCard.labels" :key="lbl.id"
                class="flex items-center gap-1 text-xs px-2 py-1 rounded-full cursor-pointer"
                :style="`background:${lbl.color}22;color:${lbl.color}`"
                @click="removeLabel(lbl.id)">
                {{ lbl.name }} ✕
              </span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span v-for="lbl in availableLabels" :key="lbl.id"
                class="text-xs px-2 py-1 rounded-full cursor-pointer opacity-50 hover:opacity-100 transition-opacity"
                :style="`background:${lbl.color}22;color:${lbl.color}`"
                @click="addLabel(lbl.id)">
                + {{ lbl.name }}
              </span>
              <button @click="showLabelCreate = !showLabelCreate"
                class="text-xs px-2 py-1 rounded-full"
                style="background:var(--surface2);color:var(--muted)">+ Nova label</button>
            </div>
            <div v-if="showLabelCreate" class="flex gap-2 mt-2 items-center">
              <input v-model="newLabel.name" placeholder="Nome" class="px-2 py-1 rounded text-xs outline-none flex-1"
                style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
              <input type="color" v-model="newLabel.color" class="w-7 h-7 rounded border-0 cursor-pointer bg-transparent" />
              <button @click="createLabel" class="text-xs px-2 py-1 rounded"
                style="background:var(--accent);color:#fff">Criar</button>
            </div>
          </div>

          <!-- Due date -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color:var(--muted)">Data de entrega</h4>
            <input type="date" v-model="localCard.due_date"
              @change="save('due_date', localCard.due_date)"
              class="px-3 py-1.5 rounded-lg text-sm outline-none"
              style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          </div>

          <!-- Description -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color:var(--muted)">Descrição</h4>
            <textarea v-model="localCard.description" rows="4"
              @blur="save('description', localCard.description)"
              placeholder="Adicionar uma descrição..."
              class="w-full px-3 py-2 rounded-lg text-sm outline-none resize-none"
              style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
          </div>

          <!-- Checklist -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-3" style="color:var(--muted)">
              Checklist
              <span v-if="localCard.checklist_items?.length" class="ml-2 font-normal normal-case">
                {{ localCard.checklist_items.filter(i => i.done).length }}/{{ localCard.checklist_items.length }}
              </span>
            </h4>

            <!-- Progress bar -->
            <div v-if="localCard.checklist_items?.length" class="h-1 rounded-full mb-3" style="background:var(--border)">
              <div class="h-1 rounded-full transition-all" style="background:var(--accent)"
                :style="`width:${checklistProgress}%`"></div>
            </div>

            <div class="flex flex-col gap-2 mb-3">
              <div v-for="item in localCard.checklist_items" :key="item.id"
                class="flex items-center gap-3 group">
                <input type="checkbox" :checked="item.done"
                  @change="toggleItem(item.id, !item.done)"
                  class="w-4 h-4 rounded cursor-pointer accent-indigo-500" />
                <span class="text-sm flex-1" :class="item.done ? 'line-through opacity-40' : ''"
                  style="color:var(--text)">{{ item.text }}</span>
                <button @click="removeItem(item.id)"
                  class="text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  style="color:var(--muted)">✕</button>
              </div>
            </div>

            <div class="flex gap-2">
              <input v-model="newItemText" placeholder="Novo item..." @keydown.enter="addItem"
                class="flex-1 px-3 py-1.5 rounded-lg text-sm outline-none"
                style="background:var(--surface2);border:1px solid var(--border);color:var(--text)" />
              <button @click="addItem" class="text-sm px-3 py-1.5 rounded-lg"
                style="background:var(--surface2);color:var(--text);border:1px solid var(--border)">+</button>
            </div>
          </div>

          <!-- Delete -->
          <div class="pt-2 border-t" style="border-color:var(--border)">
            <button @click="deleteCard"
              class="text-sm px-3 py-1.5 rounded-lg transition-colors hover:bg-red-900"
              style="color:#f87171">Apagar card</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useBoardStore } from '../../stores/board'
import { storeToRefs } from 'pinia'

const props = defineProps({ card: Object, listId: String })
const emit = defineEmits(['close'])

const store = useBoardStore()
const { labels } = storeToRefs(store)

const localCard = ref({ ...props.card, labels: [...(props.card.labels || [])], checklist_items: [...(props.card.checklist_items || [])] })
const newItemText = ref('')
const showLabelCreate = ref(false)
const newLabel = ref({ name: '', color: '#6366f1' })

const availableLabels = computed(() =>
  labels.value.filter(l => !localCard.value.labels.find(cl => cl.id === l.id))
)

const checklistProgress = computed(() => {
  const items = localCard.value.checklist_items
  if (!items?.length) return 0
  return Math.round((items.filter(i => i.done).length / items.length) * 100)
})

async function save(field, value) {
  await store.updateCard(localCard.value.id, { [field]: value || null })
}

async function addLabel(labelId) {
  await store.addLabelToCard(localCard.value.id, labelId, props.listId)
  const label = labels.value.find(l => l.id === labelId)
  if (label) localCard.value.labels.push(label)
}

async function removeLabel(labelId) {
  await store.removeLabelFromCard(localCard.value.id, labelId, props.listId)
  localCard.value.labels = localCard.value.labels.filter(l => l.id !== labelId)
}

async function createLabel() {
  if (!newLabel.value.name.trim()) return
  const created = await store.createLabel(newLabel.value)
  newLabel.value = { name: '', color: '#6366f1' }
  showLabelCreate.value = false
  await addLabel(created.id)
}

async function addItem() {
  if (!newItemText.value.trim()) return
  await store.addChecklistItem(localCard.value.id, props.listId, newItemText.value)
  const list = store.currentBoard.lists.find(l => l.id === props.listId)
  const card = list?.cards.find(c => c.id === localCard.value.id)
  if (card) localCard.value.checklist_items = [...card.checklist_items]
  newItemText.value = ''
}

async function toggleItem(itemId, done) {
  await store.toggleChecklistItem(localCard.value.id, itemId, props.listId, done)
  const item = localCard.value.checklist_items.find(i => i.id === itemId)
  if (item) item.done = done
}

async function removeItem(itemId) {
  await store.removeChecklistItem(localCard.value.id, itemId, props.listId)
  localCard.value.checklist_items = localCard.value.checklist_items.filter(i => i.id !== itemId)
}

async function deleteCard() {
  if (confirm('Apagar este card?')) {
    await store.deleteCard(localCard.value.id, props.listId)
    emit('close')
  }
}
</script>
