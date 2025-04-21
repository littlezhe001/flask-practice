// api/upload.js
import axios from 'axios'

export const UploadPhoto = async (file) => {
  const formData = new FormData()
  formData.append('PhotoFile', file) // 'file' 必须和后端参数名一致
  
  // 关键修复：让浏览器自动设置Content-Type和boundary
  const config = {
    headers: {
      'Content-Type': undefined // 或直接删除这行
    },
    transformRequest: (data) => data // 防止axios转换FormData
  }

  try {
    const response = await axios.post('/api/UploadPhoto', formData, config)
    return response.data
  } catch (error) {
    throw new Error(`上传失败: ${error.message}`)
  }
}

export const UploadVideo = async (file) => {
  const formData = new FormData()
  formData.append('VideoFile', file) // 'file' 必须和后端参数名一致
  
  // 关键修复：让浏览器自动设置Content-Type和boundary
  const config = {
    headers: {
      'Content-Type': undefined // 或直接删除这行
    },
    transformRequest: (data) => data // 防止axios转换FormData
  }

  try {
    const response = await axios.post('/api/UploadVideo', formData, config)
    return response.data
  } catch (error) {
    throw new Error(`上传失败: ${error.message}`)
  }
}