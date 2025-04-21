<template>
    <div class="history-container">
        <el-card shadow="hover" class="history-card">
            <template #header>
                <div class="card-header">
                    <el-button type="primary" size="small" :icon="Refresh" @click="fetchHistory" :loading="loading">
                        刷新
                    </el-button>
                    <el-button type="primary" size="small" @click="backUpload">重新上传</el-button>
                </div>
            </template>

            <!-- 加载状态 -->
            <el-skeleton :rows="5" animated v-if="loading" />

            <!-- 空状态 -->
            <el-empty v-else-if="history.length === 0 && !error" description="暂无上传记录" :image-size="100" />

            <!-- 错误状态 -->
            <el-alert v-else-if="error" :title="error" type="error" show-icon :closable="false" class="error-alert">
                <template #footer>
                    <el-button type="primary" size="small" @click="fetchHistory">
                        重试
                    </el-button>
                </template>
            </el-alert>

            <!-- 数据列表 -->
            <el-table v-else :data="history" stripe style="width: 100%" empty-text="暂无数据" highlight-current-row>
                <el-table-column prop="video_name" label="文件名" width="300">
                    <template #default="{ row }">
                        <div class="file-name">
                            <el-icon>
                                <VideoCamera />
                            </el-icon>
                            <span class="name-text">{{ row.video_name }}</span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column prop="upload_time" label="上传时间" width="200" />


                <el-table-column label="检测" width="120">
                    <template #default="{ row }">
                        <el-button type="success" size="small" @click="startDetection(row)">
                            开始检测
                        </el-button>
                    </template>
                </el-table-column>

                <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                        <el-button type="danger" size="small" @click="">
                            待定操作
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <!-- 检测进度对话框 -->
        <el-dialog v-model="detectionDialogVisible" title="视频检测进度" width="30%" :close-on-click-modal="false" :show-close="false">
            <el-progress :percentage="detectionProgress" :status="detectionStatus" />
            <p class="progress-text">{{ detectionMessage }}</p>
            <template #footer>
                <el-button v-if="detectionStatus === 'success'" type="primary" @click="detectionDialogVisible = false">
                    完成
                </el-button>
                <el-button v-else-if="detectionStatus === 'exception'" type="primary" @click="detectionDialogVisible = false">
                    关闭
                </el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, VideoCamera } from '@element-plus/icons-vue'
import { getVideoHistory, PredictVideo } from '@/api/preview'
import router from '@/router/index'

const history = ref([])
const loading = ref(true)
const error = ref(null)

// 检测相关状态
const detectionDialogVisible = ref(false)
const detectionProgress = ref(0)
const detectionStatus = ref('')
const detectionMessage = ref('')

const fetchHistory = async () => {
    try {
        loading.value = true
        error.value = null
        const response = await getVideoHistory()
        history.value = response.data
    } catch (err) {
        error.value = err.response?.data?.error || '获取历史记录失败'
        history.value = []
    } finally {
        loading.value = false
    }
}

const startDetection = async (row) => {
    detectionDialogVisible.value = true
    detectionProgress.value = 0
    detectionStatus.value = ''
    detectionMessage.value = '正在初始化检测...'

    try {
        // 模拟进度更新
        const updateProgress = () => {
            if (detectionProgress.value < 100) {
                detectionProgress.value += 10
                detectionMessage.value = `正在处理视频 (${detectionProgress.value}%)...`
                setTimeout(updateProgress, 500)
            } else {
                detectionStatus.value = 'success'
                detectionMessage.value = '视频检测完成'
                ElMessage.success('视频检测完成')
            }
        }

        // 实际调用API
        const response = await PredictVideo({ 
            filename: row.video_name,
            onProgress: (progress) => {
                detectionProgress.value = progress
                detectionMessage.value = `正在处理视频 (${progress}%)...`
            }
        })

        // 更新历史记录
        fetchHistory()
        updateProgress()
    } catch (err) {
        detectionStatus.value = 'exception'
        detectionMessage.value = `检测失败: ${err.message}`
        ElMessage.error(`视频检测失败: ${err.message}`)
    }
}

// 返回上传界面
const backUpload = () => {
    router.push('/upload')
}

onMounted(() => {
    fetchHistory()
})
</script>

<style scoped>
.history-container {
    padding: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.file-name {
    display: flex;
    align-items: center;
    gap: 8px;
}

.name-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.error-alert {
    margin-bottom: 20px;
}

.progress-text {
    margin-top: 10px;
    text-align: center;
    color: var(--el-text-color-secondary);
}
</style>