import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const CART_KEY = 'wechat_cart_state'

const loadState = () => {
  try {
    const raw = localStorage.getItem(CART_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export const useCartStore = defineStore('wechat-cart', () => {
  const cached = loadState()

  const items = ref(Array.isArray(cached?.items) ? cached.items : [])
  const orderContext = ref(
    cached?.orderContext || {
      tableId: null,
      tableName: '',
      orderType: 'dine_in',
      mode: 'direct'
    }
  )

  const persist = () => {
    localStorage.setItem(
      CART_KEY,
      JSON.stringify({
        items: items.value,
        orderContext: orderContext.value
      })
    )
  }

  const setContextFromRoute = (query = {}) => {
    orderContext.value = {
      tableId: query.tableId ? Number(query.tableId) : null,
      tableName: query.tableName || '',
      orderType: query.orderType || 'dine_in',
      mode: query.mode || 'direct'
    }
    persist()
  }

  const setDishQuantity = (dish, quantity) => {
    const normalizedQty = Math.max(0, Number(quantity) || 0)
    const id = Number(dish.id)
    const index = items.value.findIndex((item) => Number(item.id) === id)

    if (normalizedQty === 0) {
      if (index >= 0) {
        items.value.splice(index, 1)
      }
      persist()
      return
    }

    const normalizedItem = {
      id,
      name: dish.name,
      price: Number(dish.price || 0),
      image: dish.image_url || dish.image || '',
      quantity: normalizedQty,
      description: dish.description || ''
    }

    if (index >= 0) {
      items.value[index] = normalizedItem
    } else {
      items.value.push(normalizedItem)
    }

    persist()
  }

  const clearCart = () => {
    items.value = []
    persist()
  }

  const totalCount = computed(() => items.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0))
  const totalAmount = computed(() => items.value.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 0), 0))

  const getDishQuantity = (dishId) => {
    const item = items.value.find((row) => Number(row.id) === Number(dishId))
    return Number(item?.quantity || 0)
  }

  return {
    items,
    orderContext,
    totalCount,
    totalAmount,
    setContextFromRoute,
    setDishQuantity,
    getDishQuantity,
    clearCart
  }
})
