<template>
  <div class="form-structor">
    <div class="signup">
      <h2 class="form-title" ref="signupRef" @click="signupChange">
        <span>or</span>Sign up
      </h2>
      <div class="form-holder">
        <el-form ref="registerFormRef" class="form" :model="registerForm" :rules="registerFormrules">
          <el-form-item prop="username">
            <el-input v-model="registerForm.username" type="text" placeholder="Username" v-autofocus></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="registerForm.password" type="password" placeholder="Password" v-autofocus></el-input>
          </el-form-item>
          <el-form-item prop="phone">
            <el-input v-model="registerForm.phone" type="text" placeholder="Phone" v-autofocus></el-input>
          </el-form-item>
          <el-form-item>
            <input type="checkbox" v-model="registerForm.agreePolicy"/>
            <el-link href="https://www.baidu.com" target="_blank" style="margin-left: 10px">Privacy Policy</el-link>
          </el-form-item>
          <el-form-item>
            <button class="submit-btn" @click="handleSignUp">Sign up</button>
          </el-form-item>
        </el-form>
      </div>
    </div>
    <div class="login slide-up">
      <div class="center">
        <h2 class="form-title" ref="loginRef" @click="loginChange">
          <span>or</span>Log in
        </h2>
        <div class="form-holder">
          <el-form ref="loginFormRef" class="form" :model="loginForm" :rules="loginFormrules">
            <el-form-item prop="username">
              <el-input v-model="loginForm.username" type="text" placeholder="UserName" v-autofocus></el-input>
            </el-form-item>
            <el-form-item prop="username">
              <el-input v-model="loginForm.password" type="password" placeholder="Password" v-autofocus></el-input>
            </el-form-item>
            <el-form-item>
              <button class="submit-btn" @click="handleLogin">Log in</button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {userStore} from "@/store/user.ts";
