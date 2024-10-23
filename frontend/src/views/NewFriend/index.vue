<template>
  <el-container>
    <el-header>
      <van-nav-bar title="New friend" left-arrow @click-left="router.back()"/>
    </el-header>
    <el-main>
      <van-list v-model:loading="loading" :finished="finished" finished-text="No more..." @load="onLoad">
        <van-cell v-for="(item, index) in list" :key="index" @click="handleChat(item.id)">
          <van-row gutter="10">
            <van-col span="6" style="display: flex;align-items: center;justify-content: center;">
              <img :src="item.user.avatar" alt="">
            </van-col>
            <van-col span="12">
              <div
                  style="height: 100%;display: flex;flex-direction: column;justify-content:center;align-items: flex-start;">
                <span class="text">{{ item.user.username }}</span>
                <span class="text">
                  <van-tag type="success" v-if="item.user.online === 1">online</van-tag>
                  <van-tag type="danger" v-if="item.user.online === 0">offline</van-tag>
                  <van-tag type="warning" v-if="item.user.online === 2">busy</van-tag>
                </span>
<!--                <span class="text">-->
<!--                  <van-tag type="success" v-if="item.type_number === 0">Normal</van-tag>-->
<!--                  <van-tag type="danger" v-if="item.type_number === 1">Bottle</van-tag>-->
<!--                </span>-->
              </div>
            </van-col>
            <van-col span="6" style="display: flex;align-items: center;justify-content: center;">
              <van-button type="primary" round>agree</van-button>
            </van-col>
          </van-row>
        </van-cell>
      </van-list>
    </el-main>
  </el-container>
</template>

<script setup>
import {ref} from 'vue'
import friendApi from "@/api/friend.ts";
import {showSuccessToast, showToast} from "vant";
import router from "@/router/index.js";
import userApi from "@/api/user.ts";

const list = ref([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);

const load_re = () => {
  friendApi.GetAgreeFriend().then((res) => {
    list.value = res.data.not_friends
  })
}
const onLoad = () => {
  setTimeout(() => {
    if (refreshing.value) {
      list.value = [];
      refreshing.value = false;
    }
    load_re()
    loading.value = true;
    finished.value = true
  }, 1000);
};

const handleChat = (id) => {
  friendApi.AgreeFriend({"id": id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      router.push({name: 'Friend'})
    }
  })
}
</script>

<style lang='scss' scoped>
:deep(.el-card) {
  background-color: transparent;
  border: none;
  color: #FFFFFF;
}

:deep(.el-card__header) {
  border-bottom: none;
  padding: 5px;
}

:deep(.el-card__body) {
  padding: 5px;
}

img {
  height: 6vh;
  width: 6vh;
}

:deep(.van-nav-bar) {
  background: transparent;
}

:deep(.van-hairline--bottom:after) {
  opacity: .5;
}

:deep(.van-nav-bar__title) {
  color: #FFFFFF;
  letter-spacing: 0.2vh;
}

.el-header {
  padding: 0;
}

img {
  height: 8vh;
  width: 8vh;
  border-radius: 50%;
}

:deep(.van-cell) {
  background-color: transparent;
}

.left-back {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #FFFFFF;
}

:deep(.van-field__control) {
  color: #FFFFFF;
}

.el-container {
  height: 100%;
  background-color: rgb(30, 60, 83);
}

:deep(.van-search) {
  background: transparent;
}

:deep(.van-search__field) {
  border: 1px solid #FFFFFF;
  opacity: .5;
  border-radius: 5px;
}

:deep(.van-search__content) {
  background: transparent;
}

.el-header {
  padding: 0;
  height: auto;
}
</style>