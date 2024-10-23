<template>
  <el-container>
    <el-header>
      <van-nav-bar title="My"/>
    </el-header>
    <el-main>

      <van-row style="margin: 50px 0">
        <van-col span="12" style="text-align: center"><span class="text">Username：{{ store.user().value.username }}</span>
        </van-col>
        <van-col span="12" style="text-align: center"><span class="text">Number：{{ store.user().value.number }}</span>
        </van-col>
      </van-row>
      <van-form @submit="onSubmit" @failed="onFailed">
        <van-cell-group inset>
          <!-- 通过 pattern 进行正则校验 -->
          <van-field name="uploader" label="Avatar">
            <template #input>
              <van-uploader v-model="avatar" :max-size="isOverSize" :after-read="afterRead"
                            :before-read="beforeRead" reupload max-count="1" />
            </template>
          </van-field>
          <van-field name="switch" label="Online state">
            <template #input>
              <van-radio-group v-model="form.online" direction="horizontal">
                <van-radio :name="0" checked-color="#1989fa">offline</van-radio>
                <van-radio :name="1" checked-color="#1989fa">online</van-radio>
                <van-radio :name="2" checked-color="#1989fa">busy</van-radio>
              </van-radio-group>
            </template>
          </van-field>
          <van-field v-model="form.phone" placeholder="phone number" v-autofocus/>
        </van-cell-group>
        <div style="margin: 16px;">
          <van-button round block type="primary" native-type="submit" @click="handleEdit">
            Submit
          </van-button>
        </div>
      </van-form>
      <div style="margin: 16px;">
        <van-button round block type="danger" native-type="submit" @click="store.LogOut();router.push({name:'Login'})" loading-text="LOADING ...">
          Log out
        </van-button>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import {ref} from 'vue'
import {userStore} from "@/store/user.ts";
import {showSuccessToast, showToast} from "vant";
import userApi from "@/api/user.ts";
import axios from "axios";
import router from "@/router/index.js";

const store = userStore()
const form = ref({
  online: parseInt(store.user().value.online),
  phone: store.user().value.phone,
})
const avatar = ref([{"url": store.user().value.avatar}])
const onSubmit = (values) => {
  console.log('submit', values);
};

const onFailed = (errorInfo) => {
  console.log('failed', errorInfo);
};

const isOverSize = (file) => {
  const maxSize = file.type === 'image/jpeg' ? 500 * 1024 : 1000 * 1024;
  return file.size >= maxSize;
};

const beforeRead = (file) => {
  if (!/(jpg|jpeg|png|JPG|PNG)/i.test(file.type)) {
    showToast("Please upload images in the correct format");
    return false;
  }
  return true;
};

const afterRead = (file) => {
  // 此时可以自行将文件上传至服务器
  file.status = "uploading";
  file.message = "上传中...";
  // 创建一个空对象实例
  let formData = new FormData();
  formData.append("file", file.file);
  axios({
        url: "http://localhost:5000/file/avatar", method: "POST", data: formData,
        headers: {
          "content-type": "multipart/form-data",
          Authorization: 'bearer ' + store.token().value
        }
      }
  ).then((res) => {
    if (res.data.code === 200) {
      // 上传状态提示关闭
      file.status = "done";
      showSuccessToast(res.data.msg);
      avatar[0].url = res.data.data;
      store.user().value.avatar = res.data.data
    }
  })
};

const handleEdit = () => {
  userApi.UpdateUser({"online": form.value.online, "phone": form.value.phone}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg);
      store.user().value = res.data.user
    }
  })
}
</script>

<style lang='scss' scoped>
:deep(.van-cell-group) {
  background: transparent;
}

:deep(.van-cell__title) {
  color: #FFFFFF;
  opacity: .5;
}

:deep(.van-nav-bar) {
  background: transparent;
}

:deep(.van-nav-bar__title) {
  color: #FFFFFF;
  letter-spacing: 0.2vh;
}

:deep(.van-hairline--bottom:after) {
  opacity: .5;
}

.el-header {
  padding: 0;
}

:deep(.van-icon) {
  color: #FFFFFF;
  opacity: .5;
}

:deep(.van-cell) {
  background-color: transparent;
}

:deep(.van-cell:after) {
  left: 0;
  right: 0;
  opacity: .1;
}

.avatar-content {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;

  .text {
    font-size: large;
    color: #FFFFFF;
    letter-spacing: 0.2vw;
  }
}

.text {
  font-size: large;
  color: #FFFFFF;
  letter-spacing: 0.2vw;
  margin: 10px 0;
}

img {
  height: 10vh;
  width: 10vh;
  border-radius: 50%;
}

.el-main {
  padding: 0 !important;
}

:deep(.van-field__control) {
  color: #FFFFFF;
}

:deep(.van-radio__label) {
  color: #FFFFFF;
}
</style>