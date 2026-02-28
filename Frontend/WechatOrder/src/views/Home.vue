<template>
  <div class="home">
    <van-nav-bar 
      :title="navbarTitle" 
      fixed 
      placeholder 
      v-if="!isTableMode"
    />
    
    <!-- 场景1：桌台扫码模式 - 显示桌台信息 -->
    <div v-if="isTableMode" class="table-mode-header">
      <div class="table-welcome">
        <h2>🍽️ 欢迎光临</h2>
        <p class="table-info">{{ tableInfo }}</p>
      </div>
    </div>
    
    <div class="home-content">
      <!-- 场景2：前台扫码/公众号进入 - 就餐方式选择 -->
      <div v-if="showDiningOptions" class="dining-options">
        <h3 class="options-title">请选择就餐方式</h3>
        <div class="option-buttons">
          <van-button 
            icon="orders-o" 
            type="primary" 
            size="large" 
            class="dining-option-btn"
            @click="selectDiningOption('dine_in')"
          >
            🍽️ 堂食
          </van-button>
          <van-button 
            icon="tosend" 
            type="warning" 
            size="large" 
            class="dining-option-btn"
            @click="selectDiningOption('takeaway')"
          >
            🥡 外带
          </van-button>
          <van-button 
            icon="photo-o" 
            type="info" 
            size="large" 
            class="dining-option-btn"
            @click="selectDiningOption('pack')"
          >
            📦 打包
          </van-button>
        </div>
      </div>
      
      <!-- 场景3：老板代客下单 - 快捷点餐面板 -->
      <div v-if="showQuickOrderPanel" class="quick-order-panel">
        <h3 class="panel-title">老板代客下单</h3>
        <div class="order-controls">
          <van-button 
            type="primary" 
            size="large" 
            @click="proceedToMenuWithoutTable"
          >
            开始点菜
          </van-button>
        </div>
      </div>
      
      <!-- 默认视图：保留原有功能 -->
      <div v-if="showDefaultView" class="default-view">
        <!-- 餐厅信息 -->
        <div class="restaurant-info">
          <h1>欢迎光临</h1>
          <p>美味餐厅</p>
        </div>

        <!-- 桌台选择选项 -->
        <div class="table-options">
          <van-grid :column-num="2" :border="false">
            <van-grid-item 
              icon="scan" 
              text="扫码点餐" 
              @click="showScanner = true"
            />
            <van-grid-item 
              icon="orders-o" 
              text="直接点餐" 
              @click="proceedToMenuWithoutTable"
            />
          </van-grid>
        </div>

        <!-- 当前桌台信息 -->
        <div v-if="currentTable" class="current-table">
          <van-card
            :thumb="tableIcon"
            :title="currentTable.name"
            :desc="`区域: ${currentTable.area} | 容量: ${currentTable.capacity}人`"
            centered
          >
            <template #footer>
              <van-button size="mini" type="danger" @click="clearTable">
                更换桌台
              </van-button>
            </template>
          </van-card>
        </div>

        <!-- 主要操作按钮 -->
        <div class="main-actions">
          <van-button 
            type="primary" 
            size="large" 
            :disabled="!canProceedToMenu"
            @click="proceedToMenu"
          >
            {{ currentTable ? '进入菜单点餐' : '选择模式点餐' }}
          </van-button>
          <div class="mode-options" v-if="!currentTable">
            <p>或选择点餐模式:</p>
            <van-grid :column-num="3" :border="false" style="margin-top: 10px;">
              <van-grid-item 
                text="堂食" 
                @click="proceedToMenuWithMode('dine_in')"
              />
              <van-grid-item 
                text="外带" 
                @click="proceedToMenuWithMode('takeaway')"
              />
              <van-grid-item 
                text="打包" 
                @click="proceedToMenuWithMode('pack')"
              />
            </van-grid>
          </div>
        </div>
      </div>
    </div>

    <!-- QR扫描弹窗 -->
    <van-popup 
      v-model:show="showScanner" 
      position="bottom" 
      :style="{ height: '80%' }"
      :round="true"
    >
      <div class="popup-header">
        <h3>桌台扫描</h3>
        <van-button 
          icon="close" 
          type="default" 
          size="small" 
          @click="showScanner = false"
        />
      </div>
      <QRScanner @table-selected="handleTableSelected" />
    </van-popup>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Toast, showConfirmDialog } from 'vant';
import QRScanner from '@/components/QRScanner.vue';

