import axios from 'axios';

const api = axios.create({
  baseURL: '/api', // Use relative path for proxying
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
