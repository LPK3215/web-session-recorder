<template>
  <div class="home">
    <el-card class="control-card">
      <template #header>
        <div class="card-header">
          <h2>录制控制台</h2>
        </div>
      </template>

      <!-- Recording Configuration Form -->
      <el-form 
        :model="recordingConfig" 
        label-width="140px"
      >
        <el-form-item label="起始 URL">
          <el-select 
            v-model="selectedUrlPreset" 
            placeholder="选择预设网址"
            style="width: 100%"
            :disabled="isRecording"
            @change="onUrlPresetChange"
            filterable
            allow-create
          >
            <el-option
              v-for="preset in urlPresets"
              :key="preset.url"
              :label="preset.name"
              :value="preset.url"
            />
          </el-select>
          <div class="form-tip">选择预设网址或输入自定义 URL</div>
        </el-form-item>

        <el-form-item label="浏览器">
          <el-select 
            v-model="recordingConfig.browser" 
            placeholder="选择浏览器"
            style="width: 100%"
            :disabled="isRecording"
          >
            <el-option label="Chrome" value="chrome" />
            <el-option label="Edge" value="edge" />
            <el-option label="Firefox" value="firefox" />
          </el-select>
        </el-form-item>

        <el-form-item label="隐身模式">
          <el-switch 
            v-model="recordingConfig.incognito"
            active-text="启用"
            inactive-text="禁用"
            :disabled="isRecording"
          />
          <div class="form-tip">在隐身/无痕模式下启动浏览器</div>
        </el-form-item>

        <el-form-item label="用户数据目录">
          <el-input 
            v-model="recordingConfig.user_data_dir" 
            placeholder="留空使用默认配置（可选）"
            clearable
            :disabled="isRecording"
          />
          <div class="form-tip">可选：指定用户数据目录以保留登录状态</div>
        </el-form-item>

        <el-form-item label="窗口大小">
          <el-select 
            v-model="selectedWindowSize" 
            placeholder="选择窗口大小"
            style="width: 100%"
            :disabled="isRecording"
            @change="onWindowSizeChange"
          >
            <el-option
              v-for="preset in windowSizePresets"
              :key="preset.name"
              :label="`${preset.name}${preset.width > 0 ? ` (${preset.width}×${preset.height})` : ''}`"
              :value="preset.width > 0 ? `${preset.width}x${preset.height}` : 'custom'"
            />
          </el-select>
          <div v-if="customSizeMode" class="window-size-group" style="margin-top: 12px;">
            <el-input-number 
              v-model="recordingConfig.window_width" 
              :min="800"
              :max="3840"
              :step="100"
              :disabled="isRecording"
              controls-position="right"
            />
            <span class="size-separator">×</span>
            <el-input-number 
              v-model="recordingConfig.window_height" 
              :min="600"
              :max="2160"
              :step="100"
              :disabled="isRecording"
              controls-position="right"
            />
          </div>
          <div class="form-tip">选择预设窗口大小或自定义尺寸</div>
        </el-form-item>

        <el-form-item class="button-form-item">
          <div class="button-group">
            <el-button 
              v-if="!isRecording"
              type="primary" 
              size="large"
              :loading="isStarting"
              @click="startRecording"
              class="action-button start-button"
            >
              <el-icon :size="20"><VideoPlay /></el-icon>
              <span>开始录制</span>
            </el-button>
            
            <el-button 
              v-if="isRecording"
              type="danger" 
              size="large"
              :loading="isStopping"
              :disabled="isStopping"
              @click="stopRecording"
              class="action-button stop-button"
            >
              <el-icon :size="20"><VideoPause /></el-icon>
              <span>{{ isStopping ? '停止中...' : '停止录制' }}</span>
            </el-button>
            
            <el-button 
              v-if="isRecording"
              size="large"
              disabled
              class="action-button recording-button"
            >
              <el-icon :size="20"><VideoCamera /></el-icon>
              <span>录制中</span>
            </el-button>
            
            <el-button 
              v-if="!isRecording"
              type="success" 
              size="large"
              @click="viewData"
              class="action-button view-button"
            >
              <el-icon :size="20"><Document /></el-icon>
              <span>查看数据</span>
            </el-button>
          </div>
        </el-form-item>
      </el-form>


    </el-card>

    <!-- Data View Dialog -->
    <el-dialog
      v-model="showDataDialog"
      title="录制数据"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-table
        v-loading="loadingSessions"
        :data="sessions"
        stripe
        style="width: 100%"
        max-height="500"
        :default-sort="{ prop: 'start_time', order: 'descending' }"
      >
        <el-table-column prop="run_id" label="运行 ID" width="300" show-overflow-tooltip sortable />
        <el-table-column prop="start_url" label="起始 URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="browser_type" label="浏览器" width="100" sortable />
        <el-table-column prop="event_count" label="事件数" width="100" align="center" sortable />
        <el-table-column prop="status" label="状态" width="100" sortable>
          <template #default="{ row }">
            <el-tag :type="row.status === 'stopped' ? 'success' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="previewSession(row.run_id)"
              link
            >
              <el-icon><View /></el-icon>
              预览
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="showDataDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- Preview Dialog -->
    <el-dialog
      v-model="previewDialog.visible"
      title="会话数据预览"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-scrollbar height="600px">
        <pre class="json-preview">{{ previewDialog.content }}</pre>
      </el-scrollbar>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { VideoCamera, VideoPlay, VideoPause, Document, Download, View } from '@element-plus/icons-vue'
