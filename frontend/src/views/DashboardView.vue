<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import NotificationCenter from '../components/NotificationCenter.vue'
import WorkspaceSettingsModal from '../components/WorkspaceSettingsModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const workspaces = ref([])
const projectsByWorkspace = ref({})
const myIssues = ref([])
const selectedWorkspaceId = ref(null)
const expandedWorkspaces = ref(new Set())

const isLoading = ref(true)

const openSearch = () => {
  window.dispatchEvent(new CustomEvent('open-search'))
}

// Modals state
const showWorkspaceModal = ref(false)
const workspaceForm = ref({ name: '', description: '' })

const showProjectModal = ref(false)
const projectForm = ref({ name: '', description: '' })

const showMembersModal = ref(false)
const selectedMembersWorkspaceId = ref(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  
  try {
    await fetchWorkspaces()
    await fetchMyIssues()
  } finally {
    isLoading.value = false
  }
})

const fetchWorkspaces = async () => {
  const response = await fetch('http://127.0.0.1:8000/workspaces/', {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    workspaces.value = await response.json()
  }
}

const fetchMyIssues = async () => {
  const response = await fetch('http://127.0.0.1:8000/auth/me/issues', {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    myIssues.value = await response.json()
  }
}

const fetchProjects = async (workspaceId) => {
  const response = await fetch(`http://127.0.0.1:8000/projects/workspace/${workspaceId}`, {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    projectsByWorkspace.value[workspaceId] = await response.json()
  }
}

const toggleWorkspace = async (workspaceId) => {
  const newSet = new Set(expandedWorkspaces.value)
  if (newSet.has(workspaceId)) {
    newSet.delete(workspaceId)
  } else {
    newSet.add(workspaceId)
    if (!projectsByWorkspace.value[workspaceId]) {
      await fetchProjects(workspaceId)
    }
  }
  expandedWorkspaces.value = newSet
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const openWorkspaceModal = () => {
  workspaceForm.value = { name: '', description: '' }
  showWorkspaceModal.value = true
}

const submitWorkspace = async () => {
  if (!workspaceForm.value.name) return
  
  const response = await fetch('http://127.0.0.1:8000/workspaces/', {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(workspaceForm.value)
  })
  if (response.ok) {
    showWorkspaceModal.value = false
    fetchWorkspaces()
  }
}

const openProjectModal = (workspaceId) => {
  selectedWorkspaceId.value = workspaceId
  projectForm.value = { name: '', description: '' }
  showProjectModal.value = true
}

const openMembersModal = (workspaceId) => {
  selectedMembersWorkspaceId.value = workspaceId
  showMembersModal.value = true
}

const submitProject = async () => {
  if (!selectedWorkspaceId.value || !projectForm.value.name) return
  
  const response = await fetch('http://127.0.0.1:8000/projects/', {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
      name: projectForm.value.name, 
      description: projectForm.value.description, 
      workspace_id: selectedWorkspaceId.value 
    })
  })
  if (response.ok) {
    showProjectModal.value = false
    fetchProjects(selectedWorkspaceId.value)
    
    const newSet = new Set(expandedWorkspaces.value)
    if (!newSet.has(selectedWorkspaceId.value)) {
      newSet.add(selectedWorkspaceId.value)
      expandedWorkspaces.value = newSet
    }
  }
}

const goToProject = (projectId) => {
  router.push(`/project/${projectId}`)
}

const goToIssue = (projectId, issueId) => {
  router.push(`/project/${projectId}/issue/${issueId}`)
}

const isOverdue = (endDate) => {
  if (!endDate) return false;
  const end = new Date(endDate);
  end.setHours(23, 59, 59, 999);
  const now = new Date();
  return end < now;
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col text-slate-800">
    <!-- Navbar -->
    <header class="bg-slate-100 border-b border-slate-300 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
      <div class="flex items-center space-x-8 w-full max-w-3xl">
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Tracker</h1>
        <div class="flex-1 relative group cursor-pointer" @click="openSearch">
          <svg class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 group-hover:text-sky-500 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          <input type="text" placeholder="Search everywhere (Cmd+K)" class="w-full bg-slate-200 border border-slate-300 rounded-lg py-2 pl-10 pr-4 text-sm text-slate-700 placeholder:text-slate-400 cursor-pointer focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition" readonly />
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <NotificationCenter v-if="authStore.user" />
        <button @click="authStore.showProfileModal = true" class="text-sm font-medium text-slate-500 hover:text-sky-600 transition flex items-center space-x-2" v-if="authStore.user">
          <div class="w-8 h-8 rounded-full bg-sky-500/20 text-sky-300 flex items-center justify-center font-bold text-xs uppercase border border-sky-500/30">
            {{ (authStore.user.full_name || authStore.user.username).substring(0, 2) }}
          </div>
          <span>{{ authStore.user.full_name || authStore.user.username }}</span>
        </button>
        <button @click="logout" class="py-2 px-4 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-lg transition font-medium text-sm border border-slate-400">Logout</button>
      </div>
    </header>
    
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-500"></div>
    </div>

    <div v-else class="flex-1 flex">
      <!-- Sidebar (Workspaces) -->
      <aside class="w-64 bg-slate-100 border-r border-slate-300 p-4 flex flex-col hidden md:flex">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Workspaces</h2>
          <button @click="openWorkspaceModal" class="text-sky-500 hover:text-sky-600 transition" title="New Workspace">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          </button>
        </div>
        
        <div class="space-y-1 flex-1 overflow-y-auto">
          <div v-if="workspaces.length === 0" class="text-sm text-slate-500 py-2">
            No workspaces yet.
          </div>
          <div v-for="ws in workspaces" :key="ws.id" class="flex flex-col">
            <div class="group flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-50 transition cursor-pointer" @click="toggleWorkspace(ws.id)">
              <div class="flex items-center text-sm font-medium text-slate-700">
                <svg :class="['w-4 h-4 mr-2 transition-transform duration-200 text-slate-400', expandedWorkspaces.has(ws.id) ? 'rotate-90' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                {{ ws.name }}
              </div>
              <div class="flex items-center opacity-0 group-hover:opacity-100 transition">
                <button @click.stop="openMembersModal(ws.id)" class="text-slate-400 hover:text-indigo-500 p-1 rounded hover:bg-slate-200" title="Members">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                </button>
                <button @click.stop="openProjectModal(ws.id)" class="text-slate-400 hover:text-sky-500 p-1 rounded hover:bg-slate-200" title="Add Project">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                </button>
              </div>
            </div>
            
            <div v-if="expandedWorkspaces.has(ws.id)" class="ml-6 mt-1 space-y-1 border-l border-slate-300 pl-2">
              <div v-if="!projectsByWorkspace[ws.id] || projectsByWorkspace[ws.id].length === 0" class="text-xs text-slate-500 py-1 pl-2 italic">
                No projects
              </div>
              <button v-else v-for="proj in projectsByWorkspace[ws.id]" :key="proj.id" @click="goToProject(proj.id)" class="w-full text-left px-2 py-1.5 rounded-md text-xs font-medium text-slate-500 hover:text-sky-400 hover:bg-sky-500/20 transition truncate">
                {{ proj.name }}
              </button>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 p-8 bg-slate-50 overflow-y-auto">
        
        <!-- Welcome Section -->
        <div class="mb-8">
          <h1 class="text-3xl font-extrabold text-slate-800 mb-2">Welcome<span v-if="authStore.user">, {{ authStore.user.full_name || authStore.user.username }}</span>!</h1>
          <p class="text-slate-500">Here's a quick overview of what needs your attention.</p>
        </div>

        <!-- My Assigned Issues Section -->
        <div class="mb-12">
          <h2 class="text-xl font-bold text-slate-800 mb-6">My Assigned Tasks</h2>
          
          <div v-if="myIssues.length === 0" class="glass-panel p-8 rounded-xl text-center border-dashed border-2 border-slate-300 shadow-none">
            <h3 class="text-lg font-medium text-slate-600 mb-2">You're all caught up!</h3>
            <p class="text-slate-500">You don't have any issues assigned to you across your projects.</p>
          </div>

          <div v-else class="bg-slate-100 shadow-sm border border-slate-300 rounded-xl overflow-hidden flex flex-col">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-slate-300 text-sm text-left">
                <thead class="bg-slate-200">
                  <tr>
                    <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Task Subject</th>
                    <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Project ID</th>
                    <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Status</th>
                    <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Category</th>
                    <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Due Date</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 bg-slate-100">
                  <tr v-for="issue in myIssues" :key="issue.id" @click="goToIssue(issue.project_id, issue.id)" class="hover:bg-slate-50 cursor-pointer transition group">
                    <td class="px-4 py-3 whitespace-nowrap text-slate-800 font-medium group-hover:text-sky-600 transition">{{ issue.title }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-slate-600 font-medium">#{{ issue.project_id }}</td>
                    <td class="px-4 py-3 whitespace-nowrap">
                       <span :class="[
                         'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border',
                         issue.status === 'New' ? 'bg-sky-50 text-sky-700 border-sky-100' : 
                         issue.status === 'On Process' ? 'bg-amber-50 text-amber-700 border-amber-100' :
                         issue.status === 'Close' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' :
                         'bg-red-50 text-red-700 border-red-100'
                       ]">{{ issue.status }}</span>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap">
                       <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700 tracking-wide border border-slate-400 uppercase">{{ issue.category }}</span>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap">
                       <span :class="isOverdue(issue.end_date) ? 'text-red-600 font-bold' : 'text-slate-600'">
                         {{ issue.end_date ? new Date(issue.end_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) : 'No Due Date' }}
                       </span>
                       <span v-if="isOverdue(issue.end_date)" class="ml-2 px-1.5 py-0.5 rounded text-[9px] font-bold bg-red-100 text-red-700 uppercase tracking-wide">Overdue</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>


      </main>
    </div>

    <!-- Workspace Modal -->
    <div v-if="showWorkspaceModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-slate-100 rounded-xl shadow-2xl w-full max-w-md flex flex-col">
        <div class="p-6 border-b border-slate-300">
          <h2 class="text-xl font-bold text-slate-800">Create New Workspace</h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Name</label>
            <input type="text" v-model="workspaceForm.name" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:ring-2 focus:ring-sky-500 focus:outline-none" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea v-model="workspaceForm.description" rows="3" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:ring-2 focus:ring-sky-500 focus:outline-none resize-none"></textarea>
          </div>
        </div>
        <div class="p-6 border-t border-slate-300 bg-slate-200 flex justify-end space-x-3 rounded-b-xl">
          <button @click="showWorkspaceModal = false" class="py-2 px-4 bg-slate-200 border border-slate-400 text-slate-800 rounded-lg transition font-medium hover:bg-slate-300">Cancel</button>
          <button @click="submitWorkspace" :disabled="!workspaceForm.name" class="py-2 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg transition font-medium">Create</button>
        </div>
      </div>
    </div>

    <!-- Project Modal -->
    <div v-if="showProjectModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-slate-100 rounded-xl shadow-2xl w-full max-w-md flex flex-col">
        <div class="p-6 border-b border-slate-300">
          <h2 class="text-xl font-bold text-slate-800">Create New Project</h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Name</label>
            <input type="text" v-model="projectForm.name" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:ring-2 focus:ring-sky-500 focus:outline-none" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea v-model="projectForm.description" rows="3" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:ring-2 focus:ring-sky-500 focus:outline-none resize-none"></textarea>
          </div>
        </div>
        <div class="p-6 border-t border-slate-300 bg-slate-200 flex justify-end space-x-3 rounded-b-xl">
          <button @click="showProjectModal = false" class="py-2 px-4 bg-slate-200 border border-slate-400 text-slate-800 rounded-lg transition font-medium hover:bg-slate-300">Cancel</button>
          <button @click="submitProject" :disabled="!projectForm.name" class="py-2 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg transition font-medium">Create</button>
        </div>
      </div>
    </div>

    <!-- Members Modal -->
    <WorkspaceSettingsModal 
      :is-open="showMembersModal" 
      :workspace-id="selectedMembersWorkspaceId" 
      @close="showMembersModal = false" 
    />

  </div>
</template>
