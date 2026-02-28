<template>
  <div class="profile">
    <!-- 用户信息卡片 -->
    <van-cell-group>
      <van-cell class="user-info-cell" :border="false">
        <template #default>
          <div class="user-info">
            <van-image 
              round 
              width="60" 
              height="60" 
              src="https://img.yzcdn.cn/vant/cat.jpeg"
              class="avatar"
            />
            <div class="user-details">
              <h3 class="username">张三</h3>
              <p class="phone">138****8888</p>
            </div>
          </div>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 功能列表 -->
    <van-cell-group style="margin-top: 10px;">
      <van-cell title="我的订单" icon="orders-o" is-link @click="goToOrderHistory" />
      <van-cell title="优惠券" icon="coupon-o" is-link @click="goToCoupons" />
      <van-cell title="地址管理" icon="location-o" is-link @click="goToAddress" />
      <van-cell title="会员中心" icon="vip-card-o" is-link @click="goToVipCenter" />
      <van-cell title="帮助与反馈" icon="service-o" is-link @click="goToHelp" />
      <van-cell title="关于我们" icon="info-o" is-link @click="goToAbout" />
    </van-cell-group>

    <!-- 退出登录按钮 -->
    <div class="logout-section">
      <van-button 
        type="danger" 
        size="large" 
        @click="logout"
      >
        退出登录
      </van-button>
    </div>
  </div>
</template>

<script>
import { Toast } from 'vant'

export default {
  name: 'Profile',
  setup() {
    const goToOrderHistory = () => {
      Toast('跳转到订单历史');
    }

    const goToCoupons = () => {
      Toast('跳转到优惠券');
    }

    const goToAddress = () => {
      Toast('跳转到地址管理');
    }

    const goToVipCenter = () => {
      Toast('跳转到会员中心');
    }

    const goToHelp = () => {
      Toast('跳转到帮助与反馈');
    }

    const goToAbout = () => {
      Toast('跳转到关于我们');
    }

    const logout = () => {
      Toast('已退出登录');
    }

    return {
      goToOrderHistory,
      goToCoupons,
      goToAddress,
      goToVipCenter,
      goToHelp,
      goToAbout,
      logout
    }
  }
}
</script>

<style scoped>
.user-info-cell {
  padding: 20px 16px;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  margin-right: 15px;
}

.user-details {
  flex: 1;
}

.username {
  margin: 0 0 5px 0;
  font-size: 18px;
  font-weight: bold;
}

.phone {
  margin: 0;
  color: #969799;
  font-size: 14px;
}

.logout-section {
  margin: 20px 16px;
}

.van-cell-group {
  margin-bottom: 10px;
}
</style>