import {ref, reactive, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import {useRouter} from 'vue-router'
import {showFailToast, showSuccessToast} from "vant";
import MyServer from "@/utils/mySocket.ts";

const {socket} = MyServer.getInstance();
const router = useRouter()
const loginRef = ref(null)
const signupRef = ref(null)
const registerFormRef = ref()
const loginFormRef = ref()
const store = userStore()
const loginFormrules = reactive({
  username: [{
    required: true,
    message: 'Please enter your username',
    trigger: 'blur',
  },
    {
      min: 6,
      message: 'The username contains a minimum of 6 characters'
    }],
  password: [{
    required: true,
    message: 'Please confirm the password',
    trigger: 'blur',
  }, {
    min: 6,
    message: 'The password contains a minimum of 6 characters'
  }],
})
var checkPhone = (rule, value, callback) => {//手机号码校验
  const phoneReg = /^1[3|4|5|7|8|9][0-9]{9}$/
  if (!value) {
    return callback(new Error('Please confirm the phone number'))
  }
  setTimeout(() => {
    if (!Number.isInteger(+value)) {
      callback(new Error('Please enter a numeric value'))
    } else {
      if (phoneReg.test(value)) {
        callback()
      } else {
        callback(new Error('The phone number format is incorrect'))
      }
    }
  }, 100)
}
const registerFormrules = reactive({
  username: [{
    required: true,
    message: 'Please enter your username',
    trigger: 'blur',
  },
    {
      min: 6,
      message: 'The username contains a minimum of 6 characters'
    }],
  password: [{
    required: true,
    message: 'Please confirm the password',
    trigger: 'blur',
  }, {
    min: 6,
    message: 'The password contains a minimum of 6 characters'
  }
  ],
  phone: [{validator: checkPhone, trigger: 'blur'}],
})

const loginChange = (e) => {
  let parent = e.target.parentNode.parentNode;
  Array.from(e.target.parentNode.parentNode.classList).find((element) => {
    if (element !== "slide-up") {
      parent.classList.add('slide-up')
    } else {
      signupRef.value.parentNode.classList.add('slide-up')
      parent.classList.remove('slide-up')
    }
  });
}
const signupChange = (e) => {
  let parent = e.target.parentNode;
  Array.from(e.target.parentNode.classList).find((element) => {
    if (element !== "slide-up") {
      parent.classList.add('slide-up')
    } else {
      loginRef.value.parentNode.parentNode.classList.add('slide-up')
      parent.classList.remove('slide-up')
    }
  });
}

onMounted(() => {
  // 在组件挂载后进行网络监听
  store.joined()
  socket.on('joined_message', (data) => {
    //这是接收到的客户端消息
    console.log(data);
    socket.connect()
  })
})

const registerForm = reactive({
  username: '',
  password: '',
  agreePolicy: false,
  phone: ""
})

const loginForm = reactive({
  username: '',
  password: '',
  latitude: "",
  longitude: "",
})

const handleLogin = () => {
  loginFormRef.value.validate((valid) => {
    if (valid) {
      navigator.geolocation.getCurrentPosition(d => {
        if (d !== undefined) {
          console.log(d)
          loginForm.latitude = d.coords.latitude
          loginForm.longitude = d.coords.longitude
        }
      }, d => {
        console.log(d)
      });
      store.UserLogin(loginForm).then(() => {
        router.push({name: 'Home'})
        store.joined()
        socket.on('joined_message', (data) => {
          //这是接收到的客户端消息
          console.log(data);
          socket.connect()
        })
      })
    } else {
      return false
    }
  })
}

const handleSignUp = () => {
  registerFormRef.value.validate((valid) => {
    if (valid) {
      if (registerForm.agreePolicy) {
        store.UserRegister(registerForm).then(() => {
          registerForm.username = ''
          registerForm.password = ''
          registerForm.phone = ''
          registerForm.agreePolicy = false
        })
      } else {
        showFailToast("Please agree to the privacy policy")
      }
    } else {
      return false
    }
  })
}
</script>


<style lang='scss' scoped>
.form-structor {
  background-color: #222;
  height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  &::after {
    content: '';
    opacity: .8;
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background-repeat: no-repeat;
    background-position: left bottom;
    background-size: auto;
    background-image: url('../assets/bg.webp');
  }

  .signup {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 65%;
    z-index: 5;
    transition: all .3s ease;


    &.slide-up {
      top: 5%;
      transform: translate(-50%, 0%);
      transition: all .3s ease;
    }

    &.slide-up .form-holder,
    &.slide-up .submit-btn {
      opacity: 0;
      visibility: hidden;
    }

    &.slide-up .form-title {
      font-size: 1em;
      cursor: pointer;
    }

    &.slide-up .form-title span {
      margin-right: 5px;
      opacity: 1;
      visibility: visible;
      transition: all .3s ease;
    }

    .form-title {
      color: #fff;
      font-size: 1.7em;
      text-align: center;

      span {
        color: rgba(0, 0, 0, 0.4);
        opacity: 0;
        visibility: hidden;
        transition: all .3s ease;
      }
    }

    .form-holder {
      margin-top: 50px;
      visibility: visible;
      transition: all .3s ease;
    }

    .submit-btn {
      background-color: rgba(0, 0, 0, 0.4);
      color: rgba(256, 256, 256, 0.7);
      border: 0;
      border-radius: 15px;
      display: block;
      margin: 15px auto;
      width: 100%;
      font-size: 13px;
      font-weight: bold;
      cursor: pointer;
      opacity: 1;
      visibility: visible;
      transition: all .3s ease;

      &:hover {
        transition: all .3s ease;
        background-color: rgba(0, 0, 0, 0.8);
      }
    }
  }

  .login {
    position: absolute;
    top: 20%;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #fff;
    z-index: 5;
    transition: all .3s ease;

    &::before {
      content: '';
      position: absolute;
      left: 50%;
      top: -20px;
      transform: translate(-50%, 0);
      background-color: #fff;
      width: 200%;
      height: 250px;
      border-radius: 50%;
      z-index: 4;
      transition: all .3s ease;
    }

    .center {
      position: absolute;
      top: calc(50% - 10%);
      left: 50%;
      transform: translate(-50%, -50%);
      width: 65%;
      z-index: 5;
      transition: all .3s ease;

      .form-title {
        color: #000;
        font-size: 1.7em;
        text-align: center;

        span {
          color: rgba(0, 0, 0, 0.4);
          opacity: 0;
          visibility: hidden;
          transition: all .3s ease;
        }
      }

      .form-holder {
        margin-top: 50px;
        visibility: visible;
        transition: all .3s ease;

        .input {
          border: 0;
          outline: none;
          box-shadow: none;
          display: block;
          height: 30px;
          line-height: 30px;
          padding: 8px 15px;
          border-bottom: 1px solid #eee;
          width: 100%;
          font-size: 12px;

          &:last-child {
            border-bottom: 0;
          }

          &::-webkit-input-placeholder {
            color: rgba(0, 0, 0, 0.4);
          }
        }
      }

      .submit-btn {
        background-color: #6B92A4;
        color: rgba(256, 256, 256, 0.7);
        border: 0;
        border-radius: 15px;
        display: block;
        margin: 15px auto;
        width: 100%;
        font-size: 13px;
        font-weight: bold;
        cursor: pointer;
        opacity: 1;
        visibility: visible;
        transition: all .3s ease;

        &:hover {
          transition: all .3s ease;
          background-color: rgba(0, 0, 0, 0.8);
        }
      }
    }

    &.slide-up {
      top: 90%;
      transition: all .3s ease;
    }

    &.slide-up .center {
      top: 10%;
      transform: translate(-50%, 0%);
      transition: all .3s ease;
    }

    &.slide-up .form-holder,
    &.slide-up .submit-btn {
      opacity: 0;
      visibility: hidden;
      transition: all .3s ease;
    }

    &.slide-up .form-title {
      font-size: 1em;
      margin: 0;
      padding: 0;
      cursor: pointer;
      transition: all .3s ease;
    }

    &.slide-up .form-title span {
      margin-right: 5px;
      opacity: 1;
      visibility: visible;
      transition: all .3s ease;
    }
  }
}
</style>