<template>
  <div class="cart">
    <van-empty v-if="cartStore.items.length === 0" description="暂存单为空，先去点菜" />

    <van-cell-group v-else title="已选菜品" class="panel">
      <van-cell v-for="item in cartStore.items" :key="item.id">
        <div class="cart-item">
          <img :src="resolveImage(item.image)" class="item-image" @error="onImageError" />
          <div class="item-info">
            <h3>{{ item.name }}</h3>
            <p>¥{{ Number(item.price).toFixed(2) }}</p>
          </div>
          <van-stepper
            :model-value="item.quantity"
            theme="round"
            button-size="22"
            disable-input
            @change="(value) => onQuantityChange(item, value)"
          />
          <div class="item-total">¥{{ (Number(item.price) * Number(item.quantity)).toFixed(2) }}</div>
        </div>
      </van-cell>
    </van-cell-group>

    <div class="footer" v-if="cartStore.items.length > 0">
      <div class="price">合计 ¥{{ cartStore.totalAmount.toFixed(2) }}</div>
      <van-button type="primary" @click="goOrder">确认下单</van-button>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'

const FALLBACK_IMAGE = 'https://img.yzcdn.cn/vant/user-default.png'
const STATIC_BASE = import.meta.env.VITE_FILE_BASE_URL || ''

export default {
  name: 'Cart',
  setup() {
    const router = useRouter()
    const cartStore = useCartStore()

    const resolveImage = (url) => {
      if (!url) return FALLBACK_IMAGE
      if (/^https?:\/\//i.test(url)) return url
      if (url.startsWith('/')) return STATIC_BASE ? `${STATIC_BASE}${url}` : url
      return url
    }

    const onImageError = (event) => {
      event.target.src = FALLBACK_IMAGE
    }

    const onQuantityChange = (item, value) => {
      cartStore.setDishQuantity(item, value)
    }

    const goOrder = () => {
      router.push('/order')
    }

    return {
      cartStore,
      resolveImage,
      onImageError,
      onQuantityChange,
      goOrder
    }
  }
}
</script>

<style scoped>
.cart {
  padding: 12px;
  padding-bottom: 84px;
}

.panel {
  border-radius: 14px;
  overflow: hidden;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-image {
  width: 54px;
  height: 54px;
  border-radius: 10px;
  object-fit: cover;
  background: #f5eee7;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-info h3 {
  margin: 0 0 4px;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-info p {
  margin: 0;
  color: #c6511a;
}

.item-total {
  min-width: 76px;
  text-align: right;
  font-weight: 600;
  color: #c6511a;
}

.footer {
  position: fixed;
  left: 10px;
  right: 10px;
  bottom: 56px;
  background: #fffaf5;
  border: 1px solid #f3dfcd;
  border-radius: 14px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  box-shadow: 0 8px 20px rgba(121, 62, 29, 0.12);
}

.price {
  font-size: 18px;
  font-weight: 700;
  color: #c6511a;
}
</style>
