<template>
  <div class="menu">
    <div v-if="showContext" class="context-banner">
      <div class="context-main">{{ contextText }}</div>
      <div class="context-sub">就餐方式：{{ orderTypeLabel }}</div>
    </div>

    <van-sticky>
      <van-tabs v-model:active="activeCategory" swipeable class="menu-tabs">
        <van-tab v-for="category in categories" :key="category.id" :title="category.name" />
      </van-tabs>
    </van-sticky>

    <div class="dish-list">
      <van-loading v-if="loading" size="24px" class="loading">加载中...</van-loading>
      <van-empty v-else-if="categories.length === 0" description="暂无分类" />
      <van-empty v-else-if="currentCategoryDishes.length === 0" description="当前分类暂无菜品" />

      <div v-else v-for="dish in currentCategoryDishes" :key="dish.id" class="dish-card">
        <img :src="dish.image" class="dish-image" @error="onImageError" />
        <div class="dish-info">
          <h3 class="dish-name">{{ dish.name }}</h3>
          <p class="dish-desc">{{ dish.description || '招牌推荐' }}</p>
          <div class="dish-footer">
            <div class="dish-price">¥{{ Number(dish.price).toFixed(2) }}</div>
            <van-button class="add-btn" type="warning" size="small" @click="handleAddDish(dish)">加入暂存单</van-button>
          </div>
        </div>
      </div>
    </div>

    <div class="cart-bar" v-if="cartStore.totalCount > 0" @click="goCart">
      <div class="bar-left">
        <span class="bar-count">{{ cartStore.totalCount }} 份</span>
        <span>已加入暂存单</span>
      </div>
      <div class="bar-price">¥{{ cartStore.totalAmount.toFixed(2) }}</div>
      <van-button type="warning" size="small">去结算</van-button>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Toast } from 'vant'
import { getCategories, getDishes } from '@/services/dishService'
import { ensureWechatAuth } from '@/services/authService'
import { useCartStore } from '@/stores/cart'

const FALLBACK_IMAGE = 'https://img.yzcdn.cn/vant/user-default.png'
const STATIC_BASE = import.meta.env.VITE_FILE_BASE_URL || ''

const resolveImageUrl = (url) => {
  if (!url) return FALLBACK_IMAGE
  if (/^https?:\/\//i.test(url)) return url
  if (url.startsWith('/')) return STATIC_BASE ? `${STATIC_BASE}${url}` : url
  return url
}

export default {
  name: 'Menu',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const cartStore = useCartStore()

    const loading = ref(false)
    const activeCategory = ref(0)
    const categories = ref([])
    const dishes = ref([])
    const alive = ref(true)

    const orderTypeLabel = computed(() => {
      const type = cartStore.orderContext.orderType
      if (type === 'takeaway') return '外带'
      if (type === 'pack') return '打包'
      if (type === 'preorder') return '预定'
      return '堂食'
    })

    const showContext = computed(() => Boolean(cartStore.orderContext.tableName || cartStore.orderContext.tableId || cartStore.orderContext.mode !== 'direct'))

    const contextText = computed(() => {
      const { tableName, tableId, mode } = cartStore.orderContext
      if (tableName) return `当前桌台：${tableName}`
      if (tableId) return `当前桌台：#${tableId}`
      if (mode === 'frontdesk') return '前台代客模式'
      return '店内快速代客点单'
    })

    const currentCategoryId = computed(() => categories.value[activeCategory.value]?.id ?? null)

    const currentCategoryDishes = computed(() => {
      if (currentCategoryId.value == null) return []
      return dishes.value.filter((dish) => Number(dish.category_id) === Number(currentCategoryId.value))
    })

    const normalizeDish = (dish) => ({
      ...dish,
      id: Number(dish.id),
      category_id: Number(dish.category_id ?? 0),
      price: Number(dish.price ?? 0),
      image: resolveImageUrl(dish.image_full_url || dish.image_url || dish.image),
      description: dish.description || ''
    })

    const loadMenu = async () => {
      loading.value = true
      try {
        await ensureWechatAuth()
        const [categoryData, dishData] = await Promise.all([getCategories(0, 200), getDishes(0, 500)])
        if (!alive.value) return
        categories.value = Array.isArray(categoryData) ? categoryData : []
        dishes.value = (Array.isArray(dishData) ? dishData : []).map(normalizeDish)
      } catch (error) {
        if (alive.value) {
          Toast.fail(error?.response?.data?.detail || error.message || '加载菜单失败')
        }
      } finally {
        if (alive.value) {
          loading.value = false
        }
      }
    }

    const handleAddDish = (dish) => {
      const next = cartStore.getDishQuantity(dish.id) + 1
      cartStore.setDishQuantity(dish, next)
      Toast.success(`已加入：${dish.name}`)
    }

    const onImageError = (event) => {
      event.target.src = FALLBACK_IMAGE
    }

    const goCart = () => {
      router.push('/cart')
    }

    onMounted(() => {
      alive.value = true
      cartStore.setContextFromRoute(route.query)
      loadMenu()
    })

    onUnmounted(() => {
      alive.value = false
      loading.value = false
    })

    return {
      loading,
      activeCategory,
      categories,
      currentCategoryDishes,
      cartStore,
      showContext,
      contextText,
      orderTypeLabel,
      handleAddDish,
      onImageError,
      goCart
    }
  }
}
</script>

<style scoped>
.menu {
  padding-bottom: 76px;
}

.context-banner {
  margin: 12px;
  padding: 12px;
  border-radius: 12px;
  background: linear-gradient(110deg, #fff0de 0%, #ffe7cb 100%);
  border: 1px solid #f6d6b3;
  color: #7a431d;
}

.context-main {
  font-weight: 700;
}

.context-sub {
  margin-top: 4px;
  font-size: 12px;
}

.menu-tabs :deep(.van-tabs__nav) {
  background: #fff6ed;
}

.dish-list {
  padding: 12px;
}

.loading {
  display: block;
  text-align: center;
  margin-top: 24px;
}

.dish-card {
  display: flex;
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 14px;
  background: #fffdf9;
  border: 1px solid #f3dfcd;
  box-shadow: 0 10px 20px rgba(141, 74, 28, 0.07);
}

.dish-image {
  width: 84px;
  height: 84px;
  border-radius: 12px;
  object-fit: cover;
  background: #f5eee7;
}

.dish-info {
  flex: 1;
  margin-left: 10px;
}

.dish-name {
  margin: 0;
  font-size: 16px;
}

.dish-desc {
  margin: 6px 0;
  color: #9b775d;
  font-size: 12px;
}

.dish-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dish-price {
  color: #c6511a;
  font-size: 18px;
  font-weight: 700;
}

.add-btn {
  min-width: 94px;
  font-weight: 600;
}

.cart-bar {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: 58px;
  height: 52px;
  border-radius: 26px;
  background: linear-gradient(90deg, #6f3b1f 0%, #8f4b22 45%, #ab5e2a 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  box-shadow: 0 10px 24px rgba(102, 52, 24, 0.35);
}

.bar-left {
  display: flex;
  flex-direction: column;
  font-size: 12px;
}

.bar-count {
  font-size: 14px;
  font-weight: 700;
}

.bar-price {
  font-size: 16px;
  font-weight: 700;
}
</style>
