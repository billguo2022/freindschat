<template>
  <el-container>
    <el-header>
      <van-nav-bar title="Circle of friends" left-arrow @click-left="onClickLeft"/>
    </el-header>
    <el-main>
      <el-row :gutter="15" v-for="item in list">
        <el-col :span="3">
          <div style="display:flex;flex-direction: column;justify-content: flex-start;align-items: center;">
            <img :src="item.user.avatar" alt="" style="width: 40px;height: 40px">
          </div>
        </el-col>
        <el-col :span="21">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span style="color:#fafafa;font-size: 18px;font-weight: bold;margin-bottom:10px;display: block">{{
                    item.user.username
                  }}</span>
                <span>{{ item.content }}</span>
              </div>
            </template>
            <div class="img-content" v-if="item.image_url" style="margin-bottom: 20px">
              <div v-if="typeof item.image_url === 'string'">
                <el-image style="width: 10vh; height: 10vh" :src="item.image_url" fit="cover"/>
              </div>
              <div v-else style="display: grid;gap: 10px;grid-template-columns: repeat(3, 1fr)">
                <el-image style="width: 10vh; height: 10vh" :src="i" fit="cover" v-for="i in item.image_url"/>
              </div>
            </div>
            <div v-if="item.video_url">
              <video controls style="width: 300px;">
                <source :src="item.video_url" type="video/mp4" style="width: 100%;height: 100%">
              </video>
            </div>
            <div style="margin-top: 10px;display: flex;align-items: center;justify-content: space-between">
<!--              <TimeDiff :dateTime="item.created_at" style="font-size: 12px ;color: #9e9e9e"></TimeDiff>-->
              {{item.created_at}}
              <van-icon name="ellipsis" @click="handleArticleOther(item)"
                        style="background-color: #dedede;color: #4e6086;border-radius: 5px;padding: 2px 4px"/>
            </div>
            <div style="background-color: #f7f7f7;border-radius: 5px;padding: 2px 10px 5px 10px;margin-top: 10px">
              <el-row :gutter="15">
                <el-col :span="2">
                  <van-icon name="like-o" v-if="handleLike(item)" @click="sendLike(item)" color="#576b95"/>
                  <van-icon name="like" v-else @click="sendDisLike(item)" color="#576b95"/>
                </el-col>
                <el-col :span="6" v-for="obj in item.like">
                  <span style="color: #576b95;font-size: 12px">{{ obj.user.username }}、</span>
                </el-col>
              </el-row>
              <div style="margin: 10px 0;">
                <el-row :gutter="30" v-for="com in item.comment">
                  <el-col :span="4">
                    <span style="color: #576b95;font-size: 12px">{{ com.user.username }}：</span>
                  </el-col>
                  <el-col :span="16">
                    <span style="font-size: 12px ;color: #000000;margin-left: 5px;overflow-wrap: break-word;">{{ com.content }}</span>
                  </el-col>
                  <el-col :span="2">
                    <van-icon name="delete-o" v-if="com.user.id === store.user().value.id"
                              @click="handleArticleCommentDel(com.id)" color="#000000"/>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-card>
        </el-col>
        <div style="width: 100%;border-bottom: #FFFFFF solid 1px;margin: 20px 0"></div>
      </el-row>
      <van-back-top/>
    </el-main>
    <van-popup v-model:show="show" position="bottom" :style="{ height: '40%' }">
      <h4 style="text-align:center;padding: 10px">Modify Dynamics</h4>
      <van-form @submit="onSubmit">
        <van-field
            v-model="formEdit.content"
            name="content"
            label="内容"
            placeholder="content"
            :rules="[{ required: true, message: ' Please fill in the content ' }]"
        />
        <van-field name="uploader" label="image">
          <template #input>
            <van-uploader v-model="formEdit.image" :max-size="isOverSize" :after-read="afterRead"
                          :before-read="beforeRead" max-count="3" multiple/>
          </template>
        </van-field>
        <van-field name="uploader" label="video">
          <template #input>
            <van-uploader v-model="formEdit.video" :max-size="isOverSize" :after-read="afterReadv"
                          :before-read="beforeReadv" reupload max-count="1" accept="*"/>
          </template>
        </van-field>
        <div style="margin: 16px;">
          <van-button round block type="primary" native-type="submit" @click="handleArticleEdit()">
            submit
          </van-button>
        </div>
      </van-form>
    </van-popup>
    <van-popup v-model:show="show_other" position="bottom" :style="{ height: '40%' }">
      <div v-if="article_item.user.id === store.user().value.id"
           style="display: flex;align-items: center;justify-content: flex-start;padding: 10px">
        <van-button type="primary" @click="openArticleEdit(article_item)" style="margin-right: 10px">modify</van-button>
        <van-button type="danger" @click="handleArticleDel(article_item.id)">delete</van-button>
      </div>
      <h4 style="text-align:center;padding: 10px">Send comments</h4>
      <van-form @submit="onSubmit">
        <van-field
            v-model="formCom.content"
            name="content"
            label="content"
            placeholder="content"
            :rules="[{ required: true, message: 'Please fill in the content' }]"
        />
        <div style="margin: 16px;">
          <van-button round block type="primary" native-type="submit" @click="handleArticleComment(article_item.id)">
            submit
          </van-button>
        </div>
      </van-form>
    </van-popup>
  </el-container>
