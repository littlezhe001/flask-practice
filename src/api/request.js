import axios from 'axios'

const request = axios.create({
    // baseURL: 'http://localhost:5000',
    timeout: 50000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
request.interceptors.request.use(
    config => {
      // 在发送请求前可以做一些处理
      // 比如添加token
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    error => {
      return Promise.reject(error)
    }
  )
  
  // 响应拦截器
  request.interceptors.response.use(
    response => {
      // 对响应数据做处理
      return response.data
    },
    error => {
      // 处理错误
      if (error.response) {
        switch (error.response.status) {
          case 401:
            // 未授权处理
            console.log('未登录')
            break
          case 404:
            console.log('接口不存在')
            break
          default:
            console.log('服务器错误')
        }
      }
      return Promise.reject(error)
    }
  )
  
  // 导出封装好的方法
  export function get(url, params = {}) {
    return request({
      url,
      method: 'get',
      params // 查询参数
    })
  }
  
  export function post(url, data = {}) {
    return request({
      url,
      method: 'post',
      data // 请求体数据
    })
  }
  
  
  // 默认导出整个实例(如果需要自定义配置可以用这个)
  export default request