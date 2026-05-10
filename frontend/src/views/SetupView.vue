<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isSubmitting = ref(false)
const errorMsg = ref('')
const currentStep = ref(1)
const totalSteps = 3
const setupForm = ref(null)

const form = reactive({
  db_type: 'postgresql',
  host: 'localhost',
  port: 5432,
  user: '',
  password: '',
  db_name: '',
  admin_username: 'admin',
  admin_email: '',
  admin_password: '',
  smtp_host: '',
  smtp_port: 587,
  smtp_user: '',
  smtp_password: '',
  smtp_tls: true
})

const dbOptions = [
  { value: 'postgresql', label: 'PostgreSQL', defaultPort: 5432 },
  { value: 'mysql', label: 'MySQL', defaultPort: 3306 },
  { value: 'mssql', label: 'MS-SQL Server', defaultPort: 1433 }
]

const onDbTypeChange = () => {
  const selected = dbOptions.find(o => o.value === form.db_type)
  if (selected) {
    form.port = selected.defaultPort
  }
}

const nextStep = () => {
  if (setupForm.value.reportValidity()) {
    if (currentStep.value < totalSteps) {
      currentStep.value++
    } else {
      submitSetup()
    }
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const skipSmtpAndSubmit = () => {
  form.smtp_host = ''
  form.smtp_user = ''
  form.smtp_password = ''
  submitSetup()
}

const submitSetup = async () => {
  isSubmitting.value = true
  errorMsg.value = ''
  try {
    const response = await fetch('http://127.0.0.1:8000/setup/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || 'Setup failed')
    }
    
    router.push('/login')
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-6 relative overflow-hidden text-slate-800">
    <!-- Decorative background elements -->
    <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-sky-300 rounded-full mix-blend-multiply filter blur-[128px] opacity-60 animate-blob"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-indigo-300 rounded-full mix-blend-multiply filter blur-[128px] opacity-60 animate-blob animation-delay-2000"></div>

    <div class="glass-panel w-full max-w-2xl rounded-2xl p-8 md:p-10 z-10 relative shadow-xl border border-white/50">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-extrabold tracking-tight mb-2">Workspace <span class="primary-gradient-text">Setup</span></h1>
        <p class="text-slate-500">Complete the initial configuration to get started.</p>
      </div>

      <!-- Stepper -->
      <div class="mb-10 px-4 md:px-8">
        <div class="flex justify-between items-center relative">
          <div class="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-slate-200 z-0 rounded"></div>
          <div class="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-sky-500 z-0 rounded transition-all duration-500 ease-out" :style="{ width: ((currentStep - 1) / (totalSteps - 1)) * 100 + '%' }"></div>
          
          <div v-for="step in totalSteps" :key="step" class="z-10 flex flex-col items-center">
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-500 ease-out', currentStep >= step ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/30' : 'bg-white border-2 border-slate-200 text-slate-400']">
              <svg v-if="currentStep > step" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
              <span v-else>{{ step }}</span>
            </div>
            <span :class="['absolute -bottom-6 text-xs font-semibold whitespace-nowrap transition-colors duration-300', currentStep >= step ? 'text-slate-700' : 'text-slate-400']">
              {{ step === 1 ? 'Database' : step === 2 ? 'Admin' : 'SMTP' }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="errorMsg" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm flex items-start">
        <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span>{{ errorMsg }}</span>
      </div>

      <form ref="setupForm" @submit.prevent="nextStep">
        <transition name="slide-fade" mode="out-in">
          
          <!-- Step 1: Database Configuration -->
          <div v-if="currentStep === 1" key="step1" class="space-y-5">
            <h2 class="text-xl font-bold text-sky-600 mb-6 flex items-center">
              <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
              Database Connection
            </h2>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Database Type</label>
              <select v-model="form.db_type" @change="onDbTypeChange" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all">
                <option v-for="db in dbOptions" :key="db.value" :value="db.value">{{ db.label }}</option>
              </select>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-2">
                <label class="block text-sm font-medium text-slate-700 mb-1">Host</label>
                <input type="text" v-model="form.host" required class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Port</label>
                <input type="number" v-model="form.port" required class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Database Name</label>
              <input type="text" v-model="form.db_name" required class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">DB User</label>
                <input type="text" v-model="form.user" required class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">DB Password</label>
                <input type="password" v-model="form.password" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all" />
              </div>
            </div>

            <div class="pt-6 flex justify-end">
              <button type="submit" class="py-2.5 px-8 bg-sky-600 hover:bg-sky-500 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all">Next Step &rarr;</button>
            </div>
          </div>

          <!-- Step 2: Admin Account -->
          <div v-else-if="currentStep === 2" key="step2" class="space-y-5">
            <h2 class="text-xl font-bold text-indigo-600 mb-6 flex items-center">
              <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
              Admin Account
            </h2>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Admin Username</label>
              <input type="text" v-model="form.admin_username" required class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Admin Email</label>
              <input type="email" v-model="form.admin_email" required class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Admin Password</label>
              <input type="password" v-model="form.admin_password" required minlength="8" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" />
              <p class="text-xs text-slate-500 mt-1">Must be at least 8 characters long.</p>
            </div>

            <div class="pt-6 flex justify-between">
              <button type="button" @click="prevStep" class="py-2.5 px-6 bg-white border border-slate-300 text-slate-600 hover:bg-slate-50 font-medium rounded-lg transition-all">&larr; Back</button>
              <button type="submit" class="py-2.5 px-8 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all">Next Step &rarr;</button>
            </div>
          </div>

          <!-- Step 3: SMTP Configuration -->
          <div v-else-if="currentStep === 3" key="step3" class="space-y-5">
            <h2 class="text-xl font-bold text-rose-500 mb-2 flex items-center">
              <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
              SMTP Configuration
            </h2>
            <p class="text-sm text-slate-500 mb-6">Configure email settings to allow the system to send notifications. This step is optional and can be configured later.</p>
            
            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-2">
                <label class="block text-sm font-medium text-slate-700 mb-1">SMTP Host</label>
                <input type="text" v-model="form.smtp_host" placeholder="smtp.example.com" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-rose-500 transition-all" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Port</label>
                <input type="number" v-model="form.smtp_port" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-rose-500 transition-all" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">SMTP User</label>
                <input type="text" v-model="form.smtp_user" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-rose-500 transition-all" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">SMTP Password</label>
                <input type="password" v-model="form.smtp_password" class="w-full bg-white border border-slate-300 rounded-lg py-2.5 px-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-rose-500 transition-all" />
              </div>
            </div>

            <div class="flex items-center mt-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
              <input type="checkbox" id="tls" v-model="form.smtp_tls" class="w-4 h-4 text-rose-600 bg-white border-gray-300 rounded focus:ring-rose-500" />
              <label for="tls" class="ml-2 text-sm font-medium text-slate-700">Use TLS/SSL encryption</label>
            </div>

            <div class="pt-6 mt-4 border-t border-slate-100 flex justify-between items-center flex-wrap gap-4">
              <button type="button" @click="prevStep" class="py-2.5 px-6 bg-white border border-slate-300 text-slate-600 hover:bg-slate-50 font-medium rounded-lg transition-all">&larr; Back</button>
              
              <div class="flex space-x-3">
                 <button type="button" @click="skipSmtpAndSubmit" class="py-2.5 px-5 bg-slate-100 hover:bg-slate-200 text-slate-600 font-medium rounded-lg transition-all">
                   Skip & Complete
                 </button>
                 <button type="submit" :disabled="isSubmitting" class="py-2.5 px-6 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-600 hover:to-indigo-700 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all flex items-center disabled:opacity-50">
                   <span v-if="isSubmitting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                   {{ isSubmitting ? 'Saving...' : 'Save & Complete' }}
                 </button>
              </div>
            </div>
          </div>

        </transition>
      </form>
    </div>
  </div>
</template>

<style scoped>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}

.slide-fade-enter-active {
  transition: all 0.4s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  transform: translateY(15px);
  opacity: 0;
}
.slide-fade-leave-to {
  transform: translateY(-15px);
  opacity: 0;
}
</style>
