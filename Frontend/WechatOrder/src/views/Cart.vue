<template>
  <div class="cart">
    <van-cell-group title="购物车">
      <van-cell v-for="item in cartItems" :key="item.id" :border="false">
        <div class="cart-item">
          <div class="item-info">
            <h3>{{ item.name }}</h3>
            <p class="item-price">¥{{ item.price }}</p>
          </div>
          <div class="quantity-controls">
            <van-stepper 
              v-model="item.quantity" 
              theme="round" 
              button-size="22" 
              disable-input
              @change="(value) => updateQuantity(item, value)"
            />
          </div>
          <p class="item-total">¥{{ (item.price * item.quantity).toFixed(2) }}</p>
        </div>
      </van-cell>
    </van-cell-group>

    <div class="cart-footer">
      <div class="total-info">
        <p>总计: <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span></p>
      </div>
      <van-button 
        type="primary" 
        size="large" 
        :disabled="cartItems.length === 0"
        @click="proceedToCheckout"
      >
        去结算
      </van-button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { Toast } from 'vant'

export default {
  name: 'Cart',
  setup() {
    const cartItems = ref([
      { id: 1, name: '宫保鸡丁', price: 28.00, quantity: 1 },
      { id: 2, name: '白米饭', price: 2.00, quantity: 2 }
    ])

    const totalPrice = computed(() => {
      return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    })

    const updateQuantity = (item, value) => {
      if (value === 0) {
        // 如果数量变为0，则从购物车中移除该项目
        const index = cartItems.value.indexOf(item)
        if (index > -1) {
          cartItems.value.splice(index, 1)
        }
      }
      Toast(`已更新 ${item.name} 数量为 ${value}`)
    }

    const proceedToCheckout = () => {
      Toast('跳转到结算页面')
    }

    return {
      cartItems,
      totalPrice,
      updateQuantity,
      proceedToCheckout
    }
  }
}
</script>

<style scoped>
.cart-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f5f5f5;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: normal;
}

.item-price {
  color: #ee0a24;
  font-weight: bold;
  margin: 0;
}

.quantity-controls {
  margin: 0 15px;
}

.item-total {
  font-weight: bold;
  color: #ee0a24;
  min-width: 60px;
  text-align: right;
}

.cart-footer {
  position: fixed;
  bottom: 50px; /* 为底部导航栏留出空间 */
  left: 0;
  right: 0;
  padding: 15px;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}

.total-info {
  margin-bottom: 10px;
  text-align: right;
}

.total-price {
  font-size: 18px;
  color: #ee0a24;
  font-weight: bold;
}
</style>