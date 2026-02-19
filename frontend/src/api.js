import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// JWT 토큰을 헤더에 자동 첨부
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
