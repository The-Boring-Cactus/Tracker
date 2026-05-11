import { createRouter, createWebHistory } from 'vue-router'
import SetupView from '../views/SetupView.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProjectView from '../views/ProjectView.vue'
import IssueDetailView from '../views/IssueDetailView.vue'
import WikiDetailView from '../views/WikiDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/setup',
      name: 'setup',
      component: SetupView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/project/:id',
      name: 'project',
      component: ProjectView
    },
    {
      path: '/project/:id/issue/:issueId',
      name: 'issue-detail',
      component: IssueDetailView
    },
    {
      path: '/project/:id/wiki/:wikiId',
      name: 'wiki-detail',
      component: WikiDetailView
    }
  ]
})

export default router