import { sessionAPI } from '../api/session'
import { configAPI } from '../api/config'
import { useSession } from '../composables/useSession'

// Use session composables
const { previewDialog, previewSession, formatDateTime } = useSession()

// Recording state
const isRecording = ref(false)
const isStarting = ref(false)
const isStopping = ref(false)
const currentSessionId = ref(null)

// Presets from config
const urlPresets = ref([])
const windowSizePresets = ref([])
const selectedUrlPreset = ref('')
const selectedWindowSize = ref('')
const customSizeMode = ref(false)

// WebSocket connection
let ws = null

// Recording configuration
const recordingConfig = ref({
  url: 'https://www.baidu.com',
  browser: 'chrome',
  incognito: false,
  user_data_dir: '',
  window_width: 1280,
  window_height: 720
})

// Load presets on mount
onMounted(async () => {
  try {
    const response = await configAPI.getRecorderPresets()
    urlPresets.value = response.data.default_urls
    windowSizePresets.value = response.data.window_sizes
    
    // Set default selections
    if (urlPresets.value.length > 0) {
      selectedUrlPreset.value = urlPresets.value[0].url
      recordingConfig.value.url = urlPresets.value[0].url
    }
    
    if (windowSizePresets.value.length > 0) {
      // Find the first non-custom preset
      const defaultSize = windowSizePresets.value.find(s => s.width > 0 && s.height > 0)
      if (defaultSize) {
        selectedWindowSize.value = `${defaultSize.width}x${defaultSize.height}`
        recordingConfig.value.window_width = defaultSize.width
        recordingConfig.value.window_height = defaultSize.height
      }
    }
  } catch (error) {
    console.error('Failed to load presets:', error)
    ElMessage.warning('加载预设配置失败，使用默认值')
  }
})

// Handle URL preset change
const onUrlPresetChange = (value) => {
  recordingConfig.value.url = value
}

// Handle window size preset change
const onWindowSizeChange = (value) => {
  if (value === 'custom') {
    customSizeMode.value = true
    // Keep current custom values
  } else {
    customSizeMode.value = false
    const [width, height] = value.split('x').map(Number)
    recordingConfig.value.window_width = width
    recordingConfig.value.window_height = height
  }
}

// View data dialog
const showDataDialog = ref(false)
const sessions = ref([])
const loadingSessions = ref(false)

// View data
const viewData = async () => {
  showDataDialog.value = true
  await loadSessions()
}

// Load sessions
const loadSessions = async () => {
  loadingSessions.value = true
  try {
    const response = await sessionAPI.getSessions({ page: 1, page_size: 50 })
    sessions.value = response.data.sessions
  } catch (error) {
    console.error('Failed to load sessions:', error)
    ElMessage.error('加载会话列表失败')
  } finally {
    loadingSessions.value = false
  }
}

