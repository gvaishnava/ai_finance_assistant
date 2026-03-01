/**
 * API Service for AI Finance Assistant
 */

import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Session management
let sessionId = localStorage.getItem('session_id');

if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('session_id', sessionId);
}

export const getSessionId = () => sessionId;

// Chat API
export const sendMessage = async (message, source = 'chat', metadata = null) => {
    const response = await api.post('/chat', {
        message,
        session_id: sessionId,
        source: source,
        metadata: metadata
    });
    return response.data;
};

export const sendPortfolioMessage = async (holdings, message = 'Analyze my portfolio') => {
    const response = await api.post('/chat/portfolio', {
        holdings,
        message,
        session_id: sessionId,
    });
    return response.data;
};

export const sendGoalMessage = async (goal, message) => {
    const response = await api.post('/chat/goal', {
        ...goal,
        message,
        session_id: sessionId,
    });
    return response.data;
};

export const getChatHistory = async (source = null) => {
    const params = source ? { params: { source } } : {};
    const response = await api.get(`/chat/history/${sessionId}`, params);
    return response.data;
};

// Market API
export const getStockQuote = async (symbol) => {
    const response = await api.get(`/market/quote/${symbol}`);
    return response.data;
};

export const getMarketTrends = async () => {
    const response = await api.get('/market/trends');
    return response.data;
};

export const searchSymbol = async (query) => {
    const response = await api.get(`/market/search/${query}`);
    return response.data;
};

// User API
export const getUserProfile = async () => {
    const response = await api.get(`/user/profile/${sessionId}`);
    return response.data;
};

export const updateUserProfile = async (updates) => {
    const response = await api.put(`/user/profile/${sessionId}`, updates);
    return response.data;
};

export const getFullSession = async () => {
    const response = await api.get(`/user/session/${sessionId}`);
    return response.data;
};

// Health check
export const checkHealth = async () => {
    const response = await api.get('/health');
    return response.data;
};

export default api;
