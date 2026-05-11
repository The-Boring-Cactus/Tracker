<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const projectId = route.params.id
const issueId = route.params.issueId

const issue = ref(null)
const project = ref(null)
const users = ref([])
const isLoading = ref(true)

const commentContent = ref('')

const statuses = ['New', 'On Process', 'Close', 'Rejected']

// Quill editor instance and language selection
const commentQuill = ref(null)
const commentCodeLang = ref('')

const codeLanguages = [
  { value: '', label: 'Auto-detect' },
  { value: 'bash', label: 'Bash' },
  { value: 'c', label: 'C' },
  { value: 'cpp', label: 'C++' },
  { value: 'csharp', label: 'C#' },
  { value: 'css', label: 'CSS' },
  { value: 'html', label: 'HTML' },
  { value: 'json', label: 'JSON' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'python', label: 'Python' },
  { value: 'sql', label: 'SQL' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'yaml', label: 'YAML' }
]

const onCommentEditorReady = (q) => { commentQuill.value = q }

const onCommentCodeLangChange = () => {
  if (!commentQuill.value) return
  const range = commentQuill.value.getSelection()
  if (!range) return
  const formats = commentQuill.value.getFormat(range)
  if (formats['code-block'] !== undefined) {
    commentQuill.value.format('code-block', commentCodeLang.value || true)
  }
}

// Editor options
const editorOptions = {
  modules: {
    syntax: true
  }
}

// Time Logging State
const timeToLog = ref('')
const showTimeModal = ref(false)
const timeRole = ref('') // 'reporter' or 'assignee'

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  
  try {
    await fetchUsers()
    await fetchProject()
    await fetchIssue()
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

const fetchIssue = async () => {
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}`, {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    issue.value = await response.json()
  } else {
    router.push(`/project/${projectId}`)
  }
}

const updateStatus = async (newStatus) => {
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/status`, {
    method: 'PATCH',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status: newStatus })
  })
  if (response.ok) fetchIssue()
}

const updateAssignee = async (newAssignee) => {
  const assigneeId = newAssignee === '' ? null : parseInt(newAssignee);
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/assignee`, {
    method: 'PATCH',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ assignee_id: assigneeId })
  })
  if (response.ok) fetchIssue()
}

const addComment = async () => {
  if (!commentContent.value || commentContent.value === '<p><br></p>') return
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/comments`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ content: commentContent.value })
  })
  if (response.ok) {
    commentContent.value = ''
    fetchIssue()
  }
}

const uploadAttachment = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/attachments`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${authStore.token}` },
    body: formData
  })
  if (response.ok) fetchIssue()
}

const openTimeModal = (role) => {
  timeRole.value = role
  timeToLog.value = ''
  showTimeModal.value = true
}

