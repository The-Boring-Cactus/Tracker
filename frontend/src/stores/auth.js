import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(null)

  const login = async (username, password) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch('http://127.0.0.1:8000/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    })

    if (!response.ok) {
      throw new Error('Invalid credentials')
    }

    const data = await response.json()
    token.value = data.access_token
    localStorage.setItem('token', token.value)
    await fetchUser()
  }

  const fetchUser = async () => {
    if (!token.value) return null
    try {
      const response = await fetch('http://127.0.0.1:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
      if (response.ok) {
        user.value = await response.json()
      } else {
        logout()
      }
    } catch (err) {
      console.error('Error fetching user', err)
      logout()
    }
  }

  const showProfileModal = ref(false)

  const register = async (username, email, password, fullName) => {
    const response = await fetch('http://127.0.0.1:8000/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username,
        email,
        password,
        full_name: fullName
      })
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Registration failed')
    }
  }

  const updateProfile = async (data) => {
    const response = await fetch('http://127.0.0.1:8000/auth/me', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Profile update failed')
    }
    
    user.value = await response.json()
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, showProfileModal, login, register, updateProfile, logout, fetchUser }
})
