import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import {resolve, join} from 'path'
import legacy from '@vitejs/plugin-legacy'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue(),legacy()],
    // ******resolver配置******
    resolve: {
        alias: {
            // 别名配置
            // 键必须以斜线开始和结束
            "@": resolve(__dirname, "src"),
            components: resolve(__dirname, "./src/components"),
            assets: resolve(__dirname, "./src/assets"),
            "#": resolve(__dirname, "types"),
            build: resolve(__dirname, "build"),
        },
    },
    server: {
        // https: true,
        host: '127.0.0.1',
        port: 5173, // 端口号
        // open: true, // 自动在浏览器打开
        proxy: {
            "/api": {
                target: "http://127.0.0.1:5050", //跨域网址
                // secure: true, // 如果是https接口，需要配置这个参数
                changeOrigin: true, //自动修改http header里面的host
                ws: true, //支持websocket
                rewrite: (path) => path.replace(/^\/api/, ""),//路径的替换规则
            },
            '/socket.io': {
                target: 'ws://127.0.0.1:5050',
                ws: true,
                changeOrigin:true
            },
        },
    },
    optimizeDeps: {
      include: ['@babel/polyfill']
    }
})
