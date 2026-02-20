import axios from 'axios';

// 브라우저가 접속한 호스트 기준으로 백엔드 URL 결정
// - 맥미니 로컬: localhost → localhost:8000
// - 우분투에서 192.168.0.166:5173 접속 → 192.168.0.166:8000
const backendHost = window.location.hostname;
const api = axios.create({
  baseURL: `http://${backendHost}:8000/api`,
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
