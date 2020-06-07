import Vue from 'vue'
import Router from 'vue-router'
import index from '@/components/index'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'index',
      component: index
    },
    {
      path: '/main', // 主页面
      name: 'main',
      component: () => import('@/components/main.vue')
    }
  ]
})
