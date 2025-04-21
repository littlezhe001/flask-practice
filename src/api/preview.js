import { get, post } from './request'

export const getUploadHistory = () => get('/api/GetHistory')
export const Predict = (data) => post('/api/predict', data)
export const getVideoHistory = () => get('/api/GetHistory_Video')
export const PredictVideo = (data) => post('/api/predictVideo', data)