// Export session as JSON
const exportSession = async (runId) => {
  try {
    const response = await sessionAPI.exportSessionJSON(runId)

    // Create download link
    const url = window.URL.createObjectURL(new Blob([JSON.stringify(response.data, null, 2)]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `session_${runId}.json`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Failed to export session:', error)
    ElMessage.error('导出失败')
  }
}

// Start recording
const startRecording = async () => {
  isStarting.value = true
  
  try {
    // Prepare config (remove empty optional fields)
    const config = {
      browser: recordingConfig.value.browser,
      incognito: recordingConfig.value.incognito,
      window_width: recordingConfig.value.window_width,
      window_height: recordingConfig.value.window_height
    }
    
    if (recordingConfig.value.url) {
      config.url = recordingConfig.value.url
    }
    
    if (recordingConfig.value.user_data_dir) {
      config.user_data_dir = recordingConfig.value.user_data_dir
    }
    
    // Call API to start session
    const response = await sessionAPI.startSession(config)
    currentSessionId.value = response.data.session_id
    
    // Connect to WebSocket for status monitoring
    connectWebSocket(currentSessionId.value)
    
    isRecording.value = true
    
    ElNotification({
      title: '录制已开始',
      message: `会话 ID: ${currentSessionId.value}`,
      type: 'success',
      duration: 3000
    })
  } catch (error) {
    console.error('Failed to start recording:', error)
    
    // Extract detailed error message
    let errorMessage = '启动录制失败'
    
    if (error.response) {
      // Server responded with error
      if (error.response.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data?.message) {
        errorMessage = error.response.data.message
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      }
      
      // Add status code info
      if (error.response.status) {
        errorMessage = `[${error.response.status}] ${errorMessage}`
      }
    } else if (error.request) {
      // Request was made but no response
      errorMessage = '无法连接到后端服务器，请确保后端正在运行 (http://127.0.0.1:8000)'
    } else {
      // Something else happened
      errorMessage = error.message || '未知错误'
    }
    
    ElNotification({
      title: '启动录制失败',
      message: errorMessage,
      type: 'error',
      duration: 8000,
      dangerouslyUseHTMLString: false
    })
  } finally {
    isStarting.value = false
  }
}

// Stop recording
const stopRecording = async () => {
  console.log('Stop recording button clicked')
  console.log('Current session ID:', currentSessionId.value)
  console.log('Is stopping:', isStopping.value)
  
  if (isStopping.value) {
    console.log('Already stopping, ignoring click')
    return
  }
  
  if (!currentSessionId.value) {
    console.error('No current session ID')
    ElMessage.error('没有正在录制的会话')
    return
  }
  
  isStopping.value = true
  
  try {
    console.log('Calling stop session API...')
    // Call API to stop session
    const response = await sessionAPI.stopSession(currentSessionId.value)
    console.log('Stop session response:', response.data)
    
    // Disconnect WebSocket
    if (ws) {
      ws.close()
      ws = null
    }
    
    isRecording.value = false
    
    ElNotification({
      title: '录制已停止',
      message: `共捕获 ${response.data.event_count} 个事件`,
      type: 'success',
      duration: 5000
    })
    
    // Reset session
    currentSessionId.value = null
  } catch (error) {
    console.error('Failed to stop recording:', error)
    
    // Extract detailed error message
    let errorMessage = '停止录制失败'
    
    if (error.response) {
      if (error.response.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data?.message) {
        errorMessage = error.response.data.message
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      }
      
      if (error.response.status) {
        errorMessage = `[${error.response.status}] ${errorMessage}`
      }
    } else if (error.request) {
      errorMessage = '无法连接到后端服务器'
    } else {
      errorMessage = error.message || '未知错误'
    }
    
    ElNotification({
      title: '停止录制失败',
      message: errorMessage,
      type: 'error',
      duration: 8000
    })
  } finally {
    isStopping.value = false
  }
}

// Connect to WebSocket for status monitoring
const connectWebSocket = (sessionId) => {
  const wsUrl = `ws://127.0.0.1:8000/ws/sessions/${sessionId}`
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket connected')
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket disconnected')
    
    // Browser closed, check session status immediately
    if (isRecording.value && currentSessionId.value) {
      sessionAPI.getSession(currentSessionId.value)
        .then(response => {
          if (response.data.status === 'stopped') {
            isRecording.value = false
            ElNotification({
              title: '录制已停止',
              message: '浏览器已关闭，录制自动停止',
              type: 'info',
              duration: 3000
            })
            currentSessionId.value = null
          }
        })
        .catch(() => {
          isRecording.value = false
          currentSessionId.value = null
        })
    }
  }
}

// Cleanup on unmount
onUnmounted(() => {
  if (ws) {
    ws.close()
    ws = null
  }
})
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.control-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
}

.recording-badge {
  height: 48px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  border: 1px solid #909399;
  background: #f4f4f5;
  color: #606266;
}

.recording-icon {
  display: flex;
  align-items: center;
  color: #909399;
}

.recording-text {
  font-weight: 500;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.button-group {
  display: flex;
  gap: 12px;
  min-height: 48px;
  align-items: center;
}

.action-button {
  min-width: 160px;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.2s ease;
  border: none;
  flex-shrink: 0;
}

.action-button:hover:not(.is-disabled) {
  opacity: 0.85;
}

.action-button:active:not(.is-disabled) {
  opacity: 0.7;
}

.start-button {
  background: #409eff;
  color: #fff;
}

.stop-button {
  background: #f56c6c;
  color: #fff;
}

.view-button {
  background: #67c23a;
  color: #fff;
}

.recording-button {
  background: #909399;
  color: #fff;
  cursor: default;
}

.recording-button:hover {
  background: #909399;
  opacity: 1;
}

.recording-button.is-disabled {
  background: #909399;
  color: #fff;
  opacity: 1;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

.button-form-item {
  margin-bottom: 0;
}

.button-form-item :deep(.el-form-item__content) {
  min-height: 48px;
}

.window-size-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.size-separator {
  font-size: 18px;
  font-weight: 600;
  color: #606266;
}

.json-preview {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
