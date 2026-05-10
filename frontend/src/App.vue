<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import UserProfileModal from './components/UserProfileModal.vue'

const router = useRouter()
const isLoading = ref(true)

onMounted(async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/setup/status')
    if (response.ok) {
      const data = await response.json()
      if (data.setup_required) {
        router.push('/setup')
      } else {
        // Assume login check happens inside Login/Dashboard guards
        if(router.currentRoute.value.path === '/setup') {
          router.push('/login')
        }
      }
    }
  } catch (err) {
    console.error("Backend not reachable or error:", err)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div v-if="isLoading" class="min-h-screen flex items-center justify-center bg-slate-50">
    <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-sky-500"></div>
  </div>
  <template v-else>
    <RouterView :key="$route.fullPath" />
    <UserProfileModal />
  </template>
</template>

<style scoped>
</style>
