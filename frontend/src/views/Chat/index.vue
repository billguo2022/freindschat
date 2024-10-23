<template>
  <el-container>
    <el-header>
      <el-row :gutter="12">
        <el-col :span="4">
          <div class="left-back" @click="$router.back()">
            <van-icon name="arrow-left" size="20"/>
          </div>
        </el-col>
        <el-col :span="16">
          <div class="avatar-content">
            <img :src="user.avatar" alt="">
            <div style="display: flex;align-items: center;justify-content: space-between;width: 100%"><span
                class="text">{{ user.username }}</span><span>
              <van-tag type="success" v-if="user.online === 1">online</van-tag>
                  <van-tag type="danger" v-if="user.online === 0">offline</van-tag>
                  <van-tag type="warning" v-if="user.online === 2">busy</van-tag>
            </span></div>
          </div>
        </el-col>
      </el-row>
    </el-header>
    <el-main>
      <div v-for="(item,index) in messages" :key="index">
        <!--        <div class="chat-time">{{ dateChange(item.timestamp) }}</div>-->
        <div class="chat-time">{{ item.created_at }}</div>
        <div class="other-content" v-if="item.sender.id !== store.user().value.id">
          <div style="display: flex;flex-direction: column">
            <span style="color: #FFFFFF">{{ item.sender.username }}</span>
            <img :src="item.sender.avatar" alt="" style="width: 50px;height: 50px;margin-left: 10px">
          </div>
          <div class="my-talk-bubble" v-if="item.content">
            <div class="talktext">
              <p>{{ item.content }}</p>
            </div>
          </div>
          <img :src="item.image_url" alt="" v-else-if="item.image_url" style="border-radius: 0">
          <!--          <audio ref="audioPlayer1" controls v-else-if="item.audio_url" @click="handleAudioPlay">-->
          <!--            <source :src="item.audio_url" type="audio/mp3" ref="audioPlayer1">-->
          <!--          </audio>-->
          <audio controls v-else-if="item.audio_url">
            <source :src="item.audio_url" type="audio/mp3">
          </audio>
        </div>
        <div class="my-content" v-if="item.sender.id === store.user().value.id">
          <div class="my-talk-bubble" v-if="item.content">
            <div class="talktext">
              <p>{{ item.content }}</p>
            </div>
          </div>
          <img :src="item.image_url" alt="" v-else-if="item.image_url" style="border-radius: 0">
          <!--          <audio ref="audioPlayer1" controls v-else-if="item.audio_url" @click="handleAudioPlay">-->
          <!--            <source :src="item.audio_url" type="audio/mp3" ref="audioPlayer1">-->
          <!--          </audio>-->
          <audio controls v-else-if="item.audio_url">
            <source :src="item.audio_url" type="audio/mp3">
          </audio>
          <div style="display: flex;flex-direction: column">
            <span style="color: #FFFFFF">{{ item.sender.username }}</span>
            <img :src="item.sender.avatar" alt="" style="width: 50px;height: 50px;margin-left: 10px">
          </div>
        </div>
      </div>
    </el-main>
    <el-footer>
      <van-cell-group inset>
        <van-field v-model="form.content" placeholder="Send Your Message" v-autofocus>
          <template #left-icon>
            <el-icon size="25" color="#FFFFFF" @mousedown="startRecording" @mouseup="stopRecording"
                     @touchstart="startRecording" @touchmove="stopRecording" @touchend="stopRecording">
              <Microphone/>
            </el-icon>
            <el-icon size="25" color="#FFFFFF" @click="sendpic()" style="margin-left: 20px">
              <Picture/>
            </el-icon>
          </template>
          <template #right-icon>
            <el-icon size="25" color="#FFFFFF" @click="sendMsgToServer()">
              <Right/>
            </el-icon>
          </template>
        </van-field>
      </van-cell-group>
    </el-footer>
  </el-container>
  <van-popup v-model:show="pic_show" position="bottom" :style="{ height: '35%' }">
    <h4 style="text-align:center;padding: 10px">Send pictures</h4>
    <van-form @submit="onSubmit">
      <van-field name="uploader" label="avatar">
        <template #input>
          <van-uploader v-model="image" :max-size="isOverSize" :after-read="afterRead"
                        :before-read="beforeRead" reupload max-count="1"/>
        </template>
      </van-field>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" @click="sendMsgToServer()">
          submit
        </van-button>
      </div>
    </van-form>
  </van-popup>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import userApi from "@/api/user.ts";
import {userStore} from "@/store/user.ts";
import {showToast} from "vant";
import axios from "axios";
import MyServer from "@/utils/mySocket.ts";
import {getTimeStringAutoShort} from "@/utils/myDate.js";

// const audioPlayer1 = ref(null)
const {socket} = MyServer.getInstance();
const store = userStore()
const router = useRouter()
const route = useRoute()
const user = ref({})
const room = ref([store.user().value.id, route.params.id].sort().join('_'))
const form = ref({
  content: "",
  recipient_id: "",
  image_url: "",
  audio_url: "",
  token: store.token().value,
  room: room.value
})

