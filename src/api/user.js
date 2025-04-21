import { post } from './request'

// 定义具体的接口
export const login = (data) => post('/api/login', data)
export const register = (data) => post('/api/register', data)   