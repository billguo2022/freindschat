<template>
  <el-container style="font-size: large;">
    <el-header>
      <van-nav-bar title="Address book">
        <template #right>
          <van-icon name="add-o" size="20" is-link @click="showPopup"/>
        </template>
      </van-nav-bar>
    </el-header>
    <el-main>
      <van-list>
        <van-cell>
          <van-row gutter="10">
            <van-col span="2">
              <div class="info-content">
                <van-icon name="add-o"/>
              </div>
            </van-col>
            <van-col span="22">
              <span @click="addUser()" style="cursor: pointer">Add friends</span>
            </van-col>
          </van-row>
        </van-cell>
        <van-cell>
          <van-row gutter="10">
            <van-col span="2">
              <div class="info-content">
                <van-icon name="add-o"/>
              </div>
            </van-col>
            <van-col span="22">
              <span @click="addGroup()" style="cursor: pointer">Add a group chat</span>
            </van-col>
          </van-row>
        </van-cell>
        <van-cell>
          <van-row gutter="10">
            <van-col span="2">
              <div class="info-content">
                <van-icon name="add-o"/>
              </div>
            </van-col>
            <van-col span="22">
              <span @click="newFriend()" style="cursor: pointer">New friend</span>
            </van-col>
          </van-row>
        </van-cell>
        <van-cell>
          <van-row gutter="10">
            <van-col span="2">
              <div class="info-content">
                <van-icon name="add-o"/>
              </div>
            </van-col>
            <van-col span="22">
              <span @click="router.push(`/index/${store.user().value.id}`)" style="cursor: pointer">oneself</span>
            </van-col>
          </van-row>
        </van-cell>
      </van-list>
      <div style="color: #FFFFFF;margin:30px 20px">Friend</div>

      <van-cell v-for="item in friends">
        <van-row gutter="10">
          <van-col span="2">
            <div class="info-content">
              <img :src="item.avatar" alt="" style="width: 100%;height: 100%">
            </div>
          </van-col>
          <van-col span="16">
            <span style="cursor: pointer" @click="showUser(item)">{{ item.username }}</span>
          </van-col>
          <van-col span="6">
              <span class="text"><van-tag type="success" v-if="item.online === 1">online</van-tag>
                  <van-tag type="danger" v-if="item.online === 0">offline</van-tag>
                  <van-tag type="warning" v-if="item.online === 2">busy</van-tag></span>
          </van-col>
        </van-row>
      </van-cell>

      <div style="color: #FFFFFF;margin:20px">Group chat</div>

      <van-cell v-for="item in groups">
        <van-row gutter="10">
          <van-col span="2">
            <div class="info-content">
              <img :src="item.avatar" alt="" style="width: 100%;height: 100%">
            </div>
          </van-col>
          <van-col span="20">
            <span style="cursor: pointer" @click="showGroup(item)">{{ item.name }}</span>
          </van-col>
        </van-row>
      </van-cell>

    </el-main>
    <van-popup v-model:show="show" position="bottom" :style="{ height: '35%' }">
      <h4 style="text-align:center;padding: 10px">Create/modify group chats</h4>
      <van-form @submit="onSubmit">
        <van-field
            v-model="form.name"
            name="name"
            label="name"
            placeholder="name"
            :rules="[{ required: true, message: 'Please fill in the name' }]"
        />
        <van-field name="uploader" label="avatar">
          <template #input>
            <van-uploader v-model="form.avatar" :max-size="isOverSize" :after-read="afterRead"
                          :before-read="beforeRead" reupload max-count="1"/>
          </template>
        </van-field>

        <div style="margin: 16px;">
          <van-button round block type="primary" native-type="submit" @click="handleEdit()">
            Submit
          </van-button>
        </div>
      </van-form>
    </van-popup>
    <van-popup v-model:show="show_user" position="bottom" :style="{ height: '35%' }">
      <h4 style="text-align:center;padding: 10px">Details</h4>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" @click="handleChat()">
          Direct Message
        </van-button>
      </div>
      <div style="margin: 16px;">
        <van-button round block type="danger" native-type="submit" @click="handleUserDel()">
          Delete
        </van-button>
      </div>
    </van-popup>
    <van-popup v-model:show="show_group" position="bottom" :style="{ height: '35%' }">
      <h4 style="text-align:center;padding: 10px">Details</h4>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" @click="handleGroupChat()">
          Enter a group chat
        </van-button>
      </div>

      <div v-if="group.owner === store.user().value.number">
        <div style="margin: 16px;">
          <van-button round block type="danger" native-type="submit" @click="handleGroupMyDel()">
            Disband a group chat
          </van-button>
        </div>
        <div style="margin: 16px;">
          <van-button round block type="danger" native-type="submit" @click="handleGroupEdit()">
            Modify group chat
          </van-button>
        </div>
      </div>
      <div style="margin: 16px;" v-else>
        <van-button round block type="danger" native-type="submit" @click="handleGroupDel()">
          Exit a group chat
        </van-button>
      </div>
    </van-popup>
  </el-container>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import friendApi from "@/api/friend.ts";
