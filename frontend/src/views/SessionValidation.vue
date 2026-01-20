<template>
  <div class="session-validation">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>会话检测</h2>
          <el-button @click="goBack">
            <el-icon><Back /></el-icon>
            返回列表
          </el-button>
        </div>
      </template>

      <div class="validation-actions">
        <el-button type="primary" @click="handleValidate" :loading="loading">
          <el-icon><Search /></el-icon>
          开始检测
        </el-button>
        <el-button
          v-if="corruptedSessions.length > 0"
          type="danger"
          @click="handleBatchDelete"
        >
          批量删除 ({{ selectedSessions.length }})
        </el-button>
      </div>

      <el-alert
        v-if="validationResult"
        :title="validationResult.title"
        :type="validationResult.type"
        :description="validationResult.description"
        show-icon
        style="margin: 20px 0"
      />

      <el-table
        v-if="corruptedSessions.length > 0"
        ref="tableRef"
        :data="corruptedSessions"
        stripe
        @selection-change="handleSelectionChange"
        :default-sort="{ prop: 'run_id', order: 'ascending' }"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="run_id" label="损坏的会话 ID" sortable />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Search } from '@element-plus/icons-vue'
import { sessionAPI } from '../api/session'
import { useSession } from '../composables/useSession'

const router = useRouter()

// Use session composables
const { batchDeleteSessions } = useSession()

const loading = ref(false)
const corruptedSessions = ref([])
const selectedSessions = ref([])
const validationResult = ref(null)
const tableRef = ref(null)

const goBack = () => {
  router.push({ name: 'SessionList' })
}

const handleSelectionChange = (selection) => {
  selectedSessions.value = selection
}

const handleValidate = async () => {
  loading.value = true
  validationResult.value = null
  corruptedSessions.value = []
  selectedSessions.value = []

  try {
    const response = await sessionAPI.validateSessions()
    const corrupted = response.data.corrupted_sessions
    const total = response.data.total_checked

    if (corrupted.length === 0) {
      validationResult.value = {
        title: '检测完成',
        type: 'success',
        description: `所有 ${total} 个会话都正常，未发现损坏的会话。`
      }
    } else {
      corruptedSessions.value = corrupted.map(id => ({ run_id: id }))
      validationResult.value = {
        title: '发现损坏的会话',
        type: 'warning',
        description: `检测了 ${total} 个会话，发现 ${corrupted.length} 个损坏的会话（已自动勾选）。`
      }

      // Auto-select all corrupted sessions
      await nextTick()
      corruptedSessions.value.forEach(row => {
        tableRef.value.toggleRowSelection(row, true)
      })
    }
  } catch (error) {
    console.error('Failed to validate sessions:', error)
    ElMessage.error('检测失败')
  } finally {
    loading.value = false
  }
}

const handleBatchDelete = async () => {
  const sessionIds = selectedSessions.value.map(s => s.run_id)
  await batchDeleteSessions(sessionIds, () => {
    // Remove deleted sessions from list
    corruptedSessions.value = corruptedSessions.value.filter(
      s => !sessionIds.includes(s.run_id)
    )
    selectedSessions.value = []

    if (corruptedSessions.value.length === 0) {
      validationResult.value = {
        title: '清理完成',
        type: 'success',
        description: '所有损坏的会话已被删除。'
      }
    }
  })
}
</script>

<style scoped>
.session-validation {
  padding: 20px;
  max-width: 1200px;
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

.validation-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
</style>
