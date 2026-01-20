import axios from 'axios'

const API_BASE = '/api'

export const configAPI = {
  // Get all configurations
  getConfig() {
    return axios.get(`${API_BASE}/config`)
  },
  
  // Update configuration
  updateConfig(file, content) {
    return axios.put(`${API_BASE}/config`, { file, content })
  },
  
  // Get recorder presets (default URLs and window sizes)
  getRecorderPresets(profile) {
    const params = profile ? { profile } : {}
    return axios.get(`${API_BASE}/config/presets`, { params })
  }
}
