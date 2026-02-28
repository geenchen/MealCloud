<template>
  <div id="app">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h3>餐饮管理系统</h3>
      </div>
      <el-menu
        :default-active="activeIndex"
        :unique-opened="true"
        :router="true"
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-sub-menu index="/management">
          <template #title>
            <el-icon><List /></el-icon>
            <span>管理</span>
          </template>
          <el-menu-item index="/dishes">菜品管理</el-menu-item>
          <el-menu-item index="/tables">桌台管理</el-menu-item>
          <el-menu-item index="/table-dashboard">桌台监控</el-menu-item>
          <el-menu-item index="/users">用户管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/order">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>订单</span>
          </template>
          <el-menu-item index="/orders">订单管理</el-menu-item>
          <el-menu-item index="/order-entry">老板下单</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        
        <!-- 特殊功能菜单 -->
        <el-sub-menu index="/special">
          <template #title>
            <el-icon><Star /></el-icon>
            <span>特殊功能</span>
          </template>
          <el-menu-item index="/special-functions">今日特价/沽清</el-menu-item>
        </el-sub-menu>
        
        <!-- 高级功能菜单（可选） -->
        <el-sub-menu v-if="!minimalMode" index="/advanced">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>高级功能</span>
          </template>
          <el-menu-item index="/members">会员管理</el-menu-item>
          <el-menu-item index="/marketing">营销活动</el-menu-item>
          <el-menu-item index="/financial">财务管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 主内容区域 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button @click="toggleSidebar" class="menu-toggle">
            <el-icon><Menu /></el-icon>
          </el-button>
          <!-- 极简模式开关 -->
          <el-switch
            v-model="minimalMode"
            class="minimal-mode-switch"
            active-text="极简模式"
            inactive-text="标准模式"
            inline-prompt
            active-color="#13ce66"
            inactive-color="#ff4949"
          />
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="el-dropdown-link">
              管理员<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item>修改密码</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <div class="main-content-content">
          <router-view />
        </div>
      </el-main>
    </el-container>

    <!-- Quick Order Panel -->
    <QuickOrderPanel />
  </div>
</template>

<script>
import { House, List, Document, DataAnalysis, Menu, Setting, Star } from '@element-plus/icons-vue'
import QuickOrderPanel from '@/components/QuickOrderPanel.vue'

export default {
  name: 'App',
  components: {
    House,
    List,
    Document,
    DataAnalysis,
    Menu,
    Setting,
    Star,
    QuickOrderPanel
  },
  data() {
    return {
      activeIndex: '/',
      sidebarCollapsed: false,
      minimalMode: false // 极简模式开关
    }
  },
  methods: {
    handleSelect(key) {
      this.activeIndex = key
      if (this.$route.path !== key) {
        this.$router.push(key)
      }
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    }
  },
  watch: {
    '$route'(to) {
      this.activeIndex = to.path
    }
  },
  mounted() {
    this.activeIndex = this.$route.path
  }
}
</script>

<style>
html,
body,
#app {
  margin: 0;
  width: 100%;
  height: 100%;
}

body {
  overflow: hidden;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  width: 100vw;
  height: 100%;
  display: flex;
  overflow: hidden;
}

#app > .el-container {
  flex: 1;
  min-width: 0;
}

.sidebar {
  background: linear-gradient(180deg, #2b2d42 0%, #1d1e2c 100%);
  height: 100vh;
  flex-shrink: 0;
  transition: all 0.3s;
  box-shadow: 4px 0 20px rgba(43, 45, 66, 0.25);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  border-bottom: 1px solid #434a50;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.el-sub-menu .el-menu-item {
  min-width: 160px;
  padding-left: 45px;
}

.el-menu {
  border: none;
}

/*统一菜单项基础样式 */
.el-menu-item, .el-sub-menu__title {
  color: #bfcbd9;
  background-color: transparent !important;
  transition: all 0.3s ease;
}

/*悬停效果 */
.el-menu-item:hover, .el-sub-menu__title:hover {
  color: #ffffff !important;
  background-color: rgba(67, 97, 238, 0.25) !important;
}

/*激状态状态菜单项 */
.el-menu-item.is-active {
  background: linear-gradient(90deg, #4361ee, #3f37c9) !important;
  color: white !important;
  font-weight: 600;
}

/*激状态状态菜单项悬停 */
.el-menu-item.is-active:hover {
  background: linear-gradient(90deg, #4361ee, #3f37c9) !important;
  color: white !important;
  opacity: 0.9;
}

/*子菜单项样式 */
.el-sub-menu .el-menu-item {
  background-color: transparent !important;
  color: #bfcbd9 !important;
  padding-left: 45px;
  min-width: 160px;
}

/*子菜单项悬停 */
.el-sub-menu .el-menu-item:hover {
  background-color: rgba(67, 97, 238, 0.2) !important;
  color: #ffffff !important;
}

/*子菜单项激活状态 */
.el-sub-menu .el-menu-item.is-active {
  background: linear-gradient(90deg, #4361ee, #3f37c9) !important;
  color: white !important;
  font-weight: 600;
}

/* 图标样式统一 */
.el-menu-item .el-icon, .el-sub-menu__title .el-icon {
  color: inherit;
}

/*确保所有菜单项背景一致 */
.el-menu-item,
.el-sub-menu .el-menu-item,
.el-sub-menu__title {
  background-color: transparent !important;
}

/*Element Plus默认样式 */
.el-menu-item:focus,
.el-sub-menu__title:focus {
  background-color: transparent !important;
  outline: none;
}

/*确保菜单容器背景一致 */
.el-menu {
  background-color: transparent !important;
}

/*子菜单容器背景 */
.el-sub-menu .el-menu {
  background-color: rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px;
  margin: 5px;
  padding: 5px 0;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.18);
  background: #1f2a44;
  color: white;
  z-index: 100;
}

.header-title {
  color: white;
  font-weight: 700;
  font-size: 22px;
  letter-spacing: 0.5px;
}

.header-left {
  display: flex;
  align-items: center;
}

.menu-toggle {
  margin-right: 20px;
}

.minimal-mode-switch {
  margin-right: 20px;
}

.main-content {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 20px;
  height: calc(100vh - 60px);
  overflow: auto;
}

.main-content-content {
  background: #ffffff;
  border-radius: 18px;
  padding: 30px;
  box-shadow: 0 8px 24px rgba(20, 29, 47, 0.08);
  border: 1px solid #eef1f6;
  width: 100%;
  min-height: auto;
  box-sizing: border-box;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.92);
}

.header .el-switch__label {
  color: rgba(255, 255, 255, 0.92);
}

.header .el-button {
  border-color: rgba(255, 255, 255, 0.35);
  color: rgba(255, 255, 255, 0.92);
  background-color: rgba(255, 255, 255, 0.08);
}
</style>