const dateChange = (val) => {
  return getTimeStringAutoShort(val, true);
}
const mediaRecorder = ref(null)
const audioChunks = ref([])
const startRecording = () => {
  navigator.mediaDevices.getUserMedia({audio: true})
      .then((stream) => {
        mediaRecorder.value = new MediaRecorder(stream);
        audioChunks.value = [];
        mediaRecorder.value.ondataavailable = (e) => {
          if (e.data.size > 0) {
            audioChunks.value.push(e.data);
          }
        };
        mediaRecorder.value.start();
      })
      .catch((error) => {
        console.error('Recording failed:', error);
      });
}
const stopRecording = () => {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop();
    mediaRecorder.value.onstop = () => {
      const audioBlob = new Blob(audioChunks.value, {type: 'audio/mp3'});
      sendAudio(audioBlob);
    };
  }
}
const sendAudio = (audioBlob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.mp3');

  axios(window.location.origin + '/api/file/audio', {
    method: 'POST',
    data: formData,
    headers: {
      // "content-type": "multipart/form-data",
      Authorization: 'bearer ' + store.token().value
    }
  })
      .then((response) => {
        if (response.data.code === 200) {
          console.log(response.data.data)
          form.value.audio_url = response.data.data
          sendMsgToServer()
        }
      })
      .catch((error) => {
        console.error('Sending audio failed:', error);
      });
}

const messages = ref(store.group(room.value))
const handleAudioPlay = () => {
  if (window.navigator.userAgent.match(/(iPod|iPhone|iPad)/)) {
    audioPlayer1.value[0].play();
  }
}
const playAudio = () => {
  audioPlayer1.value[0].play();
}
onMounted(() => {
  userApi.GetUserInfoById({"id": route.params.id}).then((res) => {
    if (res.code === 200) {
      user.value = res.data
    }
  })
  store.joined_user(store.user().value.id, route.params.id)
  socket.on('joined_user_message', (data) => {
    //这是接收到的客户端消息
    messages.value = data.message
    store.group(room.value).value = data.message
  })
  // console.log(audioPlayer1.value[0])
  // audioPlayer1.value[0].addEventListener('loadeddata', playAudio);
})


socket.on('user_message', (data) => {
  //这是接收到的客户端消息
  console.log(data);
  let aa = [...messages.value, data.message]
  messages.value = aa
  store.group(room.value).value = messages.value
})

const sendMsgToServer = () => {
  if (form.value.image_url === "" && form.value.audio_url === "" && form.value.content === "") {
    return
  }
  form.value.recipient_id = user.value.id
  socket.emit('privateChat', form.value);
  form.value.content = ''
  form.value.image_url = ''
  form.value.audio_url = ''
  pic_show.value = false
  image.value = []
  console.log(form.value)
}


const image = ref([])


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
const onSubmit = (values) => {
  console.log('submit', values);
};
const afterRead = (file) => {
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
      form.value.image_url = res.data.data
      image.value = [{'url': res.data.data}]
    }
  })
};
const pic_show = ref(false)
const sendpic = () => {
  pic_show.value = true
}
</script>

<style lang='scss' scoped>
:deep(.van-cell) {
  background: rgb(20, 42, 59);
  line-height: normal;
}

:deep(.van-cell-group) {
  background: transparent;
}

.footer-icon {
  display: flex;
  justify-content: center;
  align-items: center;
}

.el-footer {
  height: auto;
  padding: 1vh 0;
}

.chat-time {
  font-size: 16px;
  color: #f0f0f0;
  line-height: 17px;
  padding: 30px 0;
  text-align: center;
}

.other-content {
  display: flex;
  justify-content: flex-start;
  padding-bottom: 2vh;
}

.my-content {
  display: flex;
  justify-content: flex-end;
  padding-bottom: 2vh;
}

.my-talk-bubble {
  border-radius: 10px 10px 0 10px;
  overflow: visible;
  text-overflow: initial;
  white-space: normal;
  height: auto;
  background-color: var(--el-menu-active-color);
  max-width: 80%;
}

.other-talk-bubble {
  border-radius: 10px 10px 10px 0;
  overflow: visible;
  text-overflow: initial;
  white-space: normal;
  height: auto;
  background-color: var(--el-menu-active-color);
  max-width: 80%;
}

.talktext {
  padding: 1.5vh;
  line-height: 2vh;
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

.van-icon {
  color: #FFFFFF;
  opacity: .5;
}

.left-back {
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.el-container {
  height: 100%;
  background-color: rgb(20, 42, 59) !important;
}

.el-header {
  height: auto;
  padding: 2vh 0;
  border-bottom: 1px solid rgba($color: #FFFFFF, $alpha: .1);
}

.el-main {
  border-bottom: 1px solid rgba($color: #FFFFFF, $alpha: .1);
}

img {
  height: 10vh;
  width: 10vh;
  border-radius: 50%;
}

:deep(.van-field__control) {
  color: #FFFFFF;
}
</style>