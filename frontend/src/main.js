import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import ganttastic from '@infectoone/vue-ganttastic'

// Register common languages explicitly for reliable detection
import 'highlight.js/lib/languages/sql'
import 'highlight.js/lib/languages/csharp'
import 'highlight.js/lib/languages/bash'
import 'highlight.js/lib/languages/json'
import 'highlight.js/lib/languages/c'
import 'highlight.js/lib/languages/cpp'
import 'highlight.js/lib/languages/python'
import 'highlight.js/lib/languages/javascript'
import 'highlight.js/lib/languages/xml'
import 'highlight.js/lib/languages/yaml'
import 'highlight.js/lib/languages/css'
import 'highlight.js/lib/languages/typescript'

window.hljs = hljs

const app = createApp(App)
app.use(ganttastic)

app.directive('highlight', {
  mounted(el) {
    highlightPreBlocks(el)
  },
  updated(el) {
    highlightPreBlocks(el)
  }
})

function highlightPreBlocks(el) {
  const blocks = el.querySelectorAll('pre')
  blocks.forEach((pre) => {
    if (pre.dataset.highlighted === 'true') return
    pre.dataset.highlighted = 'true'

    // If there's a <code> child, highlight it
    const code = pre.querySelector('code')
    if (code) {
      hljs.highlightElement(code)
      return
    }

    // Bare <pre> from Quill — wrap content in <code> so highlight.js works
    const text = pre.textContent
    // Try to detect language from Quill's class
    const langClass = Array.from(pre.classList).find(c => c.startsWith('language-'))
    const lang = langClass ? langClass.replace('language-', '') : ''
    let result
    try {
      result = lang
        ? hljs.highlight(text, { language: lang, ignoreIllegals: true })
        : hljs.highlightAuto(text)
    } catch {
      result = hljs.highlightAuto(text)
    }
    pre.innerHTML = result.value
    pre.classList.add('hljs')
  })
}

app.use(createPinia())
app.use(router)
app.component('QuillEditor', QuillEditor)

app.mount('#app')
