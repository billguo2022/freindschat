<template>
  <el-container>
    <el-header>
      <div>
        <el-row>
          <el-col :span="2">
            <div class="left-back" @click="$router.back()">
              <van-icon name="arrow-left" size="20"/>
            </div>
          </el-col>
          <el-col :span="22">
            <van-search v-model="input" show-action placeholder="Group ID, name" v-autofocus>
              <template #action>
                <div style="color: #FFFFFF;" @click="onClickButton">search</div>
              </template>
            </van-search>
          </el-col>
        </el-row>
      </div>
    </el-header>
    <el-main>
      <van-list v-model:loading="loading" :finished="finished" finished-text="No more..." @load="onLoad" v-if="show">
        <van-cell v-for="(item, index) in list" :key="index" @click="handleChat(item.id)">
          <van-row gutter="10">
            <van-col span="6" style="display: flex;align-items: center;justify-content: center;">
              <img :src="item.avatar" alt="">
            </van-col>
            <van-col span="12">
              <div
                  style="height: 100%;display: flex;flex-direction: column;justify-content:center;align-items: flex-start;">
                <span class="text">{{ item.name }}</span>
              </div>
            </van-col>
            <van-col span="6" style="display: flex;align-items: center;justify-content: center;">
              <van-button icon="plus" type="primary" round/>
            </van-col>
          </van-row>
        </van-cell>
      </van-list>
    </el-main>
  </el-container>
</template>

<script setup>
import {ref, reactive} from 'vue'
import friendApi from "@/api/friend.ts";
import {showSuccessToast, showToast} from "vant";
import router from "@/router/index.js";
import groupApi from "@/api/group.ts";

const input = ref('')

const list = ref([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);
const show = ref(false)
const onClickButton = () => {
  if (input.value === '') {
    showToast("Enter")
    return
  }
  groupApi.SelectGroup({"kw": input.value}).then((res) => {
    if (res.code === 200) {
      list.value = [res.data]
      show.value = true
      loading.value = false
      finished.value = true;
      refreshing.value = false;
    }
  })
}

const handleChat = (id) => {
  groupApi.JoinGroup({"id": id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      router.push({name: 'Friend'})
    }
  })
}
</script>

<style lang='scss' scoped>
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