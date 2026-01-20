<template>
  <div id="app">
    <el-container style="height: 100vh">
      <el-header class="app-header">
        <div class="header-title">
          <el-icon :size="24" style="margin-right: 8px"><VideoCamera /></el-icon>
          <h2>Web Session Recorder</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
          router
          class="header-menu"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/sessions">
            <el-icon><List /></el-icon>
            <span>录制列表</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { VideoCamera, HomeFilled, List, Setting } from '@element-plus/icons-vue'

const route = useRoute()

// Compute active menu based on current route
const activeMenu = computed(() => {
  return route.path
})
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  padding: 0;
}

.app-header {
  background-color: #545c64;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-title {
  display: flex;
  align-items: center;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-menu {
  border-bottom: none;
}

.header-menu .el-menu-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
