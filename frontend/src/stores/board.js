import { defineStore } from 'pinia'
import { boardsApi, listsApi, cardsApi, labelsApi } from '../api'

export const useBoardStore = defineStore('board', {
  state: () => ({
    boards: [],
    currentBoard: null,
    labels: [],
    loading: false,
  }),

  actions: {
    async fetchBoards() {
      const { data } = await boardsApi.list()
      this.boards = data
    },

    async fetchBoard(id) {
      this.loading = true
      const { data } = await boardsApi.get(id)
      this.currentBoard = data
      this.loading = false
    },

    async createBoard(payload) {
      const { data } = await boardsApi.create(payload)
      this.boards.unshift(data)
      return data
    },

    async updateBoard(id, payload) {
      const { data } = await boardsApi.update(id, payload)
      const idx = this.boards.findIndex(b => b.id === id)
      if (idx !== -1) this.boards[idx] = { ...this.boards[idx], ...data }
      if (this.currentBoard?.id === id) this.currentBoard = { ...this.currentBoard, ...data }
    },

    async deleteBoard(id) {
      await boardsApi.remove(id)
      this.boards = this.boards.filter(b => b.id !== id)
    },

    async createList(payload) {
      const { data } = await listsApi.create(payload)
      this.currentBoard.lists.push({ ...data, cards: [] })
    },

    async updateList(listId, payload) {
      await listsApi.update(listId, payload)
      const list = this.currentBoard.lists.find(l => l.id === listId)
      if (list) Object.assign(list, payload)
    },

    async deleteList(listId) {
      await listsApi.remove(listId)
      this.currentBoard.lists = this.currentBoard.lists.filter(l => l.id !== listId)
    },

    async createCard(payload) {
      const { data } = await cardsApi.create(payload)
      const list = this.currentBoard.lists.find(l => l.id === payload.list_id)
      if (list) list.cards.push(data)
      return data
    },

    async updateCard(cardId, payload) {
      const { data } = await cardsApi.update(cardId, payload)
      for (const list of this.currentBoard.lists) {
        const idx = list.cards.findIndex(c => c.id === cardId)
        if (idx !== -1) { list.cards[idx] = data; break }
      }
      return data
    },

    async moveCard(cardId, fromListId, toListId, newPosition) {
      const fromList = this.currentBoard.lists.find(l => l.id === fromListId)
      const toList = this.currentBoard.lists.find(l => l.id === toListId)
      const card = fromList.cards.find(c => c.id === cardId)
      fromList.cards = fromList.cards.filter(c => c.id !== cardId)
      toList.cards.splice(newPosition, 0, card)
      await cardsApi.update(cardId, { list_id: toListId, position: newPosition })
    },

    async deleteCard(cardId, listId) {
      await cardsApi.remove(cardId)
      const list = this.currentBoard.lists.find(l => l.id === listId)
      if (list) list.cards = list.cards.filter(c => c.id !== cardId)
    },

    async fetchLabels() {
      const { data } = await labelsApi.list()
      this.labels = data
    },

    async createLabel(payload) {
      const { data } = await labelsApi.create(payload)
      this.labels.push(data)
      return data
    },

    async addLabelToCard(cardId, labelId, listId) {
      await cardsApi.addLabel(cardId, labelId)
      const list = this.currentBoard.lists.find(l => l.id === listId)
      const card = list?.cards.find(c => c.id === cardId)
      const label = this.labels.find(l => l.id === labelId)
      if (card && label && !card.labels.find(l => l.id === labelId)) card.labels.push(label)
    },

    async removeLabelFromCard(cardId, labelId, listId) {
      await cardsApi.removeLabel(cardId, labelId)
      const list = this.currentBoard.lists.find(l => l.id === listId)
      const card = list?.cards.find(c => c.id === cardId)
      if (card) card.labels = card.labels.filter(l => l.id !== labelId)
    },

    async addChecklistItem(cardId, listId, text) {
      const { data } = await cardsApi.addChecklist(cardId, { text, position: 0 })
      const list = this.currentBoard.lists.find(l => l.id === listId)
      const card = list?.cards.find(c => c.id === cardId)
      if (card) card.checklist_items.push(data)
    },

    async toggleChecklistItem(cardId, itemId, listId, done) {
      const { data } = await cardsApi.updateChecklist(cardId, itemId, { done })
      const list = this.currentBoard.lists.find(l => l.id === listId)
      const card = list?.cards.find(c => c.id === cardId)
      if (card) {
        const item = card.checklist_items.find(i => i.id === itemId)
        if (item) item.done = data.done
      }
    },

    async removeChecklistItem(cardId, itemId, listId) {
      await cardsApi.removeChecklist(cardId, itemId)
      const list = this.currentBoard.lists.find(l => l.id === listId)
      const card = list?.cards.find(c => c.id === cardId)
      if (card) card.checklist_items = card.checklist_items.filter(i => i.id !== itemId)
    },
  },
})
