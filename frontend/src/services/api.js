import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Query endpoints
export const querySystem = async (queryData) => {
  const response = await api.post('/query', queryData);
  return response.data;
};

// Ingest endpoints
export const ingestDocument = async (ingestData) => {
  const response = await api.post('/ingest', ingestData);
  return response.data;
};

export const uploadAndIngest = async (file, metadata) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (metadata.ticker) formData.append('ticker', metadata.ticker);
  if (metadata.filing_date) formData.append('filing_date', metadata.filing_date);
  if (metadata.fiscal_year) formData.append('fiscal_year', metadata.fiscal_year);
  
  const response = await api.post('/ingest/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Entity endpoints
export const getEntities = async (params = {}) => {
  const response = await api.get('/entities', { params });
  return response.data;
};

// Company endpoints
export const getCompany = async (ticker) => {
  const response = await api.get(`/companies/${ticker}`);
  return response.data;
};

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(errorMessage));
  }
);

export default api;
