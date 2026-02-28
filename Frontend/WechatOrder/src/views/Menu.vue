<template>
  <div class="menu">
    <!-- 桌台信息和订单类型显示 -->
    <div v-if="showTableInfo" class="table-info-banner">
      <div class="table-info-content">
        <div class="table-info-left">
          <van-icon name="orders-o" size="20" color="#4361ee" />
          <span class="table-name">{{ tableName }}</span>
        </div>
        <div class="order-type-tag" :class="orderTypeClass">
          {{ orderTypeName }}
        </div>
      </div>
    </div>
    
    <!-- 分类导航 -->
    <van-sticky>
      <van-tabs v-model:active="activeCategory" swipeable @change="onTabChange">
        <van-tab 
          v-for="category in categories" 
          :key="category.id" 
          :title="category.name"
        >
        </van-tab>
      </van-tabs>
    </van-sticky>
    
    <!-- 菜品列表 -->
    <div class="dish-list">
      <div 
        v-for="dish in getCategoryDishes(categories[activeCategory].id)" 
        :key="dish.id" 
        class="dish-card"
      >
        <div class="dish-image-container">
          <img :src="dish.image" class="dish-image" @error="onImageError" />
        </div>
        <div class="dish-info">
          <h3 class="dish-name">{{ dish.name }}</h3>
          <p class="dish-desc">{{ dish.description }}</p>
          <div class="dish-footer">
            <p class="dish-price">¥{{ dish.price }}</p>
            <div class="quantity-controls">
              <van-stepper 
                v-model="dish.quantity" 
                theme="round" 
                button-size="22" 
                disable-input
                @change="(value) => onQuantityChange(dish, value)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Toast } from 'vant'

export default {
  name: 'Menu',
  setup() {
    const route = useRoute();
    const activeCategory = ref(0)
    
    // 从路由参数获取桌台和订单信息
    const tableId = route.query.tableId;
    const tableName = route.query.tableName || (tableId ? `大厅${tableId}号桌` : '未指定桌台');
    const orderType = route.query.orderType || 'dine_in';
    const mode = route.query.mode || 'normal';
    
    // 是否显示桌台信息
    const showTableInfo = computed(() => {
      return tableId || orderType !== 'dine_in' || mode !== 'normal';
    });
    
    // 订单类型名称
    const orderTypeName = computed(() => {
      switch(orderType) {
        case 'dine_in': return '堂食';
        case 'takeaway': return '外带';
        case 'pack': return '打包';
        default: return '堂食';
      }
    });
    
    // 订单类型CSS类
    const orderTypeClass = computed(() => {
      switch(orderType) {
        case 'dine_in': return 'dine-in-tag';
        case 'takeaway': return 'takeaway-tag';
        case 'pack': return 'pack-tag';
        default: return 'dine-in-tag';
      }
    });
    
    const categories = ref([
      { id: 1, name: '热销' },
      { id: 2, name: '主食' },
      { id: 3, name: '热菜' },
      { id: 4, name: '凉菜' },
      { id: 5, name: '汤类' },
      { id: 6, name: '饮品' }
    ])
    
    const dishes = ref([
      { 
        id: 1, 
        name: '宫保鸡丁', 
        description: '经典川菜，鸡肉嫩滑，花生米酥脆', 
        price: 28.00, 
        categoryId: 3,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish1.jpg',
        quantity: 0
      },
      { 
        id: 2, 
        name: '麻婆豆腐', 
        description: '麻辣鲜香，豆腐嫩滑', 
        price: 18.00, 
        categoryId: 3,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish2.jpg',
        quantity: 0
      },
      { 
        id: 3, 
        name: '红烧肉', 
        description: '肥瘦相间，甜咸适中', 
        price: 38.00, 
        categoryId: 3,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish3.jpg',
        quantity: 0
      },
      { 
        id: 4, 
        name: '鱼香肉丝', 
        description: '酸甜可口，下饭神器', 
        price: 26.00, 
        categoryId: 3,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish4.jpg',
        quantity: 0
      },
      { 
        id: 5, 
        name: '拍黄瓜', 
        description: '清爽解腻，开胃小菜', 
        price: 10.00, 
        categoryId: 4,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish5.jpg',
        quantity: 0
      },
      { 
        id: 6, 
        name: '酸辣汤', 
        description: '酸辣开胃，营养丰富', 
        price: 12.00, 
        categoryId: 5,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish6.jpg',
        quantity: 0
      },
      { 
        id: 7, 
        name: '白米饭', 
        description: '优质大米，粒粒分明', 
        price: 2.00, 
        categoryId: 2,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish7.jpg',
        quantity: 0
      },
      { 
        id: 8, 
        name: '可乐', 
        description: '冰爽畅快，解辣必备', 
        price: 5.00, 
        categoryId: 6,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish8.jpg',
        quantity: 0
      },
      // 添加热销分类的菜品
      { 
        id: 9, 
        name: '宫保鸡丁(热销)', 
        description: '最受欢迎的经典川菜', 
        price: 28.00, 
        categoryId: 1,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish1.jpg',
        quantity: 0
      },
      { 
        id: 10, 
        name: '红烧肉(热销)', 
        description: '最受欢迎的经典菜品', 
        price: 38.00, 
        categoryId: 1,
        image: 'https://img.yzcdn.cn/upload_files/2023/08/01/dish3.jpg',
        quantity: 0
      }
    ])
    
    const getCategoryDishes = (categoryId) => {
      return dishes.value.filter(dish => dish.categoryId === categoryId)
    }
    
    const onQuantityChange = (dish, value) => {
      if (value > 0) {
        Toast.success(`已添加 ${dish.name} 到购物车`);
      } else {
        Toast(`已从购物车移除 ${dish.name}`);
      }
    }
    
    const onTabChange = (index) => {
      activeCategory.value = index
    }
    
    const onImageError = (event) => {
      event.target.src = 'https://img.yzcdn.cn/vant/user-default.png'
    }
    
    return {
      activeCategory,
      categories,
      dishes,
      getCategoryDishes,
      onQuantityChange,
      onTabChange,
      onImageError,
      // 新增的响应式变量
      showTableInfo,
      tableName,
      orderTypeName,
      orderTypeClass
    }
  }
}
</script>

