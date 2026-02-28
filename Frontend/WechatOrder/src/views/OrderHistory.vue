<template>
  <div class="order-history">
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab name="all" title="全部">
        <van-list>
          <van-cell 
            v-for="order in orders" 
            :key="order.id" 
            :title="`订单号: ${order.id}`"
            :label="`下单时间: ${order.date}`"
            is-link
            @click="viewOrder(order)"
          >
            <template #value>
              <van-tag :type="getStatusType(order.status)">{{ order.status }}</van-tag>
              <div class="order-price">¥{{ order.totalPrice }}</div>
            </template>
          </van-cell>
        </van-list>
      </van-tab>
      <van-tab name="pending" title="待付款">
        <van-empty description="暂无待付款订单" v-if="pendingOrders.length === 0" />
        <van-list v-else>
          <van-cell 
            v-for="order in pendingOrders" 
            :key="order.id" 
            :title="`订单号: ${order.id}`"
            :label="`下单时间: ${order.date}`"
            is-link
            @click="viewOrder(order)"
          >
            <template #value>
              <van-tag :type="getStatusType(order.status)">{{ order.status }}</van-tag>
              <div class="order-price">¥{{ order.totalPrice }}</div>
            </template>
          </van-cell>
        </van-list>
      </van-tab>
      <van-tab name="completed" title="已完成">
        <van-empty description="暂无已完成订单" v-if="completedOrders.length === 0" />
        <van-list v-else>
          <van-cell 
            v-for="order in completedOrders" 
            :key="order.id" 
            :title="`订单号: ${order.id}`"
            :label="`下单时间: ${order.date}`"
            is-link
            @click="viewOrder(order)"
          >
            <template #value>
              <van-tag :type="getStatusType(order.status)">{{ order.status }}</van-tag>
              <div class="order-price">¥{{ order.totalPrice }}</div>
            </template>
          </van-cell>
        </van-list>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { Toast } from 'vant'

export default {
  name: 'OrderHistory',
  setup() {
    const activeTab = ref('all')

    const orders = ref([
      { 
        id: '#001', 
        date: '2023-10-01 10:30', 
        status: '已完成', 
        totalPrice: 32.00,
        items: [
          { name: '宫保鸡丁', price: 28.00, quantity: 1 },
          { name: '白米饭', price: 2.00, quantity: 2 }
        ]
      },
      { 
        id: '#002', 
        date: '2023-10-01 11:15', 
        status: '已完成', 
        totalPrice: 56.00,
        items: [
          { name: '麻婆豆腐', price: 18.00, quantity: 1 },
          { name: '红烧肉', price: 38.00, quantity: 1 }
        ]
      },
      { 
        id: '#003', 
        date: '2023-10-02 12:20', 
        status: '待付款', 
        totalPrice: 38.00,
        items: [
          { name: '鱼香肉丝', price: 26.00, quantity: 1 },
          { name: '酸辣汤', price: 12.00, quantity: 1 }
        ]
      },
      { 
        id: '#004', 
        date: '2023-10-02 14:30', 
        status: '制作中', 
        totalPrice: 86.00,
        items: [
          { name: '红烧肉', price: 38.00, quantity: 2 },
          { name: '可乐', price: 5.00, quantity: 2 }
        ]
      }
    ])

    const pendingOrders = computed(() => {
      return orders.value.filter(order => order.status === '待付款')
    })

    const completedOrders = computed(() => {
      return orders.value.filter(order => order.status === '已完成')
    })

    const getStatusType = (status) => {
      switch(status) {
        case '待付款':
        case '制作中':
          return 'warning'
        case '已完成':
          return 'success'
        case '已取消':
          return 'danger'
        default:
          return 'info'
      }
    }

    const viewOrder = (order) => {
      Toast(`查看订单详情: ${order.id}`)
    }

    return {
      activeTab,
      orders,
      pendingOrders,
      completedOrders,
      getStatusType,
      viewOrder
    }
  }
}
</script>

<style scoped>
.order-price {
  margin-top: 5px;
  text-align: right;
  font-weight: bold;
  color: #ee0a24;
}
</style>