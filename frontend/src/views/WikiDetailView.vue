<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const projectId = route.params.id
const wikiId = route.params.wikiId

const wiki = ref(null)
const project = ref(null)
const users = ref([])
const isLoading = ref(true)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  
  try {
    await fetchUsers()
    await fetchProject()
    await fetchWiki()
  } finally {
    isLoading.value = false
  }
})

const fetchUsers = async () => {
  const response = await fetch('http://127.0.0.1:8000/auth/users', {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    users.value = await response.json()
  }
}

const fetchProject = async () => {
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}`, {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    project.value = await response.json()
  }
}

const fetchWiki = async () => {
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/wikis/${wikiId}`, {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    wiki.value = await response.json()
  } else {
    router.push(`/project/${projectId}`)
  }
}

const goBack = () => {
  router.push(`/project/${projectId}`)
}

const getTags = (tagsStr) => {
  if (!tagsStr) return []
  return tagsStr.split(',').filter(t => t.trim() !== '')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col text-slate-800">
    <header class="bg-slate-100 border-b border-slate-300 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
      <div class="flex items-center space-x-4">
        <button @click="goBack" class="text-slate-500 hover:text-sky-600 transition flex items-center space-x-1 font-medium bg-slate-200 hover:bg-sky-500/20 px-3 py-1.5 rounded-lg border border-slate-300 hover:border-sky-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          <span>Back to Project</span>
        </button>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight" v-if="project">{{ project.name }} / Wiki #{{ wikiId }}</h1>
      </div>
      <div class="flex items-center space-x-4">
        <span class="text-sm font-medium text-slate-500" v-if="authStore.user">
          {{ authStore.user.username }}
        </span>
      </div>
    </header>

    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-500"></div>
    </div>

    <div v-else-if="wiki" class="flex-1 max-w-7xl mx-auto w-full p-8 flex flex-col lg:flex-row gap-8">
      
      <!-- Main Content -->
      <div class="flex-1 space-y-8">
        
        <!-- Header Section -->
        <div class="bg-slate-100 p-8 rounded-2xl shadow-sm border border-slate-300">
          <div class="flex items-center space-x-3 mb-4">
            <template v-if="getTags(wiki.tags).length > 0">
               <span v-for="tag in getTags(wiki.tags)" :key="tag" class="px-2 py-1 rounded bg-indigo-50 text-indigo-600 border border-indigo-100 text-xs font-semibold">
                 {{ tag }}
               </span>
            </template>
            <span v-else class="text-xs text-slate-500 font-medium italic">No tags</span>
          </div>
          <h2 class="text-3xl font-extrabold text-slate-900 mb-2">{{ wiki.title }}</h2>
          <div class="text-sm text-slate-500 flex items-center space-x-4">
            <span>Created: {{ new Date(wiki.created_at).toLocaleDateString() }}</span>
            <span>Last Updated: {{ new Date(wiki.updated_at).toLocaleDateString() }}</span>
          </div>
        </div>

        <!-- Content -->
        <div class="bg-slate-100 p-8 rounded-2xl shadow-sm border border-slate-300">
          <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-300 pb-2">Content</h3>
          <div v-if="wiki.content" class="prose prose-slate max-w-none" v-html="wiki.content" v-highlight></div>
          <div v-else class="text-slate-500 italic">No content provided.</div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="w-full lg:w-80 space-y-6">
        
        <div class="bg-slate-100 p-6 rounded-2xl shadow-sm border border-slate-300 space-y-6">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Author</label>
            <div class="flex items-center space-x-3 bg-slate-200 p-2.5 rounded-lg border border-slate-300">
              <div class="w-8 h-8 rounded-full bg-sky-500/20 text-sky-300 flex items-center justify-center font-bold text-xs uppercase border border-sky-500/30">
                {{ users.find(u => u.id === wiki.author_id)?.username?.substring(0, 2) || '--' }}
              </div>
              <span class="text-sm font-semibold text-slate-800">{{ users.find(u => u.id === wiki.author_id)?.username || `User ID: ${wiki.author_id}` }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
