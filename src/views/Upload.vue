<template>
    <div class="original-size-upload">
        <!-- 图片上传部分 -->
        <el-upload class="image-uploader" action="#" :auto-upload="false" :show-file-list="false"
            :on-change="handleImageChange" :before-upload="beforeImageUpload" accept="image/*">
            <template #trigger>
                <el-button type="primary">选择图片</el-button>
            </template>

            <div v-if="imageData.url" class="image-preview-container">
                <div class="preview-wrapper" :style="previewWrapperStyle">
                    <img :src="imageData.url" :alt="imageData.name" class="original-image" @load="handleImageLoad" />
                </div>
                <div class="image-info">
                    <span>{{ imageData.name }}</span>
                    <span>{{ (imageData.size / 1024).toFixed(2) }} KB</span>
                    <span>{{ imageData.width }} × {{ imageData.height }} 像素</span>
                </div>
            </div>
        </el-upload>

        <div class="upload-actions" v-if="imageData.url">
            <el-button type="success" @click="submitImageUpload">上传图片</el-button>
            <el-button @click="clearImage">清除图片</el-button>
        </div>

        <!-- 视频上传部分 -->
        <el-upload class="video-uploader" action="#" :auto-upload="false" :show-file-list="false"
            :on-change="handleVideoChange" :before-upload="beforeVideoUpload" accept="video/*">
            <template #trigger>
                <el-button type="primary">选择视频</el-button>
            </template>

            <div v-if="videoData.url" class="video-preview-container">
                <div class="preview-wrapper">
                    <video :src="videoData.url" class="original-video" controls
                        @loadedmetadata="handleVideoLoad"></video>
                </div>
                <div class="video-info">
                    <span>{{ videoData.name }}</span>
                    <span>{{ (videoData.size / 1024 / 1024).toFixed(2) }} MB</span>
                    <span>{{ videoData.duration ? videoData.duration.toFixed(2) + '秒' : '' }}</span>
                    <span>{{ videoData.width }} × {{ videoData.height }} 像素</span>
                </div>
            </div>
        </el-upload>

        <div class="upload-actions" v-if="videoData.url">
            <el-button type="success" @click="submitVideoUpload">上传视频</el-button>
            <el-button @click="clearVideo">清除视频</el-button>
        </div>

        <el-dialog v-model="dialogVisible" :title="dialogTitle" width="auto">
            <img v-if="dialogContentType === 'image'" :src="imageData.url" class="dialog-image" />
            <video v-else-if="dialogContentType === 'video'" :src="videoData.url" controls class="dialog-video"></video>
        </el-dialog>
    </div>

    <div class="original-size-upload">
        <div>
            <el-button type="primary" @click="pushHistory">图片历史记录</el-button>
        </div>
        <div>
            <el-button type="primary" @click="pushHistoryVideo">视频历史记录</el-button>
        </div>
    </div>

</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadPhoto, UploadVideo } from '@/api/upload'
import router from '@/router/index'

// 图片数据
const imageData = reactive({
    url: '',
    name: '',
    size: 0,
    width: 0,
    height: 0,
    file: null
})

// 视频数据
const videoData = reactive({
    url: '',
    name: '',
    size: 0,
    width: 0,
    height: 0,
    duration: 0,
    file: null
})

const dialogVisible = ref(false)
const dialogTitle = ref('预览')
const dialogContentType = ref('image') // 'image' 或 'video'
const previewWrapperStyle = ref({})

// 图片加载完成时获取尺寸
const handleImageLoad = (event) => {
    imageData.width = event.target.naturalWidth
    imageData.height = event.target.naturalHeight

    // 如果图片太大，添加滚动条
    if (imageData.width > 800 || imageData.height > 600) {
        previewWrapperStyle.value = {
            maxWidth: '800px',
            maxHeight: '600px',
            overflow: 'auto'
        }
    } else {
        previewWrapperStyle.value = {}
    }
}

// 视频加载元数据时获取信息
const handleVideoLoad = (event) => {
    videoData.width = event.target.videoWidth
    videoData.height = event.target.videoHeight
    videoData.duration = event.target.duration
}

// 图片选择前的验证
const beforeImageUpload = (file) => {
    const isImage = file.type.startsWith('image/')
    const isLt20M = file.size / 1024 / 1024 < 20

    if (!isImage) {
        ElMessage.error('只能上传图片文件!')
        return false
    }

    if (!isLt20M) {
        ElMessage.error('图片大小不能超过20MB!')
        return false
    }

    return true
}