</template>

<script setup>
import {ref, reactive, onMounted, watch} from 'vue'
import {useRouter} from 'vue-router'
import articleApi from "@/api/article.ts";
import {userStore} from "@/store/user.ts";
import {showConfirmDialog, showSuccessToast, showToast} from "vant";
import axios from "axios";
import TimeDiff from "@/components/TimeDiff.vue";

const store = userStore()
const router = useRouter()
const list = ref([])
const onClickLeft = () => router.back();
const load = () => {
  articleApi.GetMyArticle({}).then((res) => {
    res.data.articles.forEach(item => {
      if (item.image_url) {
        if (item.image_url.indexOf(';') !== -1) {
          item.image_url = item.image_url.split(';')
        }
      }

    })
    list.value = res.data.articles
  })
}
onMounted(() => {
  load()
})
const handleArticleDel = (id) => {
  showConfirmDialog({
    title: 'Delete',
    message:
        'Are you sure to delete',
  })
      .then(() => {
        articleApi.DeleteArticle({"id": id}).then((res) => {
          if (res.code === 200) {
            showSuccessToast(res.msg)
            load()
          }
        })
      })
      .catch(() => {
        // on cancel
      });
}


const formEdit = ref(
    {
      id: "",
      content: "",
      image: [],
      imageT: [],
      video: [],
    }
)
const show = ref(false);
const openArticleEdit = (item) => {
  formEdit.value.content = item.content
  formEdit.value.id = item.id
  if (typeof item.image_url === "string") {
    formEdit.value.image = [{"url": item.image_url}]
    formEdit.value.imageT = [{"url": item.image_url}]
  } else {
    for (let i = 0; i < item.image_url.length; i++) {
      formEdit.value.image.push({"url": item.image_url[i]})
      formEdit.value.imageT.push({"url": item.image_url[i]})
    }
  }
  if (item.video_url) {
    formEdit.value.video = [{"url": item.video_url}]
  } else formEdit.value.video = []


  show.value = true;
}

const onSubmit = (values) => {
  console.log('submit', values);
};

const onFailed = (errorInfo) => {
  console.log('failed', errorInfo);
};

const isOverSize = (file) => {
  return file.size >= 1000 * 1024 * 5;
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
      showSuccessToast(res.data.msg);
      formEdit.value.imageT.push({'url': res.data.data})
      formEdit.value.image = formEdit.value.imageT
      formEdit.value.imageT = []
    }
  })
};

const afterReadv = (file) => {
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
      showSuccessToast(res.data.msg);
      formEdit.value.video = [{'url': res.data.data}]
    }
  })
};
// 修改文章
const handleArticleEdit = () => {
  articleApi.UpdateArticle({
    "id": formEdit.value.id,
    "content": formEdit.value.content,
    "image": formEdit.value.image,
    "video": formEdit.value.video
  }).then((res) => {
    if (res.code === 200) {
      show.value = false
      showSuccessToast(res.msg);
      load()
      formEdit.value.image = []
    }
  })
}

const handleLike = (item) => {
  if (item.length === 0) {
    return true
  }
  const ids = item.like.map(i => i.user.id)
  return ids.indexOf(store.user().value.id) === -1;
}
// 喜欢
const sendLike = (item) => {
  articleApi.ArticleLike({"id": item.id}).then((res) => {
    if (res.code === 200) {
      load()
    }
  })
}

// 不喜欢
const sendDisLike = (item) => {
  articleApi.ArticleDisLike({"id": item.id}).then((res) => {
    if (res.code === 200) {
      load()
    }
  })
}

const article_item = ref({})
const show_other = ref(false)

// 其它静态框：文章修改/删除/发送评论
const handleArticleOther = (item) => {
  article_item.value = item
  show_other.value = true
}

const formCom = ref({
  content: "",
  article_id: ""
})

// 发送评论
const handleArticleComment = (article_id) => {
  formCom.value.article_id = article_id
  articleApi.ArticleComment(formCom.value).then((res) => {
    if (res.code === 200) {
      load()
      show_other.value = false
      formCom.value = {}
    } else
      showToast(res.msg);
  })
}

// 删除评论
const handleArticleCommentDel = (comment_id) => {
  articleApi.ArticleCommentDel({"id": comment_id}).then((res) => {
    if (res.code === 200) {
      load()
    } else
      showToast(res.msg);
  })
}

watch(show, (newValue, oldValue) => {
  if (newValue === false) {
    formEdit.value.image = []
  }
});
</script>

<style lang='scss' scoped>
.img-content {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  row-gap: 1vh;
  justify-items: center;
}

:deep(.el-image__inner) {
  border-radius: 5px;
}

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

.el-container {
  height: 100%;
  background-color: rgb(20, 42, 59);
}
</style>