export default {
  name: 'Home',
  components: {
    QRScanner
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const showScanner = ref(false);
    const currentTable = ref(null);
    const showDiningOptions = ref(false);
    const showQuickOrderPanel = ref(false);
    const showDefaultView = ref(true);
    const isTableMode = ref(false);
    const tableInfo = ref('');
    
    // 检测URL参数并决定显示哪个场景
    onMounted(() => {
      const { tableId, tableName, from, mode } = route.query;
      
      // 场景1：桌台扫码（包含tableId参数）
      if (tableId) {
        isTableMode.value = true;
        showDefaultView.value = false;
        tableInfo.value = `${tableName || `大厅${tableId}号桌`} · 2人用餐`;
        
        // 自动跳转到菜单页面，传递桌台信息
        setTimeout(() => {
          router.push({ 
            path: '/menu', 
            query: { 
              tableId: tableId, 
              tableName: tableName || `大厅${tableId}号桌`,
              orderType: 'dine_in',
              mode: 'table_scan'
            } 
          });
        }, 1500); // 短暂显示欢迎信息
        
        return;
      }
      
      // 场景2：前台扫码/公众号进入
      if (from === 'frontdesk' || mode === 'frontdesk') {
        showDiningOptions.value = true;
        showDefaultView.value = false;
        return;
      }
      
      // 场景3：老板代客下单
      if (mode === 'admin' || mode === 'agent') {
        showQuickOrderPanel.value = true;
        showDefaultView.value = false;
        return;
      }
      
      // 默认场景：保留原有功能
      showDefaultView.value = true;
    });

    // 计算属性：是否可以进入菜单
    const canProceedToMenu = computed(() => {
      return !!currentTable.value || currentTable.value === 'frontdesk'; // 允许前台模式
    });
    
    // 导航栏标题
    const navbarTitle = computed(() => {
      if (isTableMode.value) {
        return '正在进入餐桌';
      }
      return '餐厅点餐';
    });

    // 处理扫描结果
    const handleTableSelected = (result) => {
      if (result.type === 'table' && result.autoBind) {
        currentTable.value = result.table;
        Toast.success(result.message);
        showScanner.value = false;
      } else if (result.type === 'frontdesk') {
        currentTable.value = 'frontdesk'; // 前台模式
        Toast.success(result.message);
        showScanner.value = false;
      }
    };

    // 清除当前桌台选择
    const clearTable = () => {
      currentTable.value = null;
      Toast.info('已清除桌台选择');
    };

    // 就餐方式选择
    const selectDiningOption = (option) => {
      let orderType, mode;
      
      switch(option) {
        case 'dine_in':
          orderType = 'dine_in';
          mode = 'dine_in';
          break;
        case 'takeaway':
          orderType = 'takeaway';
          mode = 'takeaway';
          break;
        case 'pack':
          orderType = 'pack';
          mode = 'pack';
          break;
        default:
          orderType = 'dine_in';
          mode = 'dine_in';
      }
      
      // 跳转到菜单页面
      router.push({ 
        path: '/menu', 
        query: { 
          orderType: orderType,
          mode: mode
        } 
      });
    };

    // 进入菜单（有桌台）
    const proceedToMenu = () => {
      if (!canProceedToMenu.value) {
        // If no table is selected, prompt user to choose a mode
        showConfirmDialog({
          title: '点餐模式',
          message: '请选择点餐模式',
          actions: [
            { name: '堂食', value: 'dine_in' },
            { name: '外带', value: 'takeaway' },
            { name: '打包', value: 'pack' }
          ],
          showCancelButton: true
        }).then(action => {
          // 跳转到菜单页面，传递订单类型参数
          router.push({ 
            path: '/menu', 
            query: { 
              orderType: action.value || action,
              mode: 'direct'
            } 
          });
        }).catch(() => {
          // 用户取消选择
          Toast.info('已取消选择');
        });
        return;
      }
      
      // 跳转到菜单页面，传递桌台信息
      if (currentTable.value === 'frontdesk') {
        // 前台模式，外带订单
        router.push({ 
          path: '/menu', 
          query: { orderType: 'takeaway', mode: 'frontdesk' } 
        });
      } else {
        // 桌台模式
        router.push({ 
          path: '/menu', 
          query: { 
            tableId: currentTable.value?.id, 
            orderType: 'dine_in',
            tableName: currentTable.value?.name 
          } 
        });
      }
    };

    // 直接选择模式进入菜单
    const proceedToMenuWithMode = (mode) => {
      router.push({ 
        path: '/menu', 
        query: { 
          orderType: mode,
          mode: 'direct'
        } 
      });
    };

    // 直接点餐（不选择桌台）
    const proceedToMenuWithoutTable = () => {
      // 跳转到菜单页面，默认为堂食模式
      router.push({ 
        path: '/menu', 
        query: { 
          orderType: 'dine_in',
          mode: 'direct'
        } 
      });
    };

    // 桌台图标
    const tableIcon = 'https://img.yzcdn.cn/vant/table-icon.png';

    return {
      showScanner,
      currentTable,
      canProceedToMenu,
      showDiningOptions,
      showQuickOrderPanel,
      showDefaultView,
      isTableMode,
      tableInfo,
      navbarTitle,
      tableIcon,
      handleTableSelected,
      clearTable,
      selectDiningOption,
      proceedToMenu,
      proceedToMenuWithMode,
      proceedToMenuWithoutTable
    };
  }
};
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.home-content {
  padding: 60px 20px 20px;
  min-height: calc(100vh - 60px);
}

.table-mode-header {
  background: linear-gradient(90deg, #4361ee, #3f37c9);
  color: white;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.table-welcome h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.table-info {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
}

.dining-options {
  padding: 30px 20px;
  text-align: center;
}

.options-title {
  font-size: 22px;
  color: #333;
  margin-bottom: 30px;
}

.option-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.dining-option-btn {
  margin-bottom: 10px;
  height: 60px;
  font-size: 18px;
}

.quick-order-panel {
  padding: 30px 20px;
  text-align: center;
}

.panel-title {
  font-size: 22px;
  color: #333;
  margin-bottom: 30px;
}

.order-controls {
  padding: 0 20px;
}

.restaurant-info {
  text-align: center;
  margin: 30px 0;
}

.restaurant-info h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.restaurant-info p {
  font-size: 16px;
  color: #666;
}

.table-options {
  margin: 30px 0;
}

.current-table {
  margin: 20px 0;
}

.main-actions {
  margin-top: 40px;
  padding: 0 20px;
}

.mode-options {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.mode-options p {
  margin: 0 0 10px 0;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.popup-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}
</style>