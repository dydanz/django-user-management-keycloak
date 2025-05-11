import axios from 'axios';

const API_URL = '/api';

const setAuthToken = (token) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_URL}/login/`, { username, password });
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token);
      }
      setAuthToken(response.data.token);
    }
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'An error occurred during login' };
  }
};

const logout = async () => {
  try {
    await axios.post(`${API_URL}/logout/`);
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    setAuthToken(null);
  }
};

const checkKeycloakStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/keycloak-check/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to check Keycloak status' };
  }
};

const checkAdminStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/admin-check/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to check admin status' };
  }
};

// Initialize auth token from localStorage
const token = localStorage.getItem('token');
if (token) {
  setAuthToken(token);
}

const authService = {
  login,
  logout,
  checkKeycloakStatus,
  checkAdminStatus,
  setAuthToken,
};

export default authService; 