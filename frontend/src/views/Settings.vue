<template>
  <div class="settings">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2>系统设置</h2>
          <el-button type="primary" @click="refreshConfig">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-alert
        title="配置说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        编辑 YAML 配置文件以自定义系统行为。保存前会进行验证，确保配置格式正确。
      </el-alert>

      <!-- Configuration Tabs -->
      <el-tabs v-model="activeTab" type="border-card" class="config-tabs">
        <!-- App Config -->
        <el-tab-pane label="应用配置 (app.yaml)" name="app">
          <div class="config-editor">
            <div class="editor-header">
              <el-text type="info">应用和服务器设置</el-text>
              <div class="editor-actions">
                <el-button size="small" @click="resetConfig('app')">
                  <el-icon><RefreshLeft /></el-icon>
                  重置为默认值
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  :loading="saving.app"
                  @click="saveConfig('app')"
                >
                  <el-icon><Check /></el-icon>
                  保存
                </el-button>
              </div>
            </div>
            <el-input
              v-model="configs.app"
              type="textarea"
              :rows="15"
              placeholder="YAML 配置内容"
              class="yaml-editor"
              :disabled="saving.app"
            />
            <div v-if="validationErrors.app" class="validation-error">
              <el-alert :title="validationErrors.app" type="error" :closable="false" />
            </div>
          </div>
        </el-tab-pane>

        <!-- Browser Config -->
        <el-tab-pane label="浏览器配置 (browser.yaml)" name="browser">
          <div class="config-editor">
            <div class="editor-header">
              <el-text type="info">浏览器路径和启动选项</el-text>
              <div class="editor-actions">
                <el-button size="small" @click="resetConfig('browser')">
                  <el-icon><RefreshLeft /></el-icon>
                  重置为默认值
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  :loading="saving.browser"
                  @click="saveConfig('browser')"
                >
                  <el-icon><Check /></el-icon>
                  保存
                </el-button>
              </div>
            </div>
            <el-input
              v-model="configs.browser"
              type="textarea"
              :rows="15"
              placeholder="YAML 配置内容"
              class="yaml-editor"
              :disabled="saving.browser"
            />
            <div v-if="validationErrors.browser" class="validation-error">
              <el-alert :title="validationErrors.browser" type="error" :closable="false" />
            </div>
          </div>
        </el-tab-pane>

        <!-- Recorder Config -->
        <el-tab-pane label="录制配置 (recorder.yaml)" name="recorder">
          <div class="config-editor">
            <div class="editor-header">
              <el-text type="info">录制策略和事件捕获设置</el-text>
              <div class="editor-actions">
                <el-button size="small" @click="resetConfig('recorder')">
                  <el-icon><RefreshLeft /></el-icon>
                  重置为默认值
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  :loading="saving.recorder"
                  @click="saveConfig('recorder')"
                >
                  <el-icon><Check /></el-icon>
                  保存
                </el-button>
              </div>
            </div>
            <el-input
              v-model="configs.recorder"
              type="textarea"
              :rows="15"
              placeholder="YAML 配置内容"
              class="yaml-editor"
              :disabled="saving.recorder"
            />
            <div v-if="validationErrors.recorder" class="validation-error">
              <el-alert :title="validationErrors.recorder" type="error" :closable="false" />
            </div>
          </div>
        </el-tab-pane>

        <!-- Database Config -->
        <el-tab-pane label="数据库配置 (database.yaml)" name="database">
          <div class="config-editor">
            <div class="editor-header">
              <el-text type="info">数据库连接和保留策略</el-text>
              <div class="editor-actions">
                <el-button size="small" @click="resetConfig('database')">
                  <el-icon><RefreshLeft /></el-icon>
                  重置为默认值
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  :loading="saving.database"
                  @click="saveConfig('database')"
                >
                  <el-icon><Check /></el-icon>
                  保存
                </el-button>
              </div>
            </div>
            <el-input
              v-model="configs.database"
              type="textarea"
              :rows="15"
              placeholder="YAML 配置内容"
              class="yaml-editor"
              :disabled="saving.database"
            />
            <div v-if="validationErrors.database" class="validation-error">
              <el-alert :title="validationErrors.database" type="error" :closable="false" />
            </div>
          </div>
        </el-tab-pane>

        <!-- Locators Config -->
        <el-tab-pane label="定位器配置 (locators.yaml)" name="locators">
          <div class="config-editor">
            <div class="editor-header">
              <el-text type="info">定位器生成策略和优先级</el-text>
              <div class="editor-actions">
                <el-button size="small" @click="resetConfig('locators')">
                  <el-icon><RefreshLeft /></el-icon>
                  重置为默认值
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  :loading="saving.locators"
                  @click="saveConfig('locators')"
                >
                  <el-icon><Check /></el-icon>
                  保存
                </el-button>
              </div>
            </div>
            <el-input
              v-model="configs.locators"
              type="textarea"
              :rows="15"
              placeholder="YAML 配置内容"
              class="yaml-editor"
              :disabled="saving.locators"
            />
            <div v-if="validationErrors.locators" class="validation-error">
              <el-alert :title="validationErrors.locators" type="error" :closable="false" />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, RefreshLeft, Check } from '@element-plus/icons-vue'
