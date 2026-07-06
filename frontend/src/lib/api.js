import axios from 'axios'
import { clearSession, getSessionToken } from './auth'

const api = axios.create({
  baseURL: 'https://idol-survival.onrender.com/api', 
})

// Attach the session token (issued by the backend after Telegram login)
// to every outgoing request.
api.interceptors.request.use((config) => {
  const token = getSessionToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// If the backend says the session is no longer valid, drop it locally too.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearSession()
    }
    return Promise.reject(error)
  }
)

export default api
