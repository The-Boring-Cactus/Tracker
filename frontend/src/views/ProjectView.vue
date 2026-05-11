<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const projectId = route.params.id

const project = ref(null)
const activeTab = ref('issues')
const tabData = ref([])
const isLoading = ref(true)
const expandedItemId = ref(null)
const users = ref([])

// Sidebar state
const isSidebarOpen = ref(true)
const workspaces = ref([])
const projectsByWorkspace = ref({})
const expandedWorkspaces = ref(new Set())
const showProjectModal = ref(false)
const projectForm = ref({ name: '', description: '' })
const selectedWorkspaceId = ref(null)

// Table state
const filters = ref({ subject: '', assigned: '', status: '', startDate: '', dueDate: '' })
const currentPage = ref(1)
const rowsPerPage = ref(10)

const tabs = [
  { id: 'issues', name: 'Issues' },
  { id: 'board', name: 'Board' },
  { id: 'wiki', name: 'Wiki' },
  { id: 'gantt', name: 'Gantt Chart' },
  { id: 'stats', name: 'Stats' }
]

const categories = ['TODO', 'WORK', 'ISSUE', 'TASK']
const statuses = ['New', 'On Process', 'Close', 'Rejected']

// Modal States
const showCreateModal = ref(false)
const newIssue = ref({
  title: '',
  category: 'ISSUE',
  assignee_id: '',
  parent_id: '',
  tags: [],
  description: '',
  start_date: '',
  end_date: '',
  estimated_hours: ''
})
const newTag = ref('')

const showWikiModal = ref(false)
const newWiki = ref({
  title: '',
  content: '',
  tags: []
})
const wikiTagInput = ref('')

const handleAddWikiTag = () => {
  const tag = wikiTagInput.value.trim()
  if (tag && !newWiki.value.tags.includes(tag)) {
    newWiki.value.tags.push(tag)
  }
  wikiTagInput.value = ''
}

const handleRemoveWikiTag = (tag) => {
  newWiki.value.tags = newWiki.value.tags.filter(t => t !== tag)
}

const commentContent = ref('')

// Quill Editor instances and language selection
const issueQuill = ref(null)
const wikiQuill = ref(null)
const issueCodeLang = ref('')
const wikiCodeLang = ref('')

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

const applyCodeLanguage = (quill, lang) => {
  if (!quill) return
  const range = quill.getSelection()
  if (!range) return
  const formats = quill.getFormat(range)
  if (formats['code-block'] !== undefined) {
    quill.format('code-block', lang || true)
  }
}

const onIssueEditorReady = (q) => { issueQuill.value = q }
const onWikiEditorReady = (q) => { wikiQuill.value = q }

const onIssueCodeLangChange = () => { applyCodeLanguage(issueQuill.value, issueCodeLang.value) }
const onWikiCodeLangChange = () => { applyCodeLanguage(wikiQuill.value, wikiCodeLang.value) }

// Quill Editor Modules config for Syntax Highlighting
const editorOptions = {
  modules: {
    syntax: true
  }
}

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  
  try {
    await fetchUsers()
    await fetchProject()
    await loadTab(activeTab.value)
    await fetchWorkspaces()
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
  } else {
    router.push('/')
  }
}

const fetchWorkspaces = async () => {
  const response = await fetch('http://127.0.0.1:8000/workspaces/', {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    workspaces.value = await response.json()
    if (project.value && project.value.workspace_id) {
      expandedWorkspaces.value = new Set([project.value.workspace_id])
      fetchWorkspaceProjects(project.value.workspace_id)
    }
  }
}

const fetchWorkspaceProjects = async (wsId) => {
  const response = await fetch(`http://127.0.0.1:8000/projects/workspace/${wsId}`, {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  if (response.ok) {
    projectsByWorkspace.value[wsId] = await response.json()
  }
}

const toggleWorkspace = async (wsId) => {
  const newSet = new Set(expandedWorkspaces.value)
  if (newSet.has(wsId)) {
    newSet.delete(wsId)
  } else {
    newSet.add(wsId)
    if (!projectsByWorkspace.value[wsId]) {
      await fetchWorkspaceProjects(wsId)
    }
  }
  expandedWorkspaces.value = newSet
}

const openProjectModal = (wsId) => {
  selectedWorkspaceId.value = wsId
  projectForm.value = { name: '', description: '' }
  showProjectModal.value = true
}

const submitNewProject = async () => {
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
    fetchWorkspaceProjects(selectedWorkspaceId.value)
    
    const newSet = new Set(expandedWorkspaces.value)
    if (!newSet.has(selectedWorkspaceId.value)) {
      newSet.add(selectedWorkspaceId.value)
      expandedWorkspaces.value = newSet
    }
  }
}

const goToAnotherProject = (id) => {
  router.push(`/project/${id}`)
}

const loadTab = async (tab) => {
  activeTab.value = tab
  tabData.value = []
  expandedItemId.value = null
  currentPage.value = 1
  
  const endpoints = {
    'issues': `http://127.0.0.1:8000/projects/${projectId}/issues`,
    'board': `http://127.0.0.1:8000/projects/${projectId}/issues`,
    'wiki': `http://127.0.0.1:8000/projects/${projectId}/wikis`,
    'gantt': `http://127.0.0.1:8000/projects/${projectId}/issues`,
    'stats': `http://127.0.0.1:8000/projects/${projectId}/issues`
  }
  
  const response = await fetch(endpoints[tab], {
    headers: { 'Authorization': `Bearer ${authStore.token}` }
  })
  
  if (response.ok) {
    tabData.value = await response.json()
  }
}

// Kanban Handlers
const getIssuesByStatus = (status) => {
  if (!tabData.value || !Array.isArray(tabData.value)) return []
  return tabData.value.filter(issue => issue.status === status)
}

const onDragStart = (event, issue) => {
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('issueId', issue.id)
}

const onDrop = async (event, newStatus) => {
  const issueId = event.dataTransfer.getData('issueId')
  if (!issueId) return
  
  const issue = tabData.value.find(i => i.id == issueId)
  if (issue && issue.status !== newStatus) {
    issue.status = newStatus
    await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/status`, {
      method: 'PATCH',
      headers: { 
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: newStatus })
    })
  }
}

const triggerCreate = () => {
  if (activeTab.value === 'issues' || activeTab.value === 'board' || activeTab.value === 'gantt') {
    newIssue.value = { title: '', category: 'ISSUE', assignee_id: '', parent_id: '', tags: [], description: '', start_date: '', end_date: '', estimated_hours: '' }
    newTag.value = ''
    showCreateModal.value = true
  } else if (activeTab.value === 'wiki') {
    newWiki.value = { title: '', content: '', tags: [] }
    wikiTagInput.value = ''
    showWikiModal.value = true
  }
}

const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !newIssue.value.tags.includes(tag)) {
    newIssue.value.tags.push(tag)
  }
  newTag.value = ''
}

const removeTag = (index) => {
  newIssue.value.tags.splice(index, 1)
}

const submitIssue = async () => {
  const payload = {
    title: newIssue.value.title,
    description: newIssue.value.description,
    category: newIssue.value.category,
    project_id: projectId,
    tags: newIssue.value.tags.join(',')
  }
  if (newIssue.value.assignee_id) {
    payload.assignee_id = parseInt(newIssue.value.assignee_id)
  }
  if (newIssue.value.parent_id) {
    payload.parent_id = parseInt(newIssue.value.parent_id)
  }
  if (newIssue.value.start_date) {
    payload.start_date = new Date(newIssue.value.start_date).toISOString()
  }
  if (newIssue.value.end_date) {
    payload.end_date = new Date(newIssue.value.end_date).toISOString()
  }
  if (newIssue.value.estimated_hours) {
    payload.estimated_hours = parseFloat(newIssue.value.estimated_hours)
  }

  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  
  if (response.ok) {
    showCreateModal.value = false
    loadTab(activeTab.value)
  } else {
    alert("Failed to create issue")
  }
}

const submitWiki = async () => {
  if (!newWiki.value.title) return
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/wikis`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title: newWiki.value.title,
      content: newWiki.value.content,
      tags: newWiki.value.tags.join(','),
      project_id: projectId
    })
  })
  
  if (response.ok) {
    showWikiModal.value = false
    newWiki.value = { title: '', content: '', tags: [] }
    wikiTagInput.value = ''
    loadTab('wiki')
  } else {
    alert("Failed to create wiki")
  }
}