// 视频选择前的验证
const beforeVideoUpload = (file) => {
    const isVideo = file.type.startsWith('video/')
    const isLt100M = file.size / 1024 / 1024 < 100

    if (!isVideo) {
        ElMessage.error('只能上传视频文件!')
        return false
    }

    if (!isLt100M) {
        ElMessage.error('视频大小不能超过100MB!')
        return false
    }

    return true
}

// 处理图片选择
const handleImageChange = (uploadFile) => {
    if (!beforeImageUpload(uploadFile.raw)) return

    // 清除之前的图片URL
    if (imageData.url) {
        URL.revokeObjectURL(imageData.url)
    }

    // 创建新图片URL
    imageData.url = URL.createObjectURL(uploadFile.raw)
    imageData.name = uploadFile.name
    imageData.size = uploadFile.size
    imageData.file = uploadFile.raw
}

// 处理视频选择
const handleVideoChange = (uploadFile) => {
    if (!beforeVideoUpload(uploadFile.raw)) return

    // 清除之前的视频URL
    if (videoData.url) {
        URL.revokeObjectURL(videoData.url)
    }

    // 创建新视频URL
    videoData.url = URL.createObjectURL(uploadFile.raw)
    videoData.name = uploadFile.name
    videoData.size = uploadFile.size
    videoData.file = uploadFile.raw
}

// 清除图片
const clearImage = () => {
    if (imageData.url) {
        URL.revokeObjectURL(imageData.url)
    }
    Object.assign(imageData, {
        url: '',
        name: '',
        size: 0,
        width: 0,
        height: 0,
        file: null
    })
}

// 清除视频
const clearVideo = () => {
    if (videoData.url) {
        URL.revokeObjectURL(videoData.url)
    }
    Object.assign(videoData, {
        url: '',
        name: '',
        size: 0,
        width: 0,
        height: 0,
        duration: 0,
        file: null
    })
}

// 提交上传图片
const submitImageUpload = async () => {
    if (!imageData.file) {
        ElMessage.warning('请先选择图片')
        return
    }

    try {
        const result = await UploadPhoto(imageData.file)
        console.log('图片上传成功', result)
        ElMessage.success('图片上传成功')
    } catch (err) {
        console.error(err.message)
        ElMessage.error('图片上传失败')
    }
}

// 提交上传视频
const submitVideoUpload = async () => {
    if (!videoData.file) {
        ElMessage.warning('请先选择视频')
        return
    }

    try {
        const result = await UploadVideo(videoData.file)
        console.log('视频上传成功', result)
        ElMessage.success('视频上传成功')
    } catch (err) {
        console.error(err.message)
        ElMessage.error('视频上传失败')
    }
}

// 路由跳转
const pushHistory = async () => {
    router.push('/history')
}

const pushHistoryVideo = async () => {
    router.push('/videoHistory')
}
</script>

<style scoped>
.original-size-upload {
    max-width: 500px;
    margin: 20px auto;
    padding: 20px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
}

.original-size-upload>* {
    margin-bottom: 15px;
    /* 为所有直接子元素添加底部间距 */
}

.original-size-upload>*:last-child {
    margin-bottom: 0;
    /* 最后一个元素不需要底部间距 */
}

.image-uploader,
.video-uploader {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
}

.image-preview-container,
.video-preview-container {
    margin-top: 20px;
    border: 1px dashed #ddd;
    padding: 10px;
    border-radius: 4px;
}

.preview-wrapper {
    margin: 0 auto;
    text-align: center;
    background-color: #f5f7fa;
    padding: 10px;
}

.original-image {
    display: block;
    max-width: none;
    height: auto;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

.original-video {
    display: block;
    max-width: 100%;
    max-height: 400px;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

.image-info,
.video-info {
    margin-top: 10px;
    padding: 8px;
    background-color: #f9f9f9;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    font-size: 12px;
    color: #666;
    gap: 10px;
}

.upload-actions {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    gap: 15px;
}

.dialog-image {
    max-width: 80vw;
    max-height: 80vh;
    display: block;
    margin: 0 auto;
}

.dialog-video {
    max-width: 80vw;
    max-height: 80vh;
    display: block;
    margin: 0 auto;
}
</style>