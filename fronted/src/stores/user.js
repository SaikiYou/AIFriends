import {defineStore} from "pinia";
import {computed, ref} from "vue";

export const useUserStore = defineStore('user', () => {
    const id = ref()
    const username = ref('0')
    const photo = ref('')
    const profile = ref('')
    const accessToken = ref('')
    const hasPulledUserInfo = ref(false)

     const isLogin = computed(() => {
        return !!accessToken.value
    })

    function setAccessToken(token){
        accessToken.value = token
    }

    function setUserInfo(data){
        id.value = data.user_id
        username.value = data.username
        photo.value = data.photo
        profile.value = data.profile
    }

    function logout(){
        id.value = 0
        username.value = ''
        photo.value = ''
        profile.value = ''
        accessToken.value = ''
    }

    function setHasPulledUserInfo(newStatus){
        hasPulledUserInfo.value = newStatus
    }
    return{
        id,
        username,
        photo,
        profile,
        accessToken,
        setAccessToken,
        setUserInfo,
        logout,
        isLogin,
        hasPulledUserInfo,
        setHasPulledUserInfo
    }
})