import {showSuccessToast, showToast} from "vant";
import axios from "axios";
import userApi from "@/api/user.ts";
import {userStore} from "@/store/user.ts";
import groupApi from "@/api/group.ts";

const router = useRouter()
const id = ref()
const friends = ref([])
const groups = ref([])
const user = ref()
const group = ref()

// 跳转到好友聊天
const handleChat = () => {
  router.push(`/index/${user.value.id}`)
}

// 跳转到群聊天
const handleGroupChat = () => {
  router.push(`/group/${group.value.id}`)
}

// 跳转到添加用户
const addUser = () => {
  router.push('/add')
}

// 跳转到添加群聊
const addGroup = () => {
  router.push('/addGroup')
}
// 跳转到新的朋友
const newFriend = () => {
  router.push('/newFriend')
}

// 删除好友
const handleUserDel = () => {
  friendApi.DeleteFriend({"id": user.value.id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      load()
      show_user.value = false
    }
  })
}

// 解散我的群聊
const handleGroupMyDel = () => {
  groupApi.DeleteMyGroup({"id": group.value.id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      load()
      show_group.value = false
    }
  })
}

// 退出某一个群聊
const handleGroupDel = () => {
  groupApi.LeaveGroup({"id": group.value.id}).then((res) => {
    if (res.code === 200) {
      showSuccessToast(res.msg)
      load()
      show_group.value = false
    }
  })
}

// 修改我的群聊
const handleGroupEdit = () => {
  form.value.name = group.value.name
  form.value.avatar = [{"url": group.value.avatar}]
  form.value.id = group.value.id
  show.value = true
}

// 加载好友和群聊
const load = () => {
  friendApi.GetFriend({}).then((res) => {
    if (res.code === 200) {
      friends.value = res.data.friends
    }
  })
  groupApi.GetMyJoinGroup({}).then((res) => {
    if (res.code === 200) {
      groups.value = res.data.groups
    }
  })
}

onMounted(() => {
  load()
})


const show = ref(false);
const showPopup = () => {
  show.value = true;
  form.value.name = ""
  form.value.avatar = []
};
const show_user = ref(false);
const showUser = (item) => {
  show_user.value = true;
  user.value = item
};
const show_group = ref(false);
const showGroup = (item) => {
  show_group.value = true;
  group.value = item
};
const form = ref({
  name: "",
  avatar: [],
})
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

const store = userStore()
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
      showToast(res.data.msg);
      form.value.avatar = [{'url': res.data.data}]
    }
  })
};

const handleEdit = () => {
  if (form.value.id) {
    groupApi.UpdateMyGroup({"name": form.value.name, "avatar": form.value.avatar, "id": form.value.id}).then((res) => {
      if (res.code === 200) {
        show.value = false
        showSuccessToast(res.msg);
        load()
      }
    })
  } else
    groupApi.AddMyGroup({"name": form.value.name, "avatar": form.value.avatar}).then((res) => {
      if (res.code === 200) {
        show.value = false
        showSuccessToast(res.msg);
        load()
      }
    })
}


</script>

<style lang='scss' scoped>
span {
  color: #FFFFFF;
}

.van-nav-bar {
  background-color: transparent;
}

:deep(.van-nav-bar__title) {
  color: rgb(201, 208, 220);
  letter-spacing: 0.2vw;
}

.text-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
}

:depp(.van-index-bar__sidebar) {
  color: aqua;
}

:deep(.van-tag) {
  font-size: 12px;
}

.el-header {
  height: auto !important;
  padding: 0 !important;
}

.el-main {
  padding: 0 !important;
}

:deep(.van-cell) {
  background: transparent;
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
  opacity: .5;
}

:deep(.van-cell__title,
  .van-cell__value) {
  flex: 0;
}

:deep(.van-cell__value) {
  text-align: left;
}

.info-content {
  height: 35px;
  width: 35px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: orange;
  border-radius: 5px;


}

.text {
  font-size: 14px;
  color: #FFFFFF;
}

span {
  font-size: 16px;
  margin-left: 10px;
  line-height: 35px;
}

:deep(.van-cell__value) {
  color: white;
}
</style>