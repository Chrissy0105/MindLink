// js/config.js
// Detect the current host and port
const getApiBaseUrl = () => {
    // If we're running on the same port as Flask (5000)
    if (window.location.port === '5000' || window.location.hostname === 'localhost') {
        return 'http://localhost:5000/api';
    }
    // For production or other environments
    return '/api';
};

const API_BASE_URL = getApiBaseUrl();
console.log('API Base URL:', API_BASE_URL);