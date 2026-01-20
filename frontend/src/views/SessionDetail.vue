<template>
  <div class="session-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div>
            <h2>会话详情</h2>
            <el-text type="info" size="small">会话 ID: {{ sessionId }}</el-text>
          </div>
          <div class="header-actions">
            <el-button @click="handlePreview">
              <el-icon><View /></el-icon>
              预览JSON
            </el-button>
            <el-button @click="goBack">
              <el-icon><Back /></el-icon>
              返回列表
            </el-button>
          </div>
        </div>
      </template>

      <!-- Session Metadata -->
      <div v-if="session" class="session-metadata">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="会话 ID">
            <el-text class="monospace">{{ session.run_id }}</el-text>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(session.status)">
              {{ getStatusText(session.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="起始 URL">
            <el-text v-if="session.start_url">{{ session.start_url }}</el-text>
            <el-text v-else type="info">空白页面</el-text>
          </el-descriptions-item>
          <el-descriptions-item label="浏览器">
            <el-tag :type="getBrowserTagType(session.browser_type)">
              {{ session.browser_type }}
            </el-tag>
            <el-tag v-if="session.incognito" type="warning" size="small" style="margin-left: 8px">
              隐身模式
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(session.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ session.end_time ? formatDateTime(session.end_time) : '进行中' }}
          </el-descriptions-item>
          <el-descriptions-item label="持续时间">
            {{ calculateDuration(session.start_time, session.end_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="事件总数">
            <el-tag type="info">{{ session.event_count }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider />

      <!-- Events Timeline -->
      <div class="events-section">
        <div class="section-header">
          <h3>事件时间线</h3>
          <el-text type="info">共 {{ pagination.total }} 个事件</el-text>
        </div>

        <div v-if="events.length === 0 && !eventsLoading" class="empty-state">
          <el-empty description="暂无事件数据" />
        </div>

        <div v-else v-loading="eventsLoading" class="events-timeline">
          <el-timeline>
            <el-timeline-item
              v-for="event in events"
              :key="event.id"
              :timestamp="formatTimestamp(event.timestamp)"
              placement="top"
            >
              <el-card class="event-card" shadow="hover">
                <div class="event-header">
                  <div class="event-title">
                    <el-tag :type="getEventTypeColor(event.event_type)" size="large">
                      {{ event.event_type }}
                    </el-tag>
                    <el-text class="event-seq">#{{ event.seq }}</el-text>
                  </div>
                  <el-button
                    text
                    @click="toggleEventDetail(event.id)"
                    :icon="expandedEvents.has(event.id) ? 'ArrowUp' : 'ArrowDown'"
                  >
                    {{ expandedEvents.has(event.id) ? '收起' : '展开' }}
                  </el-button>
                </div>

                <div class="event-summary">
                  <div class="event-info-item">
                    <el-icon><Link /></el-icon>
                    <el-text class="event-url" size="small">{{ event.page_url }}</el-text>
                  </div>
                  <div v-if="event.page_title" class="event-info-item">
                    <el-icon><Document /></el-icon>
                    <el-text size="small">{{ event.page_title }}</el-text>
                  </div>
                </div>

                <!-- Expanded Event Details -->
                <el-collapse-transition>
                  <div v-show="expandedEvents.has(event.id)" class="event-details">
                    <el-divider />

                    <!-- Target Data -->
                    <div v-if="event.target_data" class="detail-section">
                      <h4>目标元素</h4>
                      <el-descriptions :column="1" size="small" border>
                        <el-descriptions-item
                          v-for="(value, key) in event.target_data"
                          :key="key"
                          :label="key"
                        >
                          <el-text class="detail-value">{{ formatValue(value) }}</el-text>
                        </el-descriptions-item>
                      </el-descriptions>
                    </div>

                    <!-- Locators -->
                    <div v-if="event.locators && event.locators.length > 0" class="detail-section">
                      <h4>定位器策略</h4>
                      <el-space direction="vertical" style="width: 100%">
                        <el-card
                          v-for="(locator, index) in event.locators"
                          :key="index"
                          class="locator-card"
                          shadow="never"
                        >
                          <div class="locator-header">
                            <el-tag size="small">{{ locator.strategy }}</el-tag>
                            <el-tag
                              v-if="locator.stability"
                              :type="getStabilityTagType(locator.stability)"
                              size="small"
                            >
                              {{ locator.stability }}
                            </el-tag>
                          </div>
                          <el-text class="locator-selector monospace">
                            {{ locator.selector }}
                          </el-text>
                        </el-card>
                      </el-space>
                    </div>

                    <!-- Network Data -->
                    <div v-if="event.network_data" class="detail-section">
                      <h4>网络请求</h4>
                      <el-tabs type="border-card">
                        <el-tab-pane label="请求">
                          <el-descriptions :column="1" size="small" border>
                            <el-descriptions-item label="方法">
                              <el-tag size="small">{{ event.network_data.request?.method }}</el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item label="URL">
                              <el-text class="detail-value">{{ event.network_data.request?.url }}</el-text>
                            </el-descriptions-item>
                            <el-descriptions-item v-if="event.network_data.request?.headers" label="请求头">
                              <pre class="json-display">{{ formatJSON(event.network_data.request.headers) }}</pre>
                            </el-descriptions-item>
                            <el-descriptions-item v-if="event.network_data.request?.body" label="请求体">
                              <pre class="json-display">{{ formatJSON(event.network_data.request.body) }}</pre>
                            </el-descriptions-item>
                          </el-descriptions>
                        </el-tab-pane>
                        <el-tab-pane label="响应">
                          <el-descriptions :column="1" size="small" border>
                            <el-descriptions-item label="状态码">
                              <el-tag
                                :type="getStatusCodeTagType(event.network_data.response?.status)"
                                size="small"
                              >
                                {{ event.network_data.response?.status }}
                              </el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item v-if="event.network_data.response?.headers" label="响应头">
                              <pre class="json-display">{{ formatJSON(event.network_data.response.headers) }}</pre>
                            </el-descriptions-item>
                            <el-descriptions-item v-if="event.network_data.response?.body" label="响应体">
                              <pre class="json-display">{{ formatJSON(event.network_data.response.body) }}</pre>
                            </el-descriptions-item>
                          </el-descriptions>
                        </el-tab-pane>
                      </el-tabs>
                    </div>

                    <!-- Screenshots -->
                    <div v-if="event.screenshot_path" class="detail-section">
                      <h4>截图</h4>
                      <el-image
                        :src="event.screenshot_path"
                        :preview-src-list="[event.screenshot_path]"
                        fit="contain"
                        style="max-width: 100%; max-height: 400px"
                      />
                    </div>

                    <!-- Raw Data -->
                    <div v-if="event.raw_data" class="detail-section">
                      <h4>原始数据</h4>
                      <el-collapse>
                        <el-collapse-item title="查看原始 JSON 数据" name="raw">
                          <pre class="json-display">{{ formatJSON(event.raw_data) }}</pre>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </div>
                </el-collapse-transition>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.total > 0" class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </el-card>

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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Link, Document, View } from '@element-plus/icons-vue'
import { sessionAPI } from '../api/session'
import { useSession } from '../composables/useSession'

const route = useRoute()
const router = useRouter()

// Use session composables
const {
  previewDialog,
  previewSession,
  formatDateTime,
  calculateDuration,
  getBrowserTagType,
  getStatusTagType,
  getStatusText
} = useSession()

// Session ID from route params
const sessionId = ref(route.params.id)

// Loading states
const loading = ref(false)
const eventsLoading = ref(false)

// Session data
const session = ref(null)
const events = ref([])

// Expanded events tracking
const expandedEvents = ref(new Set())

// Pagination
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// Handle preview
const handlePreview = async () => {
  await previewSession(sessionId.value)
}

// Fetch session details
const fetchSession = async () => {
  loading.value = true
  
  try {
    const response = await sessionAPI.getSession(sessionId.value)
    session.value = response.data
  } catch (error) {
    console.error('Failed to fetch session:', error)
    ElMessage.error(error.response?.data?.detail || '获取会话详情失败')
  } finally {
    loading.value = false
  }
}

// Fetch session events
const fetchEvents = async () => {
  eventsLoading.value = true
  
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    }
    
    const response = await sessionAPI.getSessionEvents(sessionId.value, params)
    events.value = response.data.events || []
    pagination.value.total = response.data.total || 0
  } catch (error) {
    console.error('Failed to fetch events:', error)
    ElMessage.error(error.response?.data?.detail || '获取事件列表失败')
  } finally {
    eventsLoading.value = false
  }
}

// Toggle event detail expansion
const toggleEventDetail = (eventId) => {
  if (expandedEvents.value.has(eventId)) {
    expandedEvents.value.delete(eventId)
  } else {
    expandedEvents.value.add(eventId)
  }
}

// Handle page size change
const handleSizeChange = (newSize) => {
  pagination.value.pageSize = newSize
  pagination.value.page = 1
  fetchEvents()
}

// Handle page change
const handlePageChange = (newPage) => {
  pagination.value.page = newPage
  fetchEvents()
}

// Go back to session list
const goBack = () => {
  router.push('/sessions')
}

// Format timestamp for timeline
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3
  })
}

