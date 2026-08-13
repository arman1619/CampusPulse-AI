import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('campuspulse_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const requestId =
    globalThis.crypto && typeof globalThis.crypto.randomUUID === 'function'
      ? globalThis.crypto.randomUUID()
      : Date.now().toString() + '-' + Math.random().toString(16).slice(2);

  config.headers['X-Request-ID'] = requestId;
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('campuspulse_token');
      localStorage.removeItem('campuspulse_user');
    }
    return Promise.reject(error);
  }
);

export default api;
