<template>
  <div class="session-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>录制会话列表</h2>
          <div class="header-actions">
            <el-button
              v-if="selectedSessions.length > 0"
              type="danger"
              @click="handleBatchDelete"
            >
              批量删除 ({{ selectedSessions.length }})
            </el-button>
            <el-button type="warning" @click="handleValidate">
              <el-icon><Warning /></el-icon>
              检测损坏
            </el-button>
            <el-button type="primary" @click="refreshSessions">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- Filters -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleFilterChange"
          />
        </el-form-item>

        <el-form-item label="浏览器">
          <el-select
            v-model="filters.browser"
            placeholder="全部浏览器"
            clearable
            @change="handleFilterChange"
            style="width: 150px"
          >
            <el-option label="Chrome" value="chrome" />
            <el-option label="Edge" value="edge" />
            <el-option label="Firefox" value="firefox" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部状态"
            clearable
            @change="handleFilterChange"
            style="width: 150px"
          >
            <el-option label="已开始" value="started" />
            <el-option label="已停止" value="stopped" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Sessions Table -->
      <el-table
        v-loading="loading"
        :data="sessions"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
        @selection-change="handleSelectionChange"
        class="sessions-table"
        :default-sort="{ prop: 'start_time', order: 'descending' }"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column prop="run_id" label="会话 ID" width="280" sortable>
          <template #default="{ row }">
            <el-text class="clickable-id">{{ row.run_id }}</el-text>
          </template>
        </el-table-column>

        <el-table-column prop="start_url" label="起始 URL" min-width="200" sortable>
          <template #default="{ row }">
            <el-text v-if="row.start_url" class="url-text">
              {{ row.start_url }}
            </el-text>
            <el-text v-else type="info">空白页面</el-text>
          </template>
        </el-table-column>

        <el-table-column prop="start_time" label="开始时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>

        <el-table-column prop="duration" label="持续时间" width="120">
          <template #default="{ row }">
            {{ calculateDuration(row.start_time, row.end_time) }}
          </template>
        </el-table-column>

        <el-table-column prop="event_count" label="事件数" width="100" align="center" sortable>
          <template #default="{ row }">
            <el-tag type="info">{{ row.event_count }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="browser_type" label="浏览器" width="100" align="center" sortable>
          <template #default="{ row }">
            <el-tag :type="getBrowserTagType(row.browser_type)">
              {{ row.browser_type }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100" align="center" sortable>
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click.stop="handlePreview(row)">预览</el-button>
            <el-button size="small" type="danger" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Warning } from '@element-plus/icons-vue'
import { sessionAPI } from '../api/session'
import { useSession } from '../composables/useSession'

const router = useRouter()

// Use session composables
const {
  previewDialog,
  previewSession,
  deleteSession,
  batchDeleteSessions,
  formatDateTime,
  calculateDuration,
  getBrowserTagType,
  getStatusTagType,
  getStatusText
} = useSession()

// Loading state
const loading = ref(false)

// Sessions data
const sessions = ref([])

// Pagination
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// Filters
const filters = ref({
  dateRange: null,
  browser: '',
  status: ''
})

// Selected sessions for batch operations
const selectedSessions = ref([])

// Handle selection change
const handleSelectionChange = (selection) => {
  selectedSessions.value = selection
}

// Handle validate sessions
const handleValidate = () => {
  router.push({ name: 'SessionValidation' })
}

// Handle batch delete
const handleBatchDelete = async () => {
  const sessionIds = selectedSessions.value.map(s => s.run_id)
  await batchDeleteSessions(sessionIds, () => {
    selectedSessions.value = []
    fetchSessions()
  })
}

// Fetch sessions from API
const fetchSessions = async () => {
  loading.value = true
  
  try {
    // Build query parameters
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    }
    
    // Add filters if set
    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
      params.start_date = filters.value.dateRange[0]
      params.end_date = filters.value.dateRange[1]
    }
    
    if (filters.value.browser) {
      params.browser_type = filters.value.browser
    }
    
    if (filters.value.status) {
      params.status = filters.value.status
    }
    
    // Call API
    const response = await sessionAPI.getSessions(params)
    
    sessions.value = response.data.sessions || []
    pagination.value.total = response.data.total || 0
  } catch (error) {
    console.error('Failed to fetch sessions:', error)
    ElMessage.error(error.response?.data?.detail || '获取会话列表失败')
  } finally {
    loading.value = false
  }
}

// Handle row click - navigate to session detail
const handleRowClick = (row) => {
  router.push({
    name: 'SessionDetail',
    params: { id: row.run_id }
  })
}

// Handle filter change
const handleFilterChange = () => {
  // Reset to first page when filters change
  pagination.value.page = 1
  fetchSessions()
}

// Reset filters
const resetFilters = () => {
  filters.value = {
    dateRange: null,
    browser: '',
    status: ''
  }
  pagination.value.page = 1
  fetchSessions()
}

// Handle page size change
const handleSizeChange = (newSize) => {
  pagination.value.pageSize = newSize
  pagination.value.page = 1
  fetchSessions()
}

// Handle page change
const handlePageChange = (newPage) => {
  pagination.value.page = newPage
  fetchSessions()
}

// Refresh sessions
const refreshSessions = () => {
  fetchSessions()
}

// Handle preview
const handlePreview = async (row) => {
  await previewSession(row.run_id)
}

// Handle delete
const handleDelete = async (row) => {
  await deleteSession(row.run_id, fetchSessions)
}

// Fetch sessions on mount
onMounted(() => {
  fetchSessions()
})
</script>

<style scoped>
.session-list {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-form {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.sessions-table {
  cursor: pointer;
}

.sessions-table :deep(.el-table__row) {
  cursor: pointer;
  transition: background-color 0.2s;
}

.sessions-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}

.clickable-id {
  color: #409eff;
  font-family: monospace;
}

.url-text {
  word-break: break-all;
  font-size: 13px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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