// Get event type color
const getEventTypeColor = (eventType) => {
  const colorMap = {
    'click': 'primary',
    'dblclick': 'primary',
    'contextmenu': 'primary',
    'input': 'success',
    'change': 'success',
    'submit': 'warning',
    'navigation': 'info',
    'dialog': 'warning',
    'download': 'danger',
    'keydown': '',
    'file_upload': 'warning'
  }
  return colorMap[eventType] || ''
}

// Get stability tag type
const getStabilityTagType = (stability) => {
  const typeMap = {
    'high': 'success',
    'medium': 'warning',
    'low': 'info'
  }
  return typeMap[stability] || ''
}

// Get status code tag type
const getStatusCodeTagType = (statusCode) => {
  if (!statusCode) return ''
  if (statusCode >= 200 && statusCode < 300) return 'success'
  if (statusCode >= 300 && statusCode < 400) return 'info'
  if (statusCode >= 400 && statusCode < 500) return 'warning'
  if (statusCode >= 500) return 'danger'
  return ''
}

// Format value for display
const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

// Format JSON for display
const formatJSON = (data) => {
  if (!data) return ''
  try {
    if (typeof data === 'string') {
      return JSON.stringify(JSON.parse(data), null, 2)
    }
    return JSON.stringify(data, null, 2)
  } catch (error) {
    return String(data)
  }
}

// Fetch data on mount
onMounted(() => {
  fetchSession()
  fetchEvents()
})
</script>

<style scoped>
.session-detail {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.session-metadata {
  margin-bottom: 20px;
}

.monospace {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
}

.events-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 20px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.events-timeline {
  margin-top: 20px;
}

.event-card {
  margin-bottom: 0;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.event-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.event-seq {
  font-family: 'Courier New', Courier, monospace;
  color: #909399;
  font-size: 14px;
}

.event-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-url {
  word-break: break-all;
  color: #606266;
}

.event-details {
  margin-top: 16px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.detail-value {
  word-break: break-all;
  font-size: 13px;
}

.locator-card {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
}

.locator-header {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.locator-selector {
  display: block;
  padding: 8px;
  background-color: #fff;
  border-radius: 4px;
  font-size: 13px;
  word-break: break-all;
}

.json-display {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  line-height: 1.5;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-timeline-item__timestamp) {
  font-size: 12px;
  color: #909399;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  background-color: #fafafa;
}

:deep(.el-collapse-item__header) {
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
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
