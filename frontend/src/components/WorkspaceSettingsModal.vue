<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  workspaceId: { type: Number, required: true },
  isOpen: { type: Boolean, required: true }
})
const emit = defineEmits(['close'])

const authStore = useAuthStore()
const members = ref([])
const users = ref([])
const newMemberId = ref('')
const newMemberRole = ref('member')
const isLoading = ref(true)

const fetchMembers = async () => {
  if (!props.workspaceId) return
  isLoading.value = true
  const response = await fetch(`http://127.0.0.1:8000/workspaces/${props.workspaceId}/members`, {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    members.value = await response.json()
  }
  isLoading.value = false
}

const fetchUsers = async () => {
  const response = await fetch('http://127.0.0.1:8000/auth/users', {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    users.value = await response.json()
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    fetchUsers()
    fetchMembers()
  }
})

const addMember = async () => {
  if (!newMemberId.value) return
  const response = await fetch(`http://127.0.0.1:8000/workspaces/${props.workspaceId}/members`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      workspace_id: props.workspaceId,
      user_id: parseInt(newMemberId.value),
      role: newMemberRole.value
    })
  })
  if (response.ok) {
    newMemberId.value = ''
    fetchMembers()
  } else {
    const errorData = await response.json()
    alert(errorData.detail || 'Failed to add member')
  }
}

const getUsername = (id) => {
  const user = users.value.find(u => u.id === id)
  return user ? user.username : `User ${id}`
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4" @click.self="emit('close')">
    <div class="bg-slate-100 rounded-xl shadow-2xl w-full max-w-lg flex flex-col transform transition-all">
      <div class="p-6 border-b border-slate-300 flex justify-between items-center">
        <h2 class="text-xl font-bold text-slate-800">Workspace Members</h2>
        <button @click="emit('close')" class="text-slate-500 hover:text-slate-700 transition">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      
      <div class="p-6 overflow-y-auto max-h-[60vh] space-y-6">
        <div v-if="isLoading" class="flex justify-center p-8">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-sky-500"></div>
        </div>
        <div v-else class="space-y-6">
            <!-- Add new member -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Add New Member</label>
              <div class="flex space-x-2">
                <select v-model="newMemberId" class="flex-1 bg-slate-200 border border-slate-400 rounded-lg p-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition">
                  <option value="" disabled>Select User</option>
                  <option v-for="user in users" :key="user.id" :value="user.id" :disabled="members.some(m => m.user_id === user.id)">{{ user.username }}</option>
                </select>
                <select v-model="newMemberRole" class="w-32 bg-slate-200 border border-slate-400 rounded-lg p-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 transition">
                  <option value="admin">Admin</option>
                  <option value="member">Member</option>
                  <option value="viewer">Viewer</option>
                </select>
                <button @click="addMember" :disabled="!newMemberId" class="px-4 py-2 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg text-sm font-bold transition">Add</button>
              </div>
            </div>

            <!-- List members -->
            <div>
              <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Current Members</h3>
              <div v-if="members.length === 0" class="text-sm text-slate-500 italic">No members found.</div>
              <div class="space-y-2">
                <div v-for="member in members" :key="member.id" class="flex items-center justify-between p-3 bg-slate-200 rounded-xl border border-slate-300 shadow-sm">
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center text-slate-700 font-bold text-xs uppercase">
                      {{ getUsername(member.user_id).substring(0, 2) }}
                    </div>
                    <span class="font-semibold text-slate-800">{{ getUsername(member.user_id) }}</span>
                  </div>
                  <span :class="[
                    'px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wide border',
                    member.role === 'admin' ? 'bg-purple-100 text-purple-800 border-purple-300' :
                    member.role === 'member' ? 'bg-sky-100 text-sky-800 border-sky-300' :
                    'bg-slate-300 text-slate-700 border-slate-400'
                  ]">{{ member.role }}</span>
                </div>
              </div>
            </div>
        </div>
      </div>
      <div class="p-5 border-t border-slate-300 bg-slate-200 flex justify-end rounded-b-xl">
        <button @click="emit('close')" class="py-2 px-6 bg-slate-200 border border-slate-400 hover:bg-slate-300 text-slate-800 rounded-lg transition font-medium text-sm">Close</button>
      </div>
    </div>
  </div>
</template>
