<template>
  <router-view v-if="isPublicPage" />

  <div v-else id="app">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h3>餐饮管理系统</h3>
      </div>

      <el-menu :default-active="activeIndex" :unique-opened="true" :router="true" class="sidebar-menu">
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="/management">
          <template #title>
            <el-icon><List /></el-icon>
            <span>基础管理</span>
          </template>
          <el-menu-item index="/dishes">菜品管理</el-menu-item>
          <el-menu-item index="/categories">分类管理</el-menu-item>
          <el-menu-item index="/tables">桌台管理</el-menu-item>
          <el-menu-item index="/table-dashboard">桌台监控</el-menu-item>
          <el-menu-item index="/users">用户管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/order">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>订单中心</span>
          </template>
          <el-menu-item index="/orders">订单管理</el-menu-item>
          <el-menu-item index="/order-entry">老板下单</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>

        <el-sub-menu index="/special">
          <template #title>
            <el-icon><Star /></el-icon>
            <span>运营工具</span>
          </template>
          <el-menu-item index="/special-functions">今日特价/沽清</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="!minimalMode" index="/advanced">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>高级模块</span>
          </template>
          <el-menu-item index="/members">会员管理</el-menu-item>
          <el-menu-item index="/marketing">营销活动</el-menu-item>
          <el-menu-item index="/financial">财务管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button @click="toggleSidebar" class="menu-toggle" circle>
            <el-icon><Menu /></el-icon>
          </el-button>
          <el-switch
            v-model="minimalMode"
            class="minimal-mode-switch"
            active-text="极简模式"
            inactive-text="标准模式"
            inline-prompt
            active-color="#e17d3f"
            inactive-color="#c8b5a4"
          />
        </div>

        <div class="header-right">
          <el-dropdown @command="handleUserCommand">
            <span class="el-dropdown-link">
              {{ username }}
              <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
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

    <QuickOrderPanel />
  </div>
</template>

<script>
import { DataAnalysis, Document, House, List, Menu, Setting, Star } from '@element-plus/icons-vue'
import QuickOrderPanel from '@/components/QuickOrderPanel.vue'
import { getCurrentUsername, logout } from '@/services/authService'

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
      minimalMode: false,
      username: getCurrentUsername()
    }
  },
  computed: {
    isPublicPage() {
      return Boolean(this.$route.meta?.public)
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
    },
    handleUserCommand(command) {
      if (command === 'logout') {
        logout()
        this.$message.success('已退出登录')
        this.$router.replace('/login')
        return
      }

      if (command === 'profile') {
        this.$message.info('个人中心待实现')
        return
      }

      if (command === 'password') {
        this.$message.info('修改密码待实现')
      }
    }
  },
  watch: {
    $route(to) {
      this.activeIndex = to.path
      this.username = getCurrentUsername()
    }
  },
  mounted() {
    this.activeIndex = this.$route.path
    this.username = getCurrentUsername()
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
  --menu-bg-start: #3a2418;
  --menu-bg-end: #2a1a12;
  --menu-text: #f4d8c4;
  --menu-hover: rgba(228, 143, 81, 0.22);
  --menu-active-start: #d96e33;
  --menu-active-end: #bf5723;
  --line: rgba(255, 230, 212, 0.14);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #3a2418;
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
  background: linear-gradient(180deg, var(--menu-bg-start) 0%, var(--menu-bg-end) 100%);
  height: 100vh;
  flex-shrink: 0;
  transition: all 0.3s;
  box-shadow: 4px 0 18px rgba(92, 48, 24, 0.28);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffe3cf;
  font-weight: 700;
  border-bottom: 1px solid var(--line);
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
  min-height: 400px;
}

.el-menu {
  border: none;
  background-color: transparent !important;
}

.el-menu-item,
.el-sub-menu__title,
.el-sub-menu .el-menu-item {
  color: var(--menu-text);
  background-color: transparent !important;
  transition: all 0.25s ease;
}

.el-sub-menu .el-menu-item {
  min-width: 176px;
  padding-left: 48px;
}

.el-menu-item:hover,
.el-sub-menu__title:hover,
.el-sub-menu .el-menu-item:hover {
  color: #fff9f5 !important;
  background-color: var(--menu-hover) !important;
}

.el-menu-item.is-active,
.el-sub-menu .el-menu-item.is-active {
  background: linear-gradient(90deg, var(--menu-active-start), var(--menu-active-end)) !important;
  color: #fff !important;
  font-weight: 700;
  box-shadow: inset 2px 0 0 rgba(255, 255, 255, 0.55);
}

.el-menu-item .el-icon,
.el-sub-menu__title .el-icon {
  color: inherit;
}

.el-menu-item:focus,
.el-sub-menu__title:focus {
  background-color: transparent !important;
  outline: none;
}

.el-sub-menu .el-menu {
  background-color: rgba(255, 255, 255, 0.04) !important;
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
  box-shadow: 0 2px 10px rgba(139, 72, 33, 0.14);
  background: #fff4ea;
  color: #613a28;
  border-bottom: 1px solid #f1dac8;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.menu-toggle {
  margin-right: 16px;
  border-color: #e5bea5;
  color: #8c502f;
  background: #fff9f3;
}

.minimal-mode-switch {
  margin-right: 16px;
}

.main-content {
  background: radial-gradient(circle at 0 0, #fff3e7 0%, #fff8f2 44%, #fffaf6 100%);
  padding: 20px;
  height: calc(100vh - 60px);
  overflow: auto;
}

.main-content-content {
  background: #fffdfb;
  border-radius: 18px;
  padding: 30px;
  box-shadow: 0 8px 24px rgba(162, 88, 44, 0.1);
  border: 1px solid #f2ddcf;
  width: 100%;
  min-height: auto;
  box-sizing: border-box;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #714833;
  font-weight: 600;
}

.header .el-switch__label {
  color: #7f563f;
}

.header .el-button {
  border-color: #e5bea5;
  color: #8c502f;
  background-color: #fff9f3;
}
</style>
