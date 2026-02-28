<template>
  <div class="home">
    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>餐饮管理系统仪表板</span>
        </div>
      </template>
      <div class="dashboard-content">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-number">128</div>
              <div class="stat-label">今日订单数</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-number">¥2,450</div>
              <div class="stat-label">今日营业额</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-number">32</div>
              <div class="stat-label">在线订单</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-number">18</div>
              <div class="stat-label">堂食桌台</div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>最近订单</span>
              </template>
              <el-table :data="recentOrders" style="width: 100%">
                <el-table-column prop="id" label="订单号" width="100" />
                <el-table-column prop="customer" label="客户" width="120" />
                <el-table-column prop="amount" label="金额" width="100" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="scope">
                    <el-tag 
                      :type="scope.row.status === '已完成' ? 'success' : 
                             scope.row.status === '制作中' ? 'warning' : 'info'"
                    >
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="time" label="时间" width="150" />
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>热门菜品</span>
              </template>
              <el-table :data="popularDishes" style="width: 100%">
                <el-table-column prop="name" label="菜品名称" />
                <el-table-column prop="sales" label="销量" width="100" />
                <el-table-column prop="rating" label="评分" width="100" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      recentOrders: [
        { id: '#001', customer: '张三', amount: '¥88', status: '已完成', time: '10:30' },
        { id: '#002', customer: '李四', amount: '¥128', status: '制作中', time: '10:35' },
        { id: '#003', customer: '王五', amount: '¥68', status: '待确认', time: '10:40' },
        { id: '#004', customer: '赵六', amount: '¥158', status: '已完成', time: '10:45' },
        { id: '#005', customer: '钱七', amount: '¥98', status: '制作中', time: '10:50' }
      ],
      popularDishes: [
        { name: '宫保鸡丁', sales: 42, rating: 4.8 },
        { name: '麻婆豆腐', sales: 38, rating: 4.7 },
        { name: '红烧肉', sales: 35, rating: 4.9 },
        { name: '鱼香肉丝', sales: 32, rating: 4.6 },
        { name: '酸辣汤', sales: 28, rating: 4.5 }
      ]
    }
  }
}
</script>

<style scoped>
.dashboard-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.dashboard-content {
  padding: 20px 0;
}
</style>