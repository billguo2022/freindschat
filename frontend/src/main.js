import App from './App.vue'
import {createApp} from 'vue'
import {createPinia} from 'pinia'
import ElementPlus from 'element-plus'
import router from './router'
import vant from 'vant';
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import 'vant/lib/index.css';
import zhCn from "element-plus/es/locale/lang/zh-cn";
import autofocus from 'vue-autofocus-directive';

const pinia = createPinia()

const app = createApp(App)

app.use(vant)
app.use(ElementPlus, {
    locale: zhCn,
})
app.directive('autofocus', autofocus);
app.use(pinia)
app.use(router)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.directive('touch', {
    // 指令的定义
    bind: function (el, binding, vnode) {
        // 判断是否为iOS移动端
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        if (isIOS) {
            el.addEventListener('touchstart', function (e) {
                // 使用e.touches代替e.changedTouches
                const touches = e.touches;
                // 将触摸点信息传递给组件
                vnode.context.$emit(binding.expression, touches);
            });
        } else {
            // 处理其他移动端触摸事件
        }
    }
})
document.addEventListener('touchstart', function (e) {
    e.preventDefault();
});

document.addEventListener('touchmove', function (e) {
    e.preventDefault();
});

document.addEventListener('copy', function (e) {
    e.preventDefault();
});
app.mount('#app')
