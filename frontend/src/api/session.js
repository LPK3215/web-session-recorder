import axios from 'axios'

const API_BASE = '/api'

export const sessionAPI = {
  // Start recording session
  startSession(config) {
    return axios.post(`${API_BASE}/sessions/start`, config)
  },
  
  // Stop recording session
  stopSession(sessionId) {
    return axios.post(`${API_BASE}/sessions/${sessionId}/stop`)
  },
  
  // Get all sessions
  getSessions(params) {
    return axios.get(`${API_BASE}/sessions`, { params })
  },
  
  // Get session by ID
  getSession(sessionId) {
    return axios.get(`${API_BASE}/sessions/${sessionId}`)
  },

  // Get session detail (full JSON)
  getSessionDetail(sessionId) {
    return axios.get(`${API_BASE}/sessions/${sessionId}`)
  },

  // Delete session
  deleteSession(sessionId) {
    return axios.delete(`${API_BASE}/sessions/${sessionId}`)
  },

  // Batch delete sessions
  batchDeleteSessions(sessionIds) {
    return axios.post(`${API_BASE}/sessions/batch-delete`, sessionIds)
  },

  // Get session events
  getSessionEvents(sessionId, params) {
    return axios.get(`${API_BASE}/sessions/${sessionId}/events`, { params })
  },
  
  // Export session as JSON
  exportSessionJSON(sessionId) {
    return axios.get(`${API_BASE}/sessions/${sessionId}/export`, {
      responseType: 'blob'
    })
  },

  // Validate all sessions
  validateSessions() {
    return axios.get(`${API_BASE}/sessions/validate`)
  }
}
