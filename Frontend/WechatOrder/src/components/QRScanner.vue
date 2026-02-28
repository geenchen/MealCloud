<template>
  <div class="qr-scanner-container">
    <div class="scanner-header">
      <h3>{{ scanMode === 'camera' ? '扫描桌台码' : '输入桌台号' }}</h3>
      <van-button 
        @click="toggleScanMode" 
        size="small" 
        type="primary"
        plain
      >
        {{ scanMode === 'camera' ? '手动输入' : '摄像头扫描' }}
      </van-button>
    </div>

    <!-- 摄像头扫描模式 -->
    <div v-if="scanMode === 'camera'" class="camera-mode">
      <div class="camera-placeholder">
        <van-icon name="scan" size="48" color="#1989fa" />
        <p class="placeholder-text">将摄像头对准桌台二维码</p>
        <p class="placeholder-desc">系统将自动识别桌台信息</p>
      </div>
      
      <div class="camera-actions">
        <van-button 
          @click="simulateQRScan" 
          type="primary" 
          size="large"
          :loading="scanning"
        >
          {{ scanning ? '识别中...' : '模拟扫描' }}
        </van-button>
      </div>
    </div>

    <!-- 手动输入模式 -->
    <div v-else class="manual-mode">
      <van-cell-group inset>
        <van-field
          v-model="tableNumber"
          label="桌台号"
          placeholder="请输入桌台号或扫描结果"
          :border="true"
        />
      </van-cell-group>
      
      <div class="manual-actions">
        <van-button 
          @click="submitTableNumber" 
          type="primary" 
          size="large"
          :disabled="!tableNumber.trim()"
        >
          确认桌台
        </van-button>
      </div>
    </div>

    <!-- 识别结果 -->
    <div v-if="scanResult" class="scan-result">
      <van-card
        :thumb="tableIcon"
        :title="scanResult.table?.name || '前台模式'"
        :desc="scanResult.message"
        :price="scanResult.autoBind ? '已绑定此桌台' : '外带模式'"
        :centered="true"
      >
        <template #footer>
          <van-button 
            size="mini" 
            type="primary"
            @click="proceedWithTable"
          >
            确认并点餐
          </van-button>
        </template>
      </van-card>
    </div>

    <!-- 使用说明 -->
    <div class="instructions">
      <h4>使用说明：</h4>
      <ul>
        <li>扫描桌台二维码自动绑定桌台</li>
        <li>扫描前台码进入外带模式</li>
        <li>可切换至手动输入模式</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { Toast } from 'vant';
import { scanQRCode, getTableQRCodeUrl } from '@/services/qrCodeService';

export default {
  name: 'QRScanner',
  emits: ['table-selected'],
  setup(props, { emit }) {
    const scanMode = ref('camera'); // 'camera' or 'manual'
    const scanning = ref(false);
    const tableNumber = ref('');
    const scanResult = ref(null);
    
    // 模拟二维码扫描（在实际项目中会替换为真实的摄像头扫描）
    const simulateQRScan = async () => {
      scanning.value = true;
      
      try {
        // 模拟扫描延迟
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 模拟扫描结果 - 这里可以替换为真实扫描得到的数据
        // 在实际应用中，这将是通过摄像头扫描获得的二维码内容
        const mockQRData = JSON.stringify({
          type: 'table',
          tableId: 1,
          tableName: '大厅1号桌'
        });
        
        const result = await scanQRCode(mockQRData);
        scanResult.value = result;
        Toast.success(result.message);
      } catch (error) {
        Toast.fail('扫描失败，请重试');
        console.error('扫描失败:', error);
      } finally {
        scanning.value = false;
      }
    };

    // 切换扫描模式
    const toggleScanMode = () => {
      scanMode.value = scanMode.value === 'camera' ? 'manual' : 'camera';
      scanResult.value = null;
      tableNumber.value = '';
    };

    // 提交桌台号（手动模式）
    const submitTableNumber = async () => {
      if (!tableNumber.value.trim()) {
        Toast.fail('请输入桌台号');
        return;
      }

      try {
        // 模拟通过桌台号查询桌台信息
        // 在实际应用中，这会调用API来获取桌台详细信息
        const result = {
          type: 'table',
          table: { 
            id: parseInt(tableNumber.value), 
            name: `桌台${tableNumber.value}`, 
            area: '大厅', 
            capacity: 4,
            table_number: tableNumber.value
          },
          autoBind: true,
          message: `已识别桌台: 桌台${tableNumber.value}`
        };
        
        scanResult.value = result;
        Toast.success(result.message);
      } catch (error) {
        Toast.fail('桌台不存在，请检查桌台号');
      }
    };

    // 确认并继续点餐
    const proceedWithTable = () => {
      if (scanResult.value) {
        emit('table-selected', scanResult.value);
      }
    };

    // 桌台图标
    const tableIcon = 'https://img.yzcdn.cn/vant/table-icon.png';

    return {
      scanMode,
      scanning,
      tableNumber,
      scanResult,
      tableIcon,
      simulateQRScan,
      toggleScanMode,
      submitTableNumber,
      proceedWithTable
    };
  }
};
</script>

<style scoped>
.qr-scanner-container {
  padding: 20px;
  min-height: 100vh;
  background: #f7f8fa;
}

.scanner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.camera-mode {
  text-align: center;
}

.camera-placeholder {
  background: white;
  border-radius: 12px;
  padding: 40px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.placeholder-text {
  margin: 15px 0 5px 0;
  font-size: 16px;
  color: #333;
}

.placeholder-desc {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.camera-actions {
  padding: 0 20px;
}

.manual-mode {
  margin-bottom: 20px;
}

.manual-actions {
  padding: 0 20px;
  margin-top: 20px;
}

.scan-result {
  margin: 20px 0;
}

.instructions {
  background: white;
  padding: 15px;
  border-radius: 12px;
  margin-top: 20px;
}

.instructions h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.instructions ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.instructions li {
  margin-bottom: 5px;
  line-height: 1.4;
}
</style>