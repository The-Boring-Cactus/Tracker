<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const notifications = ref([])
const showDropdown = ref(false)
const unreadCount = ref(0)

const fetchNotifications = async () => {
  if (!authStore.token) return
  const response = await fetch('http://127.0.0.1:8000/notifications/', {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    notifications.value = await response.json()
    unreadCount.value = notifications.value.filter(n => !n.is_read).length
  }
}

let interval
onMounted(() => {
  fetchNotifications()
  interval = setInterval(fetchNotifications, 30000) // Poll every 30s
})

onUnmounted(() => {
  clearInterval(interval)
})

const markRead = async (id, link) => {
  const response = await fetch(`http://127.0.0.1:8000/notifications/${id}/read`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    fetchNotifications()
    if (link) {
      showDropdown.value = false
      router.push(link)
    }
  }
}

const markAllRead = async () => {
  const response = await fetch('http://127.0.0.1:8000/notifications/read_all', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    fetchNotifications()
  }
}
</script>

<template>
  <div class="relative">
    <button @click="showDropdown = !showDropdown" class="relative p-2 text-slate-500 hover:text-sky-600 transition bg-slate-200 hover:bg-slate-300 rounded-full">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
      <span v-if="unreadCount > 0" class="absolute top-0 right-0 inline-flex items-center justify-center w-4 h-4 text-[10px] font-bold text-white bg-red-500 rounded-full border-2 border-slate-100">
        {{ unreadCount }}
      </span>
    </button>
    
    <div v-if="showDropdown" class="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 overflow-hidden flex flex-col max-h-[400px]">
      <div class="p-3 bg-slate-100 border-b border-slate-200 flex items-center justify-between">
        <h3 class="font-bold text-slate-800 text-sm">Notifications</h3>
        <button v-if="unreadCount > 0" @click="markAllRead" class="text-xs font-semibold text-sky-600 hover:text-sky-800">Mark all read</button>
      </div>
      <div class="overflow-y-auto flex-1 p-2 space-y-1">
        <div v-if="notifications.length === 0" class="p-4 text-center text-sm text-slate-500 italic">
          No notifications.
        </div>
        <div v-for="notif in notifications" :key="notif.id" 
             @click="markRead(notif.id, notif.link)"
             :class="['p-3 rounded-lg text-sm cursor-pointer transition', notif.is_read ? 'opacity-60 hover:bg-slate-50' : 'bg-sky-50 border border-sky-100 hover:bg-sky-100']">
          <p class="text-slate-800 font-medium">{{ notif.message }}</p>
          <p class="text-[10px] text-slate-500 mt-1">{{ new Date(notif.created_at).toLocaleString() }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