import { configAPI } from '../api/config'

// Active tab
const activeTab = ref('app')

// Loading state
const loading = ref(false)

// Saving states for each config file
const saving = reactive({
  app: false,
  browser: false,
  recorder: false,
  database: false,
  locators: false
})

// Configuration content for each file
const configs = reactive({
  app: '',
  browser: '',
  recorder: '',
  database: '',
  locators: ''
})

// Original configs for reset functionality
const originalConfigs = reactive({
  app: '',
  browser: '',
  recorder: '',
  database: '',
  locators: ''
})

// Validation errors
const validationErrors = reactive({
  app: '',
  browser: '',
  recorder: '',
  database: '',
  locators: ''
})

// Fetch all configurations
const fetchConfigs = async () => {
  loading.value = true
  
  try {
    const response = await configAPI.getConfig()
    const data = response.data
    
    // Convert config objects to YAML strings
    // The backend should return YAML strings, but if it returns objects, we'll handle both
    for (const key of ['app', 'browser', 'recorder', 'database', 'locators']) {
      if (data[key]) {
        if (typeof data[key] === 'string') {
          configs[key] = data[key]
          originalConfigs[key] = data[key]
        } else {
          // If backend returns object, convert to YAML-like format
          configs[key] = convertToYAML(data[key])
          originalConfigs[key] = convertToYAML(data[key])
        }
      }
    }
  } catch (error) {
    console.error('Failed to fetch configs:', error)
    ElMessage.error(error.response?.data?.detail || '获取配置失败')
  } finally {
    loading.value = false
  }
}

// Convert object to YAML-like string (simple implementation)
const convertToYAML = (obj, indent = 0) => {
  let yaml = ''
  const spaces = '  '.repeat(indent)
  
  for (const [key, value] of Object.entries(obj)) {
    if (value === null || value === undefined) {
      yaml += `${spaces}${key}: null\n`
    } else if (typeof value === 'object' && !Array.isArray(value)) {
      yaml += `${spaces}${key}:\n`
      yaml += convertToYAML(value, indent + 1)
    } else if (Array.isArray(value)) {
      yaml += `${spaces}${key}:\n`
      value.forEach(item => {
        if (typeof item === 'object') {
          yaml += `${spaces}  -\n`
          yaml += convertToYAML(item, indent + 2)
        } else {
          yaml += `${spaces}  - ${item}\n`
        }
      })
    } else if (typeof value === 'string') {
      yaml += `${spaces}${key}: "${value}"\n`
    } else {
      yaml += `${spaces}${key}: ${value}\n`
    }
  }
  
  return yaml
}

// Validate YAML syntax (basic validation)
const validateYAML = (content, configName) => {
  validationErrors[configName] = ''
  
  if (!content || content.trim() === '') {
    validationErrors[configName] = '配置内容不能为空'
    return false
  }
  
  // Basic YAML syntax checks
  const lines = content.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    // Skip empty lines and comments
    if (line.trim() === '' || line.trim().startsWith('#')) {
      continue
    }
    
    // Check for basic key-value format
    if (line.includes(':')) {
      const parts = line.split(':')
      if (parts.length < 2) {
        validationErrors[configName] = `第 ${i + 1} 行格式错误：缺少值`
        return false
      }
    }
  }
  
  return true
}

// Save configuration
const saveConfig = async (configName) => {
  // Validate before saving
  if (!validateYAML(configs[configName], configName)) {
    ElMessage.error('配置验证失败，请检查格式')
    return
  }
  
  saving[configName] = true
  
  try {
    await configAPI.updateConfig(configName, configs[configName])
    
    // Update original config after successful save
    originalConfigs[configName] = configs[configName]
    
    ElMessage.success(`${configName}.yaml 保存成功`)
  } catch (error) {
    console.error(`Failed to save ${configName} config:`, error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || '保存配置失败'
    ElMessage.error(errorMsg)
    
    // Set validation error if backend returns validation error
    if (error.response?.status === 400) {
      validationErrors[configName] = errorMsg
    }
  } finally {
    saving[configName] = false
  }
}

// Reset configuration to original
const resetConfig = async (configName) => {
  try {
    await ElMessageBox.confirm(
      `确定要将 ${configName}.yaml 重置为上次保存的版本吗？`,
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    configs[configName] = originalConfigs[configName]
    validationErrors[configName] = ''
    
    ElMessage.success('已重置配置')
  } catch (error) {
    // User cancelled
  }
}

// Refresh all configurations
const refreshConfig = () => {
  fetchConfigs()
  ElMessage.success('配置已刷新')
}

// Fetch configs on mount
onMounted(() => {
  fetchConfigs()
})
</script>

<style scoped>
.settings {
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

.config-tabs {
  margin-top: 20px;
}

.config-editor {
  padding: 16px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.yaml-editor {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
}

.yaml-editor :deep(textarea) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
}

.yaml-editor :deep(textarea:focus) {
  background-color: #fff;
  border-color: #409eff;
}

.validation-error {
  margin-top: 12px;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tab-pane) {
  min-height: 400px;
}
</style>
