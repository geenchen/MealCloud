<template>
  <div class="special-functions">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="今日特价" name="daily-specials">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>设置今日特价菜品</span>
              <el-button type="primary" @click="openDailyDialog">新增特价</el-button>
            </div>
          </template>

          <el-table :data="dailySpecials" stripe>
            <el-table-column prop="dishName" label="菜品" min-width="200" />
            <el-table-column prop="originalPrice" label="原价" width="120">
              <template #default="scope">￥{{ Number(scope.row.originalPrice).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="specialPrice" label="特价" width="120">
              <template #default="scope">￥{{ Number(scope.row.specialPrice).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="startDate" label="开始日期" width="140" />
            <el-table-column prop="endDate" label="结束日期" width="140" />
            <el-table-column label="操作" width="140">
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
              <span>沽清菜品</span>
              <el-button type="warning" plain @click="addOutOfStock">新增沽清</el-button>
            </div>
          </template>

          <el-table :data="outOfStockDishes" stripe>
            <el-table-column prop="dishName" label="菜品" min-width="200" />
            <el-table-column prop="reason" label="原因" min-width="200" />
            <el-table-column prop="estimatedRestock" label="预计恢复" width="180" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button size="small" @click="restoreDish(scope.row.id)">恢复</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showDailyDialog" title="新增特价" width="520px">
      <el-form :model="newDailySpecial" label-width="90px">
        <el-form-item label="菜品名称" required>
          <el-input v-model="newDailySpecial.dishName" placeholder="请输入菜品名称" />
        </el-form-item>
        <el-form-item label="原价" required>
          <el-input-number v-model="newDailySpecial.originalPrice" :min="0.01" :step="0.01" style="width: 100%" />
        </el-form-item>
        <el-form-item label="特价" required>
          <el-input-number
            v-model="newDailySpecial.specialPrice"
            :min="0.01"
            :max="Number(newDailySpecial.originalPrice)"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始日期" required>
          <el-date-picker
            v-model="newDailySpecial.startDate"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker
            v-model="newDailySpecial.endDate"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDailyDialog = false">取消</el-button>
        <el-button type="primary" @click="addDailySpecial">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const getToday = () => {
  const d = new Date()
  const y = d.getFullYear()
  const m = `${d.getMonth() + 1}`.padStart(2, '0')
  const day = `${d.getDate()}`.padStart(2, '0')
  return `${y}-${m}-${day}`
}

export default {
  name: 'SpecialFunctions',
  setup() {
    const today = getToday()

    const activeTab = ref('daily-specials')
    const showDailyDialog = ref(false)

    const dailySpecials = ref([
      {
        id: 1,
        dishName: '宫保鸡丁',
        originalPrice: 28,
        specialPrice: 22,
        startDate: today,
        endDate: today
      }
    ])

    const newDailySpecial = ref({
      dishName: '',
      originalPrice: 28,
      specialPrice: 22,
      startDate: today,
      endDate: today
    })

    const outOfStockDishes = ref([
      {
        id: 1,
        dishName: '拍黄瓜',
        reason: '原料不足',
        estimatedRestock: `${today} 20:00`
      }
    ])

    const openDailyDialog = () => {
      newDailySpecial.value = {
        dishName: '',
        originalPrice: 28,
        specialPrice: 22,
        startDate: getToday(),
        endDate: getToday()
      }
      showDailyDialog.value = true
    }

    const addDailySpecial = () => {
      if (!newDailySpecial.value.dishName) {
        ElMessage.warning('请先填写菜品名称')
        return
      }

      dailySpecials.value.unshift({
        id: Date.now(),
        ...newDailySpecial.value
      })
      showDailyDialog.value = false
      ElMessage.success('特价已添加')
    }

    const removeDailySpecial = (id) => {
      dailySpecials.value = dailySpecials.value.filter((item) => item.id !== id)
      ElMessage.success('已删除特价')
    }

    const addOutOfStock = () => {
      ElMessage.info('沽清新增表单待接入')
    }

    const restoreDish = (id) => {
      outOfStockDishes.value = outOfStockDishes.value.filter((item) => item.id !== id)
      ElMessage.success('菜品已恢复供应')
    }

    return {
      activeTab,
      showDailyDialog,
      dailySpecials,
      newDailySpecial,
      outOfStockDishes,
      openDailyDialog,
      addDailySpecial,
      removeDailySpecial,
      addOutOfStock,
      restoreDish
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
</style>
