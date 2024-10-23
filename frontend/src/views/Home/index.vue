<template>
  <el-container>
    <el-header>
      <van-nav-bar title="Message">
        <template #right>
          <van-icon name="map-marked" size="20" is-link @click="router.push({name:'Bottle'})"/>
        </template>
      </van-nav-bar>
    </el-header>
    <el-main>
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <van-list v-model:loading="loading" :finished="finished" @load="onLoad">
          <div v-for="(item, index) in histories" :key="index">
            <van-cell v-if="item.group" @click="handleGroup(item.group.id)">
              <van-row gutter="10">
                <van-col span="6" style="display: flex;align-items: center;justify-content: center;">
                  <img :src="item.group.avatar" alt="">
                </van-col>
                <van-col span="18">
                  <div class="text-content">
                    <div style="width: 100%;display: flex;justify-content: space-between;align-items: center;">
                      <span class="text">{{ item.group.name }}</span>
<!--                      <span><TimeDiff :dateTime="item.updated_at"></TimeDiff></span>-->
                      <span>{{item.updated_at}}</span>
                    </div>
                    <div>
                      <span v-if="item.message">{{ item.message }}</span>
                      <span v-else>media</span>
                    </div>
                  </div>
                </van-col>
              </van-row>
            </van-cell>
            <div v-if="item.sender">
              <van-cell v-if="item.sender.id === store.user().value.id">
                <van-row gutter="10" @click="handleChat(item.recipient.id)">
                  <van-col span="6" style="display: flex;align-items: center;justify-content: center;">
                    <img :src="item.recipient.avatar" alt="">
                  </van-col>
                  <van-col span="18">
                    <div class="text-content">
                      <div style="width: 100%;display: flex;justify-content: space-between;align-items: center;">
                        <span class="text" v-if="item.sender.id === item.recipient.id">myself</span>
                        <span class="text" v-else>{{ item.recipient.username }}</span>
<!--                        <span><TimeDiff :dateTime="item.updated_at"></TimeDiff></span>-->
                        <span>{{item.updated_at}}</span>
                      </div>
                      <div>
                        <span>{{ item.message }}</span>
                      </div>
                    </div>
                  </van-col>
                </van-row>
              </van-cell>
              <van-cell v-else>
              <van-row gutter="10" @click="handleChat(item.sender.id)">
                <van-col span="6" style="display: flex;align-items: center;justify-content: center;">
                  <img :src="item.sender.avatar" alt="">
                </van-col>
                <van-col span="18">
                  <div class="text-content">
                    <div style="width: 100%;display: flex;justify-content: space-between;align-items: center;">
                      <span class="text">{{ item.sender.username }}</span>
<!--                      <span><TimeDiff :dateTime="item.updated_at"></TimeDiff></span>-->
                      <span>{{item.updated_at}}</span>
                    </div>
                    <div>
                      <span>{{ item.message }}</span>
                    </div>
                  </div>
                </van-col>
              </van-row>
            </van-cell>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

    </el-main>
  </el-container>
</template>


<script setup>
import {ref, reactive, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import {userStore} from "@/store/user.ts";
import TimeDiff from "@/components/TimeDiff.vue";
import MyServer from "@/utils/mySocket.ts";

const {socket} = MyServer.getInstance();
const store = userStore()
const list = ref([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);
const router = useRouter()

const histories = ref(store.histories(store.user().value.number).value)

store.joined_history()
const onLoad = () => {
  setTimeout(() => {
    if (refreshing.value) {
      list.value = [];
      refreshing.value = false;
    }
    socket.emit('history', {"token": store.token().value});
    socket.on('history_message', (data) => {
      //这是接收到的客户端消息
      console.log(data);
      histories.value = data.history
      store.histories(store.user().value.number).value = data.history
    })
    loading.value = false;
    finished.value = true;
  }, 1000);
};

const onRefresh = () => {
  finished.value = false;
  loading.value = true;
  onLoad();
};

const handleChat = (i) => {
  console.log(i);
  router.push(`/index/${i}`)
}

const handleGroup = (i) => {
  console.log(i);
  router.push(`/group/${i}`)
}

</script>

<style lang='scss' scoped>
img {
  height: 8vh;
  width: 8vh;
  border-radius: 50%;
}

.text-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;

  .text {
    font-size: large;
    color: #FFFFFF;
  }
}

.el-header {
  height: auto !important;
  padding: 0 !important;
}

.el-main {
  padding: 0 !important;
  background-color: rgb(20, 42, 59) !important;
}

.el-container {
  height: 100%;
}

:deep(.van-nav-bar__right) {
  gap: 10px;
  padding: 0 10px;
}


:deep(.van-cell:after) {
  left: 0;
  right: 0;
  border-bottom: 1px solid #FFFFFF;
  opacity: .2;
}

:deep(.van-cell__title,
  .van-cell__value) {
  flex: 0;
}

:deep(.van-cell__value) {
  text-align: left;
}

:deep(.van-cell) {
  background: transparent;
  height: 12vh;
}

:deep(.van-row) {
  height: 100%;
}

:deep(.van-nav-bar__content) {
  background-color: rgb(20, 42, 59);
}

:deep(.van-nav-bar__title) {
  color: rgb(201, 208, 220);
  letter-spacing: 0.2vw;
}

:deep(.van-hairline--bottom:after) {
  opacity: .5;
}
</style>