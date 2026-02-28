<template>
  <div class="orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索订单号、客户姓名或电话" 
            style="width: 300px; margin-right: 20px;"
            @keyup.enter="searchOrders"
          />
          <el-select v-model="filterStatus" placeholder="订单状态" style="width: 150px; margin-right: 20px;" @change="applyFilters">
            <el-option label="全部" value="" />
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="制作中" value="preparing" />
            <el-option label="准备就绪" value="ready" />
            <el-option label="已上菜" value="served" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-button type="primary" @click="searchOrders">搜索</el-button>
          <el-button type="primary" @click="addOrder">新增订单</el-button>
        </div>
      </template>
      
      <el-table :data="filteredOrders" style="width: 100%" stripe>
        <el-table-column prop="order_number" label="订单号" width="150" />
        <el-table-column prop="customer_name" label="客户姓名" width="120" />
        <el-table-column prop="customer_phone" label="联系电话" width="130" />
        <el-table-column prop="table.name" label="桌台" width="100" />
        <el-table-column prop="order_type" label="订单类型" width="100">
          <template #default="scope">
            <el-tag :type="getOrderTypeTag(scope.row.order_type)">
              {{ getOrderTypeName(scope.row.order_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="scope">
            <el-tag :type="getPaymentMethodTag(scope.row.payment_method)">
              {{ getPaymentMethodName(scope.row.payment_method) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_status" label="支付状态" width="100">
          <template #default="scope">
            <el-tag :type="getPaymentStatusTag(scope.row.payment_status)">
              {{ getPaymentStatusName(scope.row.payment_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_status" label="订单状态" width="100">
          <template #default="scope">
            <el-tag :type="getOrderStatusTag(scope.row.order_status)">
              {{ getOrderStatusName(scope.row.order_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="100">
          <template #default="scope">¥{{ scope.row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="takeout_number" label="取餐号" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="150" />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="small" @click="viewOrder(scope.row)">查看</el-button>
            <el-button 
              size="small" 
              :type="getStatusButtonType(scope.row.order_status)"
              @click="updateOrderStatus(scope.row)"
            >
              {{ getStatusButtonLabel(scope.row.order_status) }}
            </el-button>
            <el-button 
              size="small" 
              type="warning"
              @click="editOrder(scope.row)"
            >
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredOrders.length"
        style="margin-top: 20px;"
      />
    </el-card>
    
    <!-- 订单详情对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px">
      <div v-if="currentOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
          <el-descriptions-item label="客户姓名">{{ currentOrder.customer_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentOrder.customer_phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="桌台信息">{{ currentOrder.table?.name || '未分配' }}</el-descriptions-item>
          <el-descriptions-item label="订单类型">
            <el-tag :type="getOrderTypeTag(currentOrder.order_type)">
              {{ getOrderTypeName(currentOrder.order_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">
            <el-tag :type="getPaymentMethodTag(currentOrder.payment_method)">
              {{ getPaymentMethodName(currentOrder.payment_method) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="支付状态">
            <el-tag :type="getPaymentStatusTag(currentOrder.payment_status)">
              {{ getPaymentStatusName(currentOrder.payment_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getOrderStatusTag(currentOrder.order_status)">
              {{ getOrderStatusName(currentOrder.order_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="取餐号">{{ currentOrder.takeout_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentOrder.created_at }}</el-descriptions-item>
          <el-descriptions-item label="小计">¥{{ currentOrder.subtotal }}</el-descriptions-item>
          <el-descriptions-item label="税费">¥{{ currentOrder.tax }}</el-descriptions-item>
          <el-descriptions-item label="服务费">¥{{ currentOrder.service_fee }}</el-descriptions-item>
          <el-descriptions-item label="打包费">¥{{ currentOrder.packing_fee }}</el-descriptions-item>
          <el-descriptions-item label="折扣">¥{{ currentOrder.discount }}</el-descriptions-item>
          <el-descriptions-item label="总金额" :span="2">
            <span style="font-size: 18px; font-weight: bold; color: #f56c6c;">¥{{ currentOrder.total_amount }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="特殊要求" :span="2">{{ currentOrder.special_requests || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 20px;">订单菜品：</h4>
        <el-table :data="currentOrder.order_items" style="width: 100%">
          <el-table-column prop="dish.name" label="菜品名称" />
          <el-table-column prop="unit_price" label="单价">
            <template #default="scope">¥{{ scope.row.unit_price }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="total_price" label="小计">
            <template #default="scope">¥{{ scope.row.total_price }}</template>
          </el-table-column>
          <el-table-column prop="special_requests" label="特殊要求" />
          <el-table-column label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.is_prepared ? 'success' : 'info'">{{ scope.row.is_prepared ? '已制作' : '待制作' }}</el-tag>
              <br>
              <el-tag :type="scope.row.is_served ? 'success' : 'info'">{{ scope.row.is_served ? '已上菜' : '未上菜' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button 
            v-if="currentOrder.order_status === 'pending'" 
            type="primary" 
            @click="confirmOrder(currentOrder.id)"
          >
            确认订单
          </el-button>
          <el-button 
            v-if="['confirmed', 'preparing', 'ready'].includes(currentOrder.order_status)" 
            type="success" 
            @click="completeOrder(currentOrder.id)"
          >
            完成订单
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 新增/编辑订单对话框 -->
    <el-dialog v-model="orderDialogVisible" :title="orderDialogTitle" width="800px">
      <el-form :model="editingOrder" :rules="orderRules" ref="orderForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单号" prop="order_number">
              <el-input v-model="editingOrder.order_number" placeholder="系统自动生成或手动输入" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="订单类型" prop="order_type">
              <el-select v-model="editingOrder.order_type" placeholder="请选择订单类型" style="width: 100%;">
                <el-option label="堂食" value="dine_in" />
                <el-option label="外带" value="takeaway" />
                <el-option label="打包" value="pack" />
                <el-option label="预约" value="preorder" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名">
              <el-input v-model="editingOrder.customer_name" placeholder="请输入客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="editingOrder.customer_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="桌台">
              <el-select v-model="editingOrder.table_id" placeholder="请选择桌台" style="width: 100%;" clearable>
                <el-option 
                  v-for="table in tables" 
                  :key="table.id" 
                  :label="`${table.name} (${table.area})`" 
                  :value="table.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="支付方式" prop="payment_method">
              <el-select v-model="editingOrder.payment_method" placeholder="请选择支付方式" style="width: 100%;">
                <el-option label="现金" value="cash" />
                <el-option label="微信" value="wechat" />
                <el-option label="支付宝" value="alipay" />
                <el-option label="混合支付" value="mixed" />
                <el-option label="赊账" value="credit" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="特殊要求">
          <el-input 
            v-model="editingOrder.special_requests" 
            type="textarea" 
            placeholder="请输入特殊要求"
            :rows="3"
          />
        </el-form-item>
        
        <el-divider content-position="left">订单菜品</el-divider>
        <el-table :data="editingOrder.order_items" style="width: 100%; margin-bottom: 20px;">
          <el-table-column prop="dish.name" label="菜品" width="150" />
          <el-table-column label="单价" width="100">
            <template #default="scope">¥{{ scope.row.unit_price }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100">
            <template #default="scope">
              <el-input-number 
                v-model="scope.row.quantity" 
                :min="1" 
                @change="updateItemTotal(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="100">
            <template #default="scope">¥{{ scope.row.total_price }}</template>
          </el-table-column>
          <el-table-column label="特殊要求" width="150">
            <template #default="scope">
              <el-input v-model="scope.row.special_requests" size="small" />
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
        
        <div style="text-align: right; margin-bottom: 20px;">
          <el-button type="primary" @click="openAddDishDialog">添加菜品</el-button>
        </div>
        
        <el-divider content-position="left">费用明细</el-divider>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="小计">
              <el-input v-model="editingOrder.subtotal" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="税费">
              <el-input-number v-model="editingOrder.tax" :min="0" :step="0.01" :precision="2" controls-position="right" class="fee-input-number" @change="calculateOrderTotals" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="服务费">
              <el-input-number v-model="editingOrder.service_fee" :min="0" :step="0.01" :precision="2" controls-position="right" class="fee-input-number" @change="calculateOrderTotals" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="打包费">
              <el-input-number v-model="editingOrder.packing_fee" :min="0" :step="0.01" :precision="2" controls-position="right" class="fee-input-number" @change="calculateOrderTotals" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="折扣">
              <el-input-number v-model="editingOrder.discount_rate" :min="0" :max="10" :step="0.1" :precision="1" controls-position="right" class="fee-input-number" @change="calculateOrderTotals" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="总金额">
              <el-input v-model="editingOrder.total_amount" readonly style="color: #f56c6c; font-weight: bold;" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="已付金额">
              <el-input-number v-model="editingOrder.paid_amount" :min="0" :step="0.01" :precision="2" controls-position="right" class="fee-input-number" @change="calculateOrderTotals" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="剩余金额">
              <el-input v-model="editingOrder.remaining_amount" readonly style="color: #f56c6c; font-weight: bold;" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="orderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveOrder">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="addDishDialogVisible" title="添加菜品" width="520px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="折扣(折)" required>
          <el-select v-model="selectedDishId" filterable clearable placeholder="输入关键字搜索菜品" style="width: 100%">
            <el-option
              v-for="dish in availableDishes"
              :key="dish.id"
              :label="`${dish.name}??${Number(dish.price).toFixed(2)}?`"
              :value="dish.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="菜品" required>
          <el-input-number v-model="addDishQuantity" :min="1" :max="99" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDishDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddDish">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDishes } from '@/services/dishService'

export default {
  name: 'Orders',
  setup() {
    const orders = ref([
      { 
        id: 1, 
        order_number: 'ORD-20231001001', 
        customer_name: '张三', 
        customer_phone: '13800138001',
        table: { id: 1, name: 'T001', area: '大厅' },
        order_type: 'dine_in', 
        payment_method: 'wechat', 
        payment_status: 'paid', 
        order_status: 'completed', 
        subtotal: 30.00,
        tax: 0.00,
        service_fee: 0.00,
        packing_fee: 0.00,
        discount: 2.00,
        total_amount: 28.00,
        paid_amount: 28.00,
        remaining_amount: 0.00,
        special_requests: '不要香菜',
        takeout_number: null,
        created_at: '2023-10-01 10:30:15',
        order_items: [
          { id: 1, dish: { name: '宫保鸡丁' }, unit_price: 28.00, quantity: 1, total_price: 28.00, special_requests: '不要香菜', is_prepared: true, is_served: true },
          { id: 2, dish: { name: '米饭' }, unit_price: 2.00, quantity: 1, total_price: 2.00, special_requests: '', is_prepared: true, is_served: true }
        ]
      },
      { 
        id: 2, 
        order_number: 'ORD-20231001002', 
        customer_name: '李四', 
        customer_phone: '13800138002',
        table: { id: 2, name: 'T002', area: '包间' },
        order_type: 'dine_in', 
        payment_method: 'cash', 
        payment_status: 'paid', 
        order_status: 'preparing', 
        subtotal: 56.00,
        tax: 0.00,
        service_fee: 0.00,
        packing_fee: 0.00,
        discount: 0.00,
        total_amount: 56.00,
        paid_amount: 56.00,
        remaining_amount: 0.00,
        special_requests: '',
        takeout_number: null,
        created_at: '2023-10-01 10:45:22',
        order_items: [
          { id: 3, dish: { name: '麻婆豆腐' }, unit_price: 18.00, quantity: 1, total_price: 18.00, special_requests: '', is_prepared: true, is_served: false },
          { id: 4, dish: { name: '红烧肉' }, unit_price: 38.00, quantity: 1, total_price: 38.00, special_requests: '', is_prepared: false, is_served: false }
        ]
      },
      { 
        id: 3, 
        order_number: 'TAKE-20231001003', 
        customer_name: '王五', 
        customer_phone: '13800138003',
        table: null,
        order_type: 'takeaway', 
        payment_method: 'alipay', 
        payment_status: 'paid', 
        order_status: 'ready', 
        subtotal: 26.00,
        tax: 0.00,
        service_fee: 0.00,
        packing_fee: 1.00,
        discount: 0.00,
        total_amount: 27.00,
        paid_amount: 27.00,
        remaining_amount: 0.00,
        special_requests: '微辣',
        takeout_number: 'T103015234',
        created_at: '2023-10-01 11:20:10',
        order_items: [
          { id: 5, dish: { name: '鱼香肉丝' }, unit_price: 26.00, quantity: 1, total_price: 26.00, special_requests: '微辣', is_prepared: true, is_served: true }
        ]
      }
    ])
    
    const availableDishes = ref([])

    const tables = ref([
      { id: 1, name: 'T001', area: '大厅', capacity: 4, status: 'available' },
      { id: 2, name: 'T002', area: '包间', capacity: 8, status: 'occupied' },
      { id: 3, name: 'T003', area: '大厅', capacity: 2, status: 'available' },
      { id: 4, name: 'T004', area: '雅座', capacity: 6, status: 'cleaning' }
    ])
    
    const currentPage = ref(1)
    const pageSize = ref(10)
    const searchQuery = ref('')
    const filterStatus = ref('')
    const dialogVisible = ref(false)
    const orderDialogVisible = ref(false)
    const addDishDialogVisible = ref(false)
    const selectedDishId = ref(null)
    const addDishQuantity = ref(1)
    const currentOrder = ref(null)
    const editingOrder = ref({
      id: null,
      order_number: '',
      customer_name: '',
      customer_phone: '',
      table_id: null,
      order_type: 'dine_in',
      payment_method: 'cash',
      order_status: 'pending',
      subtotal: 0.00,
      tax: 0.00,
      service_fee: 0.00,
      packing_fee: 0.00,
      discount: 0.00,
      discount_rate: 10.0,
      total_amount: 0.00,
      paid_amount: 0.00,
      remaining_amount: 0.00,
      special_requests: '',
      takeout_number: null,
      order_items: []
    })
    
    const orderRules = {
      order_number: [
        { required: true, message: '请输入订单号', trigger: 'blur' }
      ],
      order_type: [
        { required: true, message: '请选择订单类型', trigger: 'change' }
      ],
      payment_method: [
        { required: true, message: '请选择支付方式', trigger: 'change' }
      ]
    }
    
    const filteredOrders = computed(() => {
      let result = orders.value
      
      // 应用搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(order => 
          order.order_number.toLowerCase().includes(query) ||
          (order.customer_name && order.customer_name.toLowerCase().includes(query)) ||
          (order.customer_phone && order.customer_phone.includes(query))
        )
      }
      
      // 应用状态过滤
      if (filterStatus.value) {
        result = result.filter(order => order.order_status === filterStatus.value)
      }
      
      return result
    })
    
    const dialogTitle = computed(() => {
      return currentOrder.value ? `订单详情 - ${currentOrder.value.order_number}` : '订单详情'
    })
    
    const orderDialogTitle = computed(() => {
      return editingOrder.value.id ? '编辑订单' : '新增订单'
    })
    
    const getOrderTypeName = (type) => {
      const types = {
        'dine_in': '堂食',
        'takeaway': '外带',
        'pack': '打包',
        'preorder': '预约'
      }
      return types[type] || type
    }
    
    const getOrderTypeTag = (type) => {
      const tags = {
        'dine_in': 'primary',
        'takeaway': 'success',
        'pack': 'warning',
        'preorder': 'info'
      }
      return tags[type] || 'info'
    }
    
    const getPaymentMethodName = (method) => {
      const methods = {
        'cash': '现金',
        'wechat': '微信',
        'alipay': '支付宝',
        'mixed': '混合支付',
        'credit': '赊账'
      }
      return methods[method] || method
    }
    
    const getPaymentMethodTag = (method) => {
      const tags = {
        'cash': 'warning',
        'wechat': 'success',
        'alipay': 'blue',
        'mixed': 'orange',
        'credit': 'info'
      }
      return tags[method] || 'info'
    }
    
    const getPaymentStatusName = (status) => {
      const statuses = {
        'pending': '待支付',
        'partial': '部分支付',
        'paid': '已支付',
        'credit': '赊账'
      }
      return statuses[status] || status
    }
    
    const getPaymentStatusTag = (status) => {
      const tags = {
        'pending': 'warning',
        'partial': 'orange',
        'paid': 'success',
        'credit': 'info'
      }
      return tags[status] || 'info'
    }
    
    const getOrderStatusName = (status) => {
      const statuses = {
        'pending': '待确认',
        'confirmed': '已确认',
        'preparing': '制作中',
        'ready': '准备就绪',
        'served': '已上菜',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statuses[status] || status
    }
    
    const getOrderStatusTag = (status) => {
      const tags = {
        'pending': 'info',
        'confirmed': 'primary',
        'preparing': 'warning',
        'ready': 'warning',
        'served': 'success',
        'completed': 'success',
        'cancelled': 'danger'
      }
      return tags[status] || 'info'
    }
    
    const getStatusButtonType = (status) => {
      switch(status) {
        case 'pending': return 'primary'
        case 'confirmed': 
        case 'preparing': 
        case 'ready': return 'success'
        default: return 'info'
      }
    }
    
    const getStatusButtonLabel = (status) => {
      switch(status) {
        case 'pending': return '确认订单'
        case 'confirmed': 
        case 'preparing': 
        case 'ready': return '完成订单'
        case 'completed': return '重新处理'
        case 'cancelled': return '恢复订单'
        default: return '更新状态'
      }
    }
    
    const toNumber = (value, fallback = 0) => {
      const num = Number(value)
      return Number.isFinite(num) ? num : fallback
    }

    const normalizeOrderForEdit = (row) => {
      const orderItems = Array.isArray(row.order_items)
        ? row.order_items.map((item) => ({
            ...item,
            dish_id: item.dish_id ?? null,
            quantity: toNumber(item.quantity, 1),
            unit_price: toNumber(item.unit_price, 0),
            total_price: toNumber(item.total_price, 0)
          }))
        : []

      const subtotal = toNumber(row.subtotal, 0)
      const discount = toNumber(row.discount, 0)
      const discountRate = subtotal > 0
        ? Math.max(0, Math.min(10, Number(((1 - discount / subtotal) * 10).toFixed(1))))
        : 10

      return {
        ...row,
        subtotal,
        tax: toNumber(row.tax, 0),
        service_fee: toNumber(row.service_fee, 0),
        packing_fee: toNumber(row.packing_fee, 0),
        discount,
        discount_rate: discountRate,
        total_amount: toNumber(row.total_amount, 0),
        paid_amount: toNumber(row.paid_amount, 0),
        remaining_amount: toNumber(row.remaining_amount, 0),
        order_items: orderItems
      }
    }

    const viewOrder = (row) => {
      currentOrder.value = { ...row }
      dialogVisible.value = true
    }
    
    const editOrder = (row) => {
      editingOrder.value = normalizeOrderForEdit(row)
      calculateOrderTotals()
      orderDialogVisible.value = true
    }
    
    const addOrder = () => {
      editingOrder.value = {
        id: null,
        order_number: `ORD-${new Date().getFullYear()}${String(new Date().getMonth()+1).padStart(2, '0')}${String(new Date().getDate()).padStart(2, '0')}001`,
        customer_name: '',
        customer_phone: '',
        table_id: null,
        order_type: 'dine_in',
        payment_method: 'cash',
        order_status: 'pending',
        subtotal: 0.00,
        tax: 0.00,
        service_fee: 0.00,
        packing_fee: 0.00,
        discount: 0.00,
        discount_rate: 10.0,
        total_amount: 0.00,
        paid_amount: 0.00,
        remaining_amount: 0.00,
        special_requests: '',
        takeout_number: null,
        order_items: []
      }
      orderDialogVisible.value = true
    }
    
    const updateOrderStatus = (row) => {
      let newStatus = ''
      switch(row.order_status) {
        case 'pending':
          newStatus = 'confirmed'
          ElMessage.success('订单已确认')
          break
        case 'confirmed':
        case 'preparing':
        case 'ready':
          newStatus = 'completed'
          ElMessage.success('订单已完成')
          break
        case 'completed':
          newStatus = 'confirmed'
          ElMessage.info('订单状态已回退到已确认')
          break
        case 'cancelled':
          newStatus = 'pending'
          ElMessage.info('订单已恢复')
          break
      }
      
      if (newStatus) {
        row.order_status = newStatus
        if (newStatus === 'confirmed') {
          row.confirmed_at = new Date().toISOString().slice(0, 19).replace('T', ' ')
        } else if (newStatus === 'completed') {
          row.completed_at = new Date().toISOString().slice(0, 19).replace('T', ' ')
        }
      }
    }
    
    const confirmOrder = (orderId) => {
      const order = orders.value.find(o => o.id === orderId)
      if (order) {
        order.order_status = 'confirmed'
        order.confirmed_at = new Date().toISOString().slice(0, 19).replace('T', ' ')
        ElMessage.success('订单已确认')
      }
    }
    
    const completeOrder = (orderId) => {
      const order = orders.value.find(o => o.id === orderId)
      if (order) {
        order.order_status = 'completed'
        order.completed_at = new Date().toISOString().slice(0, 19).replace('T', ' ')
        ElMessage.success('订单已完成')
      }
    }
    
    const loadAvailableDishes = async () => {
      try {
        const list = await getDishes(0, 500)
        availableDishes.value = Array.isArray(list) ? list : []
      } catch (error) {
        console.error('加载菜品失败:', error)
        availableDishes.value = []
        ElMessage.warning('菜品数据加载失败，请检查后端接口')
      }
    }

    const openAddDishDialog = async () => {
      if (!availableDishes.value.length) {
        await loadAvailableDishes()
      }
      selectedDishId.value = null
      addDishQuantity.value = 1
      addDishDialogVisible.value = true
    }

    const confirmAddDish = () => {
      const dish = availableDishes.value.find((item) => item.id === selectedDishId.value)
      if (!dish) {
        ElMessage.warning('请先选择菜品')
        return
      }

      const quantity = Math.max(1, toNumber(addDishQuantity.value, 1))
      const unitPrice = toNumber(dish.price, 0)

      editingOrder.value.order_items.push({
        dish_id: dish.id,
        dish: { name: dish.name },
        unit_price: unitPrice,
        quantity,
        total_price: parseFloat((unitPrice * quantity).toFixed(2)),
        special_requests: ''
      })

      addDishDialogVisible.value = false
      calculateOrderTotals()
    }
    
    const removeOrderItem = (index) => {
      editingOrder.value.order_items.splice(index, 1)
      calculateOrderTotals()
    }
    
    const updateItemTotal = (item) => {
      item.total_price = parseFloat((item.unit_price * item.quantity).toFixed(2))
      calculateOrderTotals()
    }
    
    const calculateOrderTotals = () => {
      const normalizedItems = Array.isArray(editingOrder.value.order_items)
        ? editingOrder.value.order_items
        : []

      const subtotal = normalizedItems.reduce((sum, item) => {
        const totalPrice = Number(item.total_price)
        return sum + (Number.isFinite(totalPrice) ? totalPrice : 0)
      }, 0)

      editingOrder.value.subtotal = parseFloat(subtotal.toFixed(2))
      editingOrder.value.tax = toNumber(editingOrder.value.tax, 0)
      editingOrder.value.service_fee = toNumber(editingOrder.value.service_fee, 0)
      editingOrder.value.packing_fee = toNumber(editingOrder.value.packing_fee, 0)
      editingOrder.value.discount_rate = Math.max(0, Math.min(10, toNumber(editingOrder.value.discount_rate, 10)))
      editingOrder.value.discount = parseFloat((editingOrder.value.subtotal * (10 - editingOrder.value.discount_rate) / 10).toFixed(2))
      editingOrder.value.paid_amount = toNumber(editingOrder.value.paid_amount, 0)

      editingOrder.value.total_amount = parseFloat((
        editingOrder.value.subtotal +
        editingOrder.value.tax +
        editingOrder.value.service_fee +
        editingOrder.value.packing_fee -
        editingOrder.value.discount
      ).toFixed(2))

      editingOrder.value.remaining_amount = parseFloat(
        (editingOrder.value.total_amount - editingOrder.value.paid_amount).toFixed(2)
      )
    }
    
    const saveOrder = () => {
      // 验证必填字段
      if (!editingOrder.value.order_number) {
        ElMessage.error('请输入订单号')
        return
      }
      
      if (editingOrder.value.order_items.length === 0) {
        ElMessage.error('请至少添加一个菜品')
        return
      }
      
      // 保存订单
      if (editingOrder.value.id) {
        // 更新现有订单
        const index = orders.value.findIndex(o => o.id === editingOrder.value.id)
        if (index !== -1) {
          orders.value.splice(index, 1, { ...editingOrder.value })
        }
      } else {
        // 添加新订单
        const newId = Math.max(...orders.value.map(o => o.id), 0) + 1
        orders.value.push({ 
          ...editingOrder.value, 
          id: newId,
          created_at: new Date().toISOString().slice(0, 19).replace('T', ' ')
        })
      }
      
      orderDialogVisible.value = false
      ElMessage.success('订单保存成功')
    }
    
    const searchOrders = () => {
      // 实际应用中这里会调用API进行搜索
      console.log('搜索订单:', searchQuery.value)
    }
    
    const applyFilters = () => {
      // 过滤器已通过computed属性自动应用
    }
    
    const handleSizeChange = (val) => {
      pageSize.value = val
    }
    
    const handleCurrentChange = (val) => {
      currentPage.value = val
    }

    onMounted(() => {
      loadAvailableDishes()
    })

    watch(
      () => [
        editingOrder.value.tax,
        editingOrder.value.service_fee,
        editingOrder.value.packing_fee,
        editingOrder.value.discount_rate,
        editingOrder.value.paid_amount
      ],
      () => {
        if (orderDialogVisible.value) {
          calculateOrderTotals()
        }
      }
    )
    
    return {
      orders,
      tables,
      currentPage,
      pageSize,
      searchQuery,
      filterStatus,
      dialogVisible,
      orderDialogVisible,
      addDishDialogVisible,
      selectedDishId,
      addDishQuantity,
      currentOrder,
      editingOrder,
      orderRules,
      filteredOrders,
      dialogTitle,
      orderDialogTitle,
      getOrderTypeName,
      getOrderTypeTag,
      getPaymentMethodName,
      getPaymentMethodTag,
      getPaymentStatusName,
      getPaymentStatusTag,
      getOrderStatusName,
      getOrderStatusTag,
      getStatusButtonType,
      getStatusButtonLabel,
      viewOrder,
      editOrder,
      addOrder,
      updateOrderStatus,
      confirmOrder,
      completeOrder,
      openAddDishDialog,
      confirmAddDish,
      removeOrderItem,
      availableDishes,
      updateItemTotal,
      calculateOrderTotals,
      saveOrder,
      searchOrders,
      applyFilters,
      handleSizeChange,
      handleCurrentChange
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

.dialog-footer {
  text-align: right;
}

.fee-input-number {
  width: 100%;
}

:deep(.fee-input-number .el-input__inner) {
  text-align: left;
}
</style>