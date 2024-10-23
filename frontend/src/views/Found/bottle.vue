<script setup>
import {useRouter} from "vue-router";
import {onMounted, ref} from "vue"
import bottleApi from "@/api/bottle.ts";
import {showFailToast, showSuccessToast, showToast} from "vant";
import userApi from "@/api/user.ts";
import {userStore} from "@/store/user.ts";
import friendApi from "@/api/friend.ts";

const store = userStore()
const router = useRouter()
const onClickLeft = () => router.back();
const locationForm = ref({
  latitude: "",
  longitude: ""
})

onMounted(() => {
  navigator.geolocation.getCurrentPosition(d => {
    if (d !== undefined) {
      console.log(d)
      locationForm.latitude = d.coords.latitude
      locationForm.longitude = d.coords.longitude
      if (locationForm.longitude !== "" && locationForm.latitude !== "") {
        userApi.UpdateUserLocation({
          "latitude": locationForm.latitude,
          "longitude": locationForm.longitude
        }).then((res) => {
          if (res.code === 200) {
          }
        })
      } else showFailToast("Get location failure")
    }
  }, d => {
    console.log(d)
  });

  get_temporarily_bottle()
})

const formPickBottom = ref({
  bottles: store.bottle().value.id ? store.bottle().value : "",
})

const formPickBottom1 = ref({
  user: "",
})

const get_temporarily_bottle = () => {
  bottleApi.GetTemporarilyBottle().then((res) => {
    if (res.code === 200) {
      store.bottle().value = res.data.bottles
      formPickBottom.value.bottles = res.data.bottles
    }
  })
}
// 捡一个
const submitBottomPick = () => {
  bottleApi.PickBottle({}).then((res) => {
    if (res.code === 200) {
      if (!res.data) {
        showSuccessToast("There are no bottles at the moment.")
      }
      showSuccessToast(res.msg)
      formPickBottom1.value.user = res.data.user
      store.bottle1().value = res.data.user
      get_temporarily_bottle()
    }
  })
}

// 收瓶子
const submitBottomGive = (id) => {
  bottleApi.GiveBottle({"id": id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast("Wait for consent")
      store.bottle().value = {}
      formPickBottom.value = ""
    } else
      showToast(res.msg);
  })
}

// 同意
const submitBottomAgree = (friend_table_id) => {
  friendApi.AgreeFriend({"id": friend_table_id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      get_temporarily_bottle()
    }
  })
}

// 拒绝
const submitBottomRefuse = (friend_table_id) => {
  friendApi.RefuseFriend({"id": friend_table_id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      get_temporarily_bottle()
    }
  })
}

const submitTemBottomRefuse = (id) => {
  friendApi.RefuseTemFriend({"id": id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      get_temporarily_bottle()
    }
  })
}
</script>

<template>
  <el-container>
    <el-header>
      <van-nav-bar title="Current bottle" left-arrow @click-left="onClickLeft"/>
    </el-header>
    <el-main>
      <div class="wrapper">
        <div class="btns">
          <van-button type="primary" @click="submitBottomPick()">Pick up one</van-button>
        </div>
      </div>
      <div v-if="formPickBottom.bottles.length>0">
        <h3 style="color: #FFFFFF">My box</h3>
        <div style="color: #FFFFFF;border-radius: 20px;border: #FFFFFF 1px solid;margin: 20px 0;padding:20px"
             v-for="item in formPickBottom.bottles" :key="item.id">
          <el-row :gutter="15" v-if="item.user.id  === store.user().value.id">
            <el-col :span="4">
              <img :src="item.friend.avatar" alt="" style="width: 50px;height: 50px">
            </el-col>
            <el-col :span="16">
              <div style="display: flex;flex-direction: column;justify-content: flex-start;margin-left: 20px"
                   @click="router.push(`/index/${item.friend.id}`)">
                <div>
                  name: {{ item.friend.username }}
                </div>
                <span style="margin-top: 10px"><van-tag type="success"
                                                        v-if="item.friend.online === 1">online</van-tag>
                  <van-tag type="danger" v-if="item.friend.online === 0">offline</van-tag>
                  <van-tag type="warning" v-if="item.friend.online === 2">busy</van-tag></span>
              </div>
            </el-col>
            <el-col :span="4">
              <div style="display: flex;align-items: center;flex-direction: column;justify-content: center">
                <van-button size="mini" @click="submitBottomGive(item.friend.id)" icon="plus" round
                            style="margin-bottom: 10px;margin-left: 0"></van-button>
                <van-button size="mini" @click="submitTemBottomRefuse(item.id)" icon="minus" style="margin-left: 0"
                            round></van-button>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="15" v-else>
            <el-col :span="4">
              <img :src="item.user.avatar" alt="" style="width: 50px;height: 50px">
            </el-col>
            <el-col :span="16">
              <div style="display: flex;flex-direction: column;justify-content: flex-start;margin-left: 20px"
                   @click="router.push(`/index/${item.user.id}`)">
                <div>
                  name: {{ item.user.username }}
                </div>
                <span style="margin-top: 10px"><van-tag type="success"
                                                        v-if="item.user.online === 1">online</van-tag>
                  <van-tag type="danger" v-if="item.user.online === 0">offline</van-tag>
                  <van-tag type="warning" v-if="item.user.online === 2">busy</van-tag></span>
              </div>
            </el-col>
            <el-col :span="4">
              <div style="display: flex;align-items: center;flex-direction: column;justify-content: center"
                   v-if="item.state">
                <van-button size="mini" @click="submitBottomAgree(item.friend_table_id)" round
                            style="margin-bottom: 10px;margin-left: 0">agree
                </van-button>
                <van-button size="mini" @click="submitBottomRefuse(item.friend_table_id)" round style="margin-left: 0">
                  reject
                </van-button>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-main>
  </el-container>
</template>
<style>

</style>
<style scoped lang="scss">


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

.el-container {
  height: 100%;
  background-color: rgb(20, 42, 59);
}

.wrapper {
  color: #FFFFFF;

  .btns {
    margin: 10px;
    display: flex;
    align-items: center;
    justify-content: space-around;
  }
}

</style>