<template>
  <el-container style="font-size: large">
    <el-header>
      <van-nav-bar title="Discover">
        <template #right>
          <van-icon name="add-o" size="20" is-link @click="showPopup"/>
        </template>
      </van-nav-bar>
    </el-header>
    <el-main>
      <van-list>
        <van-cell title="Circle of friends" icon="friends" is-link to="index" @click="HandleFriend"
                  style="color: #FFFFFF;font-size: large">
        </van-cell>
        <!--        <van-cell title="漂流瓶" icon="map-marked" is-link to="index" @click="HandleBottle" style="color: #FFFFFF">-->
        <!--        </van-cell>-->
      </van-list>
    </el-main>
    <van-popup v-model:show="show" position="bottom" :style="{ height: '40%' }">
      <h4 style="text-align:center;padding: 10px">Release dynamic</h4>
      <van-form @submit="onSubmit">
        <van-field
            v-model="form.content"
            name="content"
            label="content"
            placeholder="content"
            :rules="[{ required: true, message: 'Please fill in the content' }]"
            v-autofocus
        />
        <van-field name="uploader" label="image">
          <template #input>
            <van-uploader v-model="form.image" :max-size="isOverSize" :after-read="afterRead"
                          :before-read="beforeRead" max-count="3" multiple/>
          </template>
        </van-field>
        <van-field name="uploader" label="video">
          <template #input>
            <van-uploader v-model="form.video" :max-size="isOverSize" :after-read="afterReadv"
                          :before-read="beforeReadv" reupload max-count="1" accept="*"/>
          </template>
        </van-field>

        <div style="margin: 16px;">
          <van-button round block type="primary" native-type="submit" @click="handleEdit()">
            Submit
          </van-button>
        </div>
      </van-form>
    </van-popup>
  </el-container>
</template>

<script setup>
import {ref, reactive} from 'vue'
import {useRouter} from 'vue-router'
import {showToast} from "vant";
import {userStore} from "@/store/user.ts";
import axios from "axios";
import groupApi from "@/api/group.ts";
import articleApi from "@/api/article.ts";

const router = useRouter()
const HandleFriend = () => {
  router.push('/friendpage')
}
const HandleBottle = () => {
  router.push({name: "Bottle"})
}
const show = ref(false);
const showPopup = () => {
  show.value = true;
};

const form = ref({
  content: "",
  image: [],
  imageT: [],
  video: [],
})
const onSubmit = (values) => {
  console.log('submit', values);
};

const onFailed = (errorInfo) => {
  console.log('failed', errorInfo);
};

const isOverSize = (file) => {
  return file.size >= 1000 * 1024 * 50; // 50mb以内
};

const beforeReadv = (file) => {
  if (!file.type.startsWith('video')) {
    showToast("Please upload a video in the correct format");
    return false;
  }
  return true;
};

const beforeRead = (file) => {
  if (!/(jpg|jpeg|png|JPG|PNG)/i.test(file.type)) {
    showToast("Please upload images in the correct format");
    return false;
  }
  return true;
};

const store = userStore()
const afterRead = (file) => {
  // 此时可以自行将文件上传至服务器
  console.log(file)
  file.status = "uploading";
  file.message = "上传中...";
  // 创建一个空对象实例
  let formData = new FormData();
  formData.append("file", file.file);
  axios({
        url: window.location.origin + "/api/file/avatar/group", method: "POST", data: formData,
        headers: {
          "content-type": "multipart/form-data",
          Authorization: 'bearer ' + store.token().value
        }
      }
  ).then((res) => {
    if (res.data.code === 200) {
      // 上传状态提示关闭
      file.status = "done";
      showToast("success！");
      form.value.imageT.push({'url': res.data.data})
      form.value.image = form.value.imageT
    }
  })
};
const afterReadv = (file) => {
  console.log(file)
  // 此时可以自行将文件上传至服务器
  file.status = "uploading";
  file.message = "上传中...";
  // 创建一个空对象实例
  let formData = new FormData();
  formData.append("file", file.file);
  axios({
        url: window.location.origin + "/api/file/avatar/group", method: "POST", data: formData,
        headers: {
          "content-type": "multipart/form-data",
          Authorization: 'bearer ' + store.token().value
        }
      }
  ).then((res) => {
    if (res.data.code === 200) {
      // 上传状态提示关闭
      file.status = "done";

      showToast("success！");
      form.value.video = [{'url': res.data.data}]
    }
  })
};
const handleEdit = () => {
  articleApi.PublishArticle({
    "content": form.value.content,
    "image": form.value.image,
    "video": form.value.video
  }).then((res) => {
    if (res.code === 200) {
      show.value = false
      showToast("success！");
    } else
      showToast(res.msg);
  })
}
</script>

<style lang='scss' scoped>
:deep(.van-nav-bar__title) {
  color: rgb(201, 208, 220);
  letter-spacing: 0.2vw;
}

:deep(.van-cell__title) {
  opacity: .5;
}

:deep(.van-icon) {
  color: #FFFFFF;
  opacity: .5;
}

:deep(.van-nav-bar) {
  background-color: transparent;
}

:deep(.van-cell) {
  background-color: transparent;
}

:deep(.van-hairline--bottom:after) {
  opacity: .5;
}


.text-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
}

.el-header {
  height: auto !important;
  padding: 0 !important;
}

.el-main {
  padding: 0 !important;
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
  opacity: .2;
}


:deep(.van-cell__value) {
  text-align: left;
}

.info-content {
  height: 24px;
  width: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: orange;
  border-radius: 5px;
}

:deep(.van-cell__value) {
  color: white;
}
</style>