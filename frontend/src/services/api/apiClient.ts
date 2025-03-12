import axios from 'axios';

// Create an axios instance with common configuration
const apiClient = axios.create({
  baseURL: '/api', // This will use the proxy set up in package.json in development
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for sessions and CSRF tokens
});

// Add a request interceptor for adding tokens, etc.
apiClient.interceptors.request.use(
  (config) => {
    // You can add CSRF token or other headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors (e.g., authentication errors)
    if (error.response) {
      if (error.response.status === 401) {
        // Handle unauthorized - perhaps redirect to login
        console.error('Authentication required');
      } else if (error.response.status === 403) {
        // Handle forbidden
        console.error('Access forbidden');
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
