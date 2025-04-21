<template>
    <div class="history-container">
        <el-row :gutter="40">
            <!-- 左侧历史记录列表 -->
            <el-col :span="25">
                <el-card shadow="hover" class="history-card">
                    <template #header>
                        <div class="card-header">
                            <el-button type="primary" size="small" :icon="Refresh" @click="fetchHistory"
                                :loading="loading">
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
                    <el-alert v-else-if="error" :title="error" type="error" show-icon :closable="false"
                        class="error-alert">
                        <template #footer>
                            <el-button type="primary" size="small" @click="fetchHistory">
                                重试
                            </el-button>
                        </template>
                    </el-alert>

                    <!-- 数据列表 -->
                    <el-table v-else :data="history" stripe style="width: 100%" empty-text="暂无数据" highlight-current-row
                        @current-change="handleRowClick">
                        <el-table-column prop="photo_name" label="文件名" width="300">
                            <template #default="{ row }">
                                <div class="file-name">
                                    <el-icon>
                                        <Document />
                                    </el-icon>
                                    <span class="name-text">{{ row.photo_name }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column prop="upload_time" label="上传时间" width="200" />

                        <el-table-column label="操作" width="100">
                            <template #default="{ row }">
                                <el-button type="primary" size="small" @click="previewImage(row)">
                                    预览
                                </el-button>
                            </template>
                        </el-table-column>

                        <el-table-column label="检测" width="120">
                            <template #default="{ row }">
                                <el-button type="success" size="small" @click="startDetection(row)">
                                    开始检测
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-col>

            <!-- 右侧图片预览区域 -->
            <el-col :span="40">
                <el-card shadow="hover" class="preview-card">
                    <template #header>
                        <div class="card-header">
                            <span>图片预览</span>
                            <el-button v-if="currentImage?.detections" type="info" size="small"
                                @click="toggleBoxVisibility">
                                {{ showBoxes ? '隐藏检测框' : '显示检测框' }}
                            </el-button>
                        </div>
                    </template>

                    <div v-if="currentImage" class="image-preview-container">
                        <!-- Canvas容器 -->
                        <div class="canvas-container" ref="canvasContainer">
                            <img :src="getImageUrl(currentImage.photo_name)" ref="sourceImage" @load="handleImageLoad"
                                crossorigin="anonymous" style="max-width: 100%; display: block;">
                            <canvas ref="detectionCanvas" style="position: absolute; top: 0; left: 0;"></canvas>
                        </div>

                        <div class="image-info">
                            <p><strong>文件名：</strong>{{ currentImage.photo_name }}</p>
                            <p><strong>上传时间：</strong>{{ currentImage.upload_time }}</p>
                            <p><strong>文件大小：</strong>{{ formatFileSize(currentImage.file_size) }}</p>
                            <div v-if="currentImage.detections" class="detection-info">
                                <el-tag type="success">检测到 {{ currentImage.detections.length }} 个对象</el-tag>
                                <el-button size="small" @click="showDetectionDetails">查看详情</el-button>
                            </div>
                        </div>
                    </div>

                    <div v-else class="empty-preview">
                        <el-empty description="请选择要预览的图片" :image-size="100" />
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 检测结果详情对话框 -->
        <el-dialog v-model="detailDialogVisible" title="检测结果详情" width="50%">
            <el-table :data="currentImage?.detections || []" border>
                <el-table-column prop="class_name" label="类别" width="120" />
                <el-table-column prop="confidence" label="置信度" width="120">
                    <template #default="{ row }">
                        {{ (row.confidence * 100).toFixed(2) }}%
                    </template>
                </el-table-column>
                <el-table-column label="坐标">
                    <template #default="{ row }">
                        [{{ row.bbox[0].toFixed(0) }}, {{ row.bbox[1].toFixed(0) }}, {{ row.bbox[2].toFixed(0) }}, {{
                            row.bbox[3].toFixed(0) }}]
                    </template>
                </el-table-column>
            </el-table>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import {
    Refresh,
    Document
} from '@element-plus/icons-vue'
import { getUploadHistory, Predict } from '@/api/preview'
import router from '@/router/index'

const history = ref([])
const loading = ref(true)
const error = ref(null)
const currentImage = ref(null)
const showBoxes = ref(true)
const detailDialogVisible = ref(false)

// DOM 引用
const sourceImage = ref(null)
const detectionCanvas = ref(null)
const canvasContainer = ref(null)

const fetchHistory = async () => {
    try {
        loading.value = true
        error.value = null
        const response = await getUploadHistory()
        history.value = response.data
    } catch (err) {
        error.value = err.response?.data?.error || '获取历史记录失败'
        history.value = []
    } finally {
        loading.value = false
    }
}

const getImageUrl = (filename) => {
    return `/api/uploaded_photos/${filename}`
}

const previewImage = (row) => {
    currentImage.value = row
    if (row.detections) {
        nextTick(() => {
            if (sourceImage.value?.complete) {
                drawDetectionBoxes()
            }
        })
    }
}

const formatFileSize = (bytes) => {
    if (!bytes) return '未知'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

// 修改startDetection方法以适配后端数据
const startDetection = async (row) => {
    const loadingInstance = ElLoading.service({
        lock: true,
        text: '正在检测中...',
        background: 'rgba(0, 0, 0, 0.7)'
    });

    try {
        currentImage.value = row;
        const response = await Predict({ filename: row.photo_name });

        // 转换数据结构：将bbox对象转为数组[x1,y1,x2,y2]
        currentImage.value.detections = response.detections.flatMap(detection =>
            detection.objects.map(obj => ({
                class_name: obj.class_name,
                confidence: obj.confidence,
                bbox: [obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax]
            }))
        );

        // 图片加载完成后自动绘制
        nextTick(() => {
            if (sourceImage.value?.complete) {
                drawDetectionBoxes();
            }
        });

        ElMessage.success('检测完成');
    } catch (err) {
        ElMessage.error(`检测失败: ${err.message}`);
    } finally {
        loadingInstance.close();
    }
}

const handleRowClick = (row) => {
    if (row) {
        currentImage.value = row
        if (row.detections) {
            nextTick(() => {
                if (sourceImage.value?.complete) {
                    drawDetectionBoxes()
                }
            })
        }
    }
}

// 图片加载完成后绘制检测框
const handleImageLoad = () => {
    if (currentImage.value?.detections) {
        drawDetectionBoxes();
    }
};

// 绘制检测框函数
const drawDetectionBoxes = () => {
    if (!sourceImage.value || !detectionCanvas.value) return;

    const canvas = detectionCanvas.value;
    const ctx = canvas.getContext('2d');
    const img = sourceImage.value;

    // 1. 获取图片的实际显示尺寸
    const displayWidth = img.clientWidth;
    const displayHeight = img.clientHeight;

    // 2. 设置 canvas 的尺寸为显示尺寸（不再用 naturalWidth/Height）
    canvas.width = displayWidth;
    canvas.height = displayHeight;

    // 3. 获取原图尺寸和缩放比例
    const scaleX = displayWidth / img.naturalWidth;
    const scaleY = displayHeight / img.naturalHeight;

    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const classColors = {
        FACE_FEMALE: '#FF1493',
        MALE_BREAST_EXPOSED: '#4169E1'
    };

    currentImage.value.detections.forEach(det => {
        const [x1, y1, x2, y2] = det.bbox;
        const width = (x2 - x1) * scaleX;
        const height = (y2 - y1) * scaleY;
        const offsetX = x1 * scaleX;
        const offsetY = y1 * scaleY;

        const color = classColors[det.class_name] || '#FFA500';

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(offsetX, offsetY, width, height);

        const text = `${det.class_name} ${(det.confidence * 100).toFixed(1)}%`;
        ctx.font = 'bold 12px Arial';
        const textWidth = ctx.measureText(text).width;

        ctx.fillStyle = color + 'CC';
        ctx.fillRect(offsetX, offsetY - 20, textWidth + 10, 20);

        ctx.fillStyle = '#FFFFFF';
        ctx.fillText(text, offsetX + 5, offsetY - 5);
    });
};


const toggleBoxVisibility = () => {
    showBoxes.value = !showBoxes.value
    if (showBoxes.value) {
        drawDetectionBoxes()
    } else {
        const canvas = detectionCanvas.value
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
}

const showDetectionDetails = () => {
    detailDialogVisible.value = true
}

// 返回上传界面
const backUpload = async() =>{
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

.image-preview-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.canvas-container {
    position: relative;
    display: inline-block;
    max-width: 100%;
}

.canvas-container canvas {
    width: 100%;  /* 让 canvas 视觉上也跟图片等宽 */
    height: auto;
}


.image-info {
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 4px;
}

.image-info p {
    margin: 5px 0;
}

.detection-info {
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.empty-preview {
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.image-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--el-color-danger);
}

.image-error .el-icon {
    font-size: 50px;
    margin-bottom: 10px;
}
</style>