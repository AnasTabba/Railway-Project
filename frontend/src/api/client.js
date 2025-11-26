import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Auth API
export const authAPI = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  getMe: () => apiClient.get('/auth/me'),
};

// Station API
export const stationAPI = {
  getAll: () => apiClient.get('/stations'),
  getById: (id) => apiClient.get(`/stations/${id}`),
  create: (data) => apiClient.post('/admin/stations', data),
  update: (id, data) => apiClient.put(`/admin/stations/${id}`, data),
  delete: (id) => apiClient.delete(`/admin/stations/${id}`),
};

// Train API
export const trainAPI = {
  getAll: () => apiClient.get('/trains'),
  getById: (id) => apiClient.get(`/trains/${id}`),
  create: (data) => apiClient.post('/admin/trains', data),
  update: (id, data) => apiClient.put(`/admin/trains/${id}`, data),
  delete: (id) => apiClient.delete(`/admin/trains/${id}`),
};

// Search API
export const searchAPI = {
  searchTrains: (source, destination, date, options = {}) => {
    const params = new URLSearchParams({ source, destination, date });
    if (options.depart_after) params.append('depart_after', options.depart_after);
    if (options.depart_before) params.append('depart_before', options.depart_before);
    if (options.max_price) params.append('max_price', options.max_price);
    if (options.className) params.append('class', options.className);
    if (options.sort_by) params.append('sort_by', options.sort_by);
    return apiClient.get(`/search?${params.toString()}`);
  },
  getAvailability: (trainId, date) =>
    apiClient.get(`/trains/${trainId}/availability?date=${date}`),
};

// Booking API
export const bookingAPI = {
  createReservation: (data) => apiClient.post('/reservations', data),
  getReservation: (pnr) => apiClient.get(`/reservations/${pnr}`),
  getUserReservations: () => apiClient.get('/reservations'),
  cancelReservation: (pnr) => apiClient.post(`/reservations/${pnr}/cancel`),
};

// Payment API
export const paymentAPI = {
  processPayment: (reservationId, data) =>
    apiClient.post(`/payments/${reservationId}`, data),
  getPayment: (paymentId) => apiClient.get(`/payments/${paymentId}`),
  getReservationPayment: (pnr) => apiClient.get(`/reservations/${pnr}/payment`),
};

// Admin API
export const adminAPI = {
  getCoachClasses: () => apiClient.get('/admin/coach-classes'),
  createCoachClass: (data) => apiClient.post('/admin/coach-classes', data),
  getCoaches: (trainId) => apiClient.get(`/admin/coaches?train_id=${trainId}`),
  createCoach: (data) => apiClient.post('/admin/coaches', data),
  getSeats: (coachId) => apiClient.get(`/admin/seats?coach_id=${coachId}`),
  createSeat: (data) => apiClient.post('/admin/seats', data),
  getFares: (classId) => apiClient.get(`/admin/fares?class_id=${classId}`),
  createFare: (data) => apiClient.post('/admin/fares', data),
  getServices: (classId) => apiClient.get(`/admin/services?class_id=${classId}`),
  createService: (data) => apiClient.post('/admin/services', data),
  getAllReservations: (page = 1) => apiClient.get(`/admin/reservations?page=${page}`),
  deleteReservation: (id) => apiClient.delete(`/admin/reservations/${id}`),
  getAllUsers: (page = 1) => apiClient.get(`/admin/users?page=${page}`),
  updateUserRole: (userId, role) => apiClient.put(`/admin/users/${userId}/role`, { role }),
};
