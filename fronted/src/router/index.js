import { createRouter, createWebHistory } from 'vue-router'
import HomepageIndex from "@/views/homepage/HomepageIndex.vue";
import FriendIndex from "@/views/friend/FriendIndex.vue";
import CreateIndex from "@/views/create/CreateIndex.vue";
import NotFoundeIndex from "@/views/error/NotFoundeIndex.vue";
import LoginIndex from "@/views/user/account/LoginIndex.vue";
import RegisterIndex from "@/views/user/account/RegisterIndex.vue";
import SpaceIndex from "@/views/user/space/SpaceIndex.vue";
import ProfileIndex from "@/views/user/profile/ProfileIndex.vue";
import {useUserStore} from "@/stores/user.js";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'homepage-index',
      component: HomepageIndex,
      meta:{
        needLogin: false,
      }
    },

    {
      path: '/friend/',
      name: 'friend-index',
      component: FriendIndex,
      meta:{
        needLogin: true,
      }
    },

    {
      path: '/create/',
      name: 'create-index',
      component: CreateIndex,
      meta:{
        needLogin: true,
      }
    },

    {
      path: '/404/',
      name: 'notfound-index',
      component: NotFoundeIndex,
      meta:{
        needLogin: false,
      }
    },


      {
      path: '/user/account/login',
      name: 'user-account-login-index',
      component: LoginIndex,
      meta:{
        needLogin: false,
      }
    },

    {
      path: '/user/account/register',
      name: 'user-account-register-index',
      component: RegisterIndex,
      meta:{
        needLogin: false,
      }
    },

    {
      path: '/user/space/:user_id/',
      name: 'user-space-index',
      component: SpaceIndex,
      meta:{
        needLogin: false,
      }
    },

    {
      path: '/user/profile/',
      name: 'user-profile-index',
      component: ProfileIndex,
      meta:{
        needLogin: true,
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notfound-index',
      component: NotFoundeIndex,
      meta:{
        needLogin: false,
      }
    }
  ],
})

router.beforeEach((to, from) => {
  const user = useUserStore()
  if (to.meta.needLogin && user.hasPulledUserInfo && !user.isLogin) {
    return{
      name: 'user-account-login-index',
    }
  }
  return true
})

export default router
