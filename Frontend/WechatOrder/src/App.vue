<template>
  <van-nav-bar 
    :title="title" 
    :left-arrow="showBackButton" 
    @click-left="goBack"
    v-if="!hideNavBar"
  />
  <div class="app-container">
    <router-view />
  </div>
  
  <van-tabbar v-model="activeTab" v-if="showTabBar" @change="onTabChange">
    <van-tabbar-item name="home" icon="home-o">首页</van-tabbar-item>
    <van-tabbar-item name="menu" icon="orders-o">菜单</van-tabbar-item>
    <van-tabbar-item name="cart" icon="cart-o" :badge="cartCount > 0 ? cartCount : undefined">购物车</van-tabbar-item>
    <van-tabbar-item name="profile" icon="user-o">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const activeTab = ref('home')
    
    // 从 Pinia 获取购物车状态（这里暂时用模拟数据）
    const cartItems = ref([
      { id: 1, name: '宫保鸡丁', price: 28.00, quantity: 1 },
      { id: 2, name: '白米饭', price: 2.00, quantity: 2 }
    ])
    
    const title = computed(() => {
      const titles = {
        '/': '餐厅首页',
        '/menu': '菜品列表',
        '/cart': '购物车',
        '/profile': '个人中心',
        '/order': '提交订单',
        '/order-history': '订单历史'
      }
      return titles[route.path] || '餐饮系统'
    })
    
    const hideNavBar = computed(() => {
      return route.path === '/login' || route.path === '/register'
    })
    
    const showBackButton = computed(() => {
      return !['/', '/menu', '/cart', '/profile'].includes(route.path) && !hideNavBar.value
    })
    
    const showTabBar = computed(() => {
      return ['/', '/menu', '/cart', '/profile'].includes(route.path) && !hideNavBar.value
    })
    
    const cartCount = computed(() => {
      return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
    })
    
    const goBack = () => {
      router.go(-1)
    }
    
    const onTabChange = (name) => {
      const tabRoutes = {
        home: '/',
        menu: '/menu',
        cart: '/cart',
        profile: '/profile'
      }
      router.push(tabRoutes[name])
    }
    
    watch(route, (newRoute) => {
      if (newRoute.path === '/') activeTab.value = 'home'
      else if (newRoute.path === '/menu') activeTab.value = 'menu'
      else if (newRoute.path === '/cart') activeTab.value = 'cart'
      else if (newRoute.path === '/profile') activeTab.value = 'profile'
    }, { immediate: true })
    
    return {
      activeTab,
      title,
      hideNavBar,
      showBackButton,
      showTabBar,
      cartCount,
      goBack,
      onTabChange
    }
  }
}
</script>

<style>
#app {
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2b2d42;
  padding-bottom: 50px;
  background: linear-gradient(135deg, #f6f9fc 0%, #e9ecef 100%);
  min-height: 100vh;
}

.app-container {
  min-height: calc(100vh - 46px);
  background: transparent;
}

.van-nav-bar {
  background: linear-gradient(90deg, #4361ee, #3f37c9);
  color: white;
  border: none;
  box-shadow: 0 4px 15px rgba(67, 97, 238, 0.3);
}

.van-nav-bar__title {
  color: white;
  font-weight: 600;
  font-size: 18px;
  letter-spacing: 0.5px;
}

.van-nav-bar__arrow {
  color: white;
  font-size: 20px;
}

.van-tabbar {
  background: linear-gradient(90deg, #4361ee, #3f37c9);
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 -4px 15px rgba(67, 97, 238, 0.2);
}

.van-tabbar-item {
  color: rgba(255, 255, 255, 0.85);
  background: transparent;
}

.van-tabbar-item--active {
  color: white;
  font-weight: 700;
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 5px 10px;
}

.van-tabbar-item__icon {
  font-size: 22px;
}

/*底固定元素样式 */
.fixed-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
</style>