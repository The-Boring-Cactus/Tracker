<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const formData = ref({
  full_name: '',
  email: '',
  password: ''
})

const isSubmitting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

// Initialize form data when modal opens or user changes
watch(() => authStore.showProfileModal, (newVal) => {
  if (newVal && authStore.user) {
    formData.value.full_name = authStore.user.full_name || ''
    formData.value.email = authStore.user.email || ''
    formData.value.password = '' // Leave password empty
    errorMsg.value = ''
    successMsg.value = ''
  }
})

const handleSave = async () => {
  isSubmitting.value = true
  errorMsg.value = ''
  successMsg.value = ''
  
  try {
    const updatePayload = {}
    if (formData.value.full_name !== authStore.user.full_name) {
      updatePayload.full_name = formData.value.full_name
    }
    if (formData.value.email !== authStore.user.email) {
      updatePayload.email = formData.value.email
    }
    if (formData.value.password) {
      updatePayload.password = formData.value.password
    }
    
    if (Object.keys(updatePayload).length > 0) {
      await authStore.updateProfile(updatePayload)
      successMsg.value = 'Profile updated successfully!'
      // Clear password field after successful update
      formData.value.password = ''
      
      setTimeout(() => {
        authStore.showProfileModal = false
      }, 1500)
    } else {
      authStore.showProfileModal = false
    }
  } catch (err) {
    errorMsg.value = err.message || 'Failed to update profile'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="authStore.showProfileModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-[100] p-4 backdrop-blur-sm">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-md flex flex-col transform transition-all">
      <div class="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50 rounded-t-xl">
        <h2 class="text-xl font-bold text-slate-800">Edit Profile</h2>
        <button @click="authStore.showProfileModal = false" class="text-slate-400 hover:text-slate-600 transition">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      
      <div class="p-6 space-y-5">
        <div v-if="successMsg" class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-700 text-sm font-medium">
          {{ successMsg }}
        </div>
        <div v-if="errorMsg" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm font-medium">
          {{ errorMsg }}
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">Full Name</label>
          <input type="text" v-model="formData.full_name" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-4 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition" placeholder="John Doe" />
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">Email Address</label>
          <input type="email" v-model="formData.email" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-4 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition" placeholder="john@example.com" />
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">New Password <span class="text-slate-400 font-normal text-xs">(leave empty to keep current)</span></label>
          <input type="password" v-model="formData.password" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-4 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition" placeholder="••••••••" />
        </div>
      </div>
      
      <div class="p-6 border-t border-slate-200 bg-slate-50 flex justify-end space-x-3 rounded-b-xl">
        <button type="button" @click="authStore.showProfileModal = false" class="py-2.5 px-5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-lg transition font-medium text-sm">Cancel</button>
        <button type="button" @click="handleSave" :disabled="isSubmitting" class="py-2.5 px-6 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg transition font-bold text-sm shadow-sm flex items-center">
          <span v-if="isSubmitting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
          Save Changes
        </button>
      </div>
    </div>
  </div>
</template>
