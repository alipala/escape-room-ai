import axios from 'axios';
import log from '../utils/logger';

const API_URL = 'http://localhost:8000'; // Replace with your backend URL

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  log.info(`Sending request: ${config.method.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  (response) => {
    log.info(`Received response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    log.error(`API error: ${error.message}`);
    return Promise.reject(error);
  }
);

export const createGame = (gameData) => api.post('/games', gameData);
export const generatePuzzle = (gameId) => api.post(`/games/${gameId}/puzzles`);
export const checkAnswer = (answerData) => api.post('/puzzles/check-answer', answerData);
export const createUser = (userData) => api.post('/users/', userData);
export const getUsers = () => api.get('/users/');
export const getUser = (userId) => api.get(`/users/${userId}`);
export const updateUser = (userId, userData) => api.put(`/users/${userId}`, userData);
export const deleteUser = (userId) => api.delete(`/users/${userId}`);