const updateIssueStatus = async (issueId, newStatus) => {
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/status`, {
    method: 'PATCH',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status: newStatus })
  })
  
  if (response.ok) {
    loadTab(activeTab.value)
  }
}

const updateIssueAssignee = async (issueId, newAssignee) => {
  const assigneeId = newAssignee === '' ? null : parseInt(newAssignee);
  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/assignee`, {
    method: 'PATCH',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ assignee_id: assigneeId })
  })
  
  if (response.ok) {
    loadTab(activeTab.value)
  }
}

const addComment = async (issueId) => {
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
    loadTab(activeTab.value)
    expandedItemId.value = issueId
  }
}

const uploadAttachment = async (event, issueId) => {
  const file = event.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/attachments`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`
    },
    body: formData
  })
  
  if (response.ok) {
    loadTab(activeTab.value)
    expandedItemId.value = issueId
  } else {
    alert("Upload failed")
  }
}

const ganttRows = computed(() => {
  if (!tabData.value || !Array.isArray(tabData.value)) return []
  return tabData.value
    .filter(issue => issue.start_date && issue.end_date)
    .map(issue => {
      let bg = "#2763B9" // Blue accent

      if (issue.status === 'New') bg = "#2763B9"
      else if (issue.status === 'On Process') {
        bg = "#ca8a04"
        if (isOverdue(issue.end_date)) bg = "#ef4444"
      }
      else if (issue.status === 'Close') bg = "#10b981"
      else if (issue.status === 'Rejected') bg = "#565B68"

      return {
        label: issue.title,
        bars: [{
          myBeginDate: `${issue.start_date.split('T')[0]} 00:00`,
          myEndDate: `${issue.end_date.split('T')[0]} 23:59`,
          ganttBarConfig: {
            id: issue.id.toString(),
            label: issue.title,
            hasHandles: true,
            style: { background: bg, borderRadius: "4px" }
          }
        }]
      }
    })
})

const ganttStart = computed(() => {
  if (ganttRows.value.length === 0) {
    const d = new Date()
    return `${d.toISOString().split('T')[0]} 00:00`
  }
  let min = new Date('2099-01-01')
  ganttRows.value.forEach(r => {
    const d = new Date(r.bars[0].myBeginDate)
    if (d < min) min = d
  })
  min.setDate(min.getDate() - 3)
  return `${min.toISOString().split('T')[0]} 00:00`
})

const ganttEnd = computed(() => {
  if (ganttRows.value.length === 0) {
    const d = new Date()
    d.setDate(d.getDate() + 30)
    return `${d.toISOString().split('T')[0]} 23:59`
  }
  let max = new Date('1970-01-01')
  ganttRows.value.forEach(r => {
    const d = new Date(r.bars[0].myEndDate)
    if (d > max) max = d
  })
  max.setDate(max.getDate() + 3)
  return `${max.toISOString().split('T')[0]} 23:59`
})

const onGanttDragEnd = async (eventData) => {
  const bar = eventData.bar || eventData
  if (!bar.ganttBarConfig) return
  const issueId = bar.ganttBarConfig.id
  
  const newStart = bar.myBeginDate.split(' ')[0]
  const newEnd = bar.myEndDate.split(' ')[0]

  const response = await fetch(`http://127.0.0.1:8000/projects/${projectId}/issues/${issueId}/schedule`, {
    method: 'PATCH',
    headers: { 
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      start_date: newStart,
      end_date: newEnd
    })
  })
  
  if (response.ok) {
    loadTab(activeTab.value)
  } else {
    alert("Failed to update schedule")
  }
}

const goToIssueDetails = (id) => {
  router.push(`/project/${projectId}/issue/${id}`)
}

const goToWikiDetails = (id) => {
  router.push(`/project/${projectId}/wiki/${id}`)
}

const toggleExpand = (id) => {
  if (activeTab.value === 'issues') {
    goToIssueDetails(id)
    return
  }
  if (expandedItemId.value === id) {
    expandedItemId.value = null
  } else {
    expandedItemId.value = id
  }
}

const expandedTreeRowIds = ref(new Set())
const toggleTreeRow = (id, event) => {
  event.stopPropagation();
  const newSet = new Set(expandedTreeRowIds.value)
  if (newSet.has(id)) newSet.delete(id)
  else newSet.add(id)
  expandedTreeRowIds.value = newSet
}

const getEntityName = (item) => {
  return item.title || item.name || 'Unnamed'
}

