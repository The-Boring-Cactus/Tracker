<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const fullName = ref('')
const email = ref('')
const isSubmitting = ref(false)
const errorMsg = ref('')
const isRegistering = ref(false)

const handleSubmit = async () => {
  isSubmitting.value = true
  errorMsg.value = ''
  try {
    if (isRegistering.value) {
      await authStore.register(username.value, email.value, password.value, fullName.value)
      await authStore.login(username.value, password.value)
    } else {
      await authStore.login(username.value, password.value)
    }
    router.push('/')
  } catch (err) {
    errorMsg.value = err.message || 'Authentication failed'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-6 text-slate-800">
    <div class="glass-panel p-8 rounded-xl w-full max-w-md shadow-lg border border-slate-200">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-extrabold text-slate-900 mb-2">{{ isRegistering ? 'Create Account' : 'Welcome Back' }}</h1>
        <p class="text-slate-500 text-sm">{{ isRegistering ? 'Sign up for a new account' : 'Sign in to your account' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        
        <div v-if="isRegistering">
          <label class="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
          <input type="text" v-model="fullName" required class="w-full bg-white border border-slate-300 rounded-lg py-2 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
        </div>
        
        <div v-if="isRegistering">
          <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input type="email" v-model="email" required class="w-full bg-white border border-slate-300 rounded-lg py-2 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Username</label>
          <input type="text" v-model="username" required class="w-full bg-white border border-slate-300 rounded-lg py-2 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input type="password" v-model="password" required class="w-full bg-white border border-slate-300 rounded-lg py-2 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
        </div>

        <div v-if="errorMsg" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {{ errorMsg }}
        </div>

        <button type="submit" :disabled="isSubmitting" class="w-full py-3 px-4 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-600 hover:to-indigo-700 text-white font-bold rounded-lg shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 flex justify-center items-center">
          <span v-if="isSubmitting" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
          {{ isSubmitting ? (isRegistering ? 'Registering...' : 'Signing in...') : (isRegistering ? 'Register' : 'Sign In') }}
        </button>
        
        <div class="text-center mt-4">
          <button type="button" @click="isRegistering = !isRegistering" class="text-sm text-sky-600 hover:text-sky-800 font-medium transition-colors">
            {{ isRegistering ? 'Already have an account? Sign in' : 'Need an account? Register' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
