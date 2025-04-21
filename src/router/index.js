import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/Upload.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/Upload.vue'),
  },
  {
    path: '/temp',
    name: 'Temp',
    component: () => import('../views/Temp.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
  },
  {
    path: '/videoHistory',
    name: 'VideoHistory',
    component: () => import('../views/VideoHistory.vue'),
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


export default router;