const submitTime = async () => {
  const hours = parseFloat(timeToLog.value)
  if (isNaN(hours) || hours <= 0) {
    alert("Please enter a valid number of hours")
    return
  }

  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/log_time`, {
    method: 'PATCH',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ role: timeRole.value, hours })
  })

  if (response.ok) {
    showTimeModal.value = false
    fetchIssue()
  } else {
    alert("Failed to log time")
  }
}

const goBack = () => {
  router.push(`/project/${projectId}`)
}

const getIssueTags = (tagsStr) => {
  if (!tagsStr) return []
  return tagsStr.split(',').filter(t => t.trim() !== '')
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
    <header class="bg-slate-100 border-b border-slate-300 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
      <div class="flex items-center space-x-4">
        <button @click="goBack" class="text-slate-500 hover:text-sky-400 transition flex items-center space-x-1 font-medium bg-slate-100 hover:bg-sky-500/20 px-3 py-1.5 rounded-lg border border-slate-300 hover:border-sky-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          <span>Back to Project</span>
        </button>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight" v-if="project">{{ project.name }} / Issue #{{ issueId }}</h1>
      </div>
      <div class="flex items-center space-x-4">
        <button @click="authStore.showProfileModal = true" class="text-sm font-medium text-slate-500 hover:text-sky-400 transition flex items-center space-x-2" v-if="authStore.user">
          <div class="w-8 h-8 rounded-full bg-sky-500/20 text-sky-300 flex items-center justify-center font-bold text-xs uppercase border border-sky-500/30">
            {{ (authStore.user.full_name || authStore.user.username).substring(0, 2) }}
          </div>
          <span>{{ authStore.user.full_name || authStore.user.username }}</span>
        </button>
      </div>
    </header>

    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-500"></div>
    </div>

    <div v-else-if="issue" class="flex-1 max-w-7xl mx-auto w-full p-8 flex flex-col lg:flex-row gap-8">
      
      <!-- Main Content -->
      <div class="flex-1 min-w-0 space-y-8">
        
        <!-- Header Section -->
        <div class="bg-slate-100 p-8 rounded-2xl shadow-sm border border-slate-300">
          <div class="flex items-center space-x-3 mb-4">
            <span :class="[
              'px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border',
              issue.status === 'New' ? 'bg-sky-50 text-sky-700 border-sky-100' : 
              issue.status === 'On Process' ? 'bg-amber-50 text-amber-700 border-amber-100' :
              issue.status === 'Close' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' :
              'bg-red-50 text-red-700 border-red-100'
            ]">
              {{ issue.status }}
            </span>
            <span class="px-3 py-1 rounded text-xs font-bold uppercase tracking-wide bg-slate-100 text-slate-600 border border-slate-300">
              {{ issue.category }}
            </span>
            <template v-if="getIssueTags(issue.tags).length > 0">
               <span v-for="tag in getIssueTags(issue.tags)" :key="tag" class="px-2 py-1 rounded bg-indigo-50 text-indigo-600 border border-indigo-100 text-xs font-semibold">
                 {{ tag }}
               </span>
            </template>
          </div>
          <h2 class="text-3xl font-extrabold text-slate-900 mb-2">{{ issue.title }}</h2>
          <div class="text-sm text-slate-500 flex items-center space-x-4">
            <span>Created: {{ new Date(issue.created_at).toLocaleDateString() }}</span>
            <span v-if="issue.parent_id">Parent Issue: #{{ issue.parent_id }}</span>
          </div>
        </div>

        <!-- Description -->
        <div class="bg-slate-100 p-8 rounded-2xl shadow-sm border border-slate-300">
          <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-300 pb-2">Description</h3>
          <div v-if="issue.description" class="prose prose-slate max-w-none max-h-96 overflow-y-auto overflow-x-auto pr-2" v-html="issue.description" v-highlight></div>
          <div v-else class="text-slate-500 italic">No description provided.</div>
        </div>

        <!-- Attachments -->
        <div class="bg-slate-100 p-8 rounded-2xl shadow-sm border border-slate-300">
          <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-300 pb-2 flex items-center justify-between">
            Attachments
            <label class="cursor-pointer py-1 px-3 bg-slate-200 border border-slate-400 rounded-lg shadow-sm text-xs font-bold text-sky-400 hover:bg-sky-500/20 hover:border-sky-400 transition inline-flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
              Upload
              <input type="file" class="hidden" @change="uploadAttachment" />
            </label>
          </h3>
          <div v-if="issue.attachments && issue.attachments.length > 0" class="flex flex-wrap gap-4">
            <a v-for="att in issue.attachments" :key="att.id" :href="`http://127.0.0.1:8000${att.file_path}`" target="_blank" class="flex items-center p-3 bg-slate-200 border border-slate-400 rounded-xl hover:bg-sky-500/20 hover:border-sky-300 hover:shadow-md transition group">
              <div class="w-10 h-10 bg-slate-200 rounded-lg flex items-center justify-center mr-3 shadow-sm text-sky-500 group-hover:text-sky-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
              </div>
              <div class="flex flex-col">
                <span class="text-sm font-semibold text-slate-700 group-hover:text-sky-700">{{ att.filename }}</span>
                <span class="text-xs text-slate-500">Uploaded by {{ users.find(u => u.id === att.uploader_id)?.username }}</span>
              </div>
            </a>
          </div>
          <div v-else class="text-slate-500 italic text-sm">No attachments uploaded yet.</div>
        </div>

        <!-- Comments -->
        <div class="bg-slate-100 p-8 rounded-2xl shadow-sm border border-slate-300">
          <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-6 border-b border-slate-300 pb-2">Comments ({{ issue.comments?.length || 0 }})</h3>
          
          <div class="space-y-6 mb-8 max-h-[500px] overflow-y-auto pr-2">
            <div v-for="comment in issue.comments" :key="comment.id" class="flex space-x-4">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full bg-slate-300 flex items-center justify-center text-slate-700 font-bold text-sm uppercase">
                  {{ users.find(u => u.id === comment.author_id)?.username?.substring(0, 2) || '--' }}
                </div>
              </div>
              <div class="flex-1 min-w-0 bg-slate-200 p-5 rounded-2xl rounded-tl-none border border-slate-400 shadow-sm">
                <div class="flex items-center justify-between mb-2">
                  <span class="font-bold text-slate-800 text-sm">{{ users.find(u => u.id === comment.author_id)?.username || 'Unknown' }}</span>
                  <span class="text-xs text-slate-500">{{ new Date(comment.created_at).toLocaleString() }}</span>
                </div>
                <div class="prose prose-sm prose-slate max-w-none overflow-x-auto" v-html="comment.content" v-highlight></div>
              </div>
            </div>
          </div>
          
          <div class="border border-slate-300 rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-sky-500 transition shadow-sm bg-slate-200">
            <div class="flex items-center gap-2 px-3 py-1.5 bg-slate-300 border-b border-slate-400">
              <span class="text-xs font-semibold text-slate-600 whitespace-nowrap">Code lang:</span>
              <select v-model="commentCodeLang" @change="onCommentCodeLangChange" class="text-xs bg-slate-200 border border-slate-400 rounded px-2 py-1 text-slate-800 focus:outline-none focus:ring-1 focus:ring-sky-500">
                <option v-for="lang in codeLanguages" :key="lang.value" :value="lang.value">{{ lang.label }}</option>
              </select>
              <span class="text-[10px] text-slate-500 ml-auto">Place cursor in a code block, then select language</span>
            </div>
            <QuillEditor theme="snow" v-model:content="commentContent" contentType="html" toolbar="full" :options="editorOptions" class="min-h-[120px]" @ready="onCommentEditorReady" />
            <div class="bg-slate-200 p-3 border-t border-slate-300 flex justify-end">
              <button @click="addComment" class="py-2 px-6 bg-sky-600 hover:bg-sky-600 text-white rounded-lg text-sm font-bold transition shadow-sm">Post Comment</button>
            </div>
          </div>
        </div>

      </div>

      <!-- Sidebar -->
      <div class="w-full lg:w-80 flex-shrink-0 space-y-6">
        
        <div class="bg-slate-100 p-6 rounded-2xl shadow-sm border border-slate-300 space-y-6">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Status</label>
            <select @change="updateStatus($event.target.value)" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2.5 px-3 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-slate-300 transition">
              <option v-for="s in statuses" :key="s" :value="s" :selected="issue.status === s">{{ s }}</option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Assignee</label>
            <select @change="updateAssignee($event.target.value)" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2.5 px-3 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-slate-300 transition">
              <option value="" :selected="!issue.assignee_id">Unassigned</option>
              <option v-for="user in users" :key="user.id" :value="user.id" :selected="issue.assignee_id === user.id">{{ user.username }}</option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Reporter</label>
            <div class="flex items-center space-x-3 bg-slate-200 p-2.5 rounded-lg border border-slate-300">
              <div class="w-8 h-8 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-xs uppercase">
                {{ users.find(u => u.id === issue.reporter_id)?.username?.substring(0, 2) || '--' }}
              </div>
              <span class="text-sm font-semibold text-slate-800">{{ users.find(u => u.id === issue.reporter_id)?.username || `User ID: ${issue.reporter_id}` }}</span>
            </div>
          </div>
        </div>

        <div class="bg-slate-100 p-6 rounded-2xl shadow-sm border border-slate-300 space-y-6">
          <h3 class="text-sm font-bold text-slate-800 border-b border-slate-300 pb-2">Schedule & Estimates</h3>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Start Date</span>
              <span class="text-sm font-medium text-slate-700">{{ issue.start_date ? new Date(issue.start_date).toLocaleDateString() : 'None' }}</span>
            </div>
            <div>
              <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Due Date</span>
              <span :class="['text-sm font-medium', isOverdue(issue.end_date) ? 'text-red-600 font-bold' : 'text-slate-700']">
                {{ issue.end_date ? new Date(issue.end_date).toLocaleDateString() : 'None' }}
              </span>
              <span v-if="isOverdue(issue.end_date)" class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700">Overdue</span>
            </div>
            <div class="col-span-2">
              <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Estimated Time</span>
              <span class="text-sm font-medium text-slate-700">{{ issue.estimated_hours ? `${issue.estimated_hours}h` : 'None' }}</span>
            </div>
          </div>
        </div>

        <div class="bg-slate-100 p-6 rounded-2xl shadow-sm border border-slate-300 space-y-6">
          <h3 class="text-sm font-bold text-slate-800 border-b border-slate-300 pb-2">Time Tracking</h3>
          
          <div class="space-y-4">
            <!-- Reporter Time -->
            <div class="bg-slate-200 p-4 rounded-xl border border-slate-300 flex flex-col items-center justify-center text-center relative overflow-hidden group">
              <div class="absolute inset-0 bg-gradient-to-br from-transparent to-slate-100 opacity-50"></div>
              <span class="relative text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Reporter Logged</span>
              <span class="relative text-2xl font-extrabold text-slate-800 mb-3">{{ issue.reporter_logged_hours.toFixed(1) }}<span class="text-sm text-slate-500 font-medium">h</span></span>
              <button @click="openTimeModal('reporter')" class="relative text-xs font-bold bg-slate-300 border border-slate-400 hover:border-sky-400 hover:text-sky-400 px-4 py-1.5 rounded-full shadow-sm transition">Grab Time</button>
            </div>
            
            <!-- Assignee Time -->
            <div class="bg-slate-200 p-4 rounded-xl border border-slate-300 flex flex-col items-center justify-center text-center relative overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-br from-transparent to-sky-50 opacity-30"></div>
              <span class="relative text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Assignee Logged</span>
              <span class="relative text-2xl font-extrabold text-sky-600 mb-3">{{ issue.assignee_logged_hours.toFixed(1) }}<span class="text-sm text-sky-400 font-medium">h</span></span>
              <button @click="openTimeModal('assignee')" class="relative text-xs font-bold bg-slate-300 border border-slate-400 hover:border-sky-400 hover:text-sky-400 px-4 py-1.5 rounded-full shadow-sm transition">Grab Time</button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Time Logging Modal -->
    <div v-if="showTimeModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-slate-100 rounded-xl shadow-2xl w-full max-w-sm flex flex-col transform transition-all">
        <div class="p-5 border-b border-slate-300 flex justify-between items-center bg-slate-200 rounded-t-xl">
          <h2 class="text-lg font-bold text-slate-800 capitalize">Log Time ({{ timeRole }})</h2>
          <button @click="showTimeModal = false" class="text-slate-500 hover:text-slate-700 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        
        <div class="p-6">
          <label class="block text-sm font-semibold text-slate-700 mb-2">Hours to add</label>
          <div class="relative">
            <input type="number" step="0.1" v-model="timeToLog" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2.5 px-4 text-slate-900 font-medium placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 transition" placeholder="e.g. 1.5" @keydown.enter="submitTime" />
            <div class="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
              <span class="text-slate-500 font-semibold">hrs</span>
            </div>
          </div>
        </div>
        
        <div class="p-5 border-t border-slate-300 bg-slate-200 flex justify-end space-x-3 rounded-b-xl">
          <button @click="showTimeModal = false" class="py-2 px-4 bg-slate-200 border border-slate-400 hover:bg-slate-300 text-slate-800 rounded-lg transition font-medium text-sm">Cancel</button>
          <button @click="submitTime" :disabled="!timeToLog" class="py-2 px-6 bg-sky-600 hover:bg-sky-600 disabled:opacity-50 text-white rounded-lg transition font-bold text-sm shadow-sm">Save Log</button>
        </div>
      </div>
    </div>

  </div>
</template>