<style scoped>
.menu {
  padding-bottom: 60px;
  background: linear-gradient(135deg, #f6f9fc 0%, #e9ecef 100%);
  min-height: 100vh;
}

/* 桌台信息横幅样式 */
.table-info-banner {
  background: linear-gradient(90deg, #4361ee, #3a0ca3);
  color: white;
  padding: 12px 15px;
  box-shadow: 0 2px 10px rgba(67, 97, 238, 0.3);
}

.table-info-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-info-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-name {
  font-size: 16px;
  font-weight: 500;
}

.order-type-tag {
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.dine-in-tag {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.takeaway-tag {
  background-color: rgba(255, 193, 7, 0.3);
  color: white;
}

.pack-tag {
  background-color: rgba(13, 202, 240, 0.3);
  color: white;
}

/* Vant Tabs样式覆盖 */
:deep(.van-tabs__nav) {
  background: linear-gradient(90deg, #4361ee, #3f37c9);
  border-radius: 0 0 20px 20px;
  box-shadow: 0 4px 15px rgba(67, 97, 238, 0.25);
}

:deep(.van-tab) {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  position: relative;
}

:deep(.van-tab--active) {
  color: white;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin: 5px;
}

:deep(.van-tabs__line) {
  background: white;
  height: 3px;
  border-radius: 2px;
}

.dish-list {
  padding: 15px;
}

.dish-card {
  display: flex;
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  margin-bottom: 15px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(168, 180, 208, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.8);
  position: relative;
}

.dish-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4361ee, #3f37c9);
}

.dish-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(168, 180, 208, 0.3);
  background: linear-gradient(145deg, #ffffff, #f5f7ff);
}

.category-title {
  background: linear-gradient(145deg, #4361ee, #3f37c9);
  backdrop-filter: blur(10px);
  padding: 15px 20px;
  margin: 15px 0 10px 0;
  border-radius: 12px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  box-shadow: 0 4px 15px rgba(67, 97, 238, 0.2);
  border: none;
  text-align: center;
  font-size: 18px;
  letter-spacing: 0.5px;
}

.dish-image-container {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.dish-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.dish-card:hover .dish-image {
  transform: scale(1.05);
}

.dish-info {
  flex: 1;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: linear-gradient(to right, rgba(255,255,255,0.95), rgba(248, 249, 255, 0.8));
}

.dish-name {
  font-size: 17px;
  font-weight: 700;
  color: #2b2d42;
  margin-bottom: 8px;
  letter-spacing: 0.3px;
  text-shadow: 0 0.5px 1px rgba(0, 0, 0, 0.05);
}

.dish-description {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 12px;
  line-height: 1.5;
}

.dish-price {
  font-size: 20px;
  font-weight: 800;
  color: #4361ee;
  margin-bottom: 12px;
  text-shadow: 0 1px 2px rgba(67, 97, 238, 0.15);
}

.add-button {
  align-self: flex-end;
}

.dish-name {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 500;
}

.dish-desc {
  font-size: 12px;
  color: #969799;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.dish-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dish-price {
  color: #ee0a24;
  font-weight: bold;
  margin: 0;
}

.quantity-controls {
  display: flex;
  align-items: center;
}
</style>