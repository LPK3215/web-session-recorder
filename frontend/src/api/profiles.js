import axios from 'axios'

const API_BASE = '/api'

export const profilesAPI = {
  listProfiles() {
    return axios.get(`${API_BASE}/profiles`)
  }
}

