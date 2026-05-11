<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isOpen = ref(false)
const searchQuery = ref('')
const results = ref({ issues: [], projects: [], wikis: [] })
const isSearching = ref(false)

const handleKeydown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    isOpen.value = true
  }
  if (e.key === 'Escape' && isOpen.value) {
    isOpen.value = false
  }
}

const handleOpenSearch = () => {
  isOpen.value = true
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('open-search', handleOpenSearch)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('open-search', handleOpenSearch)
})

const search = async () => {
  if (searchQuery.value.length < 2) {
    results.value = { issues: [], projects: [], wikis: [] }
    return
  }
  
  isSearching.value = true
  try {
    const response = await fetch(`http://127.0.0.1:8000/search/?q=${encodeURIComponent(searchQuery.value)}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (response.ok) {
      results.value = await response.json()
    }
  } finally {
    isSearching.value = false
  }
}

let timeout = null
watch(searchQuery, () => {
  clearTimeout(timeout)
  timeout = setTimeout(search, 300)
})

const goTo = (path) => {
  isOpen.value = false
  searchQuery.value = ''
  results.value = { issues: [], projects: [], wikis: [] }
  router.push(path)
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-start justify-center z-[100] pt-[10vh] px-4" @click.self="isOpen = false">
    <div class="bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh] transform transition-all">
      <div class="relative flex items-center p-4 border-b border-slate-200">
        <svg class="w-6 h-6 text-slate-400 absolute left-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search issues, projects, and wikis... (Cmd+K to open)" 
          class="w-full pl-12 pr-4 py-3 bg-transparent text-slate-800 text-lg focus:outline-none placeholder:text-slate-400"
          autofocus
        />
        <div class="absolute right-6 flex items-center space-x-2">
            <span class="text-xs font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded border border-slate-200">ESC</span>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 bg-slate-50">
        <div v-if="isSearching" class="p-8 flex justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-sky-500"></div>
        </div>
        
        <template v-else-if="results.issues.length > 0 || results.projects.length > 0 || results.wikis.length > 0">
            <div v-if="results.projects.length > 0" class="mb-6">
                <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 px-2">Projects</h3>
                <div class="space-y-1">
                    <button v-for="p in results.projects" :key="p.id" @click="goTo(`/project/${p.id}`)" class="w-full text-left px-4 py-3 rounded-xl hover:bg-sky-50 focus:bg-sky-50 transition group flex items-center justify-between border border-transparent hover:border-sky-200">
                        <span class="font-bold text-slate-700 group-hover:text-sky-700">{{ p.name }}</span>
                    </button>
                </div>
            </div>
            
            <div v-if="results.issues.length > 0" class="mb-6">
                <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 px-2">Issues</h3>
                <div class="space-y-1">
                    <button v-for="i in results.issues" :key="i.id" @click="goTo(`/project/${i.project_id}/issue/${i.id}`)" class="w-full text-left px-4 py-3 rounded-xl hover:bg-sky-50 focus:bg-sky-50 transition group flex items-center justify-between border border-transparent hover:border-sky-200">
                        <span class="font-bold text-slate-700 group-hover:text-sky-700">#{{ i.id }} - {{ i.title }}</span>
                    </button>
                </div>
            </div>
            
            <div v-if="results.wikis.length > 0">
                <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 px-2">Wikis</h3>
                <div class="space-y-1">
                    <button v-for="w in results.wikis" :key="w.id" @click="goTo(`/project/${w.project_id}/wiki/${w.id}`)" class="w-full text-left px-4 py-3 rounded-xl hover:bg-sky-50 focus:bg-sky-50 transition group flex items-center justify-between border border-transparent hover:border-sky-200">
                        <span class="font-bold text-slate-700 group-hover:text-sky-700">{{ w.title }}</span>
                    </button>
                </div>
            </div>
        </template>
        
        <div v-else-if="searchQuery.length >= 2 && !isSearching" class="p-12 text-center">
            <svg class="w-12 h-12 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <p class="text-slate-500 font-medium">No results found for "{{ searchQuery }}"</p>
        </div>
        
        <div v-else class="p-12 text-center">
            <svg class="w-12 h-12 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            <p class="text-slate-500 font-medium">Type at least 2 characters to search across everything.</p>
        </div>
      </div>
    </div>
  </div>
</template>