const filteredData = computed(() => {
  if (activeTab.value !== 'issues') return tabData.value;
  
  let result = tabData.value;
  
  const fSubj = filters.value.subject.toLowerCase();
  const fAssign = filters.value.assigned.toLowerCase();
  const fStatus = filters.value.status.toLowerCase();
  const fStart = filters.value.startDate.toLowerCase();
  const fDue = filters.value.dueDate.toLowerCase();
  
  if (!fSubj && !fAssign && !fStatus && !fStart && !fDue) return result;
  
  const matches = new Set();
  
  result.forEach(item => {
    let match = true;
    if (fSubj && !getEntityName(item).toLowerCase().includes(fSubj)) match = false;
    
    if (fAssign) {
      const username = users.value.find(u => u.id === item.assignee_id)?.username || 'Unassigned';
      if (!username.toLowerCase().includes(fAssign)) match = false;
    }
    
    if (fStatus && !(item.status && item.status.toLowerCase().includes(fStatus))) match = false;
    
    if (fStart) {
      const startStr = item.start_date ? new Date(item.start_date).toLocaleDateString('en-CA') : '';
      if (!startStr.includes(fStart)) match = false;
    }
    
    if (fDue) {
      const dueStr = item.end_date ? new Date(item.end_date).toLocaleDateString('en-CA') : '';
      if (!dueStr.includes(fDue)) match = false;
    }
    
    if (match) {
      matches.add(item.id);
      let current = item;
      while(current.parent_id) {
         matches.add(current.parent_id);
         current = result.find(i => i.id === current.parent_id);
         if (!current) break;
      }
    }
  });
  
  return result.filter(item => matches.has(item.id));
})

const flatTreeData = computed(() => {
  if (activeTab.value !== 'issues') return tabData.value

  const map = {}
  const roots = []
  
  filteredData.value.forEach(item => {
    map[item.id] = { ...item, children: [] }
  })

  Object.values(map).forEach(item => {
    if (item.parent_id && map[item.parent_id]) {
      map[item.parent_id].children.push(item)
    } else {
      roots.push(item)
    }
  })

  const flat = []
  const traverse = (items, depth) => {
    items.forEach(item => {
      flat.push({ ...item, depth })
      if (expandedTreeRowIds.value.has(item.id) && item.children.length > 0) {
        traverse(item.children, depth + 1)
      }
    })
  }
  traverse(roots, 0)
  return flat
})

const paginatedTreeData = computed(() => {
  if (activeTab.value !== 'issues') return flatTreeData.value;
  const start = (currentPage.value - 1) * rowsPerPage.value;
  return flatTreeData.value.slice(start, start + rowsPerPage.value);
})

const totalPages = computed(() => {
  if (activeTab.value !== 'issues') return 1;
  return Math.max(1, Math.ceil(flatTreeData.value.length / rowsPerPage.value));
})

const setPage = (p) => {
  if (p >= 1 && p <= totalPages.value) {
    currentPage.value = p
  }
}

