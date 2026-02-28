<template>
  <div class="special-functions">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="今日特价" name="daily-specials">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>设置今日特价菜品</span>
              <el-button type="primary" @click="addDailySpecial">添加特价菜</el-button>
            </div>
          </template>
          
          <el-table :data="dailySpecials" style="width: 100%" stripe>
            <el-table-column prop="dishName" label="菜品名称" width="200" />
            <el-table-column prop="originalPrice" label="原价" width="100">
              <template #default="scope">¥{{ scope.row.originalPrice }}</template>
            </el-table-column>
            <el-table-column prop="specialPrice" label="特价" width="100">
              <template #default="scope">
                <el-input-number 
                  v-model="scope.row.specialPrice" 
                  :min="0.01" 
                  :max="scope.row.originalPrice" 
                  :step="0.01"
                  size="small"
                  @change="updateDailySpecial(scope.row)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="discountRate" label="折扣率" width="100">
              <template #default="scope">
                {{ ((scope.row.specialPrice / scope.row.originalPrice) * 10).toFixed(1) }}折
              </template>
            </el-table-column>
            <el-table-column prop="startDate" label="开始时间" width="150" />
            <el-table-column prop="endDate" label="结束时间" width="150" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="danger" @click="removeDailySpecial(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="沽清管理" name="out-of-stock">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>设置沽清菜品</span>
            </div>
          </template>
          
          <el-table :data="outOfStockDishes" style="width: 100%" stripe>
            <el-table-column prop="dishName" label="菜品名称" width="200" />
            <el-table-column prop="reason" label="沽清原因" width="200">
              <template #default="scope">
                <el-select 
                  v-model="scope.row.reason" 
                  placeholder="选择沽清原因"
                  size="small"
                  @change="updateOutOfStock(scope.row)"
                >
                  <el-option label="原料不足" value="原料不足" />
                  <el-option label="设备故障" value="设备故障" />
                  <el-option label="人员不足" value="人员不足" />
                  <el-option label="其他" value="其他" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="estimatedRestock" label="预计补货时间" width="150">
              <template #default="scope">
                <el-date-picker
                  v-model="scope.row.estimatedRestock"
                  type="datetime"
                  placeholder="选择时间"
                  size="small"
                  @change="updateOutOfStock(scope.row)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="note" label="备注">
              <template #default="scope">
                <el-input 
                  v-model="scope.row.note" 
                  size="small"
                  @input="updateOutOfStock(scope.row)"
                  placeholder="添加备注"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="restoreDish(scope.row.id)">恢复</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div style="margin-top: 20px;">
            <el-button type="primary" @click="showAddOutOfStockDialog = true">添加沽清菜品</el-button>
          </div>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="赊账管理" name="credit-management">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>赊账客户管理</span>
              <el-button type="primary" @click="addCreditCustomer">添加客户</el-button>
            </div>
          </template>
          
          <el-table :data="creditCustomers" style="width: 100%" stripe>
            <el-table-column prop="name" label="客户姓名" width="120" />
            <el-table-column prop="phone" label="联系电话" width="150" />
            <el-table-column prop="creditLimit" label="信用额度" width="120">
              <template #default="scope">¥{{ scope.row.creditLimit }}</template>
            </el-table-column>
            <el-table-column prop="currentBalance" label="当前欠款" width="120">
              <template #default="scope">
                <span :class="scope.row.currentBalance > scope.row.creditLimit ? 'overdue' : ''">
                  ¥{{ scope.row.currentBalance }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="lastTransactionDate" label="最后交易" width="150" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
                  {{ scope.row.status === 'active' ? '正常' : '暂停' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="viewCreditDetails(scope.row)">详情</el-button>
                <el-button size="small" type="primary" @click="recordPayment(scope.row)">记账/还款</el-button>
                <el-button 
                  size="small" 
                  :type="scope.row.status === 'active' ? 'warning' : 'success'"
                  @click="toggleCreditStatus(scope.row)"
                >
                  {{ scope.row.status === 'active' ? '暂停' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="预约管理" name="reservations">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>预约订单管理</span>
              <el-button type="primary" @click="showAddReservationDialog = true">新增预约</el-button>
            </div>
          </template>
          
          <el-table :data="reservations" style="width: 100%" stripe>
            <el-table-column prop="customerName" label="客户姓名" width="120" />
            <el-table-column prop="customerPhone" label="联系电话" width="150" />
            <el-table-column prop="tableNumber" label="预约桌台" width="120" />
            <el-table-column prop="reservationTime" label="预约时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.reservationTime) }}
              </template>
            </el-table-column>
            <el-table-column prop="peopleCount" label="人数" width="80" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getReservationStatusType(scope.row.status)">
                  {{ getReservationStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="confirmReservation(scope.row)">确认</el-button>
                <el-button size="small" type="warning" @click="modifyReservation(scope.row)">修改</el-button>
                <el-button size="small" type="danger" @click="cancelReservation(scope.row)">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="手写单录入" name="handwritten-orders">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>手写单据录入</span>
              <el-button type="primary" @click="addHandwrittenOrder">新建单据</el-button>
            </div>
          </template>
          
          <el-form :model="handwrittenOrder" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="客户姓名">
                  <el-input v-model="handwrittenOrder.customerName" placeholder="请输入客户姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="handwrittenOrder.customerPhone" placeholder="请输入联系电话" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="订单类型">
              <el-radio-group v-model="handwrittenOrder.orderType">
                <el-radio label="dine_in">堂食</el-radio>
                <el-radio label="takeaway">外带</el-radio>
                <el-radio label="pack">打包</el-radio>
                <el-radio label="credit">赊账</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="订单菜品">
              <el-table :data="handwrittenOrder.items" style="width: 100%" max-height="300">
                <el-table-column prop="dishName" label="菜品名称" width="200">
                  <template #default="scope">
                    <el-input 
                      v-model="scope.row.dishName" 
                      size="small"
                      placeholder="输入菜品名"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="unitPrice" label="单价" width="120">
                  <template #default="scope">
                    <el-input-number 
                      v-model="scope.row.unitPrice" 
                      :min="0.01" 
                      :step="0.01"
                      size="small"
                      placeholder="单价"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="quantity" label="数量" width="100">
                  <template #default="scope">
                    <el-input-number 
                      v-model="scope.row.quantity" 
                      :min="1" 
                      size="small"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="totalPrice" label="小计" width="120">
                  <template #default="scope">
                    ¥{{ (scope.row.unitPrice * scope.row.quantity).toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="scope">
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="removeOrderItem(scope.$index)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div style="margin-top: 10px;">
                <el-button size="small" @click="addOrderItem">+ 添加菜品</el-button>
              </div>
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="小计">
                  <el-input v-model="handwrittenOrder.subtotal" readonly />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="总计">
                  <el-input v-model="handwrittenOrder.totalAmount" readonly style="color: #f56c6c; font-weight: bold;" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="支付信息">
              <el-radio-group v-model="handwrittenOrder.paymentInfo.method">
                <el-radio label="cash">现金</el-radio>
                <el-radio label="wechat">微信</el-radio>
                <el-radio label="alipay">支付宝</el-radio>
                <el-radio label="mixed">混合支付</el-radio>
                <el-radio label="credit">赊账</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-row :gutter="20" v-if="handwrittenOrder.paymentInfo.method === 'mixed'">
              <el-col :span="8">
                <el-form-item label="现金支付">
                  <el-input-number 
                    v-model="handwrittenOrder.paymentInfo.cashAmount" 
                    :min="0" 
                    :step="0.01"
                    size="small"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="微信支付">
                  <el-input-number 
                    v-model="handwrittenOrder.paymentInfo.wechatAmount" 
                    :min="0" 
                    :step="0.01"
                    size="small"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="支付宝支付">
                  <el-input-number 
                    v-model="handwrittenOrder.paymentInfo.alipayAmount" 
                    :min="0" 
                    :step="0.01"
                    size="small"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="备注">
              <el-input 
                v-model="handwrittenOrder.notes" 
                type="textarea" 
                :rows="3"
                placeholder="请输入备注信息"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveHandwrittenOrder">保存订单</el-button>
              <el-button @click="resetHandwrittenOrder">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 添加沽清菜品对话框 -->
    <el-dialog v-model="showAddOutOfStockDialog" title="添加沽清菜品" width="500px">
      <el-form :model="newOutOfStock" label-width="100px">
        <el-form-item label="菜品选择">
          <el-select v-model="newOutOfStock.dishId" placeholder="请选择菜品" style="width: 100%;">
            <el-option 
              v-for="dish in availableDishes" 
              :key="dish.id" 
              :label="dish.name" 
              :value="dish.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="沽清原因">
          <el-select v-model="newOutOfStock.reason" placeholder="请选择原因" style="width: 100%;">
            <el-option label="原料不足" value="原料不足" />
            <el-option label="设备故障" value="设备故障" />
            <el-option label="人员不足" value="人员不足" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="预计补货时间">
          <el-date-picker
            v-model="newOutOfStock.estimatedRestock"
            type="datetime"
            placeholder="选择时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            v-model="newOutOfStock.note" 
            type="textarea" 
            :rows="3"
            placeholder="添加备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddOutOfStockDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmAddOutOfStock">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 赊账详情对话框 -->
    <el-dialog v-model="showCreditDetailsDialog" title="客户赊账详情" width="700px">
      <div v-if="selectedCreditCustomer">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户姓名">{{ selectedCreditCustomer.name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ selectedCreditCustomer.phone }}</el-descriptions-item>
          <el-descriptions-item label="信用额度">¥{{ selectedCreditCustomer.creditLimit }}</el-descriptions-item>
          <el-descriptions-item label="当前欠款" :span="1">
            <span :class="selectedCreditCustomer.currentBalance > selectedCreditCustomer.creditLimit ? 'overdue' : ''">
              ¥{{ selectedCreditCustomer.currentBalance }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="账户状态">
            <el-tag :type="selectedCreditCustomer.status === 'active' ? 'success' : 'info'">
              {{ selectedCreditCustomer.status === 'active' ? '正常' : '暂停' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="加入日期">{{ selectedCreditCustomer.joinDate }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin: 20px 0 10px;">交易记录：</h4>
        <el-table :data="selectedCreditCustomer.transactions" style="width: 100%" max-height="300">
          <el-table-column prop="date" label="日期" width="150" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="amount" label="金额" width="100">
            <template #default="scope">
              <span :class="scope.row.type === 'payment' ? 'payment' : 'charge'">
                {{ scope.row.type === 'payment' ? '+' : '-' }}¥{{ scope.row.amount }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="balanceAfter" label="余额后" width="100">
            <template #default="scope">¥{{ scope.row.balanceAfter }}</template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreditDetailsDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 新增预约对话框 -->
    <el-dialog v-model="showAddReservationDialog" title="新增预约" width="600px">
      <el-form :model="newReservation" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名" required>
              <el-input v-model="newReservation.customerName" placeholder="请输入客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" required>
              <el-input v-model="newReservation.customerPhone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预约时间" required>
              <el-date-picker
                v-model="newReservation.reservationTime"
                type="datetime"
                placeholder="选择预约时间"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="人数" required>
              <el-input-number 
                v-model="newReservation.peopleCount" 
                :min="1" 
                :max="20"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="预约桌台">
          <el-select v-model="newReservation.tableId" placeholder="请选择桌台" style="width: 100%;">
            <el-option 
              v-for="table in availableTables" 
              :key="table.id" 
              :label="`${table.name} (${table.capacity}人)`" 
              :value="table.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input 
            v-model="newReservation.notes" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddReservationDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmAddReservation">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'SpecialFunctions',
  setup() {
    const activeTab = ref('daily-specials')
    
    // 今日特价数据
    const dailySpecials = ref([
      { 
        id: 1, 
        dishId: 1, 
        dishName: '宫保鸡丁', 
        originalPrice: 28.00, 
        specialPrice: 22.00, 
        startDate: '2023-10-01', 
        endDate: '2023-10-07' 
      },
      { 
        id: 2, 
        dishId: 3, 
        dishName: '红烧肉', 
        originalPrice: 38.00, 
        specialPrice: 32.00, 
        startDate: '2023-10-01', 
        endDate: '2023-10-07' 
      }
    ])
    
    // 柿清菜品数据
    const outOfStockDishes = ref([
      { 
        id: 1, 
        dishId: 5, 
        dishName: '拍黄瓜', 
        reason: '原料不足', 
        estimatedRestock: '2023-10-02 12:00:00', 
        note: '黄瓜供应商断货' 
      }
    ])
    
    // 示例菜品数据
    const allDishes = ref([
      { id: 1, name: '宫保鸡丁', price: 28.00 },
      { id: 2, name: '麻婆豆腐', price: 18.00 },
      { id: 3, name: '红烧肉', price: 38.00 },
      { id: 4, name: '鱼香肉丝', price: 26.00 },
      { id: 5, name: '拍黄瓜', price: 10.00 },
      { id: 6, name: '酸辣汤', price: 12.00 },
      { id: 7, name: '白米饭', price: 2.00 },
      { id: 8, name: '可乐', price: 5.00 }
    ])
    
    // 赊账客户数据
    const creditCustomers = ref([
      { 
        id: 1, 
        name: '张老板', 
        phone: '13800138001', 
        creditLimit: 1000.00, 
        currentBalance: 245.50, 
        lastTransactionDate: '2023-09-30', 
        status: 'active',
        joinDate: '2023-01-15',
        transactions: [
          { date: '2023-09-30', description: '消费', amount: 88.00, type: 'charge', balanceAfter: 245.50 },
          { date: '2023-09-28', description: '还款', amount: 100.00, type: 'payment', balanceAfter: 157.50 },
          { date: '2023-09-25', description: '消费', amount: 157.50, type: 'charge', balanceAfter: 257.50 }
        ]
      },
      { 
        id: 2, 
        name: '李经理', 
        phone: '13800138002', 
        creditLimit: 2000.00, 
        currentBalance: 0.00, 
        lastTransactionDate: '2023-09-20', 
        status: 'active',
        joinDate: '2023-03-10',
        transactions: [
          { date: '2023-09-20', description: '还款', amount: 350.00, type: 'payment', balanceAfter: 0.00 },
          { date: '2023-09-15', description: '消费', amount: 350.00, type: 'charge', balanceAfter: 350.00 }
        ]
      }
    ])
    
    //手写单据数据
    const handwrittenOrder = ref({
      customerName: '',
      customerPhone: '',
      orderType: 'dine_in',
      items: [],
      subtotal: 0,
      totalAmount: 0,
      paymentInfo: {
        method: 'cash',
        cashAmount: 0,
        wechatAmount: 0,
        alipayAmount: 0
      },
      notes: ''
    })
        
    // 新增预约数据
    const newReservation = ref({
      customerName: '',
      customerPhone: '',
      reservationTime: '',
      peopleCount: 1,
      tableId: null,
      notes: ''
    })
        
    //数据
    const reservations = ref([
      { 
        id: 1, 
        customerName: '张先生', 
        customerPhone: '13800138001', 
        tableId: 1,
        tableNumber: 'T001',
        reservationTime: '2023-10-15 18:30:00', 
        peopleCount: 4,
        status: 'pending',
        notes: '提前安排包间',
        createdAt: '2023-10-10'
      },
      { 
        id: 2, 
        customerName: '李女士', 
        customerPhone: '13800138002', 
        tableId: 3,
        tableNumber: 'T003',
        reservationTime: '2023-10-16 12:00:00', 
        peopleCount: 6,
        status: 'confirmed',
        notes: '生日聚餐',
        createdAt: '2023-10-11'
      }
    ])
        
    //数据
    const availableTables = ref([
      { id: 1, name: 'T001', capacity: 4 },
      { id: 2, name: 'T002', capacity: 6 },
      { id: 3, name: 'T003', capacity: 8 },
      { id: 4, name: 'T004', capacity: 10 },
      { id: 5, name: 'T005', capacity: 12 }
    ])
    
    //其他响应式数据
    const showAddOutOfStockDialog = ref(false)
    const showCreditDetailsDialog = ref(false)
    const showAddReservationDialog = ref(false)
    const newOutOfStock = ref({
      dishId: null,
      reason: '',
      estimatedRestock: '',
      note: ''
    })
    const selectedCreditCustomer = ref(null)
    
    // 计算属性
    const availableDishes = computed(() => {
      // 过清菜品中未包含的菜品
      const outOfStockIds = outOfStockDishes.value.map(d => d.dishId)
      return allDishes.value.filter(dish => !outOfStockIds.includes(dish.id))
    })
    
    // 方法
    const addDailySpecial = () => {
      // 这里可以添加新的特价菜品
      ElMessage.success('点击添加特价菜品')
    }
    
    const updateDailySpecial = (row) => {
      // 这里可以更新特价菜品信息到服务器
      console.log('更新特价菜品:', row)
    }
    
    const removeDailySpecial = (id) => {
      dailySpecials.value = dailySpecials.value.filter(item => item.id !== id)
      ElMessage.success('已删除特价菜品')
    }
    
    const updateOutOfStock = (row) => {
      // 这里可以更新沽清信息到服务器
      console.log('更新沽清信息:', row)
    }
    
    const restoreDish = (id) => {
      outOfStockDishes.value = outOfStockDishes.value.filter(item => item.id !== id)
      ElMessage.success('已恢复菜品供应')
    }
    
    const confirmAddOutOfStock = () => {
      if (!newOutOfStock.value.dishId || !newOutOfStock.value.reason) {
        ElMessage.error('请选择菜品和原因')
        return
      }
      
      const dish = allDishes.value.find(d => d.id === newOutOfStock.value.dishId)
      outOfStockDishes.value.push({
        id: outOfStockDishes.value.length + 1,
        dishId: newOutOfStock.value.dishId,
        dishName: dish.name,
        reason: newOutOfStock.value.reason,
        estimatedRestock: newOutOfStock.value.estimatedRestock,
        note: newOutOfStock.value.note
      })
      
      // 重置表单
      newOutOfStock.value = {
        dishId: null,
        reason: '',
        estimatedRestock: '',
        note: ''
      }
      
      showAddOutOfStockDialog.value = false
      ElMessage.success('已添加沽清菜品')
    }
    
    const addCreditCustomer = () => {
      ElMessage.success('添加赊账客户功能')
    }
    
    const viewCreditDetails = (customer) => {
      selectedCreditCustomer.value = customer
      showCreditDetailsDialog.value = true
    }
    
    const recordPayment = (customer) => {
      ElMessage.success(`为${customer.name}记账/还款`)
    }
    
    const toggleCreditStatus = (customer) => {
      customer.status = customer.status === 'active' ? 'inactive' : 'active'
      const statusText = customer.status === 'active' ? '启用' : '暂停'
      ElMessage.success(`客户状态已${statusText}`)
    }
    
    const addHandwrittenOrder = () => {
      resetHandwrittenOrder()
      ElMessage.success('新建手写单据')
    }
    
    const addOrderItem = () => {
      handwrittenOrder.value.items.push({
        dishName: '',
        unitPrice: 0,
        quantity: 1
      })
    }
    
    const removeOrderItem = (index) => {
      handwrittenOrder.value.items.splice(index, 1)
      updateHandwrittenOrderTotals()
    }
    
    const updateHandwrittenOrderTotals = () => {
      // 计算小计
      handwrittenOrder.value.subtotal = handwrittenOrder.value.items.reduce(
        (sum, item) => sum + (item.unitPrice * item.quantity), 0
      )
      
      // 计算总计（可以考虑加上服务费、打包费等）
      handwrittenOrder.value.totalAmount = handwrittenOrder.value.subtotal
      
      // 如果是混合支付，确保支付总额不超过订单总额
      if (handwrittenOrder.value.paymentInfo.method === 'mixed') {
        const totalPaid = handwrittenOrder.value.paymentInfo.cashAmount + 
                         handwrittenOrder.value.paymentInfo.wechatAmount + 
                         handwrittenOrder.value.paymentInfo.alipayAmount
        if (totalPaid > handwrittenOrder.value.totalAmount) {
          ElMessage.warning('支付总额超过订单金额')
        }
      }
    }
    
    // 监听订单项变化，自动计算总额
    watch(() => handwrittenOrder.value.items, () => {
      updateHandwrittenOrderTotals()
    }, { deep: true })
    
    const saveHandwrittenOrder = () => {
      if (handwrittenOrder.value.items.length === 0) {
        ElMessage.error('请至少添加一个菜品')
        return
      }
      
      if (!handwrittenOrder.value.customerName) {
        ElMessage.error('请输入客户姓名')
        return
      }
      
      // 这里应该调用API保存手写单据
      console.log('保存手写单据:', handwrittenOrder.value)
      ElMessage.success('手写单据已保存')
    }
    
    const resetHandwrittenOrder = () => {
      handwrittenOrder.value = {
        customerName: '',
        customerPhone: '',
        orderType: 'dine_in',
        items: [],
        subtotal: 0,
        totalAmount: 0,
        paymentInfo: {
          method: 'cash',
          cashAmount: 0,
          wechatAmount: 0,
          alipayAmount: 0
        },
        notes: ''
      }
    }
    
    // 新增预约相关方法
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    const getReservationStatusType = (status) => {
      const statusMap = {
        pending: 'warning',
        confirmed: 'success',
        cancelled: 'info',
        completed: 'primary'
      }
      return statusMap[status] || 'info'
    }
    
    const getReservationStatusLabel = (status) => {
      const statusMap = {
        pending: '待确认',
        confirmed: '已确认',
        cancelled: '已取消',
        completed: '已完成'
      }
      return statusMap[status] || '未知'
    }
    
    const confirmAddReservation = () => {
      if (!newReservation.value.customerName || !newReservation.value.customerPhone) {
        ElMessage.error('请填写客户姓名和联系电话')
        return
      }
      
      if (!newReservation.value.reservationTime) {
        ElMessage.error('请选择预约时间')
        return
      }
      
      const table = availableTables.value.find(t => t.id === newReservation.value.tableId)
      reservations.value.push({
        id: reservations.value.length + 1,
        customerName: newReservation.value.customerName,
        customerPhone: newReservation.value.customerPhone,
        tableId: newReservation.value.tableId,
        tableNumber: table ? table.name : '未指定',
        reservationTime: newReservation.value.reservationTime,
        peopleCount: newReservation.value.peopleCount,
        status: 'pending',
        notes: newReservation.value.notes,
        createdAt: new Date().toISOString().split('T')[0]
      })
      
      // 重置表单
      newReservation.value = {
        customerName: '',
        customerPhone: '',
        reservationTime: '',
        peopleCount: 1,
        tableId: null,
        notes: ''
      }
      
      showAddReservationDialog.value = false
      ElMessage.success('预约已添加')
    }
    
    const confirmReservation = (reservation) => {
      reservation.status = 'confirmed'
      ElMessage.success('预约已确认')
    }
    
    const modifyReservation = (reservation) => {
      ElMessage.success('修改预约功能')
    }
    
    const cancelReservation = (reservation) => {
      reservation.status = 'cancelled'
      ElMessage.success('预约已取消')
    }
    
    return {
      activeTab,
      dailySpecials,
      outOfStockDishes,
      creditCustomers,
      handwrittenOrder,
      reservations,
      availableTables,
      newReservation,
      showAddOutOfStockDialog,
      showCreditDetailsDialog,
      showAddReservationDialog,
      newOutOfStock,
      selectedCreditCustomer,
      availableDishes,
      addDailySpecial,
      updateDailySpecial,
      removeDailySpecial,
      updateOutOfStock,
      restoreDish,
      confirmAddOutOfStock,
      addCreditCustomer,
      viewCreditDetails,
      recordPayment,
      toggleCreditStatus,
      addHandwrittenOrder,
      addOrderItem,
      removeOrderItem,
      saveHandwrittenOrder,
      resetHandwrittenOrder,
      formatDate,
      getReservationStatusType,
      getReservationStatusLabel,
      confirmAddReservation,
      confirmReservation,
      modifyReservation,
      cancelReservation
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overdue {
  color: #f56c6c;
  font-weight: bold;
}

.payment {
  color: #67c23a;
}

.charge {
  color: #f56c6c;
}
</style>