import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sessionAPI } from '../api/session'

/**
 * 会话管理的通用功能
 */
export function useSession() {
  const loading = ref(false)
  const previewDialog = ref({
    visible: false,
    content: ''
  })

  /**
   * 预览会话JSON数据
   */
  const previewSession = async (sessionId) => {
    try {
      const response = await sessionAPI.exportSessionJSON(sessionId)
      const text = await response.data.text()
      const jsonData = JSON.parse(text)
      previewDialog.value.content = JSON.stringify(jsonData, null, 2)
      previewDialog.value.visible = true
    } catch (error) {
      console.error('Failed to load session data:', error)
      ElMessage.error('加载会话数据失败')
    }
  }

  /**
   * 删除单个会话
   */
  const deleteSession = async (sessionId, onSuccess) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除会话 ${sessionId} 吗？此操作不可恢复。`,
        '确认删除',
        {
          confirmButtonText: '删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      await sessionAPI.deleteSession(sessionId)
      ElMessage.success('删除成功')

      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Failed to delete session:', error)
        ElMessage.error('删除失败')
      }
    }
  }

  /**
   * 批量删除会话
   */
  const batchDeleteSessions = async (sessionIds, onSuccess) => {
    if (sessionIds.length === 0) {
      ElMessage.warning('请先选择要删除的会话')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${sessionIds.length} 个会话吗？此操作不可恢复。`,
        '确认批量删除',
        {
          confirmButtonText: '删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      const response = await sessionAPI.batchDeleteSessions(sessionIds)
      ElMessage.success(`成功删除 ${response.data.deleted} 个会话`)

      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Failed to batch delete sessions:', error)
        ElMessage.error('批量删除失败')
      }
    }
  }

  /**
   * 格式化日期时间
   */
  const formatDateTime = (timestamp) => {
    if (!timestamp) return '-'
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  /**
   * 计算持续时间
   */
  const calculateDuration = (startTime, endTime) => {
    if (!startTime) return '-'
    if (!endTime) return '进行中'

    const start = new Date(startTime)
    const end = new Date(endTime)
    const durationMs = end - start

    const seconds = Math.floor(durationMs / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) {
      return `${hours}小时${minutes % 60}分钟`
    } else if (minutes > 0) {
      return `${minutes}分钟${seconds % 60}秒`
    } else {
      return `${seconds}秒`
    }
  }

  /**
   * 获取浏览器标签类型
   */
  const getBrowserTagType = (browser) => {
    const typeMap = {
      'chrome': 'success',
      'edge': 'primary',
      'firefox': 'warning'
    }
    return typeMap[browser] || ''
  }

  /**
   * 获取状态标签类型
   */
  const getStatusTagType = (status) => {
    const typeMap = {
      'started': 'success',
      'stopped': 'info',
      'error': 'danger'
    }
    return typeMap[status] || ''
  }

  /**
   * 获取状态文本
   */
  const getStatusText = (status) => {
    const textMap = {
      'started': '已开始',
      'stopped': '已停止',
      'error': '错误'
    }
    return textMap[status] || status
  }

  return {
    loading,
    previewDialog,
    previewSession,
    deleteSession,
    batchDeleteSessions,
    formatDateTime,
    calculateDuration,
    getBrowserTagType,
    getStatusTagType,
    getStatusText
  }
}