const getInitials = (username) => {
  if (!username) return '--'
  return username.substring(0, 2).toUpperCase()
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

// ── Stats computed properties ──
const statsData = computed(() => {
  const issues = tabData.value
  if (!issues || !Array.isArray(issues) || issues.length === 0) {
    return { total: 0, closed: 0, delayed: 0, rejected: 0, inProgress: 0, newCount: 0 }
  }
  const total = issues.length
  const closed = issues.filter(i => i.status === 'Close').length
  const rejected = issues.filter(i => i.status === 'Rejected').length
  const onProcess = issues.filter(i => i.status === 'On Process')
  const delayed = onProcess.filter(i => i.end_date && new Date(i.end_date) < new Date()).length
  const inProgress = onProcess.length
  const newCount = issues.filter(i => i.status === 'New').length
  return { total, closed, delayed, rejected, inProgress, newCount }
})

const statsPercent = computed(() => {
  const { total, closed, delayed, rejected, inProgress, newCount } = statsData.value
  if (total === 0) return { closed: 0, delayed: 0, rejected: 0, inProgress: 0, new: 0 }
  return {
    closed: Math.round((closed / total) * 100),
    delayed: Math.round((delayed / total) * 100),
    rejected: Math.round((rejected / total) * 100),
    inProgress: Math.round((inProgress / total) * 100),
    new: Math.round((newCount / total) * 100)
  }
})

const timeStats = computed(() => {
  const issues = tabData.value
  if (!issues || !Array.isArray(issues)) {
    return { totalEstimated: 0, totalReporter: 0, totalAssignee: 0, byUser: [] }
  }
  let totalEstimated = 0
  let totalReporter = 0
  let totalAssignee = 0

  issues.forEach(i => {
    totalEstimated += parseFloat(i.estimated_hours) || 0
    totalReporter += parseFloat(i.reporter_logged_hours) || 0
    totalAssignee += parseFloat(i.assignee_logged_hours) || 0
  })

  // Per-user: combine reporter + assignee logged hours
  const userHours = {}
  issues.forEach(i => {
    const add = (uid, hours) => {
      if (!uid || !hours) return
      const h = parseFloat(hours) || 0
      if (h === 0) return
      if (!userHours[uid]) userHours[uid] = 0
      userHours[uid] += h
    }
    add(i.reporter_id, i.reporter_logged_hours)
    add(i.assignee_id, i.assignee_logged_hours)
  })

  const byUser = Object.entries(userHours)
    .map(([uid, hours]) => ({
      userId: parseInt(uid),
      username: users.value.find(u => u.id === parseInt(uid))?.username || `User #${uid}`,
      hours: Math.round(hours * 10) / 10
    }))
    .sort((a, b) => b.hours - a.hours)

  return {
    totalEstimated: Math.round(totalEstimated * 10) / 10,
    totalReporter: Math.round(totalReporter * 10) / 10,
    totalAssignee: Math.round(totalAssignee * 10) / 10,
    totalLogged: Math.round((totalReporter + totalAssignee) * 10) / 10,
    byUser
  }
})

const maxUserHours = computed(() => {
  if (timeStats.value.byUser.length === 0) return 1
  return Math.max(...timeStats.value.byUser.map(u => u.hours))
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col text-slate-800">
    <header class="bg-slate-100 border-b border-slate-300 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
      <div class="flex items-center space-x-4">
        <button @click="isSidebarOpen = !isSidebarOpen" class="text-slate-500 hover:text-slate-700 transition mr-2" title="Toggle Sidebar">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>
        <button @click="$router.push('/')" class="text-slate-500 hover:text-slate-700 transition" title="Back to Dashboard">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
        </button>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight" v-if="project">{{ project.name }}</h1>
        <div v-else class="h-8 w-48 bg-slate-200 animate-pulse rounded"></div>
      </div>
      <div class="flex items-center space-x-4">
        <button @click="authStore.showProfileModal = true" class="text-sm font-medium text-slate-500 hover:text-sky-600 transition flex items-center space-x-2" v-if="authStore.user">
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

    <div v-else class="flex-1 flex overflow-hidden">
      <!-- Sidebar -->
      <aside v-if="isSidebarOpen" class="w-64 bg-slate-100 border-r border-slate-300 p-4 flex flex-col flex-shrink-0 overflow-y-auto transition-all duration-300">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Workspaces</h2>
        </div>
        
        <div class="space-y-1 flex-1">
          <div v-if="workspaces.length === 0" class="text-sm text-slate-500 py-2">
            No workspaces yet.
          </div>
          <div v-for="ws in workspaces" :key="ws.id" class="flex flex-col">
            <div class="group flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-200 transition cursor-pointer" @click="toggleWorkspace(ws.id)">
              <div class="flex items-center text-sm font-medium text-slate-700">
                <svg :class="['w-4 h-4 mr-2 transition-transform duration-200 text-slate-400', expandedWorkspaces.has(ws.id) ? 'rotate-90' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                {{ ws.name }}
              </div>
              <button @click.stop="openProjectModal(ws.id)" class="text-slate-400 hover:text-sky-500 opacity-0 group-hover:opacity-100 transition p-1 rounded hover:bg-slate-200" title="Add Project">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
              </button>
            </div>
            
            <div v-if="expandedWorkspaces.has(ws.id)" class="ml-6 mt-1 space-y-1 border-l border-slate-300 pl-2">
              <div v-if="!projectsByWorkspace[ws.id] || projectsByWorkspace[ws.id].length === 0" class="text-xs text-slate-500 py-1 pl-2 italic">
                No projects
              </div>
              <button v-else v-for="proj in projectsByWorkspace[ws.id]" :key="proj.id" @click="goToAnotherProject(proj.id)" :class="['w-full text-left px-2 py-1.5 rounded-md text-xs font-medium transition truncate', proj.id == projectId ? 'bg-sky-500/20 text-sky-300' : 'text-slate-500 hover:text-sky-400 hover:bg-sky-500/20']">
                {{ proj.name }}
              </button>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 flex flex-col p-8 overflow-y-auto min-w-0">
      
      <!-- Tabs Navigation -->
      <div class="border-b border-slate-300 mb-8">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <button v-for="tab in tabs" :key="tab.id" @click="loadTab(tab.id)"
            :class="[
              activeTab === tab.id
                ? 'border-sky-500 text-sky-600'
                : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700',
              'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Tab Content Area -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-slate-800 capitalize">{{ activeTab }}</h2>
        <button v-if="activeTab !== 'stats'" @click="triggerCreate" class="py-2 px-4 bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition font-medium shadow-sm flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          Create New
        </button>
      </div>

      <!-- Empty State for non-Board tabs -->
      <div v-if="flatTreeData.length === 0 && activeTab !== 'board'" class="glass-panel p-10 rounded-xl text-center border-dashed border-2 border-slate-300 shadow-none mt-4">
        <h3 class="text-lg font-medium text-slate-600 mb-2">No items found</h3>
        <p class="text-slate-500 mb-6">There are no {{ activeTab }} in this project yet.</p>
        <button @click="triggerCreate" class="text-sky-600 font-medium hover:underline">Create the first one</button>
      </div>

      <!-- Kanban Board Layout -->
      <div v-else-if="activeTab === 'board'" class="flex overflow-x-auto space-x-6 pb-4 h-[calc(100vh-280px)] items-start">
        <div v-for="status in statuses" :key="status" 
             class="w-80 flex-shrink-0 bg-slate-200/70 rounded-xl p-4 flex flex-col max-h-full border border-slate-300 shadow-inner"
             @dragover.prevent
             @drop="onDrop($event, status)">
          
          <div class="flex items-center justify-between mb-4 px-1">
            <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center">
              {{ status }} 
              <span class="ml-2 bg-slate-200 text-slate-600 py-0.5 px-2.5 rounded-full text-[10px]">{{ getIssuesByStatus(status).length }}</span>
            </h3>
          </div>
          
          <div class="flex-1 overflow-y-auto space-y-3 pr-1 pb-2">
            <div v-for="issue in getIssuesByStatus(status)" :key="issue.id"
                 draggable="true" 
                 @dragstart="onDragStart($event, issue)"
                 @click="() => { goToIssueDetails(issue.id); }"
                 class="bg-slate-100 p-4 rounded-xl shadow-sm border border-slate-400 cursor-grab active:cursor-grabbing hover:border-sky-400 hover:shadow-md transition group flex flex-col min-h-[120px]">
              
              <div class="flex items-center space-x-2 mb-3">
                 <span :class="[
                   'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border',
                   issue.status === 'New' ? 'bg-sky-50 text-sky-700 border-sky-100' : 
                   issue.status === 'On Process' ? 'bg-amber-50 text-amber-700 border-amber-100' :
                   issue.status === 'Close' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' :
                   'bg-red-50 text-red-700 border-red-100'
                 ]">{{ issue.status }}</span>
                 <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600 tracking-wide border border-slate-300 uppercase">{{ issue.category }}</span>
              </div>
              
              <div class="grid grid-cols-[auto_1fr] gap-x-3 items-center mb-2 border-b border-slate-300 pb-2">
                 <span class="text-xs font-semibold text-slate-500 w-12 shrink-0">#{{ issue.id }}</span>
                 <span class="text-xs font-medium text-slate-600 truncate">Task ID</span>
              </div>

              <div class="grid grid-cols-[auto_1fr] gap-x-3 items-center mb-2 border-b border-slate-300 pb-2">
                 <span class="text-xs font-semibold text-slate-500 w-12 shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                 </span>
                 <div class="flex items-center">
                   <div v-if="issue.assignee_id" class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-300 flex items-center justify-center font-bold text-[10px] uppercase shadow-sm border border-sky-200 mr-1" :title="users.find(u => u.id === issue.assignee_id)?.username">
                      {{ getInitials(users.find(u => u.id === issue.assignee_id)?.username) }}
                   </div>
                   <div v-else class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-[10px] border border-slate-400 shadow-sm mr-1" title="Unassigned">--</div>
                   <div class="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold text-[12px] border border-slate-300 border-dashed shadow-sm cursor-pointer hover:bg-slate-100 transition">+</div>
                 </div>
              </div>

              <div class="grid grid-cols-[auto_1fr] gap-x-3 items-center mb-3">
                 <span :class="['text-xs font-semibold w-12 shrink-0 transition', isOverdue(issue.end_date) ? 'text-red-500' : 'text-slate-500']">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                 </span>
                 <span :class="['text-xs font-bold truncate', isOverdue(issue.end_date) ? 'text-red-600' : 'text-slate-800']">
                    {{ issue.end_date ? new Date(issue.end_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) : '--' }}
                 </span>
              </div>

              <div class="mt-auto bg-slate-200 rounded-lg p-3 flex flex-col justify-between items-start border border-slate-300">
                <h4 class="font-bold text-slate-800 text-sm mb-2 group-hover:text-sky-600 transition line-clamp-2 w-full">{{ issue.title }}</h4>
                <div class="w-full flex justify-end">
                   <span class="text-xs font-bold text-slate-800 bg-slate-300 px-2 py-0.5 rounded shadow-sm border border-slate-400">{{ issue.estimated_hours ? `${issue.estimated_hours}h` : '--' }}</span>
                </div>
              </div>
              
            </div>
            
            <button @click="triggerCreate" class="w-full py-2.5 flex items-center justify-center text-sm font-medium text-slate-500 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition mt-2 border border-dashed border-slate-300">
               <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
               Create issue
            </button>
          </div>
        </div>
      </div>

      <!-- Data Grid Layout for Issues -->
      <div v-else-if="activeTab === 'issues'" class="bg-slate-100 shadow-sm border border-slate-400 rounded-xl overflow-hidden flex flex-col">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm text-left">
            <thead class="bg-slate-200">
              <tr>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500 min-w-[250px]">Task Subject</th>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Assigned <svg class="inline w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg></th>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Status</th>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Start Date</th>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Due Date</th>
              </tr>
              <!-- Filter Row -->
              <tr class="border-t border-slate-300 bg-slate-200">
                <th class="px-4 py-2 font-normal"><input type="text" v-model="filters.subject" placeholder="Filter..." class="w-full text-xs border-b border-slate-300 py-1 focus:outline-none focus:border-sky-500 transition" /></th>
                <th class="px-4 py-2 font-normal"><input type="text" v-model="filters.assigned" placeholder="Filter..." class="w-full text-xs border-b border-slate-300 py-1 focus:outline-none focus:border-sky-500 transition" /></th>
                <th class="px-4 py-2 font-normal"><input type="text" v-model="filters.status" placeholder="Filter..." class="w-full text-xs border-b border-slate-300 py-1 focus:outline-none focus:border-sky-500 transition" /></th>
                <th class="px-4 py-2 font-normal"><input type="text" v-model="filters.startDate" placeholder="Filter..." class="w-full text-xs border-b border-slate-300 py-1 focus:outline-none focus:border-sky-500 transition" /></th>
                <th class="px-4 py-2 font-normal"><input type="text" v-model="filters.dueDate" placeholder="Filter..." class="w-full text-xs border-b border-slate-300 py-1 focus:outline-none focus:border-sky-500 transition" /></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-slate-100">
              <tr v-for="item in paginatedTreeData" :key="item.id" @click="goToIssueDetails(item.id)" class="hover:bg-slate-200 cursor-pointer transition group">
                <td class="px-4 py-3 whitespace-nowrap text-slate-800 font-medium flex items-center" :style="{ paddingLeft: (item.depth ? item.depth * 24 + 16 : 16) + 'px' }">
                  <div class="flex items-center w-6 mr-2">
                    <button v-if="item.children && item.children.length > 0" @click.stop="toggleTreeRow(item.id, $event)" class="text-slate-400 hover:text-slate-600 focus:outline-none">
                       <svg :class="['w-4 h-4 transition-transform duration-200', expandedTreeRowIds.has(item.id) ? 'rotate-90' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </button>
                  </div>
                  <span class="group-hover:text-sky-600 transition">{{ getEntityName(item) }}</span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-slate-600">
                  <div class="flex items-center space-x-2">
                    <div v-if="item.assignee_id" class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-300 flex items-center justify-center font-bold text-[10px] uppercase border border-sky-200">
                       {{ getInitials(users.find(u => u.id === item.assignee_id)?.username) }}
                    </div>
                    <div v-else class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 font-bold text-[10px] border border-slate-300">--</div>
                    <span>{{ users.find(u => u.id === item.assignee_id)?.username || 'Unassigned' }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-slate-600">{{ item.status || 'New' }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-slate-600">{{ item.start_date ? new Date(item.start_date).toISOString().split('T')[0] : '--' }}</td>
                <td class="px-4 py-3 whitespace-nowrap" :class="isOverdue(item.end_date) ? 'text-red-600 font-medium' : 'text-slate-600'">
                  {{ item.end_date ? new Date(item.end_date).toISOString().split('T')[0] : '--' }}
                </td>
              </tr>
              <tr v-if="paginatedTreeData.length === 0">
                 <td colspan="5" class="px-4 py-8 text-center text-slate-500">No records found.</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div class="border-t border-slate-300 bg-slate-200 px-4 py-3 flex items-center justify-between sm:px-6">
          <div class="flex items-center space-x-4 text-sm text-slate-600">
             <span>Rows per page:</span>
             <select v-model="rowsPerPage" class="border-none bg-transparent focus:ring-0 text-slate-700 cursor-pointer">
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="25">25</option>
                <option :value="50">50</option>
             </select>
          </div>
          <div class="flex items-center space-x-6 text-sm text-slate-600">
             <span>{{ (currentPage - 1) * rowsPerPage + 1 }}-{{ Math.min(currentPage * rowsPerPage, flatTreeData.length) }} of {{ flatTreeData.length }}</span>
             <div class="flex items-center space-x-2">
                <button @click="setPage(1)" :disabled="currentPage === 1" class="p-1 disabled:opacity-30 hover:text-slate-900 transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path></svg></button>
                <button @click="setPage(currentPage - 1)" :disabled="currentPage === 1" class="p-1 disabled:opacity-30 hover:text-slate-900 transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg></button>
                <span class="px-2">{{ currentPage }}</span>
                <button @click="setPage(currentPage + 1)" :disabled="currentPage === totalPages" class="p-1 disabled:opacity-30 hover:text-slate-900 transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></button>
                <button @click="setPage(totalPages)" :disabled="currentPage === totalPages" class="p-1 disabled:opacity-30 hover:text-slate-900 transition"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg></button>
             </div>
          </div>
        </div>
      </div>

      <!-- Gantt Chart Layout -->
      <div v-else-if="activeTab === 'gantt'" class="bg-slate-100 shadow-sm border border-slate-300 rounded-xl overflow-x-auto p-4 flex flex-col min-h-[500px]">
        <div v-if="ganttRows.length > 0" class="flex-1 min-w-[800px]">
          <g-gantt-chart
            :chart-start="ganttStart"
            :chart-end="ganttEnd"
            precision="day"
            bar-start="myBeginDate"
            bar-end="myEndDate"
            color-scheme="dark"
            grid
            @dragend-bar="onGanttDragEnd"
          >
            <g-gantt-row 
              v-for="row in ganttRows" 
              :key="row.label" 
              :label="row.label" 
              :bars="row.bars" 
            />
          </g-gantt-chart>
        </div>
        <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-500 py-12">
          <svg class="w-12 h-12 text-slate-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          <p class="text-lg font-medium">No Scheduled Tasks Found</p>
          <p class="text-sm mt-1">Add Start and End dates to your issues to see them here.</p>
        </div>
      </div>

      <!-- Stats Layout -->
      <div v-else-if="activeTab === 'stats'" class="space-y-6">

        <!-- Summary Cards Row -->
        <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <div class="bg-slate-100 border border-slate-300 rounded-xl p-5 text-center">
            <div class="text-3xl font-extrabold text-slate-900 mb-1">{{ statsData.total }}</div>
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Tasks</div>
          </div>
          <div class="bg-slate-100 border border-slate-300 rounded-xl p-5 text-center">
            <div class="text-3xl font-extrabold text-emerald-400 mb-1">{{ statsPercent.closed }}%</div>
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Closed</div>
            <div class="text-[10px] text-slate-500 mt-1">{{ statsData.closed }} of {{ statsData.total }}</div>
          </div>
          <div class="bg-slate-100 border border-slate-300 rounded-xl p-5 text-center">
            <div class="text-3xl font-extrabold text-amber-400 mb-1">{{ statsPercent.inProgress }}%</div>
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">In Progress</div>
            <div class="text-[10px] text-slate-500 mt-1">{{ statsData.inProgress }} of {{ statsData.total }}</div>
          </div>
          <div class="bg-slate-100 border border-slate-300 rounded-xl p-5 text-center">
            <div class="text-3xl font-extrabold text-red-400 mb-1">{{ statsPercent.delayed }}%</div>
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Delayed</div>
            <div class="text-[10px] text-slate-500 mt-1">{{ statsData.delayed }} of {{ statsData.total }}</div>
          </div>
          <div class="bg-slate-100 border border-slate-300 rounded-xl p-5 text-center">
            <div class="text-3xl font-extrabold text-red-500 mb-1">{{ statsPercent.rejected }}%</div>
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Rejected</div>
            <div class="text-[10px] text-slate-500 mt-1">{{ statsData.rejected }} of {{ statsData.total }}</div>
          </div>
        </div>

        <!-- Progress Bars -->
        <div class="bg-slate-100 border border-slate-300 rounded-xl p-6">
          <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Task Distribution</h3>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-xs font-semibold mb-1.5">
                <span class="text-emerald-400">Closed</span>
                <span class="text-slate-600">{{ statsPercent.closed }}%</span>
              </div>
              <div class="w-full bg-slate-300 rounded-full h-2.5 overflow-hidden">
                <div class="bg-emerald-500 h-full rounded-full transition-all duration-700" :style="{ width: statsPercent.closed + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs font-semibold mb-1.5">
                <span class="text-amber-400">In Progress</span>
                <span class="text-slate-600">{{ statsPercent.inProgress }}%</span>
              </div>
              <div class="w-full bg-slate-300 rounded-full h-2.5 overflow-hidden">
                <div class="bg-amber-500 h-full rounded-full transition-all duration-700" :style="{ width: statsPercent.inProgress + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs font-semibold mb-1.5">
                <span class="text-red-400">Delayed</span>
                <span class="text-slate-600">{{ statsPercent.delayed }}%</span>
              </div>
              <div class="w-full bg-slate-300 rounded-full h-2.5 overflow-hidden">
                <div class="bg-red-500 h-full rounded-full transition-all duration-700" :style="{ width: statsPercent.delayed + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs font-semibold mb-1.5">
                <span class="text-red-500">Rejected</span>
                <span class="text-slate-600">{{ statsPercent.rejected }}%</span>
              </div>
              <div class="w-full bg-slate-300 rounded-full h-2.5 overflow-hidden">
                <div class="bg-red-600 h-full rounded-full transition-all duration-700" :style="{ width: statsPercent.rejected + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Time Tracking Summary -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Time Summary Cards -->
          <div class="bg-slate-100 border border-slate-300 rounded-xl p-6">
            <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-5">Time Overview</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-slate-200 rounded-lg p-4 text-center border border-slate-300">
                <div class="text-2xl font-extrabold text-sky-400 mb-1">{{ timeStats.totalEstimated }}</div>
                <div class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Est. Hours</div>
              </div>
              <div class="bg-slate-200 rounded-lg p-4 text-center border border-slate-300">
                <div class="text-2xl font-extrabold text-indigo-400 mb-1">{{ timeStats.totalLogged }}</div>
                <div class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Logged Hours</div>
              </div>
              <div class="bg-slate-200 rounded-lg p-4 text-center border border-slate-300">
                <div class="text-lg font-extrabold text-sky-400 mb-1">{{ timeStats.totalReporter }}</div>
                <div class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Reporter Time</div>
              </div>
              <div class="bg-slate-200 rounded-lg p-4 text-center border border-slate-300">
                <div class="text-lg font-extrabold text-indigo-400 mb-1">{{ timeStats.totalAssignee }}</div>
                <div class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Assignee Time</div>
              </div>
            </div>
          </div>

          <!-- Per-User Time Chart -->
          <div class="bg-slate-100 border border-slate-300 rounded-xl p-6">
            <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-5">Time per User</h3>
            <div v-if="timeStats.byUser.length === 0" class="flex flex-col items-center justify-center py-8 text-slate-500">
              <svg class="w-10 h-10 text-slate-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <p class="text-sm">No time logged yet.</p>
            </div>
            <div v-else class="space-y-3 max-h-64 overflow-y-auto pr-2">
              <div v-for="user in timeStats.byUser" :key="user.userId" class="flex items-center gap-3">
                <span class="text-xs font-semibold text-slate-700 w-24 truncate flex-shrink-0" :title="user.username">{{ user.username }}</span>
                <div class="flex-1 bg-slate-300 rounded-full h-5 overflow-hidden">
                  <div class="bg-gradient-to-r from-sky-500 to-indigo-500 h-full rounded-full flex items-center justify-end pr-2 transition-all duration-700"
                       :style="{ width: Math.max((user.hours / maxUserHours) * 100, 8) + '%' }">
                    <span class="text-[10px] font-bold text-white">{{ user.hours }}h</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="statsData.total === 0" class="bg-slate-100 border border-slate-300 rounded-xl p-12 text-center">
          <svg class="w-16 h-16 text-slate-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
          <h3 class="text-lg font-bold text-slate-700 mb-2">No Data Yet</h3>
          <p class="text-slate-500">Create issues and log time to see project statistics.</p>
        </div>
      </div>

      <!-- Tree Grid Layout for other tabs -->
      <div v-else-if="activeTab !== 'wiki' && activeTab !== 'gantt' && activeTab !== 'stats'" class="bg-slate-100 shadow-sm border border-slate-400 rounded-xl overflow-hidden">
        <ul role="list" class="divide-y divide-slate-200">
          <li v-for="item in flatTreeData" :key="item.id" class="transition group flex flex-col">
            <div @click="toggleExpand(item.id)" :style="{ paddingLeft: (item.depth ? item.depth * 24 + 24 : 24) + 'px' }" class="py-4 pr-6 hover:bg-slate-200 cursor-pointer flex items-center justify-between border-l-4 border-transparent hover:border-sky-500">
              
              <div class="flex items-center space-x-3 w-full">
                <!-- Tree Toggle Icon -->
                <div v-if="item.children && item.children.length > 0" @click="toggleTreeRow(item.id, $event)" class="w-6 h-6 flex items-center justify-center text-slate-500 hover:text-sky-400 bg-slate-200 border border-slate-400 rounded cursor-pointer shadow-sm">
                   <svg :class="['w-3.5 h-3.5 transition-transform duration-200', expandedTreeRowIds.has(item.id) ? 'rotate-90' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
                <div v-else class="w-6 h-6"></div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2">
                    <span class="text-xs font-medium text-slate-400 w-10 shrink-0">#{{ item.id }}</span>
                    <p class="text-sm font-semibold text-slate-800 group-hover:text-sky-600 truncate">
                      {{ getEntityName(item) }}
                    </p>
                  </div>
                  
                  <div class="mt-1.5 flex items-center text-xs text-slate-500 space-x-2 overflow-x-auto pb-1 no-scrollbar">
                     <span v-if="item.status" :class="[
                       'px-2 py-0.5 rounded-full font-medium border shrink-0',
                       item.status === 'New' ? 'bg-sky-50 text-sky-700 border-sky-100' : 
                       item.status === 'On Process' ? 'bg-amber-50 text-amber-700 border-amber-100' :
                       item.status === 'Close' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' :
                       'bg-red-50 text-red-700 border-red-100'
                     ]">
                       {{ item.status }}
                     </span>
                  </div>
                </div>
              </div>

            </div>
            
            <!-- Expanded Details Area (For non-issues tabs) -->
            <div v-if="expandedItemId === item.id" class="px-6 py-6 bg-slate-200 border-t border-slate-300 flex flex-col md:flex-row gap-8 shadow-inner" :style="{ marginLeft: (item.depth ? item.depth * 24 : 0) + 'px' }">
              <div v-if="activeTab !== 'wiki' && activeTab !== 'board'">
                 <p class="text-sm text-slate-500">Details not implemented for this entity.</p>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- Data Grid Layout for Wiki -->
      <div v-else-if="activeTab === 'wiki'" class="bg-slate-100 shadow-sm border border-slate-400 rounded-xl overflow-hidden flex flex-col">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm text-left">
            <thead class="bg-slate-200">
              <tr>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Title</th>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Author</th>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Tags</th>
                <th scope="col" class="px-4 py-3 font-semibold text-slate-500">Created At</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 bg-slate-100">
              <tr v-for="item in tabData" :key="item.id" @click="goToWikiDetails(item.id)" class="hover:bg-slate-200 cursor-pointer transition group">
                <td class="px-4 py-3 whitespace-nowrap text-slate-800 font-medium group-hover:text-sky-600 transition">{{ item.title }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-slate-600">
                  <div class="flex items-center space-x-2">
                    <div class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-300 flex items-center justify-center font-bold text-[10px] uppercase border border-sky-200">
                       {{ users.find(u => u.id === item.author_id)?.username?.substring(0, 2) || '--' }}
                    </div>
                    <span>{{ users.find(u => u.id === item.author_id)?.username || 'Unknown' }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center space-x-1">
                    <template v-if="getIssueTags(item.tags).length > 0">
                       <span v-for="tag in getIssueTags(item.tags)" :key="tag" class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-600 border border-indigo-100 font-medium text-[10px]">
                         {{ tag }}
                       </span>
                    </template>
                    <span v-else class="text-xs text-slate-500 italic">No tags</span>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-slate-600">{{ new Date(item.created_at).toLocaleDateString() }}</td>
              </tr>
              <tr v-if="tabData.length === 0">
                 <td colspan="4" class="px-4 py-8 text-center text-slate-500">No wikis found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      </main>
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
          <button @click="submitNewProject" :disabled="!projectForm.name" class="py-2 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg transition font-medium">Create</button>
        </div>
      </div>
    </div>

    <!-- Create Issue Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-slate-100 rounded-xl shadow-2xl w-full max-w-3xl flex flex-col max-h-[90vh]">
        <div class="p-6 border-b border-slate-300 flex justify-between items-center">
          <h2 class="text-xl font-bold text-slate-800">Create New Issue</h2>
          <button @click="showCreateModal = false" class="text-slate-500 hover:text-slate-700 transition">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        
        <div class="p-6 overflow-y-auto flex-1 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-slate-700 mb-1">Title</label>
              <input type="text" v-model="newIssue.title" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500" placeholder="E.g. Fix login bug" required />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Category</label>
              <div class="flex space-x-2">
                <select v-model="newIssue.category" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500">
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Assign To</label>
              <select v-model="newIssue.assignee_id" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500">
                <option value="">Unassigned</option>
                <option v-for="user in users" :key="user.id" :value="user.id">{{ user.username }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Parent Issue</label>
              <select v-model="newIssue.parent_id" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500">
                <option value="">None</option>
                <option v-for="issue in tabData" :key="issue.id" :value="issue.id">#{{ issue.id }} {{ issue.title }}</option>
              </select>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-slate-700 mb-1">Tags</label>
              <div class="w-full bg-slate-200 border border-slate-400 rounded-lg p-2 flex flex-wrap gap-2 focus-within:ring-2 focus-within:ring-sky-500 transition-all">
                <span v-for="(tag, index) in newIssue.tags" :key="index" class="bg-indigo-100 text-indigo-700 px-2 py-1 rounded text-sm font-medium flex items-center">
                  {{ tag }}
                  <button @click.prevent="removeTag(index)" class="ml-1 text-indigo-400 hover:text-indigo-600 focus:outline-none">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
                </span>
                <input type="text" v-model="newTag" @keydown.enter.prevent="addTag" placeholder="Type and press Enter" class="flex-1 min-w-[150px] outline-none bg-transparent text-sm text-slate-900 py-1" />
              </div>
              <p class="text-xs text-slate-500 mt-1">Press Enter to add multiple tags.</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Start Date</label>
              <input type="date" v-model="newIssue.start_date" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">End Date (Due Date)</label>
              <input type="date" v-model="newIssue.end_date" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Estimated Time (Hours)</label>
              <input type="number" step="0.5" v-model="newIssue.estimated_hours" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500" placeholder="e.g. 2.5" />
            </div>

          </div>
          
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <div class="border border-slate-300 rounded-lg overflow-hidden bg-slate-200">
               <div class="flex items-center gap-2 px-3 py-1.5 bg-slate-300 border-b border-slate-400">
                 <span class="text-xs font-semibold text-slate-600 whitespace-nowrap">Code lang:</span>
                 <select v-model="issueCodeLang" @change="onIssueCodeLangChange" class="text-xs bg-slate-200 border border-slate-400 rounded px-2 py-1 text-slate-800 focus:outline-none focus:ring-1 focus:ring-sky-500">
                   <option v-for="lang in codeLanguages" :key="lang.value" :value="lang.value">{{ lang.label }}</option>
                 </select>
                 <span class="text-[10px] text-slate-500 ml-auto">Select a language, then click the code-block button</span>
               </div>
               <QuillEditor ref="issueQuillRef" theme="snow" v-model:content="newIssue.description" contentType="html" toolbar="full" :options="editorOptions" class="h-64" @ready="onIssueEditorReady" />
            </div>
          </div>
        </div>
        
        <div class="p-6 border-t border-slate-300 bg-slate-200 flex justify-end space-x-3 rounded-b-xl">
          <button @click="showCreateModal = false" class="py-2 px-4 bg-slate-200 border border-slate-400 hover:bg-slate-300 text-slate-800 rounded-lg transition font-medium">Cancel</button>
          <button @click="submitIssue" :disabled="!newIssue.title" class="py-2 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg transition font-medium shadow-sm">Create Issue</button>
        </div>
      </div>
    </div>

    <!-- Create Wiki Modal -->
    <div v-if="showWikiModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-slate-100 rounded-xl shadow-2xl w-full max-w-3xl flex flex-col max-h-[90vh]">
        <div class="p-6 border-b border-slate-300 flex justify-between items-center">
          <h2 class="text-xl font-bold text-slate-800">Create New Wiki Page</h2>
          <button @click="showWikiModal = false" class="text-slate-500 hover:text-slate-700 transition">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        
        <div class="p-6 overflow-y-auto flex-1 space-y-6">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Page Title</label>
            <input type="text" v-model="newWiki.title" class="w-full bg-slate-200 border border-slate-400 rounded-lg py-2 px-3 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500" placeholder="E.g. Getting Started" required />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Content</label>
            <div class="border border-slate-300 rounded-lg overflow-hidden bg-slate-200">
               <div class="flex items-center gap-2 px-3 py-1.5 bg-slate-300 border-b border-slate-400">
                 <span class="text-xs font-semibold text-slate-600 whitespace-nowrap">Code lang:</span>
                 <select v-model="wikiCodeLang" @change="onWikiCodeLangChange" class="text-xs bg-slate-200 border border-slate-400 rounded px-2 py-1 text-slate-800 focus:outline-none focus:ring-1 focus:ring-sky-500">
                   <option v-for="lang in codeLanguages" :key="lang.value" :value="lang.value">{{ lang.label }}</option>
                 </select>
                 <span class="text-[10px] text-slate-500 ml-auto">Select a language, then click the code-block button</span>
               </div>
               <QuillEditor theme="snow" v-model:content="newWiki.content" contentType="html" toolbar="full" :options="editorOptions" class="h-[300px]" @ready="onWikiEditorReady" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Tags</label>
            <div class="flex items-center space-x-2 mb-2">
              <input type="text" v-model="wikiTagInput" @keydown.enter.prevent="handleAddWikiTag" placeholder="e.g. documentation, process" class="flex-1 bg-slate-200 border border-slate-400 rounded-lg py-2.5 px-4 text-sm text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 transition" />
              <button @click="handleAddWikiTag" type="button" class="py-2.5 px-5 bg-slate-100 border border-slate-300 text-slate-700 rounded-lg text-sm font-bold hover:bg-slate-200 transition">Add Tag</button>
            </div>
            <div class="flex flex-wrap gap-2 mt-2">
              <span v-for="tag in newWiki.tags" :key="tag" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 shadow-sm">
                {{ tag }}
                <button @click="handleRemoveWikiTag(tag)" class="ml-2 text-indigo-400 hover:text-indigo-600 focus:outline-none transition">
                  <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                </button>
              </span>
            </div>
          </div>
        </div>
        
        <div class="p-6 border-t border-slate-300 bg-slate-200 flex justify-end space-x-3 rounded-b-xl">
          <button @click="showWikiModal = false" class="py-2 px-4 bg-slate-200 border border-slate-400 hover:bg-slate-300 text-slate-800 rounded-lg transition font-medium">Cancel</button>
          <button @click="submitWiki" :disabled="!newWiki.title" class="py-2 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-lg transition font-medium shadow-sm">Save Page</button>
        </div>
      </div>
    </div>

  </div>
</template>
