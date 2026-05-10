import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css' // Premium light theme
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import ganttastic from '@infectoone/vue-ganttastic'

window.hljs = hljs

const app = createApp(App)
app.use(ganttastic)

app.directive('highlight', {
  mounted(el) {
    const blocks = el.querySelectorAll('pre')
    blocks.forEach((block) => {
      hljs.highlightElement(block)
    })
  },
  updated(el) {
    const blocks = el.querySelectorAll('pre')
    blocks.forEach((block) => {
      if (!block.dataset.highlighted) {
        hljs.highlightElement(block)
        block.dataset.highlighted = "true"
      }
    })
  }
})

app.use(createPinia())
app.use(router)
app.component('QuillEditor', QuillEditor)

app.mount('#app')
