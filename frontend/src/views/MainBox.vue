<template>
  <div class="common-layout">
    <el-container>
      <el-main>
        <router-view v-slot="{ Component }">
          <keep-alive :max="4">
            <component :is="Component"></component>
          </keep-alive>
        </router-view>
      </el-main>

      <el-footer>
        <van-tabbar v-model="active" route>
          <van-tabbar-item replace to="/index" name="chat-o" icon="chat-o">Message</van-tabbar-item>
          <van-tabbar-item replace to="/friend" name="friends-o" icon="friends-o">Address book</van-tabbar-item>
          <van-tabbar-item replace to="/found" name="discount" icon="discount">Discover</van-tabbar-item>
          <van-tabbar-item replace to="/my" name="user-o" icon="user-o">My</van-tabbar-item>
        </van-tabbar>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
const active = ref("chat-o")
</script>

<style lang='scss' scoped>
.el-container {
  height: 100%;
}

.el-main {
  padding: 0 !important;
}

.common-layout {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: rgb(30, 60, 83);
}

:deep(.van-tabbar) {
  height: inherit;
  background-color: rgb(30, 60, 83);
}

:deep(.van-tabbar-item--active) {
  background-color: rgb(30, 60, 83);
  color: var(--van-tabbar-item-active-color) !important;
}

:deep(.van-tabbar-item) {
  color: rgb(76, 147, 161);
}
</style>