<template>
  <div class="home">
    <div class="hero">
      <h2>门店代客点单</h2>
      <p>本地模式运行，仅店内老板/店员使用</p>
    </div>

    <van-cell-group inset class="form-panel">
      <van-field v-model="tableId" label="桌台号" placeholder="堂食可选填，如 1" type="digit" />
      <van-field v-model="tableName" label="桌台名" placeholder="可选填，如 永和" />
    </van-cell-group>

    <div class="actions">
      <van-button block type="primary" @click="goMenu('dine_in')">开始堂食点单</van-button>
      <van-button block type="warning" @click="goMenu('takeaway')">开始外带点单</van-button>
      <van-button block color="#8fcb68" @click="goMenu('pack')">开始打包点单</van-button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const tableId = ref('')
    const tableName = ref('')

    const goMenu = (orderType) => {
      router.push({
        path: '/menu',
        query: {
          orderType,
          tableId: tableId.value || undefined,
          tableName: tableName.value || undefined,
          mode: 'direct'
        }
      })
    }

    return {
      tableId,
      tableName,
      goMenu
    }
  }
}
</script>

<style scoped>
.home {
  padding: 14px;
}

.hero {
  padding: 18px;
  border-radius: 14px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #b34d16 0%, #cb6a2f 70%, #e08c47 100%);
  color: #fff;
  box-shadow: 0 12px 24px rgba(177, 78, 25, 0.3);
}

.hero h2 {
  margin: 0;
  letter-spacing: 1px;
}

.hero p {
  margin: 8px 0 0;
  opacity: 0.9;
}

.form-panel {
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(159, 85, 35, 0.08);
}

.actions {
  margin-top: 16px;
  display: grid;
  gap: 10px;
}
</style>
