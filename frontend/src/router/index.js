import {createRouter, createWebHashHistory} from 'vue-router'

const routes = [
    {
        path: '/',
        redirect: {
            name: 'Login'
        }
    },
    {
        path: "/:pathMatch(.*)",
        redirect: "/404",
        hidden: true,
        children: [
            {
                path: "/404",
                component: () => import("@/views/404.vue"),
            },
        ],
    },
    {
        path: '/login',
        component: () => import('@/views/Login.vue'),
        name: 'Login',
        meta: ['欢迎登录']
    },
    {
        path: '/index/:id',
        component: () => import('@/views/Chat/index.vue')
    },
    {
        path: '/group/:id',
        component: () => import('@/views/GroupChat/index.vue')
    },
    {
        path: '/friendpage',
        component: () => import('@/views/FriendPage/index.vue')
    },
    {
        path: '/add',
        component: () => import('@/views/AddUser/index.vue')
    },
    {
        path: '/addGroup',
        component: () => import('@/views/AddGroup/index.vue')
    },
    {
        path: '/newFriend',
        component: () => import('@/views/NewFriend/index.vue')
    },

    {
        path: '/mainbox',
        component: () => import('@/views/MainBox.vue'),
        name: 'MainBox',
        children: [
            {
                path: '/index',
                component: () => import('@/views/Home/index.vue'),
                name: 'Home'
            },
            {
                path: '/friend',
                component: () => import('@/views/Friend/index.vue'),
                name: 'Friend'
            },
            {
                path: '/found',
                component: () => import('@/views/Found/index.vue'),
                name: 'Found'
            },
            {
                path: '/bottle',
                component: () => import('@/views/Found/bottle.vue'),
                name: 'Bottle'
            },
            {
                path: '/my',
                component: () => import('@/views/My/index.vue'),
                name: 'My'
            }
        ]
    }
]
const router = createRouter({
    history: createWebHashHistory(),
    routes
})

import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import {userStore} from "@/store/user.ts";

NProgress.configure({showSpinner: false})

const whiteList = ['/login'] // no redirect whitelist

router.beforeEach(async (to, from, next) => {
    // NProgress.start()
    const store = userStore()
    if (store.token().value) {
        if (to.path === '/login') {
            next({path: '/'})
            // NProgress.done()
        } else {
            next()
        }
    } else {
        if (whiteList.indexOf(to.path) !== -1) {
            next()
        } else {
            if (to.path === '/404') {
                next(`/login`)
            } else {
                next(`/login?redirect=${to.path}`)
            }
            // NProgress.done()
        }
    }
})

router.afterEach((to, from) => {
    // NProgress.done()
})


export default router
